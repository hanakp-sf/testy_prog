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
        print "insert into packs values (\'%s\',\'%s\',\'%s\',%s);" % (h['name'], h['version'], h['release'],h['Size'])      
main(sys.argv)
