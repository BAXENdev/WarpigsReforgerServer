# Baxen Reforger Server Setup

Made on `debian12`

Current issue: must use host networking because port mapping blocks something for the server?

## Server Setup

### Update repo
Add non-free repo to apt
```sh
echo "deb http://http.us.debian.org/debian stable main contrib non-free" | sudo tee -a /etc/apt/sources.list
```

Update the server
```sh
sudo apt update
sudo apt upgrade
sudo apt-get update
sudo apt-get upgrade
```

### Setup armaServer User
Create armaServer user
```sh
sudo adduser --allow-bad-names armaServer
sudo usermod -aG sudo armaServer
```

**Logout and login into armaServer**
Download git repo
```sh
cd
sudo apt install git
sudo git clone https://github.com/BAXENdev/WarpigsReforgerServer /home/armaServer/armaReforgerServer
```

### Install Docker
Clear pre-installed docker libaries
```sh
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
Include apt repositories for docker
```sh
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
```

Install docker
```sh
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Build server image
```sh
cd /home/armaServer/armaReforgerServer/docker/bax-arma-reforger-server
sudo bash build.sh
```

### Install Portainer
```sh
sudo docker volume create portainer_data
sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:2.21.5
```

### Install Steam and ArmaReforgerServer
```sh
sudo apt update; sudo apt install software-properties-common; sudo apt-add-repository non-free; sudo dpkg --add-architecture i386; sudo apt update
sudo apt install steamcmd
steamcmd +login anonymous +app_update 1874900 validate +exit
```

### Update Firewall
```sh
sudo iptables -A INPUT -p udp --dport 19001:19060 -j ACCEPT 
sudo iptables -A OUTPUT -p udp --dport 19001:19060 -j ACCEPT 
sudo iptables -A DOCKER-USER -p udp --dport 19001:19060 -j ACCEPT 
sudo iptables -A DOCKER -p udp --dport 19001:19060 -j ACCEPT 
```

### Add Server Commands
Adds server commands to bash
```sh
echo "alias startServer='sudo docker compose -f /home/armaServer/armaReforgerServer/docker/Servers/docker-compose.yaml up -d'" | sudo tee -a /etc/bash.bashrc;
echo "alias stopServer='sudo docker compose -f /home/armaServer/armaReforgerServer/docker/Servers/docker-compose.yaml down'" | sudo tee -a /etc/bash.bashrc;
echo "alias modifyCompose='sudo nano /home/armaServer/armaReforgerServer/docker/Servers/docker-compose.yaml'" | sudo tee -a /etc/bash.bashrc
echo "alias updateArma='steamcmd +login anonymous +app_update 1874900 validate +exit'" | sudo tee -a /etc/bash.bashrc
```

| Command | Description |
|-|-|
| startServer | Starts the arma servers listed in the docker compose |
| stopServer | Stops the arma servers |
| modifyCompose | Open the docker compose file that lists the arma server |
| updateArma | Updates the arma server files. when running this command, make sure to sign into armaServer |

### Modify the Profile Config
```sh
sudo nano /home/armaServer/armaReforgerServer/profiles/server1/config.json
```
* Change ip address for `publicAddress`
* Increment the ports
* Set the server name
* Set the admin password
* Set the scenarioId ([missions](https://community.bistudio.com/wiki?title=Arma_Reforger:Server_Config#scenarioId))
* Update or remove the rcon info

If you would like to change the folder name of the profile:
```sh
cd /home/armaServer/armaReforgerServer/profiles
mv server1 newProfileName
sudo nano /home/armaServer/armaReforgerServer/docker/Servers/docker-compose.yaml
```
* Update `server1` to your new profile name in the second volume listing
```yaml
# In the second listing, change server1 to your new profile name
    volumes:
      - /home/armaServer/armaReforgerServer/workshop:/home/reforger/workshop
      - /home/armaServer/armaReforgerServer/profiles/server1:/home/reforger/profile
      - /home/armaServer/.steam/steam/steamapps/common/Arma\ Reforger\ Server:/home/reforger/gameFiles
# to 
    volumes:
      - /home/armaServer/armaReforgerServer/workshop:/home/reforger/workshop
      - /home/armaServer/armaReforgerServer/profiles/newProfileName:/home/reforger/profile
      - /home/armaServer/.steam/steam/steamapps/common/Arma\ Reforger\ Server:/home/reforger/gameFiles
```

## Creating a New Server Instance

TBD