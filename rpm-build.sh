#! /bin/bash

PATH="/bin:/usr/bin:/sbin:/usr/sbin:/home/till/bin"

./setup.py sdist
rpmbuild-thisdir.sh -bb cnucnu.spec
