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
# GitHub CLI (gh) — PR 자동 생성 등에 사용
# ────────────────────────────────────────────────
RUN mkdir -p -m 755 /etc/apt/keyrings && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        -o /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && \
    apt-get install -y gh && \
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
ENV HOME=/home/docker_user

# ────────────────────────────────────────────────
# Claude Code 플러그인 marketplace 사전 등록
# (호스트 ~/.claude 마운트 없이도 컨테이너 안에서 /plugin 사용 가능)
# ────────────────────────────────────────────────
RUN mkdir -p /home/docker_user/.claude/plugins/marketplaces && \
    git clone --depth 1 https://github.com/anthropics/claude-plugins-official.git \
        /home/docker_user/.claude/plugins/marketplaces/claude-plugins-official && \
    printf '%s\n' \
        '{' \
        '  "claude-plugins-official": {' \
        '    "source": {"source": "github", "repo": "anthropics/claude-plugins-official"},' \
        '    "installLocation": "/home/docker_user/.claude/plugins/marketplaces/claude-plugins-official"' \
        '  }' \
        '}' > /home/docker_user/.claude/plugins/known_marketplaces.json

CMD ["bash"]
