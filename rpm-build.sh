#! /bin/bash

PATH="/bin:/usr/bin:/sbin:/usr/sbin:/home/till/bin"

./setup.py sdist
ln -s dist/cnucnu-0.0.0.tar.gz
rpmbuild-thisdir.sh -bb cnucnu.spec
rm cnucnu-0.0.0.tar.gz
