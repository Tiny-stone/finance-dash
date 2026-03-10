#!/bin/bash
# 全球市场日报系统 - 停止脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "停止服务..."

# 停止 API 服务
if [ -f logs/api.pid ]; then
    PID=$(cat logs/api.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✓ API 服务已停止 (PID: $PID)"
    else
        echo "⚠ API 服务未运行"
    fi
    rm logs/api.pid
else
    # 尝试通过端口查找
    PID=$(lsof -t -i:8000 2>/dev/null || true)
    if [ -n "$PID" ]; then
        kill $PID 2>/dev/null || true
        echo "✓ API 服务已停止 (端口 8000)"
    fi
fi

# 停止定时任务
if [ -f logs/scheduler.pid ]; then
    PID=$(cat logs/scheduler.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✓ 定时任务已停止 (PID: $PID)"
    else
        echo "⚠ 定时任务未运行"
    fi
    rm logs/scheduler.pid
else
    # 尝试通过进程名查找
    PID=$(pgrep -f "scheduler/tasks.py" 2>/dev/null || true)
    if [ -n "$PID" ]; then
        kill $PID 2>/dev/null || true
        echo "✓ 定时任务已停止"
    fi
fi

echo ""
echo "所有服务已停止"
