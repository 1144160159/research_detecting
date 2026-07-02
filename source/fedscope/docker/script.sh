#/bin/bash
docker build -f ./base.Dockerfile -t <NAME>/fedscope_base_image:latest ../
docker push <NAME>/fedscope_base_image:latest

docker build -f ./client.Dockerfile -t <NAME>/fedscope_client:latest ../
docker push <NAME>/fedscope_client:latest

docker build -f ./server.Dockerfile -t <NAME>/fedscope_server:latest ../
docker push <NAME>/fedscope_server:latest