# 使用Python官方镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 创建数据目录
RUN mkdir -p /app/data

# 设置环境变量指向数据目录中的数据库
ENV DATABASE_PATH=/app/data/software_resource.db

# 复制项目文件到容器中
COPY . .

# 安装依赖
RUN pip install --no-cache-dir flask gunicorn

# 暴露端口
EXPOSE 5066

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 启动应用
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:5066", "app:app"]