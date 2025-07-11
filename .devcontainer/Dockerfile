# Base image
FROM python:3.11

# Set working directory
WORKDIR /workspaces/nexus

# Install system dependencies and bash shell
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    coreutils \
    git \
    sudo \
    procps \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global http.sslVerify false

# Create a non-root user with bash shell and grant sudo access
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 -m --shell /bin/bash appuser && \
    echo 'appuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Ensure workspace ownership
RUN mkdir -p /workspaces/nexus && \
    chown -R appuser:appuser /workspaces/nexus


# Switch to non-root user
USER appuser

CMD ["bash"]
