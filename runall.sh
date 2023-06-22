#!/bin/bash

python3 ./testscripts/main.py --no-lic -n 11 "$@"
python3 ./testscripts/main.py -n 16 "$@"