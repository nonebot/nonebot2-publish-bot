# 这样能分别控制 uv 和 Python 版本
FROM python:3.13.2-slim
COPY --from=ghcr.io/astral-sh/uv:0.6.4 /uv /bin/uv

# 设置时区
ENV TZ=Asia/Shanghai

# 启用字节码编译，加速 NoneFlow 启动
ENV UV_COMPILE_BYTECODE=1

# 在不更新 uv.lock 文件的情况下运行
ENV UV_FROZEN=1

# 从缓存中复制而不是链接，因为缓存是挂载的
ENV UV_LINK_MODE=copy

# 安装依赖
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y git

# Python 依赖
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --project /app/ --no-dev

# 将可执行文件放在环境的路径前面
ENV PATH="/app/.venv/bin:$PATH"

# NoneFlow 本体
COPY bot.py .env /app/
COPY src /app/src/

CMD ["uv", "run", "--project", "/app/", "--no-dev", "/app/bot.py"]
