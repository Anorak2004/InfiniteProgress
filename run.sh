#!/bin/bash

# Conda 路径
CONDA_PATH=/home/Anorak/miniconda3
source $CONDA_PATH/etc/profile.d/conda.sh

# 激活环境
conda activate InfiniteProgress

# 创建日志目录（可选）
LOG_DIR=/home/Anorak/work/InfiniteProgress/logs
mkdir -p $LOG_DIR

# 启动 Streamlit 应用并保存日志
/home/Anorak/miniconda3/envs/InfiniteProgress/bin/streamlit run /home/Anorak/work/InfiniteProgress/app.py --server.port 80 --server.address 0.0.0.0 > $LOG_DIR/streamlit.log 2>&1 &

# 输出运行状态
echo "Streamlit 应用正在运行，日志保存在 $LOG_DIR/streamlit.log"

# 退出环境
conda deactivate

