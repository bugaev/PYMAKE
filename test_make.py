#! /usr/bin/env python2.7
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
MAX_PARALLEL_JOBS = 2
# Regardless of the location of the make script, the WORKDIR will always be found:
dir = os.path.dirname(os.path.abspath(sys.argv[0])) + "/WORKDIR"
os.chdir(dir)

########################################################################
########################################################################
##################              BEGIN  RULES            ################
########################################################################
########################################################################
def rule_touch(target, prereq):
    subprocess.call("touch " + target, shell=True)
PyMake.queues[rule_touch] = "express"


PyMake.rules['t0'] = rule_touch
PyMake.rules['t1'] = rule_touch
PyMake.rules['t2'] = rule_touch
PyMake.rules['t3'] = rule_touch
PyMake.rules['t4'] = rule_touch
PyMake.rules['t5'] = rule_touch
PyMake.rules['t6'] = rule_touch
PyMake.rules['t7'] = rule_touch
PyMake.rules['t8'] = rule_touch
PyMake.rules['t9'] = rule_touch
#PyMake.rules['t10'] = rule_touch # Bottom node.
#PyMake.rules['t11'] = rule_touch # Bottom node.   
#PyMake.rules['t12'] = rule_touch # Bottom node.
#PyMake.rules['t13'] = rule_touch # Bottom node.
#PyMake.rules['t15'] = rule_touch # Bottom node.
PyMake.rules['t14'] = rule_touch
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  END OF RULES  ^^^^^^^^^^^^^^^^^^^^^^^^^^

PyMake.dorule(dir, globals())

########################################################################
########################################################################
##################           BEGIN DEPENDENCIES         ################
########################################################################
########################################################################
PyMake.depend['t0'] = ['t1', 't2', 't3']
PyMake.depend['t1'] = ['t8', 't4']
PyMake.depend['t2'] = ['t9', 't5']
PyMake.depend['t3'] = ['t6', 't7']
PyMake.depend['t4'] = ['t9']
PyMake.depend['t5'] = ['t14']
PyMake.depend['t6'] = ['t14']
PyMake.depend['t7'] = ['t10']
PyMake.depend['t8'] = ['t11']
PyMake.depend['t9'] = ['t12']
PyMake.depend['t14'] = ['t13', 't15']
#^^^^^^^^^^^^^^^^^^^^^^^^^^^ END OF DEPENDENCIES  ^^^^^^^^^^^^^^^^^^^^^^


PyMake.make('t0', MAX_PARALLEL_JOBS, dir)

sys.exit()


# Problem to be solved:                         ----(0)
#  0  - the target.               	       /    / \                  
# (.) - missing files.      	              /    /   \                 
# [.] - existing files.               --------    /     \                
# {.} - new files.                   /           /       \               
#          		            /           /         \              
#      		     	           /           /           \             
#      		                 [1]         [2]           [3]           
#                                / \         /  \          / \           
#      		     	        /   \       /    \        /   \          
#      		               /    (4)    /     [5]	(6)    \         
#      		              /       \   /        \    /      	\        
#      		             /         \ /          \  /	{7}      
#      		           (8)         (9)          (14)          \      
#      		           /    	|            / \	   \     
#      		          /     	|           /   \           \    
#      		         /      	|          /     \           \   
#      		       [11]           [12]       [13]   [15]         [10]
