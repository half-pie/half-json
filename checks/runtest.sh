#!/bin/bash
id=$1
if [ ! $id ]; then
  id=1
fi
base_name=random.$id
python gen.py > $base_name.json
python broken.py $base_name.json $base_name.broken.json
cat $base_name.broken.json|sort|uniq > $base_name.broken.uniq.json
python test.py $base_name.broken.uniq.json $base_name.broken.uniq.fix.json
