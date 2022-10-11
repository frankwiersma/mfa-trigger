#!/bin/bash
IFS=" " read -r username password <<< $@

echo "Container BASH: Triggering MFA for $username"
python3 /opt/sel/mfa-trigger.py -u $username -p $password
