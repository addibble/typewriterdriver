#!/bin/bash

cd /home/pi/typewriterdriver/
./typewriter.py &

cd /home/pi/typewriterdriver/jobs
while true; do
  sync
  curl -s http://hyper.spe.wf/pickup.cgi > tmp
  sleep 5
  if [ -s tmp ] ; then
    mv tmp `date +%Y-%m-%d.%H.%M.%S.txt`
    echo "new job `date +%Y-%m-%d.%H.%M.%S.txt`"
  fi
  while [ "`ls *.in_queue 2> /dev/null`" != "" ] ; do
    echo "waiting to finish..."
    sleep 5
  done
done

