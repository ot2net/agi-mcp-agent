FROM python:3.10-slim AS builder

WORKDIR /app

# 复制依赖定义文件
COPY pyproject.toml ./

# 提取依赖并安装
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir toml && \
    python -c "import toml; config = toml.load('pyproject.toml'); print('\n'.join(f'{p}{v.replace(\"^\", \">=\")}' for p, v in config['tool']['poetry']['dependencies'].items() if p != 'python'))" > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY agi_mcp_agent ./agi_mcp_agent
COPY examples ./examples

# 生产阶段
FROM python:3.10-slim

WORKDIR /app

# 从builder阶段复制已安装的软件包和应用程序
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 暴露API端口
EXPOSE 8000

# 创建非root用户运行应用
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

# 运行应用
CMD ["python", "-m", "uvicorn", "agi_mcp_agent.api.server:app", "--host", "0.0.0.0", "--port", "8000"] 