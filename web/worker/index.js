// Cloudflare Worker - 财经日报 API + 前端静态资源
// 支持：前端请求 + Python 抓取服务推送数据

// 前端 HTML 模板（内嵌，避免 assets 配置问题）
const FRONTEND_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全球市场日报</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6; color: #333; background: #f8f9fa; padding: 0;
        }
        
        .container {
            max-width: 800px; margin: 0 auto; background: white;
            min-height: 100vh;
        }
        
        /* Header */
        header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white; padding: 24px 20px; text-align: center;
        }
        
        h1 { 
            font-size: 22px; font-weight: 600; margin-bottom: 8px;
            display: flex; align-items: center; justify-content: center; gap: 8px;
        }
        
        .date-display {
            font-size: 14px; color: rgba(255,255,255,0.7);
            margin-bottom: 16px;
        }
        
        /* Date Picker */
        .date-picker {
            display: flex; align-items: center; justify-content: center; gap: 12px;
            margin-bottom: 16px;
        }
        
        .date-btn {
            background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
            color: white; width: 36px; height: 36px; border-radius: 8px;
            cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center;
            transition: all 0.2s;
        }
        
        .date-btn:hover { background: rgba(255,255,255,0.2); }
        
        .date-input {
            background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
            color: white; padding: 8px 12px; border-radius: 8px; font-size: 14px;
            text-align: center; cursor: pointer;
        }
        
        /* Time Slot Tabs */
        .time-tabs {
            display: flex; gap: 8px; justify-content: center;
        }
        
        .time-tab {
            padding: 8px 16px; border: none; background: rgba(255,255,255,0.1);
            border-radius: 20px; cursor: pointer; font-size: 13px; color: rgba(255,255,255,0.8);
            transition: all 0.2s; font-weight: 500;
        }
        
        .time-tab:hover { background: rgba(255,255,255,0.2); }
        
        .time-tab.active { 
            background: #1890ff; color: white; 
            box-shadow: 0 2px 8px rgba(24,144,255,0.4);
        }
        
        .time-tab .badge {
            display: inline-block; margin-left: 4px; padding: 2px 6px;
            background: rgba(255,255,255,0.2); border-radius: 10px;
            font-size: 10px;
        }
        
        /* Main Content */
        main { padding: 20px; }
        
        /* Hot Summary Section */
        .hot-summary {
            background: linear-gradient(135deg, #fff7e6 0%, #fff2cc 100%);
            border: 1px solid #ffd591; border-radius: 12px;
            padding: 16px; margin-bottom: 20px;
        }
        
        .hot-summary-header {
            display: flex; align-items: center; gap: 8px;
            margin-bottom: 12px; color: #d46b08; font-weight: 600; font-size: 14px;
        }
        
        .hot-summary-content {
            font-size: 14px; line-height: 1.7; color: #5c3d00;
        }
        
        /* Section Cards */
        .section-card {
            background: white; border: 1px solid #e8e8e8;
            border-radius: 12px; padding: 16px; margin-bottom: 16px;
        }
        
        .section-header {
            display: flex; align-items: center; gap: 8px;
            margin-bottom: 12px; font-weight: 600; font-size: 15px; color: #1a1a1a;
        }
        
        .section-header .icon { font-size: 18px; }
        
        /* Market Indices */
        .indices-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
        }
        
        .index-item {
            background: #f8f9fa; border-radius: 8px; padding: 12px;
            text-align: center;
        }
        
        .index-name { font-size: 12px; color: #666; margin-bottom: 4px; }
        
        .index-value { 
            font-size: 18px; font-weight: 600; margin-bottom: 2px;
        }
        
        .index-change { font-size: 12px; font-weight: 500; }
        
        .up { color: #cf1322; }
        .down { color: #389e0d; }
        .flat { color: #666; }
        
        /* Stats Grid */
        .stats-grid {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
        }
        
        .stat-item {
            text-align: center; padding: 12px 8px;
            background: #f8f9fa; border-radius: 8px;
        }
        
        .stat-label { font-size: 11px; color: #999; margin-bottom: 4px; }
        
        .stat-value { font-size: 20px; font-weight: 600; }
        
        .stat-value.up { color: #cf1322; }
        .stat-value.down { color: #389e0d; }
        
        /* Watchlist */
        .watchlist {
            display: flex; flex-direction: column; gap: 8px;
        }
        
        .stock-item {
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px; background: #f8f9fa; border-radius: 8px;
        }
        
        .stock-info { display: flex; flex-direction: column; }
        
        .stock-name { font-weight: 500; font-size: 14px; }
        
        .stock-code { font-size: 11px; color: #999; }
        
        .stock-price {
            text-align: right;
        }
        
        .stock-current { font-size: 16px; font-weight: 600; }
        
        .stock-change { font-size: 12px; }
        
        /* Report Content */
        .report-text {
            font-size: 14px; line-height: 1.8; color: #333;
            white-space: pre-wrap; word-wrap: break-word;
        }
        
        .report-text h3 {
            font-size: 15px; font-weight: 600; margin: 16px 0 8px 0;
            color: #1a1a1a; padding-bottom: 4px; border-bottom: 1px solid #e8e8e8;
        }
        
        .report-text p { margin-bottom: 12px; }
        
        /* History Section */
        .history-section {
            margin-top: 24px; padding-top: 24px;
            border-top: 1px solid #e8e8e8;
        }
        
        .history-header {
            display: flex; align-items: center; gap: 8px;
            margin-bottom: 16px; font-weight: 600; font-size: 15px;
        }
        
        .history-list {
            display: flex; flex-direction: column; gap: 8px;
        }
        
        .history-item {
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px 16px; background: #f8f9fa; border-radius: 8px;
            cursor: pointer; transition: all 0.2s;
        }
        
        .history-item:hover { background: #e8e8e8; }
        
        .history-item.active { 
            background: #e6f7ff; border: 1px solid #91d5ff;
        }
        
        .history-date { font-weight: 500; }
        
        .history-types {
            display: flex; gap: 6px;
        }
        
        .type-badge {
            padding: 2px 8px; border-radius: 10px; font-size: 11px;
        }
        
        .type-badge.premarket { background: #f6ffed; color: #389e0d; }
        .type-badge.noon { background: #fff7e6; color: #d46b08; }
        .type-badge.daily { background: #e6f7ff; color: #096dd9; }
        
        /* Loading & Error */
        .loading {
            text-align: center; padding: 40px; color: #999;
        }
        
        .error {
            background: #fff1f0; border: 1px solid #ffa39e;
            padding: 16px; border-radius: 8px; color: #f5222d; margin-bottom: 16px;
        }
        
        .empty-state {
            text-align: center; padding: 40px; color: #999;
        }
        
        .empty-state .icon { font-size: 48px; margin-bottom: 12px; }
        
        /* Footer */
        footer {
            text-align: center; padding: 20px;
            font-size: 12px; color: #999;
        }
        
        /* Responsive */
        @media (max-width: 480px) {
            header { padding: 20px 16px; }
            h1 { font-size: 18px; }
            main { padding: 16px; }
            .time-tab { padding: 6px 12px; font-size: 12px; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .indices-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📈 全球市场日报</h1>
            <div class="date-display" id="currentDate"></div>
            <div class="date-picker">
                <button class="date-btn" onclick="changeDate(-1)">‹</button>
                <input type="date" class="date-input" id="datePicker" onchange="onDateChange(this.value)">
                <button class="date-btn" onclick="changeDate(1)">›</button>
            </div>
            <div class="time-tabs">
                <button class="time-tab" data-type="premarket" onclick="switchTab('premarket')">
                    🔥 盘前简报
                </button>
                <button class="time-tab" data-type="noon" onclick="switchTab('noon')">
                    ☀️ 午间速览
                </button>
                <button class="time-tab active" data-type="daily" onclick="switchTab('daily')">
                    📊 全天复盘
                </button>
            </div>
        </header>
        
        <main>
            <div id="errorBox" class="error" style="display: none;"></div>
            
            <!-- Hot Summary -->
            <div class="hot-summary" id="hotSummarySection" style="display: none;">
                <div class="hot-summary-header">
                    <span>🔥</span>
                    <span>市场热点</span>
                </div>
                <div class="hot-summary-content" id="hotSummaryContent"></div>
            </div>
            
            <!-- Market Data -->
            <div id="marketDataSection" style="display: none;">
                <!-- Indices -->
                <div class="section-card">
                    <div class="section-header">
                        <span class="icon">📊</span>
                        <span>主要指数</span>
                    </div>
                    <div class="indices-grid" id="indicesGrid"></div>
                </div>
                
                <!-- Market Stats -->
                <div class="section-card">
                    <div class="section-header">
                        <span class="icon">📈</span>
                        <span>涨跌统计</span>
                    </div>
                    <div class="stats-grid" id="statsGrid"></div>
                </div>
                
                <!-- Watchlist -->
                <div class="section-card" id="watchlistCard" style="display: none;">
                    <div class="section-header">
                        <span class="icon">👀</span>
                        <span>关注个股</span>
                    </div>
                    <div class="watchlist" id="watchlist"></div>
                </div>
            </div>
            
            <!-- Report Content -->
            <div class="section-card" id="reportSection" style="display: none;">
                <div class="section-header">
                    <span class="icon">📝</span>
                    <span>详细报告</span>
                </div>
                <div class="report-text" id="reportContent"></div>
            </div>
            
            <!-- Loading State -->
            <div class="loading" id="loadingState">
                <div>加载中...</div>
            </div>
            
            <!-- Empty State -->
            <div class="empty-state" id="emptyState" style="display: none;">
                <div class="icon">📭</div>
                <div>该时段暂无报告</div>
                <div style="font-size: 12px; margin-top: 8px;">请切换其他时段或日期</div>
            </div>
            
            <!-- History -->
            <div class="history-section" id="historySection">
                <div class="history-header">
                    <span>📚</span>
                    <span>历史存档</span>
                </div>
                <div class="history-list" id="historyList"></div>
            </div>
        </main>
        
        <footer>
            <div>最后更新：<span id="lastUpdate">-</span></div>
        </footer>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        let currentDate = new Date().toISOString().split('T')[0];
        let currentType = 'daily';
        let currentReport = null;
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('datePicker').value = currentDate;
            updateDateDisplay();
            loadReport();
            loadHistory();
        });
        
        // Date functions
        function updateDateDisplay() {
            const date = new Date(currentDate);
            document.getElementById('currentDate').textContent = date.toLocaleDateString('zh-CN', {
                year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
            });
        }
        
        function changeDate(delta) {
            const date = new Date(currentDate);
            date.setDate(date.getDate() + delta);
            currentDate = date.toISOString().split('T')[0];
            document.getElementById('datePicker').value = currentDate;
            updateDateDisplay();
            loadReport();
            loadHistory();
        }
        
        function onDateChange(dateStr) {
            currentDate = dateStr;
            updateDateDisplay();
            loadReport();
            loadHistory();
        }
        
        // Tab switching
        function switchTab(type) {
            currentType = type;
            document.querySelectorAll('.time-tab').forEach(tab => {
                tab.classList.toggle('active', tab.dataset.type === type);
            });
            loadReport();
        }
        
        // Load report for current date and type
        async function loadReport() {
            const loadingState = document.getElementById('loadingState');
            const emptyState = document.getElementById('emptyState');
            const errorBox = document.getElementById('errorBox');
            const hotSummarySection = document.getElementById('hotSummarySection');
            const marketDataSection = document.getElementById('marketDataSection');
            const reportSection = document.getElementById('reportSection');
            
            // Reset states
            loadingState.style.display = 'block';
            emptyState.style.display = 'none';
            errorBox.style.display = 'none';
            hotSummarySection.style.display = 'none';
            marketDataSection.style.display = 'none';
            reportSection.style.display = 'none';
            
            try {
                const response = await fetch(`${API_BASE}/api/reports?date=${currentDate}&report_type=${currentType}`);
                
                if (!response.ok) {
                    throw new Error('加载失败');
                }
                
                const data = await response.json();
                
                loadingState.style.display = 'none';
                
                if (data.count === 0) {
                    emptyState.style.display = 'block';
                    currentReport = null;
                } else {
                    currentReport = data.data[0];
                    renderReport(currentReport);
                }
                
            } catch (err) {
                loadingState.style.display = 'none';
                errorBox.textContent = `加载失败：${err.message}`;
                errorBox.style.display = 'block';
            }
        }
        
        // Render report data
        function renderReport(report) {
            const hotSummarySection = document.getElementById('hotSummarySection');
            const marketDataSection = document.getElementById('marketDataSection');
            const reportSection = document.getElementById('reportSection');
            
            // Hot summary
            if (report.hot_summary) {
                document.getElementById('hotSummaryContent').textContent = report.hot_summary;
                hotSummarySection.style.display = 'block';
            }
            
            // Parse metadata
            let metadata = {};
            try {
                metadata = JSON.parse(report.metadata || '{}');
            } catch (e) {}
            
            // Render indices
            if (metadata.indices && metadata.indices.length > 0) {
                renderIndices(metadata.indices);
                marketDataSection.style.display = 'block';
            }
            
            // Render stats
            if (metadata.market_stats) {
                renderStats(metadata.market_stats);
            }
            
            // Render watchlist
            if (metadata.watchlist && metadata.watchlist.length > 0) {
                renderWatchlist(metadata.watchlist);
            }
            
            // Render report content
            if (report.content) {
                document.getElementById('reportContent').innerHTML = formatContent(report.content);
                reportSection.style.display = 'block';
            }
            
            // Update last update time
            document.getElementById('lastUpdate').textContent = new Date(report.created_at).toLocaleString('zh-CN');
        }
        
        function renderIndices(indices) {
            const grid = document.getElementById('indicesGrid');
            grid.innerHTML = indices.map(idx => {
                const changeClass = idx.change > 0 ? 'up' : idx.change < 0 ? 'down' : 'flat';
                const changeSign = idx.change > 0 ? '+' : '';
                return `
                    <div class="index-item">
                        <div class="index-name">${idx.name}</div>
                        <div class="index-value ${changeClass}">${idx.value}</div>
                        <div class="index-change ${changeClass}">${changeSign}${idx.change}%</div>
                    </div>
                `;
            }).join('');
        }
        
        function renderStats(stats) {
            const grid = document.getElementById('statsGrid');
            const total = stats.up + stats.down + stats.flat;
            grid.innerHTML = `
                <div class="stat-item">
                    <div class="stat-label">上涨</div>
                    <div class="stat-value up">${stats.up || 0}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">下跌</div>
                    <div class="stat-value down">${stats.down || 0}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">平盘</div>
                    <div class="stat-value">${stats.flat || 0}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">涨跌比</div>
                    <div class="stat-value">${total > 0 ? ((stats.up/total)*100).toFixed(1) : 0}%</div>
                </div>
            `;
        }
        
        function renderWatchlist(stocks) {
            const container = document.getElementById('watchlist');
            document.getElementById('watchlistCard').style.display = 'block';
            container.innerHTML = stocks.map(stock => {
                const changeClass = stock.change > 0 ? 'up' : stock.change < 0 ? 'down' : 'flat';
                const changeSign = stock.change > 0 ? '+' : '';
                return `
                    <div class="stock-item">
                        <div class="stock-info">
                            <div class="stock-name">${stock.name}</div>
                            <div class="stock-code">${stock.code}</div>
                        </div>
                        <div class="stock-price">
                            <div class="stock-current ${changeClass}">${stock.price}</div>
                            <div class="stock-change ${changeClass}">${changeSign}${stock.change}%</div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function formatContent(content) {
            // Simple markdown-like formatting
            return content
                .replace(/^### (.+)$/gm, '<h3>$1</h3>')
                .replace(/^## (.+)$/gm, '<h3>$1</h3>')
                .replace(/^# (.+)$/gm, '<h3>$1</h3>')
                .replace(/\n\n/g, '</p><p>')
                .replace(/\n/g, '<br>');
        }
        
        // Load history
        async function loadHistory() {
            try {
                const response = await fetch(`${API_BASE}/api/reports/by-date/${currentDate}`);
                if (!response.ok) throw new Error('加载历史失败');
                
                const data = await response.json();
                renderHistory(data.data || []);
            } catch (err) {
                console.error('History load error:', err);
            }
        }
        
        function renderHistory(reports) {
            const list = document.getElementById('historyList');
            
            if (reports.length === 0) {
                list.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">暂无历史记录</div>';
                return;
            }
            
            // Group by date
            const byDate = {};
            reports.forEach(r => {
                if (!byDate[r.report_date]) byDate[r.report_date] = [];
                byDate[r.report_date].push(r);
            });
            
            const sortedDates = Object.keys(byDate).sort().reverse().slice(0, 7);
            
            list.innerHTML = sortedDates.map(date => {
                const dayReports = byDate[date];
                const types = dayReports.map(r => r.report_type);
                const isToday = date === currentDate;
                
                return `
                    <div class="history-item ${isToday ? 'active' : ''}" onclick="goToDate('${date}')">
                        <div class="history-date">${formatDate(date)}</div>
                        <div class="history-types">
                            ${types.includes('premarket') ? '<span class="type-badge premarket">盘前</span>' : ''}
                            ${types.includes('noon') ? '<span class="type-badge noon">午间</span>' : ''}
                            ${types.includes('daily') ? '<span class="type-badge daily">全天</span>' : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function goToDate(date) {
            currentDate = date;
            document.getElementById('datePicker').value = date;
            updateDateDisplay();
            loadReport();
            loadHistory();
        }
        
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
        }
    </script>
</body>
</html>`;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

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
      // 前端首页
      if (path === '/' || path === '/index.html') {
        return new Response(FRONTEND_HTML, {
          headers: { 'Content-Type': 'text/html; charset=utf-8' }
        });
      }

      // ===== 公开 API =====
      
      if (path === '/api/health') {
        return jsonResponse({ 
          status: 'ok', 
          timestamp: new Date().toISOString(), 
          version: '3.0.0',
          service: 'finance-dash-api'
        }, corsHeaders);
      }

      // 列表查询 - 支持 date 和 report_type 过滤
      if (path === '/api/reports') {
        return await handleListReports(env, url, corsHeaders);
      }

      // 获取某日所有时段报告
      if (path.match(/^\/api\/reports\/by-date\/[^/]+$/)) {
        const date = path.split('/').pop();
        return await handleReportsByDate(env, date, corsHeaders);
      }

      // 获取单个报告
      if (path.match(/^\/api\/reports\/\d+$/)) {
        const reportId = parseInt(path.split('/').pop());
        return await handleGetReport(env, reportId, corsHeaders);
      }

      // 获取最新报告（兼容旧接口）
      if (path === '/api/reports/latest') {
        return await handleLatestReport(env, url, corsHeaders);
      }

      if (path === '/api/symbols') {
        return await handleSymbols(env, request, corsHeaders);
      }

      if (path === '/api/market/summary') {
        return await handleMarketSummary(env, corsHeaders);
      }

      // ===== 内部 API（Python 抓取服务调用）=====

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

  // 定时任务
  async scheduled(event, env, ctx) {
    console.log('Cron triggered:', event.cron);
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

// ===== API 处理函数 =====

async function handleListReports(env, url, corsHeaders) {
  const params = new URLSearchParams(url.search);
  const limit = parseInt(params.get('limit') || '20');
  const reportType = params.get('report_type');
  const date = params.get('date');

  let query = 'SELECT * FROM daily_reports';
  const conditions = [];
  const values = [];

  if (date) {
    conditions.push('report_date = ?');
    values.push(date);
  }

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

async function handleReportsByDate(env, date, corsHeaders) {
  // 获取某日期所有时段的报告
  const stmt = env.DB.prepare(
    'SELECT * FROM daily_reports WHERE report_date = ? ORDER BY created_at ASC'
  ).bind(date);
  const { results } = await stmt.all();

  // 按时段分组
  const byType = { premarket: null, noon: null, daily: null };
  (results || []).forEach(r => {
    if (byType.hasOwnProperty(r.report_type)) {
      byType[r.report_type] = r;
    }
  });

  return jsonResponse({
    date: date,
    count: results?.length || 0,
    data: results || [],
    by_type: byType
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
  const result = await env.DB.prepare(
    'SELECT * FROM market_summary ORDER BY date DESC LIMIT 1'
  ).first();
  
  if (!result) {
    return jsonResponse({ error: 'No market data found' }, corsHeaders, 404);
  }
  
  return jsonResponse(result, corsHeaders);
}

async function handlePushReport(env, request, corsHeaders) {
  if (!await verifyInternalAuth(request, env)) {
    return jsonResponse({ error: 'Unauthorized' }, corsHeaders, 401);
  }

  const data = await request.json();
  const { report_date, report_type, content, summary, hot_summary, metadata } = data;

  if (!report_date || !report_type || !content) {
    return jsonResponse({ error: 'Missing required fields' }, corsHeaders, 400);
  }

  try {
    const existing = await env.DB.prepare(
      'SELECT id FROM daily_reports WHERE report_date = ? AND report_type = ?'
    ).bind(report_date, report_type).first();

    if (existing) {
      await env.DB.prepare(
        `UPDATE daily_reports SET content = ?, summary = ?, hot_summary = ?, metadata = ?, updated_at = ? WHERE id = ?`
      ).bind(content, summary || content.substring(0, 200), 
        hot_summary || null,
        metadata ? JSON.stringify(metadata) : null,
        new Date().toISOString(), existing.id).run();
      
      return jsonResponse({ success: true, action: 'updated', id: existing.id }, corsHeaders);
    } else {
      const result = await env.DB.prepare(
        `INSERT INTO daily_reports (report_date, report_type, content, summary, hot_summary, metadata, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?)`
      ).bind(report_date, report_type, content, summary || content.substring(0, 200),
        hot_summary || null,
        metadata ? JSON.stringify(metadata) : null, new Date().toISOString()).run();
      
      return jsonResponse({ success: true, action: 'created', id: result.meta?.last_row_id }, corsHeaders);
    }
  } catch (error) {
    return jsonResponse({ error: error.message }, corsHeaders, 500);
  }
}

async function handlePushMarketData(env, request, corsHeaders) {
  if (!await verifyInternalAuth(request, env)) {
    return jsonResponse({ error: 'Unauthorized' }, corsHeaders, 401);
  }

  const data = await request.json();
  const { date, market, up_count, down_count, flat_count, limit_up, limit_down, indices, metadata } = data;

  if (!date || !market) {
    return jsonResponse({ error: 'Missing required fields' }, corsHeaders, 400);
  }

  try {
    const existing = await env.DB.prepare(
      'SELECT id FROM market_summary WHERE date = ? AND market = ?'
    ).bind(date, market).first();

    const total = (up_count || 0) + (down_count || 0) + (flat_count || 0);
    const up_ratio = total > 0 ? ((up_count || 0) / total * 100).toFixed(2) : 0;

    if (existing) {
      await env.DB.prepare(
        `UPDATE market_summary SET up_count = ?, down_count = ?, flat_count = ?, 
         limit_up = ?, limit_down = ?, up_ratio = ?, indices = ?, metadata = ?, updated_at = ? WHERE id = ?`
      ).bind(up_count || 0, down_count || 0, flat_count || 0, limit_up || 0, limit_down || 0, 
        up_ratio, indices ? JSON.stringify(indices) : null, metadata ? JSON.stringify(metadata) : null,
        new Date().toISOString(), existing.id).run();
      
      return jsonResponse({ success: true, action: 'updated' }, corsHeaders);
    } else {
      await env.DB.prepare(
        `INSERT INTO market_summary (date, market, up_count, down_count, flat_count, limit_up, limit_down, up_ratio, indices, metadata, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      ).bind(date, market, up_count || 0, down_count || 0, flat_count || 0, limit_up || 0, limit_down || 0,
        up_ratio, indices ? JSON.stringify(indices) : null, metadata ? JSON.stringify(metadata) : null,
        new Date().toISOString()).run();
      
      return jsonResponse({ success: true, action: 'created' }, corsHeaders);
    }
  } catch (error) {
    return jsonResponse({ error: error.message }, corsHeaders, 500);
  }
}
