
## commands
| Command | Description | Command |
|-|-|-|
| aptupdate | Updates repositories | `sudo apt update; sudo apt upgrade; sudo apt-get update; sudo apt-get upgrade` |
| modifyServerCompose | Launches nano into the compose file. | `sudo nano /home/steam/arma_reforger_server/dockerfiles/Bax_ReforgerServer/docker-compose.yaml` |
| startServer | Initializes the docker containers for the arma server | `sudo docker compose -f /home/steam/arma_reforger_server/dockerfiles/Bax_ReforgerServer/docker-compose.yaml up` |
| stopServer | Removes the docker containers for the arma server | `sudo docker compose -f /home/steam/arma_reforger_server/dockerfiles/Bax_ReforgerServer/docker-compose.yaml down` |
| reboot | Restart server | `sudo systemctl reboot` |

## Port Mappings
* public ports start at `2001` and increment up
* a2s ports start at `18001` and increment up
* rcon ports start at `18101` and increment up
