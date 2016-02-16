FROM simplenet/services
COPY ./simplenet_packages /tmp/simplenet_packages/
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
EXPOSE 8081
RUN apt-get update
CMD ls -la /tmp
RUN dpkg -i /tmp/simplenet_packages/*.deb; exit 0;
RUN apt-get --no-install-recommends -y --force-yes install -f
RUN apt-get --no-install-recommends -y install python-pika
RUN /etc/init.d/simplenet-firewall-agent start
RUN /etc/init.d/simplenet-server start
VOLUME /tmp/simplenet_packages
