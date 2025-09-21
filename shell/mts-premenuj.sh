#!/bin/sh

# zobrazenie vsetkych casovych znaciek v mts subore
#exiftool -s -time:all 00001.MTS

if test $# != 2 ; then
echo -n "Zly pocet parametrov, treba 2 parametre: `basename $0` <import_id> <adresar>"
else
# premenuje *.mts subory v adresari $adresar podla DateTimeOriginal timestamp-u ulozeneho v metadatach daneho suboru
/usr/bin/exiftool -ext mts "-FileName<DateTimeOriginal" -d "%Y-%m-%d_%H-%M-%S_i$1.%%e" $2
fi
