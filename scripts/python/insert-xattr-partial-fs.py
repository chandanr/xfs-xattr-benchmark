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
	# ['-n 10000', '-s 50', '255', '-D 400'],
	# ['-n 10000', '-s 50', '255', '-N 400'],

	# ['-n 1000000', '-s 50', '40', '-N 400000'],
	# ['-n 1000000', '-s 50', '60', '-N 400000'],
	# ['-n 1000000', '-s 50', '255', '-N 400000'],
	# ['-n 1000000', '-s 50', '20 40 60 80 100', '-N 400000'],
	# ['-n 1000000', '-s 50', '120 150 200 220 255', '-N 400000'],
	# ['-n 1000000', '-s 50', '20 40 60 80 100 120 150 200 220 255', '-N 400000'],

	# ['-n 1000000', '-s 50', '40', '-D 400000'],
	# ['-n 1000000', '-s 50', '60', '-D 400000'],
	# ['-n 1000000', '-s 50', '255', '-D 400000'],
	# ['-n 1000000', '-s 50', '20 40 60 80 100', '-D 400000'],
	# ['-n 1000000', '-s 50', '120 150 200 220 255', '-D 400000'],
	# ['-n 1000000', '-s 50', '20 40 60 80 100 120 150 200 220 255', '-D 400000'],
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
	# Setup test dabtree
	cmd = [benchmark_exec] + [t[0]] + [t[1]]
	for i in t[2].split():
		cmd = cmd + ['-l ' + i]
	cmd = cmd + ['-f' + testfile]

	print('cmd =', cmd)

	output = subprocess.check_output(cmd)
	print(output)
	with open(log_file, 'w+') as f:
		f.write(output)
		f.write('\n')

	with open('/proc/sys/vm/drop_caches', 'w') as f:
		f.write('3')

	# Execute insert/delete workload
	cmd = cmd + [t[3]]
	cmd = ['/usr/bin/time'] + ['-o{0}'.format(time_file)] + ['-f \'%e %U %S\''] + cmd

	print('cmd =', cmd)

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
		ftemplate = 'test' + t[0].replace(' ','')
		ftemplate = ftemplate + '-' + t[1].replace(' ','-')
		ftemplate = ftemplate + '-' + t[2].replace(' ','-')
		ftemplate = ftemplate + '-' + t[3].replace(' ','-')

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

		exec_leaf_space_calc(t, leaf_space_calc, str(ostat.st_ino),
				     log_file, json_file)

if __name__ == '__main__':
	if len(sys.argv) != 5:
		print('Usage ', sys.argv[0], ' <benchmark executable> <leaf-space-calculator> <log dir> <json dir>',
		      file=sys.stderr)
		sys.exit(1);

	start_benchmark(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
