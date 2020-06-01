#!/usr/bin/zsh -f

device=/dev/sdd1
mntpnt=/mnt/
testfile=${mntpnt}/testfile

test_setup()
{
	umount $device > /dev/null 2>&1

	print -n "Creating filesystem on ${device} ..."
	mkfs.xfs -f $device > /dev/null 2>&1 || { print "Unable to create fs"; exit 1 }
	print " done"
	mount $device $mntpnt || { print "Unable to mount $device"; exit 1 }
}

test_loop()
{
	nr_attr=$1
	benchmark_exec=$2

	print "Number of attrs = $nr_attr" | tee -a create.log delete.log

	print "Creating attributes:"
	\time -o create.log -a -f "%e %U %S" ${benchmark_exec} -l 40 -n ${nr_attr} -f ${testfile} 

	print ""

	echo 3 > /proc/sys/vm/drop_caches

	print "Deleting attributes:"
	\time -o delete.log -a -f "%e %U %S" ${benchmark_exec} -l 40 -n ${nr_attr} -r -f ${testfile} 
}

test_reset()
{
    	print "Unmounting $device"
	umount $device || { print "Unable to umount $device"; exit 1 }
}

if [[ $ARGC != 1 ]]; then
	print "Usage: $0 <benchmark executable>"
	exit 1
fi

benchmark_exec=$1

:> create.log
:> delete.log

iters=(1000000 2000000 3000000 4000000 5000000 6000000 7000000 8000000 9000000 10000000)
for nr in $iters; do
	test_setup
	test_loop $nr $benchmark_exec
	test_reset
done
