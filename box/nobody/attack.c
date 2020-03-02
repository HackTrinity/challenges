#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
	if (setuid(0) == -1) {
		perror("setuid()");
		return -1;
	}

	system("cat /flag.txt");
}
