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
unsigned long nr_xattrs = 0;
unsigned long post_setup_ins_nr_xattrs = 0;
unsigned long post_setup_del_nr_xattrs = 0;
unsigned long xattr_const_size = 0;
unsigned long xattr_val_len[VAL_LEN_SIZE];
int nr_xattr_val_len = 0;
int max_val = 0;
unsigned char *value = NULL;
char *filename = NULL;
int inline_delete_percent = 0;
int inline_delete_interval = 0;
int inline_overwrite_percent = 0;
int inline_overwrite_interval = 0;
int setup_delete_percent = 0;
int setup_delete_interval = 0;

static void usage(void)
{
	fprintf(stderr, "Pass the right arguments please.\n");

	return;
}

static void do_insert(int fd, int i, int j, int flags)
{
	int ret;

	snprintf(name, NAME_LEN, NAME_FORMAT, i);
	/* printf("j = %d; xattr_val_len[j] = %lu.\n", j, xattr_val_len[j]); */
	ret = fsetxattr(fd, name, value, xattr_val_len[j], flags);
	if (ret == -1)
		perror("fsetxattr");
}

static void do_delete(int fd, int low, int high, int delete_interval)
{
	int ret;
	int i;

	for (i = low; i < high; i += delete_interval) {
		/* printf("Removing %d.\n", i); */
		snprintf(name, NAME_LEN, NAME_FORMAT, i);
		/* printf("Removing xattr %s.\n", name); */
		ret = fremovexattr(fd, name);
		if (ret == -1) {
			perror("fremovexattr");
			return;
		}
	}
}

static void do_overwrite(int fd, int low, int high, int overwrite_interval)
{
	int i, j;

	for (i = low, j = 0; i < high;
	     i += overwrite_interval, j = (j+1) % nr_xattr_val_len)
		do_insert(fd, i, j, XATTR_REPLACE);
}

static void do_test(void)
{
	int fd;
	int i, j;
	int oflags;

	oflags = O_RDWR;
	if (!post_setup_ins_nr_xattrs && !post_setup_del_nr_xattrs)
		oflags |= O_CREAT | O_EXCL;

	fd = open(filename, oflags, 0666);
	if (fd == -1) {
		perror("open");
		return;
	}

	if (!post_setup_ins_nr_xattrs && !post_setup_del_nr_xattrs) {
		for (i = 0, j = 0; i < nr_xattrs; i++, j = (j+1) % nr_xattr_val_len) {
			do_insert(fd, i, j, XATTR_CREATE);

			if (inline_delete_percent && !((i + 1) % DELETE_THRESHOLD))
				do_delete(fd, i + 1 - DELETE_THRESHOLD, i,
					inline_delete_interval);

			if (inline_overwrite_percent && !((i + 1) % OVERWRITE_THRESHOLD))
				do_overwrite(fd, i + 1 - OVERWRITE_THRESHOLD, i,
					inline_overwrite_interval);
		}

		if (setup_delete_interval) {
			printf("Performing Setup deletion.\n");
			do_delete(fd, 0, nr_xattrs, setup_delete_interval);
		}
	}

	if (post_setup_ins_nr_xattrs) {
		int idx;
		printf("Inserting Post-setup xattrs\n");
		for (i = 0, j = 0;
		     i < post_setup_ins_nr_xattrs;
		     i++, j = (j+1) % nr_xattr_val_len) {
			idx = i * setup_delete_interval;
			/* printf("Inserting %d.\n", idx); */
			do_insert(fd, idx, j, XATTR_CREATE);
		}
	}

	if (post_setup_del_nr_xattrs) {
		int nr_grps = nr_xattrs / setup_delete_interval;
		int grp_idx, grp;
		int ret;

		printf("Deleting Post-setup xattrs\n");
		grp = 0;
		grp_idx = 1;
		for (i = 0; i < post_setup_del_nr_xattrs; i++) {
			/* printf("Deleting %d.\n", (grp * setup_delete_interval) + grp_idx); */
			snprintf(name, NAME_LEN, NAME_FORMAT,
				(grp * setup_delete_interval) + grp_idx);
			ret = fremovexattr(fd, name);
			if (ret == -1) {
				perror("fremovexattr");
				return;
			}
			++grp_idx;
			if (grp_idx == setup_delete_interval) {
				grp_idx = 1;
				++grp;
			}
			assert(grp < nr_grps);
		}
	}

	close(fd);
}

