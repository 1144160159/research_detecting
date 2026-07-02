

FROM <NAME>/fedscope_base_image:latest

COPY ./.venv/lib/python3.12/site-packages/flwr/                     /usr/local/lib/python3.12/site-packages/flwr/ 
COPY ./.venv/lib/python3.12/site-packages/flwr-1.8.0.dist-info/     /usr/local/lib/python3.12/site-packages/flwr-1.8.0.dist-info/   


#Required for the log
RUN mkdir -p /fedscope/log
RUN mkdir -p /fedscope/dataset

#Copying the source file
COPY ./client.py        /fedscope/client.py
COPY ./src/             /fedscope/src/


WORKDIR /fedscope/
ENTRYPOINT [ "python", "client.py"]

#FOR BUILDING
#  docker build -f ./client.Dockerfile -t <NAME>/fedscope_client:latest ../
#FOR RUNNING
#  docker run --net host <NAME>/fedscope_client:latest --cid 1
#FOR UPLOADING 
# docker tag fedscope_client:latest <NAME>/fedscope_client:latest
# docker push <NAME>/fedscope_client:latest

