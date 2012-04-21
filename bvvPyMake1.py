#{{{ Importing python modules:
import os
import errno
import sys
import subprocess
import topsort
import time
import math
import glob
import re
#}}}

# A line to create merge conflict.

script_dir = os.getcwd()

depend = {}
rules = {}
queues = {}
default_que = "express"

def find_path(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return None
        for node in graph[start]:
            if node not in path:
                newpath = find_path(graph, node, end, path)
                if newpath: return newpath
        return None


def find_all_paths(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if not graph.has_key(start):
            return []
        paths = []
        for node in graph[start]:
            if node not in path:
                newpaths = find_all_paths(graph, node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths


def find_shortest_path(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return None
        shortest = None
        for node in graph[start]:
            if node not in path:
                newpath = find_shortest_path(graph, node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

# START HERE FROM DELETION
def test_rules(rules, tsorted, depend, thetarget, echo=0):
 """ Test if all rules are present.
 Return only entries from tsorted which are relevant to thetarget.
 Add an empty prereq for targets that dont have any.
 """
 sorted_related = []

 for target in tsorted:
    if target == None: # In case thetarget doesn't have any prerequisites.
        continue
    if not find_path(depend, thetarget, target):
        if echo: print "Removed from the chain: " + target
        continue
    else:
        if echo: print "Path between", thetarget, "and", target + ":", find_path(depend, thetarget, target)
        sorted_related.append(target)
 
 if echo: print "Ordered rules:"
 for i in sorted_related:
      if i in rules:
           if i not in depend: depend[i] = [] 
           if echo: print str(rules[i]) + "(" + str(i) + str(depend[i]) + ")"
           # target needs not to have any
           # prerequisites, but need to have an entry in 'depend' associative
           # array.
      elif i in depend:
           print bcolors.FAIL + "ERROR: Rule for --->" + str(i) + "<--- not found. Exit!" + bcolors.ENDC
           sys.exit()
      else:
           file_present = os.path.isfile(i)
           if file_present:
                if echo: print "Input file", i
           else:
                print bcolors.FAIL + "ERROR: Both input file --->" + str(i) +\
                "<--- and its rule do not exist. Exit!" + bcolors.ENDC
                sys.exit()
 print bcolors.OKGREEN + "All rules found:)" + bcolors.ENDC
 return sorted_related



def need_update(targets, changed_files, kids, echo = 0):
    tobeupdated = []
    preserved = []
    def mark_kids_changed(target, changed_files):
        if target not in kids: return
        for kid in kids[target]:
            changed_files.add(kid) 

    for target in targets:
     file_present = os.path.isfile(target)
     outfile_exists, status_defined, status_success = check_bsub_success(target + ".out")
     if not file_present:
      tobeupdated.append(target)
      if echo: print target + " will be updated:  doesn't exist."
      mark_kids_changed(target, changed_files)
     elif outfile_exists and not status_success:
      if echo: print target + " exists but its *.out file indicates it is invalid."
      mark_kids_changed(target, changed_files)
      tobeupdated.append(target)
     else: # Target file exists.
      if target in changed_files:
       tobeupdated.append(target)
       if echo: print target + " will be updated: ancestor(s) will change."
       mark_kids_changed(target, changed_files)
      else: # File already exists, will it be updated?
       #target_mod = time.ctime(os.path.getmtime(target))
       target_mod = os.path.getmtime(target)
       for dep in depend[target]:
        dep_mod = os.path.getmtime(dep)
        if dep_mod > target_mod:
         tobeupdated.append(target)
         if echo:
             print target + " will be updated: " + dep + " is newer; " +\
             target + ": " + str(target_mod) + ", " + dep + ": " + str(dep_mod)
         mark_kids_changed(target, changed_files)
         break # Found a prerequisite newer than the target
       else: # all reasons to rebuild the target are exhausted.
        preserved.append(target) # Target doesn't need any updates.

    return tobeupdated, preserved

def strip_input_files(tsorted, depend):
    """ Exclude input files from tsorted.
    """
    return filter(lambda(x): x in depend, tsorted)

def check_bsub_success(filename, echo = False):
    """ Looking for the word 'Done' in a given *.out file
        Return a pair of boolean: (File Found, Status Found, Status Success)
    """
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            for line in f:
                matchobj = re.match('Subject: Job.*> (.*)$', line)
                if matchobj:
                    status = matchobj.group(1)
                    if echo: print matchobj.group(0) 
                    if status == 'Done':
                        return (True, True, True)
                    else:
                        return (True, True, False)
            else:
                return (True, False, False)
    else:
        return (False, False, False)


def get_tobeupdated(targets, sorted_related, kids, echo = 1):
    tobeupdated = []
    preserved = []
    def get_times(targets):
        times = {}
        for target in targets:
            if os.path.isfile(target):
                target_mod = os.path.getmtime(target)
                times[target] = target_mod
        return times

    times = get_times(targets)
    if echo: print 'times: ', times
    updated = []
    changed = set()
    for target in targets:
        for path in find_all_paths(kids, target, 'T'):
            for t in path:


def make(thetarget, MAX_PARALLEL_JOBS, dir):
    """ Make Loop
    """
    if thetarget not in depend: depend[thetarget] = [None]
    lockdir = dir + "/LOCKS"
    os.chdir(dir)
    # Produce "parent" list suitable for topsort:
    depend_flat = [(k, lst) for k, v in depend.iteritems() for lst in v] # assoc. array --> list transformation.
    parent_pairs = [(dep[1], dep[0]) for dep in depend_flat]

    kids = {}
    for pair in parent_pairs:
     parent, child = pair
     if parent not in kids:
      kids[parent] = []
     kids[parent].append(child)

    sorted_nodes = topsort.topsort(parent_pairs)

    sorted_related = test_rules(rules, sorted_nodes, depend, thetarget, echo = 0)
    targets=strip_input_files(sorted_related, depend)
    print "Final target list: ", targets
    print 'kids: ', kids

    get_tobeupdated(targets, sorted_related, kids, echo = 1) 


    sys.exit()

    changed_files = set()

    tobeupdated, preserved = need_update(targets, changed_files, kids, echo
                                        = 1)

    print bcolors.OKBLUE + "Targets that will be preserved: " + str(preserved) + bcolors.ENDC
    print bcolors.HEADER + "Targets that will be updated: " + str(tobeupdated) + bcolors.ENDC

    print bcolors.HEADER + "Rules will be executed in the following order:" + bcolors.ENDC
    for target in tobeupdated:
     if target in rules: 
         if rules[target] in queues:
             queue = queues[rules[target]]
         else:
             queue = default_que
         print rules[target].__name__ + "(" + target + ", " + str(depend[target]) + ")" + "[" + queue + "]"
     else: # This is not likely to happen - a similar check is done earlier.
      print bcolors.FAIL + "ERROR: Rule for --->" + str(target) + "<--- not found. Exit!" + bcolors.ENDC
      sys.exit()

    answer = raw_input("Proceed? Say \"y\" or \"Y\" if yes >>> ") 
    if answer != "y" and answer != "Y":
     print "Aborted by user"
     sys.exit()

    # Create lockdir, exit if a regular file with the same name exists.
    try:
        os.mkdir(lockdir)
    except OSError as (errnum, errmsg):
        if not (errnum == errno.EEXIST and os.path.isdir(lockdir)):
            print "Remove file", lockdir, "from the way."
            raise
    running_job_ids = set()
    bsubout = subprocess.check_output("bjobs")
    for i in bsubout.splitlines()[1:]:
        running_job_ids.add(int(i.split(' ', 1)[0]))


    found_running_id = False
    for filename in glob.glob(lockdir + "/make*.lock"):
        with open(filename) as file:
            id = int(file.readline()) 
            if id in running_job_ids:
                found_running_id = True
                print bcolors.FAIL + str(id)
    if found_running_id:
        print "Processess from previous make session are still running.\
         Exit." + bcolors.ENDC
        sys.exit()


    for filename in glob.glob(lockdir + "/make*.lock"):
        os.remove(filename)
    for filename in glob.glob(lockdir + "/make*.done"):
        os.remove(filename)

    ind = -1
    rules_done = set()
    cnt_done_prev = 0
    cnt_done = 0
    first_job_started = False
    while True:
        files_done = glob.glob1(lockdir,"make*.done")
        cnt_done = len(files_done)
        # We noticed that the number of *.done files changed:
        if cnt_done > cnt_done_prev:
            print "cnt_done:", cnt_done
            # Lets update rules_done set:
            for file in files_done:
                matchobj = re.match('make(.*).done', file)
                num = matchobj.group(1)
                if int(num) not in rules_done:
                    outfilename = tobeupdated[int(num)] + '.out'
                    file_found, status_found, status_success = check_bsub_success(outfilename, echo = True)
                    if status_success:
                        rules_done.add(int(num))
                        print "rules_done: ", str(rules_done)
                        os.remove(lockdir + '/make' + num + '.lock')
                    elif file_found and status_found and not status_success:
                        print bcolors.FAIL + "Error: " + outfilename + ": status unsuccessful:"\
                              + bcolors.ENDC
                        sys.exit()
                    else:
                        # *.done file exists, but *.out file is not ready yet.
                        # Maybe, next cycle it will be ready.
                        # Number of actually done rules
                        # (len(files_done)) is less than
                        # the number of *.done files (cnt_done):
                        cnt_done = cnt_done - 1
                    if len(rules_done) == cnt_done: break

        rules_lock_present = set()
        files_lock = glob.glob1(lockdir,"make*.lock")
        for file in files_lock:
            matchobj = re.match('make(.*).lock', file)
            num = matchobj.group(1)
            rules_lock_present.add(int(num))
        # Check if any ready *.out file exist for corresponding *.lock files:
        for num in rules_lock_present:
            outfile = tobeupdated[num] + '.out'
            lastline = subprocess.check_output("( tail -n 2 " + outfile + " | head -n 1 ) 2>/dev/null", shell = True)
            if lastline:
                matchobj = re.match('Read file <[^>]+> for stderr output of this job.', lastline)
                if matchobj:
                    print bcolors.WARNING + "Warning: -->" + outfile + "<-- found, but its lock file still exists!", bcolors.ENDC
                    file_found, status_found, status_success = check_bsub_success(outfile, echo = False)
                    if not status_success:
                        print bcolors.FAIL + "Error: -->" + outfile + "<-- status unsuccessful:"
                        file_found, status_found, status_success = check_bsub_success(outfile, echo = True)
                        print  bcolors.ENDC
                        sys.exit()


        # If some targets are built, launch more jobs.
        if (cnt_done > cnt_done_prev) and cnt_done != len(tobeupdated) or not first_job_started:
            cnt_done_prev = cnt_done
            
            rules_lock_future = set(rules_lock_present)
            print "rules_lock_present before adding", rules_lock_present

            # find first unfinished target:
            for i in range(len(tobeupdated)):
                if i not in rules_done:
                    first_unfinished = i
                    print "first_unfinished: ", first_unfinished, tobeupdated[first_unfinished]
                    break

            safe2start = []
            for i in range(first_unfinished, len(tobeupdated)):
                if (i not in rules_done) and (i not in rules_lock_present):
                    #"i": index of a rule that potentially can be started.
                    print "Checking if rule ", i, tobeupdated[i], " can be started..."
                    for j in range(first_unfinished, i): # i == first_unfinished: cycle is empty, no unfinished ancestors.
                        if j in rules_done:
                            print j, tobeupdated[j], " is finished, not an obstacle."
                            continue # Finished target is not an obstacle.
                        if find_path(depend, tobeupdated[i], tobeupdated[j]):
                            print j, tobeupdated[j], " is an ancestor for ", i, tobeupdated[i], " cannot start ", i
                            break # "j" is an ancestor of "i" --> cannot start this "i", lets check "i + 1".
                    else:
                        # If we are here, it is safe to start "i"th rule.
                        print "No unfinished ancestors for ", i, tobeupdated[i]
                        safe2start.append(i)
                        rules_lock_future.add(i)
            print "safe2start: ", safe2start
            MAX_ADD_JOBS = MAX_PARALLEL_JOBS - len(rules_lock_present)
            print "MAX_ADD_JOBS:", MAX_ADD_JOBS, "JOBS CURRENTLY:", len(rules_lock_present)
            for ind in safe2start[0: MAX_ADD_JOBS]:
                if os.path.isfile(tobeupdated[ind] + '.out'): os.remove(tobeupdated[ind] + '.out')
                if os.path.isfile(tobeupdated[ind] + '.err'): os.remove(tobeupdated[ind] + '.err')
                if rules[tobeupdated[ind]] in queues:
                    queue = queues[rules[tobeupdated[ind]]]
                else:
                    queue = default_que
                command = "bsub " + "-q " + queue + " -o " + dir + "/" + tobeupdated[ind] + ".out " + "-e " + dir + "/" + tobeupdated[ind] + ".err " + script_dir + "/" + sys.argv[0] + " " + rules[tobeupdated[ind]].__name__ + " " + tobeupdated[ind] + " " + '"' + str(depend[tobeupdated[ind]]) + '" ' + str(ind)
                print command
                bsubout = subprocess.check_output(command, shell = True)
                matchobj = re.match('Job <(\d*)> is submitted', bsubout)
                if not matchobj:
                    print "bsub output: ", bsubout
                    print bcolors.FAIL + "Job was not submitted. Exit!" +\
                            bcolors.ENDC
                    sys.exit()
                else:
                    jobid = matchobj.group(1)
                    first_job_started = True
                f = open(lockdir + '/make' + str(ind) + '.lock', 'w')
                f.write(jobid + '\n')
                f.write(command)
                f.close()
                rules_lock_present.add(ind)
                print "rules_lock_present after adding", rules_lock_present
            print "Number of jobs in the queue: ", len(rules_lock_present)
        if cnt_done < len(tobeupdated):
            time.sleep(1)
        else:
            break
    print bcolors.OKGREEN + "All Done!:)" + bcolors.ENDC


def dorule(dir, arg_globals):
    #{{{ Case when the script is called with parameters:
    lockdir = dir + "/LOCKS"
    argc = len(sys.argv)
    target = prereq = ''
    if  argc > 1:
        cnt = 0
        fname = sys.argv[1]
        if argc > 2:
            target = sys.argv[2]
            if argc > 3:
                prereq = eval(sys.argv[3])
                if argc > 4:
                    ind = sys.argv[4]
        arg_globals[fname](target, prereq)
#       funcall = fname + '(' + target + ',' + prereq + ')'
#       eval(funcall, arg_globals)
        outfile = open(lockdir + "/make" + str(ind) + ".done", "w")
        outfile.write("done")
        outfile.close() 
        sys.exit()
    #}}}
