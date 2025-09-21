#! /bin/sh
# konvertuje dv subory ( avi Type2) na MPEG 2
# parametre <src_dir> <dest_dir>
# <src_dir> adresar kde su dv subory
# <dest_dir> adresar kde sa ulozia mpeg2 subory

if test $# != 2; then
  echo "Zly pocet parametrov, treba 2 parametre: video-konverzia.sh <src_dir> <dest_dir>"
else 
  for avifile in $1/*.avi
    do
      echo "Converting" $avifile
      bname=`basename $avifile .avi`
      lav2wav $avifile > $2/$bname.wav
      mp2enc -v 0 -o $2/$bname.mp2 < $2/$bname.wav
      lav2yuv $avifile | mpeg2enc -v 0 -f 8 -o $2/$bname.m1v
      mplex -v 0 -f 8 $2/$bname.mp2 $2/$bname.m1v -o $2/$bname.mpeg
      rm $2/$bname.mp2 $2/$bname.m1v $2/$bname.wav
    done 
fi
