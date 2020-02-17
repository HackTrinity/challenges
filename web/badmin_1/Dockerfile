ARG DOCKER_REGISTRY
FROM $DOCKER_REGISTRY/chad/challbase

RUN apk --no-cache add python3
RUN setcap 'cap_net_bind_service=+ep' /usr/bin/python3.8

COPY pre-drop.sh /etc/challbase/

WORKDIR /usr/local/lib/cool_server
COPY cool_server/ ./
EXPOSE 80/tcp
STOPSIGNAL SIGINT
CMD ["python3", "-m", "cool_server"]
