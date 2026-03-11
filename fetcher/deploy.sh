#!/bin/bash
#
# Finance Dash 抓取服务部署脚本
# 用法: ./deploy.sh [安装路径]
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认安装路径
INSTALL_DIR="${1:-/opt/finance-dash/fetcher}"
SERVICE_NAME="finance-dash-fetcher"
CURRENT_USER=$(whoami)

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Finance Dash 抓取服务部署脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠ 警告: 未使用 root 权限运行，部分功能可能受限${NC}"
    echo "建议: sudo ./deploy.sh"
    echo ""
fi

echo -e "${BLUE}[1/6] 检查系统环境...${NC}"

# 检查 Python 版本
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ 未找到 Python3，请先安装 Python 3.8+${NC}"
    exit 1
fi

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠ 未找到 pip3，尝试安装...${NC}"
    apt-get update && apt-get install -y python3-pip
fi

echo -e "${BLUE}[2/6] 创建安装目录...${NC}"
if [ "$EUID" -eq 0 ]; then
    mkdir -p "$INSTALL_DIR"
    # 设置目录权限给当前用户
    chown -R "$CURRENT_USER:$CURRENT_USER" "$INSTALL_DIR"
else
    mkdir -p "$INSTALL_DIR"
fi
echo -e "${GREEN}✓ 安装目录: $INSTALL_DIR${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}[3/6] 复制项目文件...${NC}"
cp -r "$SCRIPT_DIR"/*.py "$INSTALL_DIR/"
cp "$SCRIPT_DIR"/requirements.txt "$INSTALL_DIR/"
if [ -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env" "$INSTALL_DIR/"
    echo -e "${GREEN}✓ 已复制环境变量文件${NC}"
else
    cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env"
    echo -e "${YELLOW}⚠ 未找到 .env，已复制 .env.example，请编辑 $INSTALL_DIR/.env 配置实际值${NC}"
fi
echo -e "${GREEN}✓ 文件复制完成${NC}"

echo -e "${BLUE}[4/6] 安装 Python 依赖...${NC}"
cd "$INSTALL_DIR"
pip3 install -r requirements.txt --user 2>/dev/null || pip3 install -r requirements.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"

echo -e "${BLUE}[5/6] 创建日志目录...${NC}"
LOG_DIR="/var/log/finance-dash"
if [ "$EUID" -eq 0 ]; then
    mkdir -p "$LOG_DIR"
    chown -R "$CURRENT_USER:$CURRENT_USER" "$LOG_DIR"
else
    LOG_DIR="$HOME/.local/log/finance-dash"
    mkdir -p "$LOG_DIR"
fi
echo -e "${GREEN}✓ 日志目录: $LOG_DIR${NC}"

# 创建日志文件
 touch "$LOG_DIR/fetcher.log"
 touch "$LOG_DIR/fetcher-error.log"

echo -e "${BLUE}[6/6] 配置定时任务...${NC}"

# 生成 crontab 内容
CRON_CONTENT="# Finance Dash 抓取服务定时任务
# 午间速览 - 工作日 11:35
35 11 * * 1-5 cd $INSTALL_DIR && python3 main.py noon >> $LOG_DIR/fetcher.log 2>> $LOG_DIR/fetcher-error.log

# 全天复盘 - 工作日 15:35
35 15 * * 1-5 cd $INSTALL_DIR && python3 main.py daily >> $LOG_DIR/fetcher.log 2>> $LOG_DIR/fetcher-error.log

# 市场数据推送 - 工作日每小时
0 9-15 * * 1-5 cd $INSTALL_DIR && python3 main.py market >> $LOG_DIR/fetcher.log 2>> $LOG_DIR/fetcher-error.log
"

# 保存 crontab 到文件
echo "$CRON_CONTENT" > "$INSTALL_DIR/crontab.txt"
echo -e "${GREEN}✓ 定时任务配置已保存到: $INSTALL_DIR/crontab.txt${NC}"

# 尝试安装 crontab
if command -v crontab &> /dev/null; then
    # 备份当前 crontab
    crontab -l > "$INSTALL_DIR/crontab.backup" 2>/dev/null || true

    # 添加新任务
    (crontab -l 2>/dev/null | grep -v "Finance Dash"; echo "$CRON_CONTENT") | crontab -
    echo -e "${GREEN}✓ 定时任务已安装${NC}"
    echo ""
    echo -e "${BLUE}当前定时任务:${NC}"
    crontab -l | grep -A 10 "Finance Dash"
else
    echo -e "${YELLOW}⚠ 未找到 crontab，请手动添加以下定时任务:${NC}"
    echo ""
    echo "$CRON_CONTENT"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}安装路径:${NC} $INSTALL_DIR"
echo -e "${BLUE}日志路径:${NC} $LOG_DIR"
echo ""
echo -e "${YELLOW}后续步骤:${NC}"
echo "  1. 编辑环境变量: nano $INSTALL_DIR/.env"
echo "  2. 测试 API 连通: $INSTALL_DIR/test.sh"
echo "  3. 查看日志: tail -f $LOG_DIR/fetcher.log"
echo "  4. 手动运行: cd $INSTALL_DIR && python3 main.py health"
echo ""
echo -e "${YELLOW}systemd 服务安装 (可选):${NC}"
echo "  sudo cp $SCRIPT_DIR/finance-dash-fetcher.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable finance-dash-fetcher"
echo "  sudo systemctl start finance-dash-fetcher"
echo ""
