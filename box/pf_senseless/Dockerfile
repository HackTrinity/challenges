ARG DOCKER_REGISTRY
FROM $DOCKER_REGISTRY/chad/challbase

RUN apk --no-cache add qemu-system-aarch64

ENV KEEP_ROOT=1
ENV KEEP_NET_ADMIN=1
ENV CHALLENGE_IP=192.168.147.1/17

WORKDIR /opt/pf_senseless
COPY kout/kernel.gz kernel.img
RUN truncate -s 16M kernel.img

COPY fsout/rootfs.f2fs.gz rootfs.img.gz
RUN gunzip rootfs.img.gz

COPY qemu-ifup /etc/qemu-ifup
COPY challenge-entrypoint.sh /
CMD ["/challenge-entrypoint.sh"]
