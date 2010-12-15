#!/bin/bash

# parameters
DEST_PATH=tarballs

##########################################################################

usage()
{
	echo "Usage: $0 <version> <destination>"
}

UPVERSION=$1
if [ -z "${UPVERSION}" ]; then
	usage
	exit 1
fi

FILENAME="freeswitch_${UPVERSION}+dfsg.orig.tar.gz"

if [ -e "${DEST_PATH}/${FILENAME}" ]; then
	echo "A tarball already exist for this version ; remove it if you want to regenerate."
	exit 0
fi

UPFILENAME="freeswitch-${UPVERSION}.orig.tar.bz2"
URL="http://files.freeswitch.org/freeswitch-${UPVERSION}.tar.bz2"

echo "Downloading ${UPFILENAME} from ${URL}"
wget -nv -T10 -t3 -O ${DEST_PATH}/${UPFILENAME} ${URL}
if [ $? != 0 ]; then
	rm -f ${DEST_PATH}/${UPFILENAME}
	echo "Could not find tarball."
	exit 2
fi

echo "Repacking as DFSG-free..."
mkdir -p ${DEST_PATH}/freeswitch-${UPVERSION}.tmp/
cd ${DEST_PATH}/freeswitch-${UPVERSION}.tmp
tar xfj ../${UPFILENAME}
if [ -e "freeswitch-${UPVERSION}" ]; then
	(
	cd freeswitch-${UPVERSION}
#	find  -depth -type f -name 'fpm-*.mp3' -exec rm -rf {} \;
	rm -rf debian
#	rm -rf asterisk-${UPVERSION}/contrib/firmware/
#	rm -rf codecs/ilbc/* codecs/codec_ilbc.c
#	printf "all:\nclean:\n.PHONY: all clean\n" >codecs/ilbc/Makefile
	)
	tar cfz ../${FILENAME} freeswitch-${UPVERSION}
else
	echo "Source tarball layout changed. Check by yourself in '${DEST_PATH}/freeswitch-${UPVERSION}.tmp/'."
	exit 2
fi

echo "Cleaning up..."
cd - >/dev/null
rm -rf ${DEST_PATH}/${UPFILENAME} ${DEST_PATH}/freeswitch-${UPVERSION}.tmp/

