#!/bin/sh

VER=$(cat ASTERISK-VERSION)

rm -rf tmp
mkdir tmp
cd tmp
tar xzf ../tarballs/asterisk_${VER}+dfsg.orig.tar.gz
cd asterisk-${VER}
ln -s ../../patches/ patches
quilt push -a

