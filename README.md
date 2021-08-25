## General
Docker container running the original P1 Monitor from https://www.ztatz.nl/p1-monitor/

For more information see https://www.ztatz.nl/p1-monitor/ (Dutch language)

## Start the container
Best way to start the container is using the included docker-compose file. That way your instance will also automatically start again after a host reboot
I run the container using the following run command:

    docker-compose up -d

## Docker repository
A docker image is available from docker hub. An example docker-compose is included mapping external port 81 to the container.

## Updating
Follow instructions from the original author on updating to a new version.

## Migrate
Copy files from a previous version (1.2.0 or later) in the defined 'alldata' directory in subdirectory 'data'
