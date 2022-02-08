#!/bin/bash
STT_CONTAINER_ID=$(docker compose run -Td app)
docker network connect bridge $STT_CONTAINER_ID
