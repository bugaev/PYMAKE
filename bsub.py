#! /usr/bin/env python2.7
#{{{ Importing python modules:
import sys
import os
import subprocess
import pipes
#}}}

known_options = set(['-o', '-e'])

def get_opt(key):
    """ Look for the option with the key "key"
    """
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == key:
            return sys.argv[i + 1]
    else:
        print "Error in " + sys.argv[0] + ": couldn't find option " + key
        sys.exit(1)

def get_command(known_options):
    last_seen_option_index = 0
    for i in range(1, len(sys.argv)):
        if (sys.argv[i] in known_options):
            last_seen_option_index = i
    quoted = [pipes.quote(i) for i in sys.argv[last_seen_option_index + 2:]]
    return ' '.join(quoted)

out_file_name = get_opt('-o')
err_file_name = get_opt('-e')

command = pipes.quote(get_command(known_options) + "&")
command1 = os.path.dirname(os.path.abspath(sys.argv[0])) + "/bsub_monitor.py " + out_file_name + " " + err_file_name + " " + command
#print 'In bsub: command:', command
#print '\nIn bsub: command1:', command1
res = subprocess.call(command1, shell = True)
if not res: print 'Job <999999> is submitted'


