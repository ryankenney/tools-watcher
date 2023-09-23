#!/bin/bash

# Exit the script if any command fails
set -e
# Exit the script if any uninitialized variable is used
set -u
# Exit the script if a command in a pipeline fails
set -o pipefail

# Function to execute arbitrary command using rootless podman
execute_rootless_podman() {
  podman "$@"
}

# Function to execute arbitrary command using rootless docker
execute_rootless_docker() {
  docker "$@"
}

# Function to execute arbitrary command using rootful podman
execute_rootful_podman() {
  sudo podman "$@"
}

# Function to execute arbitrary command using rootful docker
execute_rootful_docker() {
  sudo docker "$@"
}

# Check for argument (command)
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <command> <args-for-command>"
  exit 1
fi

# Check for each tool and perform the specified command using the first available one
if command -v podman &> /dev/null && podman info &> /dev/null && [ "$EUID" -ne 0 ]; then
  echo "Using rootless podman."
  execute_rootless_podman "$@"
elif command -v docker &> /dev/null && docker info &> /dev/null && [ "$EUID" -ne 0 ]; then
  echo "Using rootless docker."
  execute_rootless_docker "$@"
elif command -v podman &> /dev/null && sudo podman info &> /dev/null; then
  echo "Using rootful podman."
  execute_rootful_podman "$@"
elif command -v docker &> /dev/null && sudo docker info &> /dev/null; then
  echo "Using rootful docker."
  execute_rootful_docker "$@"
else
  echo "No supported container tool found or insufficient permissions."
  exit 1
fi
