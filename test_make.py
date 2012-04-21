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
import PyMake
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
PyMake.queues[rule_touch] = "express"


PyMake.rules['T'] = rule_touch
PyMake.rules['t9'] = rule_touch
PyMake.rules['t8'] = rule_touch
PyMake.rules['t7'] = rule_touch
PyMake.rules['t6'] = rule_touch
PyMake.rules['t5'] = rule_touch
PyMake.rules['t4'] = rule_touch
PyMake.rules['t3'] = rule_touch
PyMake.rules['t2'] = rule_touch
PyMake.rules['t1'] = rule_touch
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  END OF RULES  ^^^^^^^^^^^^^^^^^^^^^^^^^^

PyMake.dorule(dir, globals())

########################################################################
########################################################################
##################           BEGIN DEPENDENCIES         ################
########################################################################
########################################################################
PyMake.depend['T'] = ['t9']
PyMake.depend['t9'] = ['t6', 't7', 't8']
PyMake.depend['t8'] = ['t5']
PyMake.depend['t7'] = ['t3', 't4']
PyMake.depend['t5'] = ['t1', 't2']
PyMake.depend['t6'] = ['t5']
#^^^^^^^^^^^^^^^^^^^^^^^^^^^ END OF DEPENDENCIES  ^^^^^^^^^^^^^^^^^^^^^^


PyMake.make('T', MAX_PARALLEL_JOBS, dir)

sys.exit()

 
