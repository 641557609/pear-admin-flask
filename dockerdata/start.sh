#!/bin/bash

# 这里可以设置同步时间等操作

# 运行程序
echo "Starting application..."

# 这里可以修改运行命令
gunicorn -b 0.0.0.0:5000 app:app