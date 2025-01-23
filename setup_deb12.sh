
# For debian12

# add non-free to get steam
echo "deb http://http.us.debian.org/debian stable main contrib non-free" | sudo tee -a /etc/apt/sources.list
# update
sudo apt update
sudo apt upgrade
sudo apt-get update
sudo apt-get upgrade

#

sudo sudo usermod -aG sudo armaServer
echo "armaServer:tempPassword123Fake" | sudo chpasswd
sudo -u armaServer -s
cd /home/armaServer/
echo "tempPassword123Fake" | sudo -S ls # login into sudo

# Git
# download files


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
cd /home/armaServer/baxArmaReforgerServer
sudo docker build -t baxArmaReforgerServer .

# SteamCMD and Reforger
sudo apt-get install steamcmd
# root user will have to accept
steamcmd +login anonymous +app_update 1874900 validate +exit

# Do I add the server command to /etc/bash.basrc
# start servers
# stop servers
# modify compose
# new server script

# lock steam user and tell to change password
exit # logout out of armaServer user
sudo passwd -l armaServer
printf "*********************\nLocked password for 'steam'\nUse `sudo passwd steam` to change the password for the steam user.\n`
