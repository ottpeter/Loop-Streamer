FROM debian:9.13
LABEL description="This is a Docker Image for the Loop-Streamer app"
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN mkdir /home/test
# Testing ENV command
ENV nginx_conf /etc/nginx/nginx.conf
COPY . /app
VOLUME /home/data /data
VOLUME [ "/home/test" ]
# NGINX need to run
# We need to start the script
EXPOSE 1935
