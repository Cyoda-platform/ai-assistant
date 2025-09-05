# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies first (this layer will be cached)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        curl \
        wget \
        unzip \
        sudo \
        build-essential \
        ca-certificates \
        gnupg \
        lsb-release \
        python3-dev \
        python3-venv \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        libffi-dev \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        liblzma-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Java 21 from Eclipse Temurin
RUN wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor | tee /etc/apt/trusted.gpg.d/adoptium.gpg > /dev/null && \
    echo "deb https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list && \
    apt-get update && \
    apt-get install -y temurin-21-jdk maven && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Gradle
RUN wget -q https://services.gradle.org/distributions/gradle-8.10.2-bin.zip -O /tmp/gradle.zip && \
    unzip -q /tmp/gradle.zip -d /opt/ && \
    ln -s /opt/gradle-8.10.2/bin/gradle /usr/local/bin/gradle && \
    rm /tmp/gradle.zip

# Set JAVA_HOME for Temurin JDK 21
ENV JAVA_HOME=/usr/lib/jvm/temurin-21-jdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Install Auggie CLI
RUN npm install -g @augmentcode/auggie

# Upgrade pip and install Python package management tools
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir pipx virtualenv poetry && \
    pipx ensurepath

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -s /bin/bash appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Copy application code
COPY . .

# Set ownership and permissions efficiently
RUN chown -R appuser:appuser /app && \
    find /app -name "*.sh" -exec chmod +x {} \;

# Verify installations
RUN python --version && \
    pip --version && \
    pipx --version && \
    poetry --version && \
    java --version && \
    gradle --version && \
    mvn --version && \
    node --version && \
    npm --version

# Set build arguments for GitHub credentials
ARG GITHUB_API_TOKEN
ARG GITHUB_USERNAME
ENV GITHUB_API_TOKEN=${GITHUB_API_TOKEN}
ENV GITHUB_USERNAME=${GITHUB_USERNAME}

# Configure Git with credentials
RUN git config --global credential.helper store && \
    echo "https://${GITHUB_USERNAME}:${GITHUB_API_TOKEN}@github.com" > ~/.git-credentials && \
    git config --global user.email "app-builder@example.com" && \
    git config --global user.name "app-builder"

# Switch to non-root user
USER appuser

# Set up Python environment for appuser
ENV PATH="/home/appuser/.local/bin:$PATH"
RUN pipx ensurepath

# Configure Git for appuser with credentials
RUN git config --global credential.helper store && \
    echo "https://${GITHUB_USERNAME}:${GITHUB_API_TOKEN}@github.com" > ~/.git-credentials && \
    git config --global user.email "app-builder@example.com" && \
    git config --global user.name "app-builder"

# Expose port
EXPOSE 5000

# Run the application
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "1"]
