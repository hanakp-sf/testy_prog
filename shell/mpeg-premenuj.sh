#! /bin/sh

ls *.mpeg | awk -F "." '{ system( "mv -v \"" $0 "\" " $2 "-" $3 "-" $4 "_" $1 "." $5 ) }'
