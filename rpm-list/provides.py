#!/usr/bin/python
# output record
# <package_name>;<package_version>;<package_release>;<provides_name>;<provides_version>
# PACKAGES: <package_id>;<package_name>;<package_version>;<package_release>
# FEATURES: <feature_id>;<feature_name>;<feature_version>
# PROVIDES: <package_id>,<feature_id>
# REQUIRES: <package_id>,<feature_id>
#
# a = {'prvy': (1,2,3)}


import rpm, sys
def stringfromds(ds):
  retlist=[]
  for dataset in ds:
    t=dataset[0]
    values=t.split(" ")[1:]
    retlist.append("\',\'".join(values))
  return retlist

def main(argv):
    ts = rpm.TransactionSet()
    for h in ts.dbMatch( ):
      if h['name'][0:10] <> 'gpg-pubkey':
        #print "%s-%s-%s" % (h['name'], h['version'], h['release'])      
        ds = rpm.ds(h, 'provides')
        if ds:
          lst = stringfromds(ds)
          for d in lst:
            if d.find(',') == -1:
              rst = ',\'=\',\'0\''
            else:
              rst = ''
            print "insert into provides values (\'%s\',\'%s\',\'%s\',%s,\'%s\'%s);" % (h['name'], h['version'], h['release'],h['size'],d,rst)
main(sys.argv)
