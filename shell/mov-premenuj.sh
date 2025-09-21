#!/bin/sh

# zobrazenie vsetkych casovych znaciek v mov subore
#exiftool -s -time:all 00001.MOV

if test $# != 2 ; then
echo -n "Zly pocet parametrov, treba 2 parametre: `basename $0` <import_id> <adresar>"
else
# premenuje *.mov subory v adresari $adresar podla DateTimeOriginal timestamp-u ulozeneho v metadatach daneho suboru
/usr/bin/exiftool -ext mov "-FileName<DateTimeOriginal" -d "%Y-%m-%d_%H-%M-%S_i$1.%%e" $2
fi
