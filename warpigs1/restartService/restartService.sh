#!/bin/bash

LOG_FILE="/home/armaServer/armaReforgerServer/restartService/service.log"
COMPOSE_FILE="/home/armaServer/armaReforgerServer/docker/Servers/docker-compose.yaml"
DOCKER_BUILD="/home/armaServer/armaReforgerServer/docker/bax-arma-reforger-server/build.sh"
REBUILD_FLAG="/home/armaServer/armaReforgerServer/restartService/rebuild_queued"

log_message() {
	echo "$1" >> $LOG_FILE
}

touch $LOG_FILE

if [[ -f "$REBUILD_FLAG" ]]; then
	log_message "Rebuilding at $(TZ='America/New_York' date)"
	docker compose -f $COMPOSE_FILE down
	"$DOCKER_BUILD"
	sudo -i -u armaServer steamcmd +login anonymous +app_update 1874900 validate +exit
	docker compose -f $COMPOSE_FILE up -d
	rm "$REBUILD_FLAG"
else
	log_message "Restarting at $(TZ='America/New_York' date)"+
	for containerName in $(docker container list --format '{{.Names}}' | grep 'arma-reforger'); do
		log_message "Restarting server $containerName"
		docker container stop $containerName
		sudo -i -u armaServer steamcmd +login anonymous +app_update 1874900 validate +exit
		docker container start $containerName
	done
fi
