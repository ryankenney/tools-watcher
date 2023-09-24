# Use an official Python runtime as a parent image
FROM python:3.9 as builder

RUN set -x && \
    apt-get update && \
    apt-get install -y \
        # Bash unit testing
        bats \
        # Used to install node
        curl && \
    # Install node/npm
    # --------
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install nodejs -y && \
    # Cleanup apt
    # --------
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Check Node.js and NPM
RUN /usr/bin/node -v
RUN /usr/bin/npm -v
RUN /usr/bin/npx -v

# Install python dependencies
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install node dependencies
WORKDIR /app
COPY menu-app/package.json /app/menu-app/
COPY menu-app/package-lock.json /app/menu-app/
RUN set -x && \
    cd menu-app && \
    export HOME=/app && \
    npm install

# This is the second phase where we actually want to run our code
FROM python:3.9-slim

RUN set -x && \
    apt-get update && \
    apt-get install -y \
        # Needed for opencv access to video
        libgl1-mesa-glx libglib2.0-0 && \
    # Install node/npm
    # --------
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install nodejs -y && \
    # Cleanup apt
    # --------
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the installed dependencies from the previous stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app/menu-app/node_modules /app/menu-app/node_modules

# Check Node.js and NPM
RUN /usr/bin/node -v
RUN /usr/bin/npm -v
RUN /usr/bin/npx -v

# Copy Node source code
WORKDIR /app
COPY menu-app/package.json /app/menu-app/
COPY menu-app/package-lock.json /app/menu-app/
COPY menu-app/src/ /app/menu-app/src/
COPY menu-app/public/ /app/menu-app/public/

# Build Node app
RUN set -x && \
    cd menu-app && \
    export HOME=/app && \
    npm run build

# Copy python source code (after node build to minimize rebuild time)
WORKDIR /app
COPY app.py /app/

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]