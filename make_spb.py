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
import bvvPyMake
import subprocess
#}}}
MAX_PARALLEL_JOBS = 30
dir = "/nfs/farm/g/glast/u36/agisSims/SPB/g"
SCRIPTDIR = "/u/gi/bugaev/AGIS_SCRIPTS_SLAC"
AREA_DIR = "MLT"
CORSIKA_DIR = dir + "/" + AREA_DIR
os.chdir(dir)

Ze       =                  0
Energies =              [  30,  100] # GeV.
BaseNums =              [1000, 2000] # Base number to start with.
Stats    =              [  5,  200] # Total Number Of Events.
MaxNumsPerShower =      [  5,    5] # Maximum Number of showers Per Run.

ind = 0

def num2par(num):
    return "DAT{:06d}.telescope.par".format(num)

def num2cor(num):
    return "DAT{:06d}.telescope.bz2".format(num)

def par_stat(filename):
    with open(filename) as f:
        for line in f:
            print line.split(None, 3)[2]
            break


pfiles = glob.glob1(CORSIKA_DIR, "DAT*.telescope.par")
for pfile in pfiles:
    matchobj = re.match('DAT(.*).telescope.par', pfile)
    num = matchobj.group(1)
    print pfile, int(num), num2par(int(num))
    par_stat(CORSIKA_DIR + "/" + num2par(int(num)))

sys.exit()




BaseNum = BaseNums[ind]
Stat = Stats[ind]
Energy = Energies[ind]
MaxNumPerShower = MaxNumsPerShower[ind]
n = Stat / MaxNumPerShower
r = Stat % MaxNumPerShower

BaseNumsSorted = sorted(BaseNums)
MaxNumAllowed = BaseNumsSorted[BaseNumsSorted.index(BaseNum) + 1]
LargerBaseNum = BaseNumsSorted.index(BaseNum) + 1

if LargerBaseNum == len(BaseNums):
    MaxNumAllowed = 0 # No limits.
else:
    MaxNumAllowed = BaseNumsSorted[LargerBaseNum] - 1

nums = [i for i in range(BaseNum, BaseNum + n)] + [BaseNum + n for i in [1] if r]
nps  = [MaxNumPerShower for i in range(BaseNum, BaseNum + n)] + [r for i in [1] if r]

if MaxNumAllowed and MaxNumAllowed < nums[-1]:
    print bvvPyMake.bcolors.FAIL + "Last number to be calculated (" + str(nums[-1]) + ") exceeds the Maximum Allowed Number (" + str(MaxNumAllowed) + ")" + bvvPyMake.bcolors.ENDC
    sys.exit()

all_corsika_files = map(lambda x: "MLT/DAT{:06d}.telescope.bz2".format(x), nums) 
all_corsika_pfiles = map(lambda x: "MLT/DAT{:06d}.telescope.par".format(x), nums)

for i in range(len(nums)):
    filename = all_corsika_pfiles[i]
    with open(filename, "w") as f:
        args = str(nums[i]) + " " + str(Ze) + " " + str(nps[i]) + " " + str(nps[i]) + " " + str(Energy) + " multiple " + dir 
        f.write(args)

########################################################################
########################################################################
##################              BEGIN  RULES            ################
########################################################################
########################################################################
def rule_consistency_check(target, prereq = None):
    print target + " checked:)"
    print "prereq: ", prereq
    #sys.exit(1)

def rule_touch(target, prereq):
    subprocess.call("touch " + target, shell=True)

bvvPyMake.queues[rule_touch] = "express"

def rule_corsika(target, prereq):
    os.chdir(SCRIPTDIR)
    # A command to run a corsika batch file with arguments in its
    # parameter file.
    command = "./mm_sub_corsika_spb.sh $(cat " + dir + "/" + prereq[0] + ")"
    subprocess.check_call(command, shell = True)
    # you may want to add some code checking the quality of the output.

bvvPyMake.queues[rule_corsika] = "short"

bvvPyMake.rules['MLT/test'] = rule_touch
bvvPyMake.rules['all_corsika_files'] = rule_touch
bvvPyMake.rules['all_corsika_pfiles'] = rule_consistency_check

for file in all_corsika_files:
    bvvPyMake.rules[file] = rule_corsika
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  END OF RULES  ^^^^^^^^^^^^^^^^^^^^^^^^^^

bvvPyMake.dorule(dir, globals())

########################################################################
########################################################################
##################           BEGIN DEPENDENCIES         ################
########################################################################
########################################################################
for i in range(len(all_corsika_files)):
    bvvPyMake.depend[all_corsika_files[i]] = [all_corsika_pfiles[i]]

bvvPyMake.depend['all_corsika_files'] = all_corsika_files
#^^^^^^^^^^^^^^^^^^^^^^^^^^^ END OF DEPENDENCIES  ^^^^^^^^^^^^^^^^^^^^^^


bvvPyMake.make('all_corsika_files', MAX_PARALLEL_JOBS, dir)

sys.exit()

 
