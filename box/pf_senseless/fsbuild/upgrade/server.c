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

#ifdef SIG_CHECK
#include "sha1.h"
#include "sigcheck.h"
#endif

#define KERNEL_DEV "/dev/mmcblk0"
#define UPGRADE_FILE "/upgrade.f2fs.gz"

#define PORT 6969
#define KERNEL_MAX 64 * 1024 * 1024
#define ROOTFS_MAX 64 * 1024 * 1024

#define MAGIC 0x69420
#define REQ_UPGRADE 0

#define RES_OK          0
#define ERR_BAD_REQ     1
#define ERR_BAD_MAGIC   2
#define ERR_TOO_BIG     3
#define ERR_SIG         4
#define ERR_KERNEL      5
#define ERR_ROOTFS      6

bool res_client(int client, uint8_t r) {
    if (send(client, &r, 1, 0) != 1) {
        perror("send()");
        return false;
    }
}

bool chunk_write(int fd, const void *buf, size_t count) {
    while (count) {
        size_t w = count;
        if (w > 4096) {
            w = 4096;
        }

        if (write(fd, buf, w) != w) {
            perror("write()");
            return false;
        }

        count -= w;
        buf += w;
    }

    return true;
}

void handle_client(int client, struct sockaddr_in addr) {
    uint8_t *kernel = NULL;
    uint8_t *rootfs = NULL;

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
        fprintf(stderr, "%s:%d sent invalid request type %d\n", addr_str, addr.sin_port, type);
        res_client(client, ERR_BAD_REQ);
        goto die;
    }

    uint32_t magic;
    if (recv(client, &magic, sizeof(uint32_t), MSG_WAITALL) != sizeof(uint32_t)) {
        perror("recv()");
        goto die;
    }

    magic = ntohl(magic);
    if (magic != MAGIC) {
        fprintf(stderr, "%s:%d sent invalid magic 0x%x\n", addr_str, addr.sin_port, magic);
        res_client(client, ERR_BAD_MAGIC);
        goto die;
    }

#ifdef SIG_CHECK
    uint8_t signature[256];
    if (recv(client, signature, 256, MSG_WAITALL) != 256) {
        perror("recv()");
        goto die;
    }
#endif

    uint32_t sizes[2];
    if (recv(client, sizes, 2 * sizeof(uint32_t), MSG_WAITALL) != 2 * sizeof(uint32_t)) {
        perror("recv()");
        goto die;
    }

    uint32_t k_size = ntohl(sizes[0]);
    uint32_t r_size = ntohl(sizes[1]);
    if (k_size > KERNEL_MAX || r_size > ROOTFS_MAX) {
        fprintf(stderr, "%s:%d sent an upgrade that was too large\n", addr_str, addr.sin_port);
        res_client(client, ERR_TOO_BIG);
        goto die;
    }

#ifdef SIG_CHECK
    SHA1_CTX sha1;
    SHA1Init(&sha1);
#endif

    if (k_size != 0) {
        kernel = malloc(k_size);
        if (recv(client, kernel, k_size, MSG_WAITALL) != k_size) {
            perror("recv()");
            goto die;
        }
#ifdef SIG_CHECK
        SHA1Update(&sha1, kernel, k_size);
#endif
    }
    if (r_size != 0) {
        rootfs = malloc(r_size);
        if (recv(client, rootfs, r_size, MSG_WAITALL) != r_size) {
            perror("recv()");
            goto die;
        }
#ifdef SIG_CHECK
        SHA1Update(&sha1, rootfs, r_size);
#endif
    }

#ifdef SIG_CHECK
    unsigned char hash[20];
    SHA1Final(hash, &sha1);
    if (!validate_signature(signature, hash)) {
        fprintf(stderr, "%s:%d sent an upgrade with an invalid signature\n", addr_str, addr.sin_port);
        res_client(client, ERR_SIG);
        goto die;
    }
#endif

#ifndef LOCAL
    if (kernel) {
        int out = open(KERNEL_DEV, O_RDWR);
        if (out == -1) {
            perror("open()");
            res_client(client, ERR_KERNEL);
            goto die;
        }

        if (!chunk_write(out, kernel, k_size)) {
            res_client(client, ERR_KERNEL);
            goto die;
        }
    }
    if (rootfs) {
        int out = creat(UPGRADE_FILE, O_RDWR);
        if (out == -1) {
            perror("open()");
            res_client(client, ERR_ROOTFS);
            goto die;
        }

        if (!chunk_write(out, rootfs, r_size)) {
            res_client(client, ERR_ROOTFS);
            goto die;
        }
    }
#endif

    fprintf(stderr, "%s:%d issued an upgrade, rebooting...\n", addr_str, addr.sin_port);
    free(rootfs);
    free(kernel);
    res_client(client, RES_OK);
    close(client);
#ifndef LOCAL
    system("poweroff");
#endif
    return;
die:
    free(rootfs);
    free(kernel);
    close(client);
}

int main(int argc, char **argv) {
#ifndef LOCAL
    int console = open("/dev/console", O_WRONLY);
    if (console == -1) {
        perror("open()");
        return -1;
    }
    if (dup2(console, STDERR_FILENO) == -1) {
        perror("dup2()");
        close(console);
        return -1;
    }
    close(console);
    setbuf(stderr, NULL);
#endif

    int server = socket(AF_INET, SOCK_STREAM, 0);
    if (server == -1) {
        perror("socket()");
        return -1;
    }

    int ret = 0;
    if (setsockopt(server, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) == -1) {
        perror("setsockopt()");
        ret = -2;
        goto edie;
    }

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
