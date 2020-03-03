#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <unistd.h>

bool send_byte(pid_t proc, uint8_t byte) {
    for (size_t i = 0; i < 8; byte >>= 1, i++) {
        int sig = (byte & 1) == 0 ? SIGUSR1 : SIGUSR2;
        if (kill(proc, sig) == -1) {
            return false;
        }

        usleep(10 * 1000);
    }

    return true;
}
bool send_string(pid_t proc, const char *str) {
    for (size_t i = 0; i < strlen(str) + 1; i++) {
        if (!send_byte(proc, (uint8_t)str[i])) {
            return false;
        }
    }

    return true;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <program> [args...]\n", argv[0]);
        return 1;
    }

    pid_t child = fork();
    if (child == -1) {
        perror("fork()");
        return -1;
    } else if (child == 0) {
        execvp(argv[1], argv + 1);
        perror("execvp()");
        return -2;
    } else {
        usleep(300 * 1000);
        if (!send_string(child, FLAG)) {
            perror("send_string()");
            return -3;
        }

        if (wait(NULL) == -1) {
            perror("wait()");
            return -4;
        }
    }

    return 0;
}
