#!/bin/bash

DBROOT=~/Documents/zalohydb
touch ~/.pgpass
chmod 600 ~/.pgpass

# version of PostgreSQL
VERSION=(`psql -d postgres -t -c 'SHOW server_version_num;'`)

# ucty
. ~/.hk_classes/postgres/uctovnik.prodb.conf
echo $DBPASSWORD > ~/.pgpass
~/bin/ucty/zalohadat.sh $DBUSER $DATABASE $DBROOT/ucty/schema3.12/data`date +%Y%m%d`v${VERSION[0]}.sql

# platby - nove
. ~/.hk_classes/postgres/vuctovnik.prodb.conf
echo $DBPASSWORD > ~/.pgpass
~/bin/mesacneplatby/zalohadat.sh $DBUSER $DATABASE $DBROOT/mesacneplatby/schema4.00/data`date +%Y%m%d`v${VERSION[0]}.sql

# vydavky - nove
. ~/.hk_classes/postgres/vuctovnik.prodb.conf
echo $DBPASSWORD > ~/.pgpass
~/bin/vydavky/zalohadat.sh $DBUSER $DATABASE $DBROOT/vydavky/schema1.00/data`date +%Y%m%d`v${VERSION[0]}.sql

# conformed
. ~/.hk_classes/postgres/vuctovnik.prodb.conf
echo $DBPASSWORD > ~/.pgpass
~/bin/conformed/zalohadat.sh $DBUSER $DATABASE $DBROOT/conformed/schema0.12/data`date +%Y%m%d`v${VERSION[0]}.sql

rm ~/.pgpass
