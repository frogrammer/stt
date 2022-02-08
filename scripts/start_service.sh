#!/bin/bash
docker cp $1 $STT_CONTAINER_ID:/stt/in
docker exec $STT_CONTAINER_ID python process.py
docker cp $STT_CONTAINER_ID:/stt/out ./