#!/bin/bash
python gen.py > random.1.json
python broken.py random.1.json random.1.broken.json
python clear.py random.1.broken.json random.1.broken.fix.json