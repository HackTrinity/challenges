#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <time.h>

#define PORT 6969
#define MAGIC 0x69420

bool running = true;

int msleep(long msec) {
    if (msec < 0) {
        errno = EINVAL;
        return -1;
    }

    struct timespec ts = {0};
    ts.tv_sec = msec / 1000;
    ts.tv_nsec = (msec % 1000) * 1000000;

    return nanosleep(&ts, &ts);
}

void term_handler(int signum) {
    running = false;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s <interface>\n", argv[0]);
        return 1;
    }
    if (strlen(argv[1]) > IFNAMSIZ - 1) {
        fprintf(stderr, "interface name %s too long\n", argv[1]);
        return 2;
    }

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock == -1) {
        perror("socket()");
        return -1;
    }
    int ret = 0;

    struct ifreq ifr = {0};
    ifr.ifr_addr.sa_family = AF_INET;
    strncpy(ifr.ifr_name, argv[1], IFNAMSIZ-1);

    if (ioctl(sock, SIOCGIFBRDADDR, &ifr) == -1) {
        perror("ioctl()");
        ret = -1;
        goto die;
    }

    if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) == -1) {
        perror("setsockopt()");
        ret = -2;
        goto die;
    }
    if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &(int){1}, sizeof(int)) == -1) {
        perror("setsockopt()");
        ret = -2;
        goto die;
    }

    struct sigaction action = {0};
    action.sa_handler = term_handler;
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    if (sigaction(SIGINT, &action, NULL) == -1 || sigaction(SIGTERM, &action, NULL) == -1) {
        perror("sigaction()");
        ret = -3;
        goto die;
    }

    struct sockaddr_in dst = {0};
    dst.sin_family = AF_INET;
    dst.sin_addr = ((struct sockaddr_in*)&ifr.ifr_broadaddr)->sin_addr;
    dst.sin_port = htons(PORT);

    uint32_t magic = htonl(MAGIC);
    while (running) {
        if (sendto(sock, &magic, sizeof(magic), 0, (struct sockaddr*)&dst, sizeof(dst)) != sizeof(magic)) {
            perror("sendto()");
            ret = -4;
            goto die;
        }

        msleep(1000);
    }

die:
    close(sock);
    return ret;
}
