# /bin/bash
while IFS="," read -r rec_column1 rec_column2
#starting portnumber
COUNTER=4444
do
    echo "Bash: Triggering MFA for $rec_column1"
    docker run -d -p $COUNTER:4444 -v /dev/shm:/dev/shm -v mfa-trigger $rec_column1 $rec_column2&
    sleep 10
    COUNTER=$(( COUNTER + 1 ))
done