#!/bin/bash
docker compose build
STT_CONTAINER_ID=$(docker compose run -Td app)
docker network connect bridge $STT_CONTAINER_ID
