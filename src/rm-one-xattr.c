#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include <unistd.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <attr/xattr.h>

#define NAME_LEN 25

char name[NAME_LEN];

int main(int argc, char *argv[])
{
	uint64_t xattr_id;
	int fd;
	int ret;

	if (argc != 3) {
		fprintf(stderr, "Usage: %s <file name> <xattr id>.\n",
			argv[0]);
		goto out1;
	}

	fd = open(argv[1], O_RDWR);
	if (fd == -1) {
		perror("open");
		goto out1;
	}

	xattr_id = strtoul(argv[2], NULL, 10);

	snprintf(name, NAME_LEN, "trusted.name%lu", xattr_id);
	ret = fremovexattr(fd, name);
	if (ret == -1) {
		perror("fremovexattr");
		goto out2;
	}

	close(fd);

	exit(0);

out2:
	close(fd);
out1:
	exit(1);
}
