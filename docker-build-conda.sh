#! /bin/bash

docker build \
    --force-rm \
    --no-cache \
    --progress=plain \
    -t axiom-fact-checking-service-api:local \
    -f docker/Dockerfile.conda . \
    2>&1 | tee build.log