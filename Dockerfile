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
WORKDIR /app/
# Install all dependencies
RUN apt-get install -y build-essential libpcre3 libpcre3-dev libssl-dev zlibc zlib1g zlib1g-dev python3.5 python3-pip ffmpeg

RUN tar xvfz nginx-1.18.0.tar.gz
RUN mkdir -p /app/nginx-1.18.0/nginx-rtmp-module
RUN mv /app/nginx-rtmp-module/* /app/nginx-1.18.0/nginx-rtmp-module
WORKDIR /app/nginx-1.18.0/
RUN ./configure --with-http_ssl_module --add-module=nginx-rtmp-module/
RUN make
RUN make install
COPY nginx.conf /usr/local/nginx/conf/nginx.conf

# Install moviepy
RUN pip3 install moviepy

# Create logs directory
RUN mkdir -p /home/logs

# Start app
#ENTRYPOINT ["/usr/local/nginx/sbin/nginx"]
WORKDIR /app
#ENTRYPOINT ["python3.5", "main.py", "/app/"]
ENTRYPOINT ["/app/start.sh"]

# We need to start the script
EXPOSE 1935
#ENTRYPOINT cat


