#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import subprocess

device = '/dev/sda4'
mntpnt = '/mnt/'
testfile = mntpnt + '/testfile'
devnull = open(os.devnull, 'w')

test_cmd_line = [
	# ['-n 400000', '40'],
	# ['-n 400000', '60'],
	['-n 400000', '255'],
	# ['-n 400000', '20 40 60 80 100'],
	# ['-n 400000', '120 150 200 220 255'],
	# ['-n 400000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 100', '120 150 200 220 255'],
    # ['-n 1000', '120 150 200 220 255'],
    # ['-n 100000', '120 150 200 220 255'],
    # ['-n 1000000', '120 150 200 220 255'],
    # ['-n 10000000', '120 150 200 220 255'],
    # ['-n 1000000', '120 150 200 220 255'],
    # ['-n 2000000', '120 150 200 220 255'],
    # ['-n 3000000', '120 150 200 220 255'],
    # ['-n 4000000', '120 150 200 220 255'],
    # ['-n 5000000', '120 150 200 220 255'],
    # ['-n 6000000', '120 150 200 220 255'],
    # ['-n 7000000', '120 150 200 220 255'],
    # ['-n 10000000', '120 150 200 220 255'],

    # ['-n 100', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 1000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 100000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 1000000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 10000000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 2000000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 3000000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 4000000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 5000000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 6000000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 7000000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 10000000', '20 40 60 80 100 120 150 200 220 255'],

    # ['-n 100000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 1000000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 2000000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 3000000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 4000000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 5000000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 6000000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 7000000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 10000000', '20 255 40 220 60 200 80 150 100 120'],

    # ['-n 1000000', '40'],
    # ['-n 1000000', '40', '-d 25'],
    # ['-n 1000000', '40', '-o 25'],
    # ['-n 1000000', '60'],
    # ['-n 1000000', '60', '-d 25'],
    # ['-n 1000000', '60', '-o 25'],
    # ['-n 1000000', '255'],
    # ['-n 1000000', '255', '-d 25'],
    # ['-n 1000000', '255', '-o 25'],
    # ['-n 1000000', '20 40 60 80 100'],
    # ['-n 1000000', '20 40 60 80 100', '-d 25'],
    # ['-n 1000000', '20 40 60 80 100', '-o 25'],
    # ['-n 1000000', '120 150 200 220 255'],
    # ['-n 1000000', '120 150 200 220 255', '-d 25'],
    # ['-n 1000000', '120 150 200 220 255', '-o 25'],
    # ['-n 1000000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 1000000', '20 40 60 80 100 120 150 200 220 255', '-d 25'],
    # ['-n 1000000', '20 40 60 80 100 120 150 200 220 255', '-o 25'],
    # ['-n 1000000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 1000000', '20 255 40 220 60 200 80 150 100 120', '-d 25'],
    # ['-n 1000000', '20 255 40 220 60 200 80 150 100 120', '-o 25'],
    # ['-n 1000000', '255 220 200 150 120 100 80 60 40 20'],
    # ['-n 1000000', '255 220 200 150 120 100 80 60 40 20', '-d 25'],
    # ['-n 1000000', '255 220 200 150 120 100 80 60 40 20', '-o 25'],

    # ['-n 100000', '40'],
    # ['-n 100000', '40', '-d 25'],
    # ['-n 100000', '40', '-o 25'],
    # ['-n 100000', '60'],
    # ['-n 100000', '60', '-d 25'],
    # ['-n 100000', '60', '-o 25'],
    # ['-n 100000', '255'],
    # ['-n 100000', '255', '-d 25'],
    # ['-n 100000', '255', '-o 25'],
    # ['-n 100000', '20 40 60 80 100'],
    # ['-n 100000', '20 40 60 80 100', '-d 25'],
    # ['-n 100000', '20 40 60 80 100', '-o 25'],
    # ['-n 100000', '120 150 200 220 255'],
    # ['-n 100000', '120 150 200 220 255', '-d 25'],
    # ['-n 100000', '120 150 200 220 255', '-o 25'],
    # ['-n 100000', '20 40 60 80 100 120 150 200 220 255'],
    # ['-n 100000', '20 40 60 80 100 120 150 200 220 255', '-d 25'],
    # ['-n 100000', '20 40 60 80 100 120 150 200 220 255', '-o 25'],
    # ['-n 100000', '20 255 40 220 60 200 80 150 100 120'],
    # ['-n 100000', '20 255 40 220 60 200 80 150 100 120', '-d 25'],
    # ['-n 100000', '20 255 40 220 60 200 80 150 100 120', '-o 25'],
    # ['-n 100000', '255 220 200 150 120 100 80 60 40 20'],
    # ['-n 100000', '255 220 200 150 120 100 80 60 40 20', '-d 25'],
    # ['-n 100000', '255 220 200 150 120 100 80 60 40 20', '-o 25'],
]

def test_setup():
    try:
        subprocess.check_call(['umount', device],
                              stdout=devnull, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        pass

    subprocess.check_call(['mkfs.xfs', '-f', device],
                          stdout=devnull, stderr=subprocess.STDOUT)
    subprocess.check_call(['mount', device, mntpnt],
                          stdout=devnull, stderr=subprocess.STDOUT)

def test_reset():
    subprocess.check_call(['umount', device])

def exec_benchmark(t, benchmark_exec, log_file):
	time_file = '/tmp/time.log'

	cmd = [benchmark_exec] + [t[0]]
	for i in t[1].split():
		cmd = cmd + ['-l ' + i]
	if len(t) > 2:
		cmd = cmd + [t[2]]
	cmd = cmd + ['-f' + testfile]
	time_cmd = ['/usr/bin/time'] + ['-o{0}'.format(time_file)] + ['-f \'%e %U %S\'']
	cmd = time_cmd + cmd

	output = subprocess.check_output(cmd)

	with open(time_file, 'r') as f:
		timestamp = f.read()
	print(output)
	with open(log_file, 'a+') as f:
		f.write(output)
		f.write('cpu-usage = ' + timestamp.replace("'",""))


def exec_leaf_space_calc(t, leaf_space_calc, ino, log_file, json_file):
    cmd = [leaf_space_calc] + [device] + [ino] + [json_file]

    with open(log_file, "a+") as f:
        subprocess.check_call(cmd, stdout=f)

def start_benchmark(benchmark_exec, leaf_space_calc, log_dir, json_dir):
    for t in test_cmd_line:
	ftemplate = 'test' + t[0].replace(' ','') + '-' + t[1].replace(' ','-')
        if len(t) > 2:
            ftemplate = ftemplate + t[2].replace(' ','')

        log_file = log_dir + '/' + ftemplate + '.log'
	json_file = json_dir + '/' + ftemplate + '.json'

        test_setup()

	exec_benchmark(t, benchmark_exec, log_file)

	ostat = os.stat(testfile)
	s = 'Inode number = {0}\n'.format(ostat.st_ino)
	print(s)
	with open(log_file, 'a+') as f:
		f.write(s)

        test_reset()

        print('Calculating leaf space used and hash distribution ...\n')
        exec_leaf_space_calc(t, leaf_space_calc, str(ostat.st_ino),
			     log_file, json_file)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage ', sys.argv[0],
	      ' <benchmark executable> <leaf-space-calculator> <log dir> <json dir>')
        sys.exit(1)

    start_benchmark(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
