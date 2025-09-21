#!/bin/sh

if test $# != 3 ; then
echo -n "Zly pocet parametrov, treba 3 parametre: runsql.sh <pouzivatel> <db> <vstupsubor>"
else
/usr/bin/psql -d $2 -1 -p 5432 -U $1 -f $3
fi 
