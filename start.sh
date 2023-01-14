#!/bin/bash

# for local use only

# Start the app locally

docker rm -f klerlyappcontainer
# Run the Django Docker image
docker run -d --env-file env -v $(pwd)/app:/app -p 8080:8080 --name klerlyappcontainer klerlyapp --rm $(docker build -q -t klerlyapp .)