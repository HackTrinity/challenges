FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY 2048.conf /etc/nginx/conf.d/

COPY flag.txt /tmp/
RUN wget -P /tmp https://github.com/gabrielecirulli/2048/archive/master.zip && \
    unzip /tmp/master.zip && \
    mv 2048-master/ /opt/2048 && \
    cat /tmp/flag.txt >> /opt/2048/style/main.css && \
    rm /tmp/flag.txt /tmp/master.zip
