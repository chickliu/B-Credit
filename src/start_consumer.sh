#!/bin/bash
for i in `seq 0 15`
do
    index=`printf "%x" $i`
    nohup python3.6 consumer.py $index >> consumer-$index.log 2>&1 &
done
