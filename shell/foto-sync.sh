#!/bin/bash

# / na konci je dolezite, berie obsah adresar
SRC=/home/rodina/fotografie/
TGT=/run/media/pato/filmy/fotografie
EXCL=nie_na_ext_disk

if [ -n "$EXCL" ]; then
  EXCL=--exclude=$EXCL
fi

rsync -a --progress $EXCL $SRC $TGT
