#!/bin/bash

python cpu_bound.py $1 $2 $3 $4 $5 $6 $7 $8 &
touch progress.txt

TOTAL_TASKS=$(( $1 * $6 ))
COMPLETED_TASKS=`wc -l progress.txt | awk '{ print $1 }'`

while [ "$COMPLETED_TASKS" -ne "$TOTAL_TASKS" ] 
do
        PROGRESS=`echo "$COMPLETED_TASKS / $TOTAL_TASKS" | bc -l | awk '{printf "%08f\n", $0}'`
        COMPLETED_TASKS=`wc -l progress.txt | awk '{ print $1 }'`
        echo "`date +[%Y-%m-%dT%H:%M:%SZ]`[Progress]: #$PROGRESS" >> $9
        sleep 1
done

echo "`date +[%Y-%m-%dT%H:%M:%SZ]`[Progress]: #1.0" >> $9

rm progress.txt

#sleep 10

#shutdown -h now

