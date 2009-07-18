#! /bin/bash

PATH="/bin:/usr/bin:/sbin:/usr/sbin"
echo "checking: ${1}"
wget -O - http://download.fedora.redhat.com/pub/fedora/linux/development/source/SRPMS | grep --color=auto "${1}"
#wget -O - http://download.fedoraproject.org/pub/fedora/linux/development/source/SRPMS | grep --color=auto "${1}"
