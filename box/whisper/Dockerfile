ARG DOCKER_REGISTRY
FROM $DOCKER_REGISTRY/chad/challbase

ENV KEEP_ROOT=1
RUN apk --no-cache add dropbear musl-dev gcc && \
    mkdir /etc/dropbear && \
    addgroup whisper && \
    adduser -G whisper -D whisper && \
    passwd -d whisper

#COPY meme.jpg .
COPY challenge-entrypoint.sh /
COPY whisper.c /opt/whisper.c

EXPOSE 22/tcp
CMD ["/challenge-entrypoint.sh"]
