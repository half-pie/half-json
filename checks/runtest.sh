#!/bin/bash
id=$1
if [ ! $id ]; then
  id=1
fi
base_name=random.$id
python3 autogen.py > $base_name.json
python3 broken.py $base_name.json $base_name.broken.json
cat $base_name.broken.json|sort|uniq > $base_name.broken.uniq.json
python3 check.py $base_name.broken.uniq.json $base_name.broken.uniq.fix.json
