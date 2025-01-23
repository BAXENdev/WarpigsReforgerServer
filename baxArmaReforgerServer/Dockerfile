
FROM debian:bullseye-slim
SHELL ["/bin/bash", "-o", "pipefall", "-c"]
RUN apt-get update \
	&& apt-get install -y --no-install-recommends --no-install-suggests lib32stc++6 lib32gcc-s1 ca-certificates libcurl4 net-tools libssl1.1 \
	&& apt-get remove --purge -y \
	&& apt-get clean autoclean \
	&& apt-get autoremove -y
# CMD or ENTRYPOINT? https://docs.docker.com/reference/dockerfile/#shell-and-exec-form
CMD cd /home/reforger/binary \
	./ArmaReforgerServer -profile /home/reforger/profile -config /home/reforger/profile/config.json -addonsDir /home/reforger/workshop/addons -addonDownloadDir /home/reforger/workshop
STOPSIGNAL SIGINT
