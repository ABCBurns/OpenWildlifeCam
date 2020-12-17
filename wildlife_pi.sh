#!/bin/sh

killall python

nohup python -u wildlife.py -c config_pi.json > wildlife.log &

