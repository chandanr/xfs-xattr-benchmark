#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <assert.h>

#include <unistd.h>
#include <limits.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <attr/xattr.h>

#include "benchmark-xattrs.h"

char name[NAME_LEN];
unsigned long max_nr_xattrs = 0;

static void usage(const char *prog)
{
	fprintf(stderr, "%s -n <max-nr-xattrs-to-scan> -f <filename>\n",
		prog);

	return;
}

void count_nr_xattrs(char *filename)
{
	ssize_t ret;
	int nr_xattrs;
	int fd;
	int i;

	fd = open(filename, O_RDONLY);
	if (fd == -1) {
		perror("open");
		goto out1;
	}

	for (i = 0, nr_xattrs = 0; i < max_nr_xattrs; i++) {
		snprintf(name, NAME_LEN, NAME_FORMAT, i);
		ret = fgetxattr(fd, name, NULL, 0);
		if ((ret == -1) && (errno != ENOATTR)) {
			perror("fgetxattr");
			goto out2;
		} else if (ret != -1) {
			++nr_xattrs;
		}
	}

	printf("Nr xattrs found = %d\n", nr_xattrs);
out2:
	close(fd);
out1:
	return;
}

int main(int argc, char *argv[])
{
	char *filename;
	int opt;

	while ((opt = getopt(argc, argv, "f:n:")) != -1) {
		switch (opt) {
		case 'f':
			filename = optarg;
			break;

		case 'n':
			max_nr_xattrs = strtoul(optarg, NULL, 10);
			if (max_nr_xattrs == ULONG_MAX && errno == ERANGE)
				goto out1;
			break;

		case '?':
			usage(argv[0]);
			goto out1;
			break;
		}
	}

	if (!max_nr_xattrs) {
		usage(argv[0]);
		goto out1;
	}

	count_nr_xattrs(filename);

	exit(0);
out1:
	exit(1);
}
