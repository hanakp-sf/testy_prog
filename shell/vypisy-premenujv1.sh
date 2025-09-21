#! /bin/sh
# premenovanie mesacnych vypisov
ls * | awk '/^M/ || /^E/ { split($NF,a,/\./);split(a[1],b,/_/);_
system( "mv -v \"" $0 "\" " b[5] "_" b[1] "_" b[3] "." a[2] ) }'
# premenovanie koncorocnych vypisov
