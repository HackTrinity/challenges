#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>

bool read_byte(uint8_t *byte) {
    *byte = 0;

    for (size_t i = 0; i < 8; i++) {
        sigset_t set;
        sigemptyset(&set);
        sigaddset(&set, SIGUSR1);
        sigaddset(&set, SIGUSR2);

        int sig;
        if (sigwait(&set, &sig) != 0) {
            return false;
        }

        if (sig == SIGUSR2) {
            *byte |= (1 << i);
        }
    }

    return true;
}
bool read_string(char *buf, size_t max) {
    for (size_t i = 0; i < max; i++) {
        if (!read_byte((uint8_t*)(buf + i))) {
            return false;
        }
        if (buf[i] == 0) {
            break;
        }
    }

    return true;
}

int main(int argc, char **argv) {
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);
    sigaddset(&mask, SIGUSR2);
    if (sigprocmask(SIG_BLOCK, &mask, NULL) == -1) {
        perror("sigprocmask()");
        return -1;
    }

    char flag[256];
    if (!read_string(flag, sizeof(flag))) {
        perror("read_string()");
        return -2;
    }

    printf("received: %s\n", flag);
    return 0;
}
