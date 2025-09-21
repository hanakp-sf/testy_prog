#! /bin/sh

TOOL=/usr/bin/diff
SRC=/home/rodina/fotografie
TGT=/run/media/pato/filmy/fotografie

if test $# != 1 ; then
echo -n "Zly pocet parametrov, treba 1 parameter: `basename $0` <rok_adresar>"
else
$TOOL $SRC/$1 $TGT/$1
fi