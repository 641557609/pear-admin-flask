FROM python:3.11-bookworm

# 复制项目文件
RUN mkdir -p /app
COPY . /app/
COPY ./dockerdata/start.sh /app/start.sh
WORKDIR /app/

# 设置必备项
ENV TIME_ZONE Asia/Shanghai

RUN echo "${TIME_ZONE}" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime

# 安装必备库
RUN python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 安装
RUN python3 -m pip install gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 初始化数据库
RUN flask db init
RUN flask db migrate
RUN flask db upgrade
RUN flask admin init

# 运行命令
RUN chmod +x start.sh

# 保持执行
CMD /bin/sh
