# Use Python 3.11 base image with Huawei Cloud mirror
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Configure APT to use Aliyun mirror (for faster package downloads in China)
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's|security.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources; \
    else \
        echo "deb https://mirrors.aliyun.com/debian/ bookworm main" > /etc/apt/sources.list && \
        echo "deb https://mirrors.aliyun.com/debian/ bookworm-updates main" >> /etc/apt/sources.list && \
        echo "deb https://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list; \
    fi

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure pip to use Tsinghua mirror (needed for installing uv)
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# Install uv using pip (faster and more reliable than the install script)
RUN pip install --no-cache-dir uv

# Copy project metadata files needed for dependency installation
# NOTE: README.md must be copied before installing dependencies because pyproject.toml references it
COPY README.md .
COPY pyproject.toml .
COPY src/ ./src/

# Install Python dependencies using uv from pyproject.toml
# uv will read dependencies from [project.dependencies] section
# Using Tsinghua mirror for faster downloads in China
RUN uv pip install --system --no-cache \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -e .

# Copy remaining project files
COPY examples/ ./examples/
COPY langgraph.json .

# Expose LangGraph dev server port
EXPOSE 2024

# Default command: run langgraph dev
# Bind to 0.0.0.0 to allow external access from Docker host
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "2024"]

