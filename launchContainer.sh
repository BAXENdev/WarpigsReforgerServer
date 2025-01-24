#!/bin/bash

docker run \
-p 19001:2001/udp -p 19011:17777/udp -p 19021:19999/udp \
-v /home/armaServer/.steam/steam/steamapps/common/Arma\ Reforger\ Server:/home/reforger/gameFiles \
-v /home/armaServer/armaReforgerServer/workshop:/home/reforger/workshop \
-v /home/armaServer/armaReforgerServer/profiles/warpig1:/home/reforger/profile \
--name test-server bax-arma-reforger-server
