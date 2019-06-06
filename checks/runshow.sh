#!/bin/bash
id=$1
if [ ! $id ]; then
  id=1
fi
base_name=random.$id
cat $base_name.broken.uniq.fix.json|jq -r 'select((.fixed == true) and (.hited == false))|("orgin: "+."origin", "broken:"+."broken","fix:   "+."fix")'
# cat $base_name.broken.uniq.fix.json|jq -r 'select((.fixed == false))|("orgin: "+."origin", "broken:"+."broken","fix:   "+."fix")'
