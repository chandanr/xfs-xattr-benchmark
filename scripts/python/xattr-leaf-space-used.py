#!/usr/bin/env python

from __future__ import print_function

import sys
import subprocess
import threading
import numpy
import json

nr_threads = 0
grp_size = 3

leaf_used_bytes = {}
hash_distribution = {}
xattrs_per_hash = {}
nr_leaves = {}

total_leaf_used_bytes = {}
total_hash_distribution = {}
total_xattrs_per_hash = {}
total_nr_leaves = 0

xfs_db_cmd_inode = []

def traverse_xattr_btree(tid, dev, ino, ablock):
	xfs_db_cmd_ablock = xfs_db_cmd_inode + ["-c", "ablock %s" % (ablock)]
	xfs_db_cmd_ablock_magic = xfs_db_cmd_ablock + ["-c", "print hdr.info.hdr.magic"]
	xfs_db_cmd_ablock_count = xfs_db_cmd_ablock + ["-c", "print hdr.count"]
	xfs_db_cmd_ablock_usedbytes = xfs_db_cmd_ablock + ["-c", "print hdr.usedbytes"]
	xfs_db_cmd_ablock_holes = xfs_db_cmd_ablock + ["-c", "print hdr.holes"]
	xfs_db_cmd_ablock_entries = xfs_db_cmd_ablock + ["-c", "print entries"]
    
	output = subprocess.check_output(xfs_db_cmd_ablock_magic)
	magic = output.split('=')[1].strip()

	if magic == "0x3ebe":       # XFS_DA3_NODE_MAGIC
		output = subprocess.check_output(xfs_db_cmd_ablock_count)
		nr_entries = output.split('=')[1].strip()
		nr_entries = int(nr_entries)

		for i in xrange(nr_entries):
			xfs_db_cmd_ablock_before = xfs_db_cmd_ablock \
				+ ["-c", "print btree[%d].before" % i]
			output = subprocess.check_output(xfs_db_cmd_ablock_before)
			child_ablock = output.split('=')[1].strip()
			child_ablock = int(child_ablock)
			traverse_xattr_btree(tid, dev, ino, child_ablock)
        
	elif magic == "0x3bee":  # XFS_ATTR3_LEAF_MAGIC
		global leaf_used_bytes
		global nr_leaves

		output = subprocess.check_output(xfs_db_cmd_ablock_count)
		nr_entries = output.split('=')[1].strip()
		nr_entries = int(nr_entries)

		output = subprocess.check_output(xfs_db_cmd_ablock_usedbytes)
		used_bytes = output.split('=')[1].strip()
		used_bytes = int(used_bytes)

		idx = nr_leaves[tid]

		leaf_used_bytes[tid][idx] = 80 + (nr_entries * 8) + used_bytes

		output = subprocess.check_output(xfs_db_cmd_ablock_entries)
		output = output.split('\n')
		output = output[1:len(output) - 1]
		hash_list = [i.split(':')[1].split(',')[0][1:]  for i in output]

		for h in hash_list:
			if h in xattrs_per_hash[tid]:
				xattrs_per_hash[tid][h] = xattrs_per_hash[tid][h] + 1
			else:
				xattrs_per_hash[tid][h] = 1

		hash_set = set(hash_list)
		hash_list = list(hash_set)
		hash_distribution[tid][idx] = len(hash_list)

		nr_leaves[tid] = nr_leaves[tid] + 1
	else:
		# something unknown
		print("Unknown magic =", magic, file=sys.stderr)
		return None


def thread_main(tid, grp_start, grp_size, dev, ino):
	xfs_db_cmd_ablock = xfs_db_cmd_inode + ["-c", "ablock %s" % (0)]

	grp_end = grp_start + grp_size - 1

	for i in xrange(grp_start, grp_end + 1):
		xfs_db_cmd_ablock_before = xfs_db_cmd_ablock \
			+ ["-c", "print btree[%d].before" % i]
		output = subprocess.check_output(xfs_db_cmd_ablock_before)
		child_ablock = output.split('=')[1].strip()
		child_ablock = int(child_ablock)
		traverse_xattr_btree(tid, dev, ino, child_ablock)
	

