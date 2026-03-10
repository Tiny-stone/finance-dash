// Cloudflare Worker - 财经日报 API
// 替代原来的 FastAPI 后端

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS 处理
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // 路由处理
      if (path === '/api/health') {
        return jsonResponse({ status: 'ok', timestamp: new Date().toISOString(), version: '2.0.0' }, corsHeaders);
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

      if (path === '/api/generate/noon') {
        return await handleGenerateReport(env, 'noon', corsHeaders);
      }

      if (path === '/api/generate/daily') {
        return await handleGenerateReport(env, 'daily', corsHeaders);
      }

      if (path === '/api/symbols') {
        return await handleSymbols(env, request, corsHeaders);
      }

      // 404
      return new Response('Not Found', { status: 404, headers: corsHeaders });

    } catch (error) {
      console.error('Error:', error);
      return jsonResponse({ error: error.message }, { ...corsHeaders, 'Content-Type': 'application/json' }, 500);
    }
  }
};

function jsonResponse(data, headers = {}, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...headers, 'Content-Type': 'application/json' }
  });
}

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

  query += ' ORDER BY report_date DESC LIMIT ?';
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
    const { results } = await env.DB.prepare(query).bind(reportType).first();
    if (!results) {
      return jsonResponse({ error: 'No reports found' }, corsHeaders, 404);
    }
    return jsonResponse(results, corsHeaders);
  } else {
    const result = await env.DB.prepare(query + ' ORDER BY report_date DESC LIMIT 1').first();
    if (!result) {
      return jsonResponse({ error: 'No reports found' }, corsHeaders, 404);
    }
    return jsonResponse(result, corsHeaders);
  }
}

async function handleGenerateReport(env, reportType, corsHeaders) {
  // 简化版：生成示例报告
  const date = new Date().toISOString().split('T')[0];
  const content = `📊 ${reportType === 'noon' ? '午间速览' : '全天复盘'} | ${date}
============================================================

🇨🇳 A 股市场
----------------------------------------
涨跌比：待接入

📈 主要指数
----------------------------------------
数据收集中...

============================================================
生成时间：${new Date().toISOString()}`;

  const stmt = env.DB.prepare(`
    INSERT INTO daily_reports (report_date, report_type, content, summary, created_at)
    VALUES (?, ?, ?, ?, ?)
  `);

  await stmt.bind(date, reportType, content, content.substring(0, 200), new Date().toISOString()).run();

  return jsonResponse({
    message: 'Report generated',
    report_type: reportType,
    content: content
  }, corsHeaders);
}

async function handleSymbols(env, request, corsHeaders) {
  if (request.method === 'GET') {
    const { results } = await env.DB.prepare('SELECT * FROM symbols WHERE is_active = 1').all();
    return jsonResponse({ count: results?.length || 0, data: results || [] }, corsHeaders);
  }

  if (request.method === 'POST') {
    const data = await request.json();
    const stmt = env.DB.prepare(`
      INSERT INTO symbols (symbol, name, market, category, is_active)
      VALUES (?, ?, ?, ?, 1)
    `);
    await stmt.bind(data.symbol, data.name, data.market, data.category || 'stock').run();
    return jsonResponse({ message: 'Symbol added' }, corsHeaders);
  }

  return jsonResponse({ error: 'Method not allowed' }, corsHeaders, 405);
}
