#!/usr/local/bin/python2.7
#{{{ Import this, import that...
import os
import bz2
import sys
import time
import array
import math
import glob
import re
import errno
import bvvPyMake1
import subprocess
#}}}
MAX_PARALLEL_JOBS = 30
dir = "/nfs/farm/g/glast/u36/agisSims/SPB/g/MLT"
SCRIPTDIR = "/u/gi/bugaev/AGIS_SCRIPTS_SLAC"
AREA_DIR = "MLT"
CORSIKA_DIR = dir + "/" + AREA_DIR
os.chdir(dir)

########################################################################
########################################################################
##################              BEGIN  RULES            ################
########################################################################
########################################################################
def rule_touch(target, prereq):
    subprocess.call("touch " + target, shell=True)
bvvPyMake1.queues[rule_touch] = "express"


bvvPyMake1.rules['T'] = rule_touch
bvvPyMake1.rules['t9'] = rule_touch
bvvPyMake1.rules['t8'] = rule_touch
bvvPyMake1.rules['t7'] = rule_touch
bvvPyMake1.rules['t6'] = rule_touch
bvvPyMake1.rules['t5'] = rule_touch
bvvPyMake1.rules['t4'] = rule_touch
bvvPyMake1.rules['t3'] = rule_touch
bvvPyMake1.rules['t2'] = rule_touch
bvvPyMake1.rules['t1'] = rule_touch
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  END OF RULES  ^^^^^^^^^^^^^^^^^^^^^^^^^^

bvvPyMake1.dorule(dir, globals())

########################################################################
########################################################################
##################           BEGIN DEPENDENCIES         ################
########################################################################
########################################################################
bvvPyMake1.depend['T'] = ['t9']
bvvPyMake1.depend['t9'] = ['t6', 't7', 't8']
bvvPyMake1.depend['t8'] = ['t5']
bvvPyMake1.depend['t7'] = ['t3', 't4']
bvvPyMake1.depend['t5'] = ['t1', 't2']
bvvPyMake1.depend['t6'] = ['t5']
#^^^^^^^^^^^^^^^^^^^^^^^^^^^ END OF DEPENDENCIES  ^^^^^^^^^^^^^^^^^^^^^^


bvvPyMake1.make('T', MAX_PARALLEL_JOBS, dir)

sys.exit()

 
