#FROM python:3.12

FROM <NAME>/fedscope_base_image:latest
COPY ./.venv/lib/python3.12/site-packages/flwr/                     /usr/local/lib/python3.12/site-packages/flwr/ 
COPY ./.venv/lib/python3.12/site-packages/flwr-1.8.0.dist-info/     /usr/local/lib/python3.12/site-packages/flwr-1.8.0.dist-info/   

#Required for the log
RUN mkdir -p /fedscope/log
RUN mkdir -p /fedscope/vocabularies
RUN mkdir -p /fedscope/models
RUN mkdir -p /fedscope/interess

#Copying the source file
COPY ./server.py 	/fedscope/server.py
COPY ./src/ 		/fedscope/src/


WORKDIR /fedscope/
ENTRYPOINT [ "python", "server.py"]
EXPOSE 8080/tcp
EXPOSE 8080/udp

#FOR BUILDING
#  docker build -f ./server.Dockerfile -t <NAME>/fedscope_server:latest ../
#FOR RUNNING
#  docker run --net host  -p 8080:8080 <NAME>/fedscope_server:latest
#FOR UPLOADING 
# docker tag fedscope_server:latest <NAME>/fedscope_server
# docker push <NAME>/fedscope_server:latest


