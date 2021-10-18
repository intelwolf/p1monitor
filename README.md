## General
Docker container running the original P1 Monitor from https://www.ztatz.nl/p1-monitor/

For more information see https://www.ztatz.nl/p1-monitor/ (Dutch language) and https://marcel.duketown.com/p1-monitor-docker-versie/ for the latest updated information on usage

## Start the container
Best way to start the container is using the included docker-compose file. That way your instance will also automatically start again after a host reboot
Run the container using the following run command:

    docker-compose up -d

## Docker repository
A docker image is available from docker hub at https://hub.docker.com/r/mclaassen/p1mon. An example docker-compose is included mapping external port 81 to the container.

## Updating
Shut down the container using 'docker-compose down' and use 'docker-compose pull' to update to the latest image version. Start the container as mentioned above

## Migrate
Copy files from a previous version (1.2.0 or later on docker) in the defined 'alldata' directory (see included docker-compose file) in subdirectory 'data' (alldata/data). The import function is also fully functional to migrate from Raspberry Pi to docker

## Forum
A forum for all questions on P1 Monitor is available at https://forum.p1mon.nl
