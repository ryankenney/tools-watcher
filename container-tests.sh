#!/usr/bin/env bats

@test "build with rootless podman" {
  # Mock commands
  podman() {
    echo "Using podman $@"
  }
  export -f podman
  docker() {
    echo "This should not be called"
  }
  export -f docker

  # Mock EUID to simulate non-root user
  EUID=1000

  # Run the script and capture its output and status
  run source ./build-container build "-t my-image ."
  
  # Verify output and status
  [ "$status" -eq 0 ]
  [[ "$output" == *"Using rootless podman."* ]]
  [[ "$output" == *"Using podman build -t my-image .* ]]
}

@test "run with rootless docker when podman is unavailable" {
  # Mock commands
  podman() {
    return 1
  }
  export -f podman
  docker() {
    echo "Using docker $@"
  }
  export -f docker

  # Mock EUID to simulate non-root user
  EUID=1000

  # Run the script and capture its output and status
  run source ./build-container run "my-image"
  
  # Verify output and status
  [ "$status" -eq 0 ]
  [[ "$output" == *"Using rootless docker."* ]]
  [[ "$output" == *"Using docker run my-image"* ]]
}

@test "build with rootful podman when rootless is not possible" {
  # Mock commands
  podman() {
    echo "Using podman $@"
  }
  export -f podman
  docker() {
    echo "This should not be called"
  }
  export -f docker

  # Mock EUID to simulate root user
  EUID=0

  # Run the script and capture its output and status
  run source ./build-container build "-t my-image ."
  
  # Verify output and status
  [ "$status" -eq 0 ]
  [[ "$output" == *"Using rootful podman."* ]]
  [[ "$output" == *"Using podman build -t my-image .* ]]
}

@test "run with rootful docker when podman is unavailable" {
  # Mock commands
  podman() {
    return 1
  }
  export -f podman
  docker() {
    echo "Using docker $@"
  }
  export -f docker

  # Mock EUID to simulate root user
  EUID=0

  # Run the script and capture its output and status
  run source ./build-container run "my-image"
  
  # Verify output and status
  [ "$status" -eq 0 ]
  [[ "$output" == *"Using rootful docker."* ]]
  [[ "$output" == *"Using docker run my-image"* ]]
}

@test "fail when no tools are available" {
  # Mock commands to fail
  podman() {
    return 1
  }
  export -f podman
  docker() {
    return 1
  }
  export -f docker

  # Run the script and capture its output and status
  run source ./build-container build "-t my-image ."
  
  # Verify output and status
  [ "$status" -eq 1 ]
  [[ "$output" == *"No supported container tool found or insufficient permissions."* ]]
}

@test "fail when no arguments are passed" {
  # Mock any command, it won't be reached anyway
  podman() {
    echo "Using podman $@"
  }
  export -f podman

  # Run the script and capture its output and status
  run source ./build-container
  
  # Verify output and status
  [ "$status" -eq 1 ]
  [[ "$output" == *"Usage: $0 <command> <args-for-command>"* ]]
}
