#!/bin/bash
mkdir -p ./src/in
cp ../assets/test.mp4 ./src/in/test.mp4
docker run --network bridge -v /home/moss/code/stt/app/src/in:/stt/in:z -v /home/moss/code/stt/app/src/out:/stt/out:z --env-file ./stt.env app_app python process.py