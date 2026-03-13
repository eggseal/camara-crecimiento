FROM alpine:latest

RUN apk add --no-cache ffmpeg netcat-openbsd

COPY ./client.sh /usr/local/bin/client.sh

RUN chmod +x /usr/local/bin/client.sh

CMD [ "/bin/sh", "/usr/local/bin/client.sh" ]