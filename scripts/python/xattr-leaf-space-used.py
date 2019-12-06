#!/usr/bin/env python

import sys
import subprocess
import numpy
import json

leaf_used_bytes = {}
hash_distribution = {}
xattrs_per_hash = {}

xfs_db_cmd_inode = []
nr_leaves = 0

def traverse_xattr_btree(dev, ino, ablock):
    xfs_db_cmd_ablock = xfs_db_cmd_inode + ["-c", "ablock %s" % (ablock)]
    xfs_db_cmd_ablock_magic = xfs_db_cmd_ablock + ["-c", "print hdr.info.hdr.magic"]
    xfs_db_cmd_ablock_level = xfs_db_cmd_ablock + ["-c", "print hdr.level"]
    xfs_db_cmd_ablock_count = xfs_db_cmd_ablock + ["-c", "print hdr.count"]
    xfs_db_cmd_ablock_usedbytes = xfs_db_cmd_ablock + ["-c", "print hdr.usedbytes"]
    xfs_db_cmd_ablock_holes = xfs_db_cmd_ablock + ["-c", "print hdr.holes"]
    xfs_db_cmd_ablock_entries = xfs_db_cmd_ablock + ["-c", "print entries"]
    
    output = subprocess.check_output(xfs_db_cmd_ablock_magic)

    magic = output.split('=')[1].strip()

    if magic == "0x3ebe":       # XFS_DA3_NODE_MAGIC
        output = subprocess.check_output(xfs_db_cmd_ablock_level)
        level = output.split('=')[1].strip()

        output = subprocess.check_output(xfs_db_cmd_ablock_count)
        nr_entries = output.split('=')[1].strip()
        nr_entries = int(nr_entries)

        for i in xrange(nr_entries):
            xfs_db_cmd_ablock_before = xfs_db_cmd_ablock + ["-c", "print btree[%d].before" % i]
            output = subprocess.check_output(xfs_db_cmd_ablock_before)
            child_ablock = output.split('=')[1].strip()
            child_ablock = int(child_ablock)
            traverse_xattr_btree(dev, ino, child_ablock)
        
    elif magic == "0x3bee":  # XFS_ATTR3_LEAF_MAGIC
        global leaf_used_bytes
        global nr_leaves

        output = subprocess.check_output(xfs_db_cmd_ablock_count)
        nr_entries = output.split('=')[1].strip()
        nr_entries = int(nr_entries)

        output = subprocess.check_output(xfs_db_cmd_ablock_usedbytes)
        used_bytes = output.split('=')[1].strip()
        used_bytes = int(used_bytes)

        leaf_used_bytes[nr_leaves] = 80 + (nr_entries * 8) + used_bytes

        output = subprocess.check_output(xfs_db_cmd_ablock_entries)
        output = output.split('\n')
        output = output[1:len(output) - 1]
        hash_list = [i.split(':')[1].split(',')[0][1:]  for i in output]

        for h in hash_list:
            if h in xattrs_per_hash:
                xattrs_per_hash[h] = xattrs_per_hash[h] + 1
            else:
                xattrs_per_hash[h] = 1

	hash_set = set(hash_list)
        hash_list = list(hash_set)
	hash_distribution[nr_leaves] = len(hash_list)

        nr_leaves = nr_leaves + 1
    else:
        # something unknown
        print "Unknown magic =", magic
        return None


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Usage: %s <device name> <inode number> <dump json file>" % sys.argv[0]
        sys.exit(1)

    dev = sys.argv[1]
    ino = sys.argv[2]
    json_dump = sys.argv[3]
    
    xfs_db_cmd_inode = ["xfs_db", dev, "-c", "inode %s" % (ino)]
    traverse_xattr_btree(dev, ino, 0)

    sum = 0
    min = 0
    max = 0
    for ablock,used_bytes in leaf_used_bytes.items():
        sum = sum + used_bytes
        if min == 0:
            min = used_bytes
        elif used_bytes < min:
            min = used_bytes

        if max == 0:
            max = used_bytes
        elif used_bytes > max:
            max = used_bytes

    avg = sum / len(leaf_used_bytes)

    deviation = numpy.std(leaf_used_bytes.values())
    deviation = int(deviation)

    nr_below_avg = 0
    for leaf_index,used_bytes in leaf_used_bytes.items():
        if used_bytes < avg:
            nr_below_avg = nr_below_avg + 1

    with open(json_dump, "w+") as f:
        j = [leaf_used_bytes, hash_distribution, xattrs_per_hash]
        json.dump(j, f)

    nr_hashes = 0;
    for i in hash_distribution.values():
        nr_hashes = nr_hashes + i

    print "Number of leaves =", nr_leaves, "Number of hash values =", nr_hashes, "Below average space used =", nr_below_avg, "Average space used =", avg, "Standard deviation =", deviation,  "Minimum =", min, "Maximum =", max
