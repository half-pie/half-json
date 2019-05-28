#!/bin/bash
seq 1 20|xargs -I {} ./runtest.sh|grep ratio: |awk '{t += $3; h+= $6}{print h/t}'|tail -1