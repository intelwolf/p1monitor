# Build stage - includes compilation tools
FROM debian:bookworm-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install ALL build dependencies needed for compiling Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        gcc \
        g++ \
        make \
        libffi-dev \
        libssl-dev && \
#        cargo \
#        rustc && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages (will compile on ARM v7)
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --target=/install/lib/python3.11/site-packages --no-cache-dir --break-system-packages -r /tmp/requirements.txt

# Runtime stage - minimal dependencies
FROM debian:bookworm-slim

ENV TZ="Europe/Amsterdam" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install only runtime dependencies (no build tools)
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-cryptography \
        python3-bcrypt \
        python3-falcon \
        python3-cairo \
        python3-apt \
        python3-nacl \
        ca-certificates \
        net-tools \
        nginx-full \
        php-fpm \
        php-sqlite3 \
        sqlite3 \
        vim \
        cron \
        sudo \
        logrotate \
        curl \
        iputils-ping \
        iproute2 \
        libffi8 \
        libssl3 \
        socat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy compiled Python packages from builder to correct location
COPY --from=builder /install/lib/python3.11/site-packages /usr/local/lib/python3.11/dist-packages

# Copy binaries/executables (like gunicorn, etc.)
COPY --from=builder /install/lib/python3.11/site-packages/bin /usr/local/bin

# Create groups and user
RUN groupadd -g 1002 gpio && \
    groupadd -g 1001 p1mon && \
    useradd -m -u 1001 -g 1001 -s /bin/bash p1mon && \
    usermod -aG p1mon www-data && \
    usermod -aG www-data,gpio,dialout p1mon

# Setup sudo
RUN echo "p1mon ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo "www-data ALL=(p1mon) NOPASSWD: /p1mon/scripts/*" >> /etc/sudoers

# Verify packages are installed and importable
RUN python3 -c "import psutil; import pytz; import crontab; print('✓ All critical imports successful')"

# Copy application files
COPY --chown=p1mon:p1mon p1mon/ /p1mon/
# Copy additional files
COPY addonsbin /
COPY --chown=p1mon:p1mon addons /

# Pre-compile Python files for faster startup
#RUN python3 -m compileall /usr/local/lib/python3.11/dist-packages/ /p1mon/ 2>/dev/null || true
RUN python3 -m compileall /p1mon/ 2>/dev/null || true

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://127.0.0.1/nginx_status/ || exit 1

USER p1mon

ENTRYPOINT ["/entrypoint.sh"]
