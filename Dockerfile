FROM debian:9.13
LABEL description="This is a Docker Image for the Loop-Streamer app"
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
# Testing ENV command
ENV nginx_conf /etc/nginx/nginx.conf
COPY . /app
# Change to app directory
WORKDIR /app
#VOLUME /home/data /data
#VOLUME [ "/home/test" ]
#VOLUME [ "/home/data" ]
# Install nginx...
WORKDIR /app/nginx-rtmp-module
RUN ./configure --with-http_ssl_module --add-module=nginx-rtmp-module/
RUN make
RUN make install
RUN /usr/local/nginx/sbin/nginx
# NGINX need to run
# We need to start the script
EXPOSE 1935
#ENTRYPOINT cat