int main(int argc, char *argv[])
{
	int opt;
	int i;

	while ((opt = getopt(argc, argv, "d:D:f:l:n:N:o:s:")) != -1) {
		switch (opt) {
		case 'd':
			inline_delete_percent = strtoul(optarg, NULL, 10);
			if (inline_delete_percent > 50) {
				fprintf(stderr, "Invalid inline delete percentage\n");
				goto out1;
			}
			inline_delete_interval = DELETE_THRESHOLD * inline_delete_percent / 100;
			inline_delete_interval = DELETE_THRESHOLD / inline_delete_interval;
			break;

		case 'D':
			post_setup_del_nr_xattrs = strtoul(optarg, NULL, 10);
			if (post_setup_del_nr_xattrs == ULONG_MAX && errno == ERANGE)
				goto out1;
			break;

		case 'f':
			filename = optarg;
			/* unlink(filename); */
			/* printf("Got file name as %s.\n", filename); */
			break;

		case 'l':
			if (nr_xattr_val_len >= VAL_LEN_SIZE)
				goto out1;
			xattr_val_len[nr_xattr_val_len]
				= strtoul(optarg, NULL, 10);
			if (xattr_val_len[nr_xattr_val_len] > max_val)
				max_val = xattr_val_len[nr_xattr_val_len];
			++nr_xattr_val_len;
			break;

		case 'n':
			nr_xattrs = strtoul(optarg, NULL, 10);
			if (nr_xattrs == ULONG_MAX && errno == ERANGE)
				goto out1;
			break;

		case 'N':
			post_setup_ins_nr_xattrs = strtoul(optarg, NULL, 10);
			if (post_setup_ins_nr_xattrs == ULONG_MAX && errno == ERANGE)
				goto out1;
			break;

		case 'o':
			inline_overwrite_percent = strtoul(optarg, NULL, 10);
			if (inline_overwrite_percent == ULONG_MAX && errno == ERANGE)
				goto out1;
			inline_overwrite_interval = OVERWRITE_THRESHOLD * inline_overwrite_percent / 100;
			inline_overwrite_interval = OVERWRITE_THRESHOLD / inline_overwrite_interval;
			break;

		case 's':
			setup_delete_percent = strtoul(optarg, NULL, 10);
			if (setup_delete_percent == ULONG_MAX && errno == ERANGE)
				goto out1;

			if (setup_delete_percent > 50) {
				fprintf(stderr, "Invalid post delete percentage\n");
				goto out1;
			}
			setup_delete_interval = DELETE_THRESHOLD * setup_delete_percent / 100;
			setup_delete_interval = DELETE_THRESHOLD / setup_delete_interval;
			break;

		case '?':
			usage();
			goto out1;
			break;
		}
	}

	if (!filename) {
		usage();
		goto out1;
	}
#if 0
	if (!((!!nr_xattrs) ^ (!!post_setup_ins_nr_xattrs))) {
		usage();
		goto out1;
	}

	if (!((!!nr_xattrs) ^ (!!post_setup_del_nr_xattrs))) {
		usage();
		goto out1;
	}
#else
	if (!nr_xattrs) {
		usage();
		goto out1;
	}
#endif
	if (post_setup_ins_nr_xattrs && post_setup_del_nr_xattrs) {
		usage();
		goto out1;
	}

	if (post_setup_ins_nr_xattrs
		&& (inline_delete_percent || inline_overwrite_percent)) {
		usage();
		goto out1;
	}

	if (post_setup_del_nr_xattrs
		&& (inline_delete_percent || inline_overwrite_percent)) {
		usage();
		goto out1;
	}

	printf("Filename = %s\n", filename);
	printf("Xattrs inserted = %lu\n", nr_xattrs);
	printf("Xattrs inserted post-setup = %lu\n", post_setup_ins_nr_xattrs);
	printf("Xattrs deleted post-setup = %lu\n", post_setup_del_nr_xattrs);
	printf("Possible value sizes =");
	for (i = 0; i < nr_xattr_val_len; i++)
		printf(" %lu", xattr_val_len[i]);
	printf("\n");
	printf("Inline delete percentage = %d\n", inline_delete_percent);
	printf("Inline delete interval = %d\n", inline_delete_interval);
	printf("Inline overwite percentage = %d\n", inline_overwrite_percent);
	printf("Inline overwrite interval = %d\n", inline_overwrite_interval);
	printf("Setup delete percentage = %d\n", setup_delete_percent);
	printf("Setup delete interval = %d\n", setup_delete_interval);

	value = malloc(max_val);
	if (!value) {
		printf("Unable to allocate memory.\n");
		goto out1;
	}

	memset(value, 'a', max_val);

	do_test();

	free(value);

	exit(0);

out1:
	exit(1);
}
