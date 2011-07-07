#!/bin/sh

VER=$(cat SOURCE-VERSION)

rm -rf tmp
mkdir tmp
cd tmp
tar xzf ../tarballs/libpri_${VER}.orig.tar.gz
cd libpri-${VER}/
ln -s ../../patches/ patches
quilt push -a
if [ $? -eq 0 ]; then
    echo "Done"
else
    echo "Errors"
fi
