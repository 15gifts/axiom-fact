#! /bin/bash

docker build \
    --force-rm \
    --no-cache \
    -t fact-api:local \
    -f docker/Dockerfile.conda . \
    2>&1 | tee build.log