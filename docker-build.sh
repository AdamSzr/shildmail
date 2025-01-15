#!/bin/bash

if [ "$1" == "build" ]; then
    echo "Building and starting the container..."
    docker build -t shildmail . &&
    docker compose up -d &&
    docker logs -f shildmail
elif [ "$1" == "clean" ]; then
    echo "Stopping and cleaning up the container..."
    docker kill shildmail &&
    docker rm shildmail &&
    docker rmi shildmail
else
    echo "Invalid parameter. Use 'build' to build and start, or 'clean' to stop and remove."
fi
