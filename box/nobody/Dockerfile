ARG DOCKER_REGISTRY
FROM $DOCKER_REGISTRY/chad/challbase

RUN ln -s /run/secrets/flag.txt /flag.txt
ENV KEEP_ROOT=1

WORKDIR /opt/stuff
COPY meme.jpg .
COPY term_server.c /tmp/
RUN apk --no-cache add musl-dev gcc && \
    gcc -o /usr/local/bin/term_server /tmp/term_server.c && \
    rm /tmp/term_server.c && \
    apk --no-cache del musl-dev gcc

EXPOSE 23/tcp
CMD ["term_server"]
