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
RUN apk update && apk add --no-cache supervisor gcc g++ ;\
    pip3 install -r /app/conf/requirements.txt
RUN set -ex ;\
    ## install consul-template
    wget -q -O - http://rst-public.oss-cn-hangzhou.aliyuncs.com/docker/consul-template_0.18.0_linux_amd64.tgz | tar zxf - ;\
    mv consul-template /usr/local/bin
RUN cp ./bin/docker-entrypoint.sh /entrypoint.sh
VOLUME ["/data"]
EXPOSE 9019
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord"]
