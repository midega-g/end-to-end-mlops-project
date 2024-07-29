#!/usr/bin/env bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")"
fi

CONTAINER_ID=$(docker ps -q --filter "name=cnncls")

if [ -n "$CONTAINER_ID" ]; then
  echo "Stopping container with ID $CONTAINER_ID..."
  docker stop "$CONTAINER_ID"
  
  echo "Removing container with ID $CONTAINER_ID..."
  docker rm -fv "$CONTAINER_ID"
else
  echo "No running container named 'cnncls' found. Starting a new container..."
  docker run -d -p 9696:9696 --name=cnncls \
    -e 'AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }}' \
    -e 'AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }}' \
    -e 'AWS_REGION=${{ secrets.AWS_REGION }}' \
    ${{secrets.AWS_ECR_LOGIN_URI}}/${{ secrets.ECR_REPOSITORY_NAME }}:latest
fi