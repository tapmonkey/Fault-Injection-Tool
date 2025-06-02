#!/bin/bash

echo "  Fault Injector 安装与环境准备"

ARCH=$(uname -m)
echo " 当前系统架构: $ARCH"

# Python3 检查与安装提示
if ! command -v python3 &>/dev/null; then
    echo " 未检测到 Python3，请先手动安装。"
    exit 1
fi

# 创建虚拟环境（可选）
# python3 -m venv venv
# source venv/bin/activate

# 安装依赖
echo " 安装 Python 依赖..."
pip3 install -r requirements.txt

# 编译注入器
echo " 编译 libinjector.so..."
cd injector
make clean
make
cd ..

if [[ ! -f injector/libinjector.so ]]; then
    echo " 编译失败，请检查 gcc 工具链和 Makefile"
    exit 1
fi

echo " 安装完成！可以通过 ./start.py 启动系统"

