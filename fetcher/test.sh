#!/bin/bash
#
# Finance Dash 抓取服务测试脚本
# 用法: ./test.sh [health|noon|daily|market|all]
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 测试命令
TEST_CMD="${1:-all}"

# 加载环境变量
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
    echo -e "${GREEN}✓ 已加载环境变量${NC}"
else
    echo -e "${YELLOW}⚠ 未找到 .env 文件，使用默认值${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Finance Dash 抓取服务测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 测试 API 连通性
test_health() {
    echo -e "${BLUE}[测试] API 健康检查...${NC}"
    cd "$SCRIPT_DIR"
    if python3 main.py health; then
        echo -e "${GREEN}✓ API 健康检查通过${NC}"
        return 0
    else
        echo -e "${RED}✗ API 健康检查失败${NC}"
        return 1
    fi
}

# 测试市场数据获取
test_market() {
    echo -e "${BLUE}[测试] 市场数据获取...${NC}"
    cd "$SCRIPT_DIR"
    if python3 main.py market; then
        echo -e "${GREEN}✓ 市场数据获取成功${NC}"
        return 0
    else
        echo -e "${RED}✗ 市场数据获取失败${NC}"
        return 1
    fi
}

# 测试午间速览生成
test_noon() {
    echo -e "${BLUE}[测试] 午间速览生成...${NC}"
    cd "$SCRIPT_DIR"
    if python3 main.py noon; then
        echo -e "${GREEN}✓ 午间速览生成成功${NC}"
        return 0
    else
        echo -e "${RED}✗ 午间速览生成失败${NC}"
        return 1
    fi
}

# 测试全天复盘生成
test_daily() {
    echo -e "${BLUE}[测试] 全天复盘生成...${NC}"
    cd "$SCRIPT_DIR"
    if python3 main.py daily; then
        echo -e "${GREEN}✓ 全天复盘生成成功${NC}"
        return 0
    else
        echo -e "${RED}✗ 全天复盘生成失败${NC}"
        return 1
    fi
}

# 运行所有测试
run_all_tests() {
    local failed=0

    echo -e "${BLUE}运行全部测试...${NC}"
    echo ""

    test_health || ((failed++))
    echo ""

    test_market || ((failed++))
    echo ""

    test_noon || ((failed++))
    echo ""

    test_daily || ((failed++))
    echo ""

    echo -e "${BLUE}========================================${NC}"
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}  所有测试通过!${NC}"
    else
        echo -e "${RED}  $failed 个测试失败${NC}"
    fi
    echo -e "${BLUE}========================================${NC}"

    return $failed
}

# 主逻辑
case "$TEST_CMD" in
    health)
        test_health
        ;;
    market)
        test_market
        ;;
    noon)
        test_noon
        ;;
    daily)
        test_daily
        ;;
    all)
        run_all_tests
        ;;
    *)
        echo "用法: $0 [health|market|noon|daily|all]"
        echo ""
        echo "命令说明:"
        echo "  health  - 测试 API 连通性"
        echo "  market  - 测试市场数据获取"
        echo "  noon    - 测试午间速览生成"
        echo "  daily   - 测试全天复盘生成"
        echo "  all     - 运行全部测试 (默认)"
        exit 1
        ;;
esac
