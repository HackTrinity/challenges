#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/select.h>
#include <sys/signalfd.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>

#define KERNEL_DEV "/dev/mmcblk0"
#define UPGRADE_FILE "/upgrade.f2fs.gz"

#define PORT 6969
#define KERNEL_MAX 64 * 1024 * 1024
#define ROOTFS_MAX 64 * 1024 * 1024

#define REQ_UPGRADE 0

#define RES_OK      0
#define ERR_BAD_REQ 1
#define ERR_TOO_BIG 2
#define ERR_KERNEL  3
#define ERR_ROOTFS  4

bool res_client(int client, uint8_t r) {
    if (send(client, &r, 1, 0) != 1) {
        perror("send()");
        return false;
    }
}
bool copy(int dst, int client, size_t n) {
    uint8_t buf[4096];
    while (n) {
        size_t r = n;
        if (r > sizeof(buf)) {
            r = sizeof(buf);
        }

        if (recv(client, buf, r, MSG_WAITALL) != r) {
            perror("recv()");
            return false;
        }
        if (write(dst, buf, r) != r) {
            perror("write()");
            return false;
        }

        n -= r;
    }

    return true;
}
void handle_client(int client, struct sockaddr_in addr) {
    char addr_str[256];
    if (inet_ntop(AF_INET, &addr.sin_addr.s_addr, addr_str, sizeof(addr_str)) == NULL) {
        perror("inet_ntop()");
        goto die;
    }
    fprintf(stderr, "connection from %s:%d\n", addr_str, addr.sin_port);

    uint8_t type;
    if (recv(client, &type, 1, 0) != 1) {
        perror("recv()");
        goto die;
    }

    if (type != REQ_UPGRADE) {
        res_client(client, ERR_BAD_REQ);
        goto die;
    }

    uint32_t sizes[2];
    if (recv(client, sizes, 2 * sizeof(uint32_t), MSG_WAITALL) != 2 * sizeof(uint32_t)) {
        perror("recv()");
        goto die;
    }

    uint32_t k_size = ntohl(sizes[0]);
    uint32_t r_size = ntohl(sizes[1]);
    if (k_size > KERNEL_MAX || r_size > ROOTFS_MAX) {
        res_client(client, ERR_TOO_BIG);
        goto die;
    }

    if (k_size != 0) {
        int out = open(KERNEL_DEV, O_RDWR);
        if (out == -1) {
            perror("open()");
            res_client(client, ERR_KERNEL);
            goto die;
        }

        if (!copy(out, client, k_size)) {
            close(out);
            res_client(client, ERR_KERNEL);
            goto die;
        }
    }

    if (r_size != 0) {
        int out = creat(UPGRADE_FILE, O_RDWR);
        if (out == -1) {
            perror("open()");
            res_client(client, ERR_ROOTFS);
            goto die;
        }

        if (!copy(out, client, r_size)) {
            close(out);
            res_client(client, ERR_ROOTFS);
            goto die;
        }
    }

    res_client(client, RES_OK);
    close(client);
    system("reboot");
die:
    close(client);
}

int main(int argc, char **argv) {
    int server = socket(AF_INET, SOCK_STREAM, 0);
    if (server == -1) {
        perror("socket()");
        return -1;
    }

    int ret = 0;

    struct sockaddr_in bind_addr = {0};
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_addr.s_addr = INADDR_ANY;
    bind_addr.sin_port = htons(PORT);

    if (bind(server, (struct sockaddr*)&bind_addr, sizeof(struct sockaddr_in)) == -1) {
        perror("bind()");
        ret = -3;
        goto edie;
    }
    if (listen(server, 16) == -1) {
        perror("listen()");
        ret = -3;
        goto edie;
    }

    signal(SIGPIPE, SIG_IGN);

    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);
    if (sigprocmask(SIG_BLOCK, &mask, NULL) == -1) {
        perror("sigprocmask()");
        ret = -4;
        goto edie;
    }

    int sfd = signalfd(-1, &mask, 0);
    if (sfd == -1) {
        perror("signalfd()");
        ret = -4;
        goto edie;
    }

    int nfds = (sfd > server ? sfd : server) + 1;
    fd_set rfds;
    for (;;) {
        FD_ZERO(&rfds);
        FD_SET(sfd, &rfds);
        FD_SET(server, &rfds);
        int ret = select(nfds, &rfds, NULL, NULL, NULL);
        if (ret == -1) {
            perror("select()");
            ret = -5;
            goto die;
        } else if (ret == 0) {
            continue;
        }

        if (FD_ISSET(server, &rfds)) {
            struct sockaddr_in client_addr;
            socklen_t addr_size = sizeof(struct sockaddr_in);
            int client = accept(server, (struct sockaddr*)&client_addr, &addr_size);
            if (client == -1) {
                perror("accept()");
                ret = -6;
                goto die;
            }

            handle_client(client, client_addr);
        }
        if (FD_ISSET(sfd, &rfds)) {
            break;
        }
    }

die:
    close(sfd);
edie:
    close(server);
}
