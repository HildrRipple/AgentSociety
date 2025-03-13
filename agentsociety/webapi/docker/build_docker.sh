#!/bin/bash
set -e

# 显示帮助信息
function show_help {
    echo "AgentSociety Docker 镜像构建脚本"
    echo "用法: ./build_docker.sh [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -t, --tag TAG  指定镜像标签 (默认: agentsociety-runner:latest)"
    echo ""
    exit 0
}

# 默认标签
TAG="agentsociety-runner:latest"

# 解析参数
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            ;;
        -t|--tag)
            TAG="$2"
            shift
            shift
            ;;
        *)
            echo "未知选项: $1"
            show_help
            ;;
    esac
done

echo "开始构建 AgentSociety Docker 镜像..."
echo "镜像标签: $TAG"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "脚本目录: $SCRIPT_DIR"

# 获取项目根目录（假设脚本位于agentsociety/agentsociety/webapi/docker/）
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../../../.." && pwd )"
echo "项目根目录: $PROJECT_ROOT"

# 复制Dockerfile和entrypoint.sh到项目根目录
cp "$SCRIPT_DIR/Dockerfile" "$PROJECT_ROOT/"
cp "$SCRIPT_DIR/entrypoint.sh" "$PROJECT_ROOT/"

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 确保 entrypoint.sh 有执行权限
chmod +x entrypoint.sh

# 构建 Docker 镜像
echo "正在构建 Docker 镜像..."
docker build -t $TAG .

# 构建完成后删除临时文件
rm -f "$PROJECT_ROOT/Dockerfile" "$PROJECT_ROOT/entrypoint.sh"

# 检查构建结果
if [ $? -eq 0 ]; then
    echo "Docker 镜像构建成功: $TAG"
    echo ""
    echo "使用示例:"
    echo "  docker run --rm $TAG --help"
    echo ""
    echo "更多信息请参考 $SCRIPT_DIR/README.docker.md"
else
    echo "Docker 镜像构建失败"
    exit 1
fi 