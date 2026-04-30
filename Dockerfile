# ────────────────────────────────────────────────
# Base: Ubuntu 22.04 + Python 3.10
# ────────────────────────────────────────────────
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ────────────────────────────────────────────────
# System dependencies
# ────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python3-pip \
    git wget curl \
    && rm -rf /var/lib/apt/lists/*

# Node.js 20 LTS — Claude Code 설치에 필요
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# ────────────────────────────────────────────────
# Claude Code CLI
# ────────────────────────────────────────────────
RUN npm install -g @anthropic-ai/claude-code

RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# ────────────────────────────────────────────────
# Python dependencies
# ────────────────────────────────────────────────
RUN pip install --upgrade pip && \
    pip install pytest

# ────────────────────────────────────────────────
# Project setup
# ────────────────────────────────────────────────
WORKDIR /workspace/harness_framework

COPY . .

RUN chmod +x scripts/*.sh

# ────────────────────────────────────────────────
# Non-root user
# ────────────────────────────────────────────────
RUN useradd -m -s /bin/bash docker_user && \
    chown -R docker_user:docker_user /workspace/harness_framework

USER docker_user

CMD ["bash"]
