#!/bin/bash
set -e

sed -i 's/enabled = no/enabled = yes/' /etc/asterisk/manager.conf

echo "[${AMI_USER}]" >> /etc/asterisk/manager.conf
echo "secret = ${AMI_SECRET}" >> /etc/asterisk/manager.conf
echo "permit = 0.0.0.0/0.0.0.0" >> /etc/asterisk/manager.conf
echo "read = all" >> /etc/asterisk/manager.conf
echo "write = all" >> /etc/asterisk/manager.conf


echo "[${AMI_USER}]" >> /etc/asterisk/ari.conf
echo "type = user" >> /etc/asterisk/ari.conf
echo "read_only = no" >> /etc/asterisk/ari.conf
echo "password = ${AMI_SECRET}" >> /etc/asterisk/ari.conf
echo "password_format = plain" >> /etc/asterisk/ari.conf

exec "$@"