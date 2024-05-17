#! /bin/bash

docker build \
    --force-rm \
    --no-cache \
    -t fact-api-conda:local \
    -f docker/Dockerfile.conda . \
    2>&1 | tee build.log