ARG DOCKER_REGISTRY
FROM $DOCKER_REGISTRY/chad/challbase
ENV KEEP_INTERNET=1

WORKDIR /opt/CTFd
RUN apk --no-cache add musl-dev gcc libffi-dev git sqlite libffi python3 python3-dev && \
    git clone --branch 2.2.2 https://github.com/CTFd/CTFd . && \
    rm -rf .git/ && \
    pip3 install -r requirements.txt && \
    apk --no-cache del musl-dev gcc libffi-dev git python3-dev

ENV UPDATE_CHECK=no

COPY pre-drop.sh /etc/challbase/
COPY challenge-entrypoint.sh /

COPY render_version.patch /tmp/
COPY ctfd.db CTFd/ctfd.db
RUN setcap 'cap_net_bind_service=+ep' /usr/bin/python3.8 && \
    patch -p1 < /tmp/render_version.patch && \
    rm /tmp/render_version.patch && \
    chown -R nobody:nogroup .
EXPOSE 80/tcp
CMD ["/challenge-entrypoint.sh"]
