#ifndef _BENCHMARK_XATTRS_H
#define _BENCHMARK_XATTRS_H

/*
 * 'name' consumes 4 out of 15 bytes. With the remaining 11 bytes,
 * we could generate 10^11 = 100,000,000,000 unique names.
 */
#define NAME_FORMAT "trusted.name%011d"
#define NAME_LEN (8 + (15 + 1))
#define VAL_LEN_SIZE 20
#define DELETE_THRESHOLD 500
#define OVERWRITE_THRESHOLD 500

#endif /* _BENCHMARK_XATTRS_H */
