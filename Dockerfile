FROM debian:9.13
LABEL description="This is a Docker Image for the Loop-Streamer app"
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update
# Testing ENV command
ENV nginx_conf /etc/nginx/nginx.conf
COPY . /app

#VOLUME /home/data /data
#VOLUME [ "/home/test" ]
#VOLUME [ "/home/data" ]

# Install nginx...
WORKDIR /app/nginx-1.18.0
RUN apt-get install build-essential libpcre3 libpcre3-dev libssl-dev zlibc zlib1g zlib1g-dev
RUN ./configure --with-http_ssl_module --add-module=nginx-rtmp-module/
RUN make
RUN make install
# Start nginx
RUN /usr/local/nginx/sbin/nginx

# We need to start the script
EXPOSE 1935
#ENTRYPOINT cat

