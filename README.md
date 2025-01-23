# WarpigsReforgerServer
 
```sh
sudo sudo usermod -aG sudo armaServer
echo "armaServer:tempPassword123Fake" | sudo chpasswd
sudo -u armaServer -s
cd /home/armaServer/
echo "tempPassword123Fake" | sudo -S ls # login into sudo

# Git
# download files
git clone https://github.com/BAXENdev/WarpigsReforgerServer .

sudo bash setup_ub2204.sh

exit # logout out of armaServer user
sudo passwd -l armaServer
printf "*********************\nLocked password for 'steam'\nUse `sudo passwd steam` to change the password for the steam user.\n`
```
