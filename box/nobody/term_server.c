#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/select.h>
#include <sys/signalfd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <grp.h>

#define PORT 23
#define COMMAND "/bin/sh"

#define UID 65534
#define GID 65534

void handle_client(int client, struct sockaddr_in addr) {
    int enable = 1;
    if (setsockopt(client, IPPROTO_TCP, TCP_NODELAY, &enable, sizeof(int)) == -1) {
        perror("setsockopt()");
        goto die;
    }

    char addr_str[256];
    if (inet_ntop(AF_INET, &addr.sin_addr.s_addr, addr_str, sizeof(addr_str)) == NULL) {
        perror("inet_ntop()");
        goto die;
    }
    fprintf(stderr, "connection from %s:%d\n", addr_str, addr.sin_port);

    pid_t c_pid = fork();
    if (c_pid == -1) {
        perror("fork()");
        goto die;
    } else if (c_pid == 0) {
        if (setgroups(0, NULL) == -1) {
            perror("setgroups()");
        }
        if (setgid(GID) == -1) {
            perror("setgid()");
        }
        if (seteuid(UID) == -1) {
            perror("setuid()");
        }

        if (dup2(client, STDIN_FILENO) == -1) {
            perror("stdin dup2()");
            goto die;
        }
        if (dup2(client, STDOUT_FILENO) == -1) {
            perror("stdout dup2()");
            goto die;
        }
        if (dup2(client, STDERR_FILENO) == -1) {
            perror("stderr dup2()");
            goto die;
        }

        close(client);
        execlp(COMMAND, COMMAND, "-il", NULL);
        perror("exec()");
    }
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
    //return ret;
    kill(-getpid(), SIGKILL);
}
