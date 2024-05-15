#! /bin/bash

CODEARTIFACT_AUTH_TOKEN=`aws codeartifact get-authorization-token --profile user_nonlive_developer --domain code-15gifts --domain-owner 334231600460 --region eu-west-1 --query authorizationToken --output text`

docker build \
    --force-rm \
    --no-cache \
    --build-arg CODEARTIFACT_AUTH_TOKEN=$CODEARTIFACT_AUTH_TOKEN \
    -t axiom-fact-checking-service-api:local \
    -f docker/Dockerfile.conda . \
    2>&1 | tee build.log