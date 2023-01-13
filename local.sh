#!/bin/bash

# Start the app locally
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

# Run the Django Docker image
docker run -d --env-file env -v $(pwd)/app:/app -p 8080:8080 klerlyapp --rm $(docker build -q -t klerlyapp .) 