#!/usr/bin/env bash

# checks if script is running within a GitHub Actions environment.
# if not, change working directory to the script's directory
if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")"
fi

CONTAINER_NAME="ifood-docker-image"

# get container ID with the given container name 
CONTAINER_ID=$(docker ps -q --filter "name=${CONTAINER_NAME}")

if [ -n "$CONTAINER_ID" ]; then
  echo "Stopping container with ID $CONTAINER_ID..."
  docker stop "$CONTAINER_ID" || { echo "Error stopping the container"; exit 1; }
  
  echo "Removing container with ID $CONTAINER_ID..."
  docker rm -fv "$CONTAINER_ID" || { echo "Error removing the container"; exit 1; }

  echo "No running container named '$CONTAINER_NAME' found. Starting a new container..."
  docker run -d -p 9696:9696 --name="$CONTAINER_NAME" \
    -e 'AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }}' \
    -e 'AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }}' \
    -e 'AWS_REGION=${{ secrets.AWS_REGION }}' \
    ${{secrets.AWS_ECR_LOGIN_URI}}/${{ secrets.ECR_REPOSITORY_NAME }}:latest
  || { echo "Error starting the container"; exit 1; }
else
  echo "No running container named '$CONTAINER_NAME' found. Starting a new container..."
  docker run -d -p 9696:9696 --name="$CONTAINER_NAME" \
    -e 'AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }}' \
    -e 'AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }}' \
    -e 'AWS_REGION=${{ secrets.AWS_REGION }}' \
    ${{secrets.AWS_ECR_LOGIN_URI}}/${{ secrets.ECR_REPOSITORY_NAME }}:latest
  || { echo "Error starting the container"; exit 1; }
fi