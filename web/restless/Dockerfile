ARG DOCKER_REGISTRY
FROM $DOCKER_REGISTRY/chad/challbase

RUN apk --no-cache add python3
RUN setcap 'cap_net_bind_service=+ep' /usr/bin/python3.8
COPY requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt

COPY pre-drop.sh /etc/challbase/

WORKDIR /opt
COPY restless.py ./
EXPOSE 80/tcp
CMD ["gunicorn", "restless:app", "--bind", "[::]:80", "--workers", "1"]
