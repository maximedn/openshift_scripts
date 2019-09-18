#!/usr/bin/env sh

export EXEC_PATH=./get_logs
export BACKUP_PATH="/Users/maxime/bosa/onedrive/OneDrive - GCloud Belgium/logs"
export OC_PATH=/Users/maxime/oc
export OC_USERNAME=bosa-ext-maxd
export OC_PASSWORD=lol

python3 get_logs.py --env bosa-dt-acc-hcp-fedapi
