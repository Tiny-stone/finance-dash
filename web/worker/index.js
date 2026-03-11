// Cloudflare Worker - 财经日报 API + 前端静态资源
// 支持：前端请求 + Python 抓取服务推送数据

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // 前端静态资源请求（ASSETS binding 自动处理）
    if (path === '/' || path === '/index.html' || !path.startsWith('/api/')) {
      if (env.ASSETS) {
        return env.ASSETS.fetch(request);
      }
    }

    // CORS 处理
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // ===== 公开 API（前端调用）=====
      
      if (path === '/api/health') {
        return jsonResponse({ 
          status: 'ok', 
          timestamp: new Date().toISOString(), 
          version: '2.0.0',
          service: 'finance-dash-api'
        }, corsHeaders);
      }

      if (path === '/api/reports') {
        return await handleListReports(env, url, corsHeaders);
      }

      if (path.match(/^\/api\/reports\/\d+$/)) {
        const reportId = parseInt(path.split('/').pop());
        return await handleGetReport(env, reportId, corsHeaders);
      }

      if (path === '/api/reports/latest') {
        return await handleLatestReport(env, url, corsHeaders);
      }

      if (path === '/api/symbols') {
        return await handleSymbols(env, request, corsHeaders);
      }

      if (path === '/api/market/summary') {
        return await handleMarketSummary(env, corsHeaders);
      }

      // ===== 内部 API（Python 抓取服务调用，需要密钥验证）=====

      if (path === '/api/internal/push-report') {
        return await handlePushReport(env, request, corsHeaders);
      }

      if (path === '/api/internal/push-market-data') {
        return await handlePushMarketData(env, request, corsHeaders);
      }

      // 404
      return new Response('Not Found', { status: 404, headers: corsHeaders });

    } catch (error) {
      console.error('Error:', error);
      return jsonResponse({ error: error.message }, { ...corsHeaders, 'Content-Type': 'application/json' }, 500);
    }
  },

  // 定时任务触发（Cron）
  async scheduled(event, env, ctx) {
    console.log('Cron triggered:', event.cron);
    
    // 可以在这里调用外部 Python 服务的 HTTP 接口
    // 或者只是记录日志，让 Python 服务自己定时运行
    
    // 示例：调用外部抓取服务
    if (env.FETCHER_URL && env.FETCHER_SECRET) {
      try {
        const reportType = event.cron.includes('11:30') ? 'noon' : 'daily';
        await fetch(`${env.FETCHER_URL}/trigger`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${env.FETCHER_SECRET}`
          },
          body: JSON.stringify({ type: reportType })
        });
        console.log(`Triggered fetcher for ${reportType} report`);
      } catch (e) {
        console.error('Failed to trigger fetcher:', e);
      }
    }
  }
};

// ===== 工具函数 =====

function jsonResponse(data, headers = {}, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...headers, 'Content-Type': 'application/json' }
  });
}

async function verifyInternalAuth(request, env) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return false;
  }
  const token = authHeader.slice(7);
  return token === env.FETCHER_SECRET;
}

// ===== 公开 API 处理函数 =====

async function handleListReports(env, url, corsHeaders) {
  const params = new URLSearchParams(url.search);
  const limit = parseInt(params.get('limit') || '20');
  const reportType = params.get('report_type');

  let query = 'SELECT * FROM daily_reports';
  const conditions = [];
  const values = [];

  if (reportType) {
    conditions.push('report_type = ?');
    values.push(reportType);
  }

  if (conditions.length > 0) {
    query += ' WHERE ' + conditions.join(' AND ');
  }

  query += ' ORDER BY report_date DESC, created_at DESC LIMIT ?';
  values.push(limit);

  const stmt = env.DB.prepare(query).bind(...values);
  const { results } = await stmt.all();

  return jsonResponse({
    count: results?.length || 0,
    data: results || []
  }, corsHeaders);
}

async function handleGetReport(env, reportId, corsHeaders) {
  const stmt = env.DB.prepare('SELECT * FROM daily_reports WHERE id = ?');
  const result = await stmt.bind(reportId).first();

  if (!result) {
    return jsonResponse({ error: 'Report not found' }, corsHeaders, 404);
  }

  return jsonResponse(result, corsHeaders);
}

async function handleLatestReport(env, url, corsHeaders) {
  const params = new URLSearchParams(url.search);
  const reportType = params.get('report_type');

  let query = 'SELECT * FROM daily_reports';
  if (reportType) {
    query += ' WHERE report_type = ?';
    const result = await env.DB.prepare(query).bind(reportType).first();
    if (!result) {
      return jsonResponse({ error: 'No reports found' }, corsHeaders, 404);
    }
    return jsonResponse(result, corsHeaders);
  } else {
    const result = await env.DB.prepare(query + ' ORDER BY report_date DESC, created_at DESC LIMIT 1').first();
    if (!result) {
      return jsonResponse({ error: 'No reports found' }, corsHeaders, 404);
    }
    return jsonResponse(result, corsHeaders);
  }
}

async function handleSymbols(env, request, corsHeaders) {
  if (request.method === 'GET') {
    const { results } = await env.DB.prepare('SELECT * FROM symbols WHERE is_active = 1 ORDER BY market, name').all();
    return jsonResponse({ count: results?.length || 0, data: results || [] }, corsHeaders);
  }

  return jsonResponse({ error: 'Method not allowed' }, corsHeaders, 405);
}

async function handleMarketSummary(env, corsHeaders) {
  // 获取最新的市场概览数据
  const result = await env.DB.prepare(
    'SELECT * FROM market_summary ORDER BY date DESC LIMIT 1'
  ).first();
  
  if (!result) {
    return jsonResponse({ error: 'No market data found' }, corsHeaders, 404);
  }
  
  return jsonResponse(result, corsHeaders);
}

// ===== 内部 API 处理函数（Python 服务推送）=====

async function handlePushReport(env, request, corsHeaders) {
  // 验证密钥
  if (!await verifyInternalAuth(request, env)) {
    return jsonResponse({ error: 'Unauthorized' }, corsHeaders, 401);
  }

  const data = await request.json();
  const { report_date, report_type, content, summary, metadata } = data;

  if (!report_date || !report_type || !content) {
    return jsonResponse({ error: 'Missing required fields' }, corsHeaders, 400);
  }

  try {
    // 检查是否已存在，存在则更新
    const existing = await env.DB.prepare(
      'SELECT id FROM daily_reports WHERE report_date = ? AND report_type = ?'
    ).bind(report_date, report_type).first();

    if (existing) {
      // 更新
      await env.DB.prepare(
        `UPDATE daily_reports 
         SET content = ?, summary = ?, metadata = ?, updated_at = ?
         WHERE id = ?`
      ).bind(
        content, 
        summary || content.substring(0, 200), 
        metadata ? JSON.stringify(metadata) : null,
        new Date().toISOString(),
        existing.id
      ).run();
      
      return jsonResponse({ 
        success: true, 
        action: 'updated',
        id: existing.id,
        report_date,
        report_type
      }, corsHeaders);
    } else {
      // 插入新记录
      const result = await env.DB.prepare(
        `INSERT INTO daily_reports (report_date, report_type, content, summary, metadata, created_at)
         VALUES (?, ?, ?, ?, ?, ?)`
      ).bind(
        report_date,
        report_type,
        content,
        summary || content.substring(0, 200),
        metadata ? JSON.stringify(metadata) : null,
        new Date().toISOString()
      ).run();
      
      return jsonResponse({ 
        success: true, 
        action: 'created',
        id: result.meta?.last_row_id,
        report_date,
        report_type
      }, corsHeaders);
    }
  } catch (error) {
    console.error('Push report error:', error);
    return jsonResponse({ error: error.message }, corsHeaders, 500);
  }
}

async function handlePushMarketData(env, request, corsHeaders) {
  // 验证密钥
  if (!await verifyInternalAuth(request, env)) {
    return jsonResponse({ error: 'Unauthorized' }, corsHeaders, 401);
  }

  const data = await request.json();
  const { date, market, up_count, down_count, flat_count, limit_up, limit_down, indices, metadata } = data;

  if (!date || !market) {
    return jsonResponse({ error: 'Missing required fields' }, corsHeaders, 400);
  }

  try {
    // 检查是否已存在
    const existing = await env.DB.prepare(
      'SELECT id FROM market_summary WHERE date = ? AND market = ?'
    ).bind(date, market).first();

    const total = (up_count || 0) + (down_count || 0) + (flat_count || 0);
    const up_ratio = total > 0 ? ((up_count || 0) / total * 100).toFixed(2) : 0;

    if (existing) {
      await env.DB.prepare(
        `UPDATE market_summary 
         SET up_count = ?, down_count = ?, flat_count = ?, limit_up = ?, limit_down = ?, 
             up_ratio = ?, indices = ?, metadata = ?, updated_at = ?
         WHERE id = ?`
      ).bind(
        up_count || 0, down_count || 0, flat_count || 0, 
        limit_up || 0, limit_down || 0, up_ratio,
        indices ? JSON.stringify(indices) : null,
        metadata ? JSON.stringify(metadata) : null,
        new Date().toISOString(),
        existing.id
      ).run();
      
      return jsonResponse({ success: true, action: 'updated' }, corsHeaders);
    } else {
      await env.DB.prepare(
        `INSERT INTO market_summary 
         (date, market, up_count, down_count, flat_count, limit_up, limit_down, up_ratio, indices, metadata, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      ).bind(
        date, market, up_count || 0, down_count || 0, flat_count || 0,
        limit_up || 0, limit_down || 0, up_ratio,
        indices ? JSON.stringify(indices) : null,
        metadata ? JSON.stringify(metadata) : null,
        new Date().toISOString()
      ).run();
      
      return jsonResponse({ success: true, action: 'created' }, corsHeaders);
    }
  } catch (error) {
    console.error('Push market data error:', error);
    return jsonResponse({ error: error.message }, corsHeaders, 500);
  }
}
