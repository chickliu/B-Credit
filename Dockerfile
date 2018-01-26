#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
##
##   @DESCRIPTION : Microservice For bsmserver
##   @NAME        : Dockerfile
##   @VERSION     : 1.0.0
##   @CREATE      : 2017-01-16 15:44:06
##   @UPDATE      : 2017-02-09 15:41:06
##   @MAINTAINER  : colin.lee<likunyao@rongshutong.com>
##
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
FROM hub.rongshutong.com/library/python3:alpine
WORKDIR /app
RUN mkdir -p /data
ADD . /app
RUN pip3 install -r /app/conf/requirements.txt ;\
    apk update && apk add gcc g++ openssl-dev
RUN cp ./bin/docker-entrypoint.sh /entrypoint.sh
VOLUME ["/data"]
EXPOSE 9019
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord"]
