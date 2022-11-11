# MFA-trigger (Built with Selenium Grid)
## Trigger MFA of a single user with a single command

> Note: For now, this fails when authentication is redirected to ADFS.

### Clone the mfa trigger from this repository
```
git clone https://github.com/frankwiersma/mfa-trigger
cd ./mfa-trigger
```

### Build the container
```
docker build -t mfa-trigger .
```

### Run the container
```
docker run -d -p 4444:4444 -v /dev/shm:/dev/shm mfa-trigger
```

### List name of running container
```
docker ps
```

### Enter the container
```
docker exec <name of running container> bash
```

### Run the python script ###
```
python3 /opt/sel/mfa-trigger.py -u "username" -p "password" --retry True --retrycount 3 --phonenumber "+12312389123" --sendsms True
```

## Trigger MFA for multiple users by running multiple Docker containers (to be run outside of the container)
```
./multi-user-docker.sh < /your/path/users_passwords.csv
```


# Todo: 
	- [ ] Add functionality to start MFA-Trigger outside of the container.

__Example:__
### Run the container with username and password as arguments
```
docker run -d -p 4444:4444 -v /dev/shm:/dev/shm mfa-trigger "username" "password"
```