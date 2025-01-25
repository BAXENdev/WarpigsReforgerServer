
FROM debian:bullseye-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends --no-install-suggests lib32stdc++6 lib32gcc-s1 ca-certificates libcurl4 net-tools libssl1.1 \
 && apt-get remove --purge -y \
 && apt-get clean autoclean \
 && apt-get autoremove -y
ENTRYPOINT [ "/home/reforger/gameFiles/ArmaReforgerServer" ]
CMD [ \
 "-profile", "/home/reforger/profile", \
 "-config", "/home/reforger/profile/config.json", \
 "-addonsDir", "/home/reforger/gameFiles/addons,/home/reforger/workshop/addons", \
 "-addonDownloadDir", "/home/reforger/workshop", \
 "-maxFPS 60 -backendlog -nothrow -rplEncodeAsLongJobs" \
]
STOPSIGNAL SIGINT
