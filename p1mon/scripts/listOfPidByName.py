import subprocess

########################################################
# find a list of pid if the process name or part of    #
# process name is running                              #
########################################################
def listOfPidByName( process_name ):
    p = subprocess.Popen("ps -eo pid,cmd | awk '{print $1\" \"$2\" \"$3\" \"$4\" \"$5\" \"$6\" \"$7\" \"$8\" \"$9}'" , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.stdout.readlines()
    process_pid_name_dict = {}
    try:
        for line in output:
            process_line = line.decode('utf-8').replace('\n','')
            split_set = process_line.split()
            pid = split_set[0]
            if pid == 'PID': #skip header
                continue
            process = ''.join( split_set[1:] )      # add all but the pid to one string
            process_pid_name_dict[pid] = process    # add to dict
    except Exception:
        pass

    process_pid_list  = list()
    process_name_list = list()
    # build a list of process that satisfy the name
    for item in process_pid_name_dict.items():
        if str( process_name ) in item[1]:
            process_pid_list.append( int(item[0])  )  # add pid to list and convert to int.
            process_name_list.append( process_name )  # add process name to list
    return process_pid_list, process_name_list