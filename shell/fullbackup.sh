#!/bin/bash

. /home/pato/backups/backup.conf

echo `date +%Y-%m-%d\ %H:%M:%S`' full backup started' >> $LOG_FILE
tar cvzf $TARGET_DIR/`date +%Y%m%d-%H%M-`full.tar.gz $CONT &>> $LOG_FILE
touch ~pato/.full_done
echo `date +%Y-%m-%d\ %H:%M:%S`' full backup finished' >> $LOG_FILE
