
| Command | Description |
|-|-|
| iptables -S | List firewall chains |
| iptables -L | list firewall rules |
| ps -ef \| grep "pattern" | list processes filtered for the pattern |
| tcpdump -n udp port 2001 | monitor udp port 2001 |
| systemctl --full --type service --all | List services |
| sudo journalctl -u myservice.service | Print service logs |
| sudo lshw -short -C memory | list memory info |
| sudo dmidecode --type 17 \| grep "Speed" | Show memory  

Clear logs
sudo journalctl --rotate -u armaDailyRestart.service
sudo journalctl --vacuum-time=1s -u armaDailyRestart.service

reload systems
systemctl daemon-reload
