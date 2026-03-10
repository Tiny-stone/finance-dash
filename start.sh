#!/bin/bash
# 全球市场日报系统 - 启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================"
echo "  全球市场财经日报系统"
echo "======================================"
echo ""

# 检查 Python 版本
python3 --version

# 检查依赖（如已安装则跳过）
echo ""
echo "检查依赖..."
pip3 install --break-system-packages -q -r requirements.txt 2>/dev/null || echo "✓ 依赖已就绪"

# 初始化数据库
echo ""
echo "初始化数据库..."
python3 -c "from database.models import init_db; init_db()"
echo "✓ 数据库就绪"

# 启动 API 服务（后台）
echo ""
echo "启动 API 服务..."
nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
API_PID=$!
echo "✓ API 服务已启动 (PID: $API_PID)"

# 启动定时任务（后台）
echo ""
echo "启动定时任务..."
nohup python3 scheduler/tasks.py > logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "✓ 定时任务已启动 (PID: $SCHEDULER_PID)"

# 保存 PID
echo "$API_PID" > logs/api.pid
echo "$SCHEDULER_PID" > logs/scheduler.pid

echo ""
echo "======================================"
echo "  系统已启动"
echo "======================================"
echo ""
echo "📊 Web 访问：http://localhost:8000"
echo "📝 API 文档：http://localhost:8000/docs"
echo ""
echo "日志文件:"
echo "  - API: logs/api.log"
echo "  - Scheduler: logs/scheduler.log"
echo ""
echo "停止服务：./stop.sh"
echo "查看日志：tail -f logs/api.log"
echo ""
