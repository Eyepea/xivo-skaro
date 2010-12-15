#!/bin/sh

VER=$(cat FREESWITCH-VERSION)

rm -rf tmp
mkdir tmp
cd tmp
tar xzf ../tarballs/freeswitch_${VER}+dfsg.orig.tar.gz
cd freeswitch-${VER}
ln -s ../../patches patches
quilt push -a

