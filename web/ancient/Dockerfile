ARG DOCKER_REGISTRY
FROM $DOCKER_REGISTRY/chad/challbase

ENV KEEP_ROOT=1

RUN apk --no-cache add nginx php7-fpm
RUN setcap 'cap_net_bind_service=+ep' /usr/sbin/nginx && \
    mkdir /run/nginx && \
    sed -i 's:^listen = .*$:listen = /run/php-fpm.sock:g' /etc/php7/php-fpm.d/www.conf && \
    sed -i 's:^.*listen.group = .*$:listen.group = nginx:g' /etc/php7/php-fpm.d/www.conf && \
    sed -i 's:^user = .*$:user = root:g' /etc/php7/php-fpm.d/www.conf && \
    sed -i 's:^group = .*$:group = root:g' /etc/php7/php-fpm.d/www.conf
COPY nginx.conf /etc/nginx/nginx.conf

WORKDIR /opt/html
COPY www/ ./

COPY challenge-entrypoint.sh /
EXPOSE 80/tcp
CMD ["/challenge-entrypoint.sh"]
