####################################################################
# shared lib for procces related functions functions               #
# !!! TODO migrate other scripts to this lib.                      #
####################################################################
#import const
import inspect
import os
import pwd
import subprocess

PROCESS_DEFAULT_TIMEOUT = 30 # timeout in sec before a process calls returns

#############################################################################################
# run a process                                                                              #
# return code > 0 means trouble                                                              #
# timeout = None just launches the program, return value is from the first script or program #
#                                                                                            #
##############################################################################################
def run_process( cms_str=None, use_shell=True, give_return_value=True, flog=None, timeout=PROCESS_DEFAULT_TIMEOUT ):

    returncode = 1
    stdout = subprocess.PIPE
    stderr = subprocess.PIPE

    if flog != None:
        flog.debug('cmd str runprocess = ' + str( cms_str ) + " voor user " + pwd.getpwuid( os.getuid() ).pw_name + " timeout = " + str(timeout) )

    if give_return_value == False:
        stdout = None

    if timeout != None:

        proc = subprocess.Popen( [ cms_str ], shell=use_shell, stdout=stdout, stderr=subprocess.PIPE  )
        try:
            stdout, stderr  = proc.communicate( timeout=timeout )
            if flog != None:
                flog.debug('stdout = ' + str( stdout ) + " stderr = " + str( stderr) )
            returncode = int( proc.wait() )
        except Exception as e:
            proc.kill() # clean up left over bits.
            if flog != None:
                flog.error( inspect.stack()[0][3] + "cmd(2) = " + str(cms_str) + " " +str(e) )
    else:

        try:
            returncode = subprocess.call( cms_str, shell=True )
        except Exception as e:
            if flog != None:
                flog.error( inspect.stack()[0][3] + "cmd(2) = " + str(cms_str) + " " +str(e) )
    if flog != None:
        flog.debug( "return " + str( [ stdout, stderr, int( returncode ) ] ) )
        
    if ( give_return_value ):
        return [ stdout, stderr, int( returncode ) ]
