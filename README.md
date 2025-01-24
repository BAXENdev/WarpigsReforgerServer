# Baxen Reforger Server Setup

Made on `debian12`

## Server Setup

### Setup armaServer User
```sh
# Create armaServer user
sudo usermod -aG sudo armaServer
# Set its password (required)
sudo passwd armaServer

# LOG INTO USER AND RUN THE REST UNDER armaServer
# You should log into armaServer when you want to manage this stuff
sudo -u armaServer -s
cd /home/armaServer/

# Git
# download files
git clone https://github.com/BAXENdev/WarpigsReforgerServer /home/armaServer/armaReforgerServer
```

### Update repo
```sh
# Add non-free to install steam later
echo "deb http://http.us.debian.org/debian stable main contrib non-free" | sudo tee -a /etc/apt/sources.list
# run updates
sudo apt update
sudo apt upgrade
sudo apt-get update
sudo apt-get upgrade
```

### Install and Setup Docker
```sh
# Docker
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Portainer
docker volume create portainer_data
docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:2.21.5
```

### Install Steam and ArmaReforgerServer
```sh
sudo apt-get install steamcmd
# Accept terms
steamcmd +force_install_dir /home/armaServer/armaReforgerServer/gameFiles +login anonymous +app_update 1874900 validate +exit
```

### Build Docker and Server Commands
```sh
# build docker image
sudo docker build -t bax-arma-reforger-server /home/armaServer/armaServerReforger/docker/bax-arma-reforger-server
# setup server commands
echo "alias startServer='docker compose -f /home/armaServer/armaServerReforger/docker/Servers/docker-compose.yaml up -d' >> sudo /etc/bash.bashrc
echo "alias stopServer='docker compose -f /home/armaServer/armaServerReforger/docker/Servers/docker-compose.yaml down' >> sudo /etc/bash.bashrc
echo "alias modifyCompose='nano /home/armaServer/armaServerReforger/docker/Servers/docker-compose.yaml' >> sudo /etc/bash.bashrc
echo "alias updateArma='steamcmd +force_install_dir /home/armaServer/armaReforgerServer/gameFiles +login anonymous +app_update 1874900 validate +exit' >> sudo /etc/bash.bashrc
```

| Command | Description |
|-|-|
| startServer | Starts the arma servers listed in the docker compose |
| stopServer | Stops the arma servers |
| modifyCompose | Open the docker compose file that lists the arma server |
| updateArma | Updates the arma server files |
