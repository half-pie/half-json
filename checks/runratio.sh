#!/bin/bash
mode=$1
if [ ! $mode ]; then
  mode=fix
fi
seq 1 3|xargs -I {} ./runtest.sh {}|grep ratio:|grep $mode|awk -v mode="$mode" '{t += $3}END{printf("%s: %f \n", mode, t/NR)}'
rm random.*
