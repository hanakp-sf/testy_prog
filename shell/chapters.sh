#!/bin/bash
# premenovanie video suborov
ls $1 | tr "._" "-" | awk -F - "{ print \"20\" \$2 \"-\" \$3 \"-\" \$4 \" \" \$5 \":\" \$6 \":\" \$7}"