def split_root_node(dev, ino):
	global total_nr_leaves
	global nr_threads
	global grp_size

	xfs_db_cmd_ablock = xfs_db_cmd_inode + ["-c", "ablock %s" % (0)]
	xfs_db_cmd_ablock_magic = xfs_db_cmd_ablock + ["-c", "print hdr.info.hdr.magic"]
	xfs_db_cmd_ablock_count = xfs_db_cmd_ablock + ["-c", "print hdr.count"]
	threads = []
    
	output = subprocess.check_output(xfs_db_cmd_ablock_magic)
	magic = output.split('=')[1].strip()	
	if magic != "0x3ebe":  # XFS_DA3_NODE_MAGIC
		print('Root is not a non-leaf node\n')
		sys.exit(1)

	output = subprocess.check_output(xfs_db_cmd_ablock_count)
	nr_entries = output.split('=')[1].strip()
	nr_entries = int(nr_entries)

	nr_threads = nr_entries / grp_size
	rem = nr_entries % grp_size
	if rem:
		nr_threads = nr_threads + 1

	print('nr_entries = ', nr_entries, '; nr_threads = ', nr_threads, '\n')

	s = ''
	for tid in xrange(0, nr_threads):
		leaf_used_bytes[tid] = {}
		hash_distribution[tid] = {}
		xattrs_per_hash[tid] = {}
		nr_leaves[tid] = 0
		
		grp_start = tid * grp_size

		if rem and tid == (nr_threads - 1):
			grp_size = nr_entries % grp_size

		tobj = threading.Thread(target=thread_main,
					args=(tid, grp_start, grp_size,
					      dev, ino))
		threads.append(tobj)
		tobj.start()

		grp_end = grp_start + grp_size - 1
		output = 'Thread id = {0} \tgrp_size = {1} \t grp_start = {2} \tgrp_end = {3}\n'.format(tid, grp_size, grp_start, grp_end)
		s = s + output

	print(s)

	for tobj in threads:
		tobj.join()

	idx = 0
	for tid in xrange(0, nr_threads):
		for leaf_nr, space_used in sorted(leaf_used_bytes[tid].items()):
			total_leaf_used_bytes[idx] = space_used
			idx = idx + 1

	idx = 0
	for tid in xrange(0, nr_threads):
		for leaf_nr, nr_hashes in sorted(hash_distribution[tid].items()):
			total_hash_distribution[idx] = nr_hashes
			idx = idx + 1

	for tid in xrange(0, nr_threads):
		total_nr_leaves = total_nr_leaves + nr_leaves[tid]

	for h, nr_val in sorted(xattrs_per_hash[tid].items()):
		if h in total_xattrs_per_hash:
			total_xattrs_per_hash[h] = total_xattrs_per_hash[h] + nr_val
		else:
			total_xattrs_per_hash[h] = nr_val


if __name__ == '__main__':
	if len(sys.argv) != 4:
		print("Usage: ", sys.argv[0],
		      " <device name> <inode number> <dump json file>",
		      file=sys.stderr)
		sys.exit(1)

	dev = sys.argv[1]
	ino = sys.argv[2]
	json_dump = sys.argv[3]
    
	xfs_db_cmd_inode = ["xfs_db", dev, "-c", "inode %s" % (ino)]

	split_root_node(dev, ino)

	sum = 0
	min = 0
	max = 0
	for leaf_nr, used_bytes in total_leaf_used_bytes.items():
		sum = sum + used_bytes
		if min == 0:
			min = used_bytes
		elif used_bytes < min:
			min = used_bytes

		if max == 0:
			max = used_bytes
		elif used_bytes > max:
			max = used_bytes

	avg = sum / len(total_leaf_used_bytes)

	deviation = numpy.std(total_leaf_used_bytes.values())
	deviation = int(deviation)

	nr_below_avg = 0
	for leaf_index, used_bytes in total_leaf_used_bytes.items():
		if used_bytes < avg:
			nr_below_avg = nr_below_avg + 1

	with open(json_dump, "w+") as f:
		j = [total_leaf_used_bytes, total_hash_distribution, total_xattrs_per_hash]
		json.dump(j, f)

	total_nr_hashes = 0;
	for i in total_hash_distribution.values():
		total_nr_hashes = total_nr_hashes + i

	print("Number of leaves =", total_nr_leaves, "Number of hash values =", total_nr_hashes,
	      "Below average space used =", nr_below_avg,
	      "Average space used =", avg, "Standard deviation =", deviation,
	      "Minimum =", min, "Maximum =", max)
