#!/bin/bash

# Build the Docker image
docker build -t mandarin-flashcards .

# Run the container
docker run -p 8502:8502 mandarin-flashcards
