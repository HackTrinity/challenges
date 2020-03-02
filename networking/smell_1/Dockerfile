ARG DOCKER_REGISTRY
FROM $DOCKER_REGISTRY/chad/challbase

RUN apk --no-cache add python3 && pip3 install pypacker

ENV KEEP_ROOT=1

COPY server.py /
CMD ["python3", "/server.py"]
