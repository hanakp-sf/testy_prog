#!/bin/sh

if test $# != 3; then
echo "Zly pocet parametrov, treba 3 parametre: obnovadat.sh <pouzivatel> <db> <vstupsubor>"
else 
/usr/bin/pg_restore -a  -d $2 --disable-triggers -1 -p 5432 -U $1 $3 
fi
