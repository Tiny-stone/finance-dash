#!/bin/bash
# 定时任务守护进程

cd /root/.openclaw/workspace/finance-dash

# 添加所有必要路径
export PYTHONPATH="/root/.openclaw/workspace/finance-dash:$PYTHONPATH"

# 启动调度器
exec python3 -c "
import sys
sys.path.insert(0, '/root/.openclaw/workspace/finance-dash')
sys.path.insert(0, '/root/.openclaw/workspace/finance-dash/database')
sys.path.insert(0, '/root/.openclaw/workspace/finance-dash/backend')

from scheduler.tasks import start_scheduler
start_scheduler()
" 2>&1
