#!/bin/sh

if test $# != 2 ; then 
  echo "Zly pocet parametrov, treba 2 parametre: knoda-rt.sh <pouzivatel> <db>"
  exit 1
fi

if [ ! -f ~/.hk_classes/postgres/$1.$2.conf ] ; then
  echo "Neexistuje konfiguracny subor ~/.hk_classes/postgres/$1.$2.conf"
  exit 1
fi

. ~/.hk_classes/postgres/$1.$2.conf

cat << _EOF > ~/.hk_classes/postgres/driver.conf
<?xml version="1.0" ?>
<DBCONFIGURATION>
  <HOST>$DBSERVER</HOST>
  <USER>$DBUSER</USER>
  <TCP-PORT>$DBPORT</TCP-PORT>
  <BOOLEANEMULATION>$BOOLEANEMULATION</BOOLEANEMULATION>
  <DATABASE>$DATABASE</DATABASE>
  <PASSWORD>$DBPASSWORD</PASSWORD>
</DBCONFIGURATION>
_EOF

#/opt/kde3/bin/knoda -d postgres -b $2 -f fstart -strongruntime
/usr/bin/knoda5-rt -d postgres -b $2 -f fstart
