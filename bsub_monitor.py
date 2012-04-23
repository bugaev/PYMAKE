#! /usr/bin/env python2.7
#{{{ Importing python modules:
import sys
import subprocess
#}}}

out_file_name = sys.argv[1]
err_file_name = sys.argv[2]
command = sys.argv[3]

with open(out_file_name, 'w') as out_file, open(err_file_name, 'w') as err_file:
    res = subprocess.call(command, stdin=None, stdout=out_file, stderr=err_file, shell=True)
    if not res:
        status = 'Done'
    else:
        status = 'Exit'

    out_file.write("\nSubject: Job 999999: <" + command + "> " + status + "\n")
