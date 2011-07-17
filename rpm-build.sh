#! /bin/bash

PATH="/bin:/usr/bin:/sbin:/usr/sbin:/home/till/bin"

rm -- noarch/*
./setup.py sdist
ln -s dist/cnucnu-0.0.0.tar.gz
rpmbuild-thisdir.sh --rmsource --clean -bb cnucnu.spec
