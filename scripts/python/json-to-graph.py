#!/usr/bin/env python

import os
import sys
import json
import subprocess

space_usage_prog = '''
set autoscale
set grid

set xlabel "Leaf sl no."
set ylabel "Leaf space used (in bytes)"

set xtic auto
set ytic auto

set xrange [1:]
set yrange [1:5000]

# 1916,1012
# 30000,2024
set terminal pngcairo enhanced size 30000,2024
set output "%s"

set title "Xattrs: %s; Nr leaves: %s; Nr leaves below 2700 bytes: %s; Percentage = %d %%; Total leaf space = %s; Space wasted = %s; Percentage = %d %%"

plot "%s" using 2 title "" with histogram
'''

hash_usage_prog = '''
set autoscale
# set logscale x 2
# set logscale y 2

set grid

set xlabel "Leaf sl no."
set ylabel "No. of Hash values"

# set xtic auto
# set ytic auto

set xrange [0:]
set yrange [0:]

# 1916,1012
# 30000,2024
set terminal pngcairo enhanced size 30000,2024
set output "%s"

set title "%s xattrs"

plot "%s" using 2 title "" with histogram
'''

xattrs_per_hash_prog = '''
# set logscale y 2

set autoscale
set grid

set xlabel "Hash value"
set ylabel "Nr xattrs"

# set xtic auto
# set ytic auto

set xrange [0:]
set yrange [0:]

# 1916,1012
# 30000,2024
set terminal pngcairo enhanced size 1916,1012
set output "%s"

set title "%s xattrs"

plot "%s" using 2 title "" with histogram
'''

def gen_graph(src_file, dst_dir):
    space_file = '/tmp/space.dat'
    hash_file = '/tmp/hash.dat'
    xattrs_per_hash_file = '/tmp/xattrs_per_hash.dat'
    
    stats_file = 'stats.log'
    nr_space_threshold_leaves = 0
    nr_leaves = 0
    space_wasted = 0
    
    with open(src_file, 'r') as f:
        o = json.load(f)

    with open(space_file, 'w') as f:
        # leaf space usage
        d = {int(k):v for k, v in o[0].items()}
        for leaf_nr, space_used in sorted(d.items()):
            nr_leaves = nr_leaves + 1
            if d[leaf_nr] < 2700:
                nr_space_threshold_leaves = nr_space_threshold_leaves + 1
                space_wasted = space_wasted + (4096 - d[leaf_nr])
            f.write(str(leaf_nr) + ' ' + str(space_used) + '\n')

    with open(hash_file, 'w') as f:
        # No. of hashes in each leaf
        d = {int(k):v for k, v in o[1].items()}
        for leaf_nr,nr_hashes in sorted(d.items()):
            f.write(str(leaf_nr) + ' ' + str(nr_hashes) + '\n')

    if len(o) > 2:
        with open(xattrs_per_hash_file, 'w') as f:
            for hash_val,nr_xattrs in o[2].items():
                # print 'hash val:', hash_val, 'Nr xattrs:', nr_xattrs
                f.write(str(hash_val) + ' ' + str(nr_xattrs) + '\n')

    basename = os.path.basename(src_file)
    extension = '.png'
    basename = basename.replace('.json', extension)
    basename = basename.replace('test-', 'test-space-')

    graph_file = dst_dir + '/' + basename
    nr_attrs = basename.split('-')[2][1:]
    nr_attrs = int(nr_attrs)
    percentage = nr_space_threshold_leaves * 100 / nr_leaves
    total_leaf_space = nr_leaves * 4096
    space_wasted_percent = space_wasted * 100.0 / total_leaf_space
    
    prog = space_usage_prog % (graph_file, '{:,}'.format(nr_attrs), \
                               '{:,}'.format(nr_leaves), \
                               '{:,}'.format(nr_space_threshold_leaves), \
                               percentage, '{:,}'.format(total_leaf_space),
                               '{:,}'.format(space_wasted), \
                               space_wasted_percent, space_file)

    stats_file = dst_dir + '/' + stats_file
    with open(stats_file, 'a') as f:
        f.write('| Nr leaves:{1:,} | Nr leaves below 2700 bytes:{2:,} | Percentage:{3} |  Total leaf space:{4:,} | Space wasted:{5:,} | Percentage:{6} | {0} |\n'\
                .format(graph_file.replace('.png',''), nr_leaves,
                        nr_space_threshold_leaves, percentage,
                        total_leaf_space, space_wasted, space_wasted_percent))

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(prog)

    basename = os.path.basename(src_file)
    extension = '.png'
    basename = basename.replace('.json', extension)
    basename = basename.replace('test-', 'test-hash-')

    graph_file = dst_dir + '/' + basename
    nr_attrs = basename.split('-')[2][1:]
    nr_attrs = int(nr_attrs)
    prog = hash_usage_prog % (graph_file, '{:,}'.format(nr_attrs), hash_file)

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(prog)

    basename = os.path.basename(src_file)
    extension = '.png'
    basename = basename.replace('.json', extension)
    basename = basename.replace('test-', 'test-xattrs-per-hash-')

    if len(o) > 2:
        graph_file = dst_dir + '/' + basename
        nr_attrs = basename.split('-')[4][1:]
        nr_attrs = int(nr_attrs)
        prog = xattrs_per_hash_prog % (graph_file, '{:,}'.format(nr_attrs), xattrs_per_hash_file)

        subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(prog)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: %s <src-file> <dst-dir>' % sys.argv[0]
        sys.exit(1)

    gen_graph(sys.argv[1], sys.argv[2])

