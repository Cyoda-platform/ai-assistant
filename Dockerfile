# Use an official Python runtime as a parent image
FROM python:3.12@sha256:f78ea8a345769eb3aa1c86cf147dfd68f1a4508ed56f9d7574e4687b02f44dd1

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install essential development tools and Java/Gradle
RUN apt-get update && \
    apt-get install -y \
        git \
        curl \
        wget \
        unzip \
        sudo \
        build-essential \
        software-properties-common \
        ca-certificates \
        gnupg \
        lsb-release \
        && \
    (apt-get install -y openjdk-21-jdk || apt-get install -y openjdk-17-jdk) && \
    apt-get install -y maven && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Gradle (latest version compatible with Java 21)
RUN wget https://services.gradle.org/distributions/gradle-8.10.2-bin.zip -P /tmp && \
    unzip -d /opt/gradle /tmp/gradle-8.10.2-bin.zip && \
    ln -s /opt/gradle/gradle-8.10.2/bin/gradle /usr/bin/gradle && \
    rm /tmp/gradle-8.10.2-bin.zip

# Set JAVA_HOME (detect Java version automatically)
RUN if [ -d "/usr/lib/jvm/java-21-openjdk-amd64" ]; then \
        echo "export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64" >> /etc/environment; \
    elif [ -d "/usr/lib/jvm/java-17-openjdk-amd64" ]; then \
        echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64" >> /etc/environment; \
    else \
        echo "export JAVA_HOME=$(readlink -f /usr/bin/java | sed 's:/bin/java::')" >> /etc/environment; \
    fi

# Source the environment and set for this build
RUN . /etc/environment && export JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Install Auggie CLI globally
RUN npm install -g @augmentcode/auggie

# Set GitHub credentials as build arguments (to avoid hardcoding)
ARG GITHUB_TOKEN
ARG GITHUB_USERNAME

ENV GITHUB_TOKEN=${GITHUB_TOKEN}
ENV GITHUB_USERNAME=${GITHUB_USERNAME}

# Create a non-root user with sudo privileges for better security
RUN useradd -m -s /bin/bash appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Configure Git to use the Personal Access Token in a global .git-credentials file
RUN git config --global credential.helper store && \
    echo "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com" > ~/.git-credentials && \
    git config --global user.email "app-builder@example.com" && \
    git config --global user.name "app-builder"

# Set up Git credentials for the appuser as well
USER appuser
RUN git config --global credential.helper store && \
    echo "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com" > ~/.git-credentials && \
    git config --global user.email "app-builder@example.com" && \
    git config --global user.name "app-builder"

# Switch back to root for remaining setup
USER root

# Verify installations
RUN auggie --version || echo "Auggie CLI installation verification failed"
RUN gradle --version || echo "Gradle installation verification failed"
RUN java --version || echo "Java 21 installation verification failed"
RUN mvn --version || echo "Maven installation verification failed"

# Display versions for debugging
RUN echo "=== Development Environment Versions ===" && \
    echo "Java: $(java --version | head -1)" && \
    echo "Gradle: $(gradle --version | grep Gradle)" && \
    echo "Maven: $(mvn --version | head -1)" && \
    echo "Node.js: $(node --version)" && \
    echo "Auggie: $(auggie --version 2>/dev/null || echo 'Not available')" && \
    echo "========================================="

# Set proper permissions for the app directory
RUN chown -R appuser:appuser /app
RUN chmod -R 755 /app

# Make sure scripts are executable
RUN find /app -name "*.sh" -exec chmod +x {} \;

# Expose the port the app runs on
EXPOSE 5000

# Switch to appuser for running the application (better security)
USER appuser

# Run Django's development server
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "1"]
