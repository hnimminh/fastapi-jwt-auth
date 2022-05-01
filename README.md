
# AUTH - FastAPI JWT Authentication Module

## Requirements
```
You need to build a small authentication server using python (we recommend you use Flask, Starlette or another low footprint framework supporting it) or Golang.
The server will serve the following endpoints:

User registration: given an email address and a password as parameters, it creates a user record
User login: given an email and password, it returns a session token if successful, or 40* error is not (distinguish between the different types of error)
Password change: given an email, current password and new password.

The authentication server should be built using a mySQL database.
Passwords should not be stored in open form in the database, the administrator should not be able to see the current passwords of users.
The session token returned by the auth server should encode the user ID, the creation date and any other information you deem interesting. You can use a jwt token or define your own.
Please provide:

A working server using Docker and Dockerfile to run it, with information in the readme on how to run it.
Unit tests for the server.
Well commented code that can serve as documentation of the  system.

In order to work on the project please clone the repo into your own account.
Once finished, please invite the following people to your repo:

Bonus points: Add a script that tests the API end-to-end that can be used as an automated regression test.
```

## How to Run?

### Prerequisites
* Docker version 20.10.12, build e91ed57 (or later)
* docker-compose version 1.29.2, build 5becea4c (or later)


*This work cover for docker deployment style only*

### Dev Environment
#### Start Auth Server
```shell
docker-compose --file docker-compose.dev.yml up --build
```

#### Run UnitTest
> docker exec -it {docker-container-name} python3 -m pytest -vvs

* Example:

```shell
docker exec -it ebdc-authapi python3 -m pytest -v
```
 
 or

```
docker exec -it ebdc-authapi pytest -v
```

### Prod Environment
```shell
docker build . -t authapi:latest
docker run --name authapi [-p port:port] [-e VAR="<VALUE>] -d authapi:latest
```

* Here are these variables you might want to look into for enviroment configuration.
    * MYSQL_USER
    * MYSQL_PASSWORD
    * MYSQL_DB
    * MYSQL_HOST
    * MYSQL_PORT
    * LOGLEVEL
    * API_WORKERS
    * DEFAULT_TOKEN_EXPIRY
    * SECRET_KEY

## What I have done
* User registration API
* User login API
* User change password API
* Docker for server
* Docker compose for dev environment
* Test Scripts
* Log level and tracable request uuid


### Future Work Todo-List
* Support refresh token beside access token
* Token Black/Block List for critical data in the JWT token is changed (change password, delet/block user, change permissions)
* Use TLS/SSL HTTPS instead of HTTP
* Email should be validation by sending email

