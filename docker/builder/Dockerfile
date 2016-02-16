FROM debian:jessie
RUN apt-get update;
RUN apt-get install python python-setuptools python-dev git libmysqlclient-dev libevent-dev debhelper -y;
RUN easy_install pip;
ADD docker/builder/build_deb_package.sh /usr/local/bin/build_deb_package
RUN chmod +x /usr/local/bin/build_deb_package
COPY ./ /root/simplenet
VOLUME /root/simplenet-packages
