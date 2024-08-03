# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set noninteractive frontend and configure the timezone
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y tzdata git curl libssl-dev libffi-dev libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libxkbcommon0 libfontconfig1 libfreetype6 ffmpeg && \
    ln -fs /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && \
    echo "America/Los_Angeles" > /etc/timezone

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Install pipx using pip
RUN pip install pipx

# Add pipx to PATH
ENV PATH="/root/.local/bin:$PATH"

# Install Node.js and npm
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Create directories to hold /root and /usr data within /app
RUN mkdir -p /app/root /app/usr

# Move existing /root and /usr contents to the new directories
RUN cp -a /root/. /app/root/ && cp -a /usr/. /app/usr/

# Remove original /root and /usr directories
RUN rm -rf /root /usr

# Create symbolic links to /app/root and /app/usr
RUN ln -s /app/root /root && ln -s /app/usr /usr

# Set the working directory to /app
WORKDIR /app

# Add the existing local clone of the repository
COPY . /app

# Run setup.sh script after copying the files
RUN chmod +x /app/setup.sh && /app/setup.sh

# Reset the DEBIAN_FRONTEND environment variable
ENV DEBIAN_FRONTEND=dialog

# Ensure that the container runs indefinitely to allow access for testing and further configuration
CMD ["tail", "-f", "/dev/null"]
