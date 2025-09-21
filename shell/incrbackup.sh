#!/bin/bash

. /home/pato/backups/backup.conf

echo `date +%Y-%m-%d\ %H:%M:%S`' incremental backup started' >> $LOG_FILE
tar cvzf $TARGET_DIR/`date +%Y%m%d-%H%M-`incr.tar.gz  -N ~pato/.full_done $CONT &>> $LOG_FILE
echo `date +%Y-%m-%d\ %H:%M:%S`' incremental backup finished' >> $LOG_FILE
