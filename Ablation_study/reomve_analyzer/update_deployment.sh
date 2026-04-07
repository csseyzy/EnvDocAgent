#!/bin/bash
# Azure OpenAI 部署名称更新脚本

echo "============================================="
echo "Azure OpenAI 部署名称更新工具"
echo "============================================="
echo ""
echo "当前配置:"
grep "AZURE_OPENAI_DEPLOYMENT=" .env
echo ""
echo "请输入正确的部署名称（从 Azure Portal 或 Studio 中获取）:"
read -p "部署名称: " deployment_name

if [ -z "$deployment_name" ]; then
    echo "❌ 部署名称不能为空"
    exit 1
fi

echo ""
echo "正在更新 .env 文件..."

# 使用 sed 更新配置
sed -i "s/^AZURE_OPENAI_DEPLOYMENT=.*/AZURE_OPENAI_DEPLOYMENT=$deployment_name/" .env

echo "✓ 已更新为: AZURE_OPENAI_DEPLOYMENT=$deployment_name"
echo ""
echo "新配置:"
grep "AZURE_OPENAI_DEPLOYMENT=" .env
echo ""
echo "============================================="
echo "现在可以运行测试验证配置:"
echo "  source readme/bin/activate"
echo "  python test_azure_openai.py"
echo "============================================="



























