#!/bin/sh
cp -r /root/simplenet /tmp/;
cd /tmp/simplenet
pip install -r pip-requires;
dpkg-buildpackage -us -uc -rfakeroot;
mv /tmp/*.deb /root/simplenet-packages/
