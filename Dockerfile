# Use an official Python runtime as a parent image
FROM python:3.9 as builder

# Install BATS testing framework
RUN set -x && \
    apt-get update && \
    apt-get install -y bats && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# This is the second phase where we actually want to run our code
FROM python:3.9-slim

# Install BATS testing framework
RUN set -x && \
    apt-get update && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0 && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the installed dependencies from the previous stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the source code
WORKDIR /app
COPY app.py /app/

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]