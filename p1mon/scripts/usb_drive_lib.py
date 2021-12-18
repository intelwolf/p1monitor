####################################################################
# shared lib for processing usb_drives                             #
####################################################################
import const
import inspect
import subprocess

USB_LIST = [ '/dev/sda1', '/dev/sdb1' , '/dev/sdc1' , '/dev/sdd1' ]
MOUNTPOINT = const.DIR_USB_MOUNT
MOUNT_TIMEOUT = 30

#############################################
# mount a device like /dev/sda1 on a given  #
# mount point                               #
# return code > 0 means trouble             #
#############################################
def mount_device( device=USB_LIST[0], flog=None, mount=const.DIR_USB_MOUNT, timeout=MOUNT_TIMEOUT ):

    status_str = ""
    returncode = 1

    try:
        flog.debug('start van mount van usb drive/stick ' + str( device ) )
        status_str = ''

        cmd = "/usr/bin/sudo mount -o 'uid=p1mon,gid=p1mon' " + device + " " + mount
        proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )
        stdout, stderr  = proc.communicate( timeout )
        returncode = int( proc.wait() )

        try:
            status_str = str( stderr.decode('utf-8').replace('\n', ' ') )
        except Exception:
            pass

    except Exception as e:
        flog.error(inspect.stack()[0][3] + str(e) )
        status_str = str(e)

    flog.debug( "mount USB status: " + str( [status_str, int( returncode) ]) )
    return [ status_str, int( returncode) ]


#############################################
# un mount a device from a mount point      #
# return code > 0 means trouble             #
#############################################
def unmount_device( mount=const.DIR_USB_MOUNT, flog=None, timeout=MOUNT_TIMEOUT ):

    status_str = ""
    returncode = 1

    try:

        flog.debug('start van unmount van usb drive/stick op mount point ' + str( mount ) )

        cmd = '/usr/bin/sudo umount ' + mount
        proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )
        stdout, stderr  = proc.communicate( timeout )
        returncode = int( proc.wait() )
        
        try:
            status_str = str( stderr.decode('utf-8').replace('\n', ' ') )
        except Exception:
            pass
       
    except Exception as e:
        flog.error(inspect.stack()[0][3] + str(e) )
        status_str = str(e)

    flog.debug( "unmount USB status: " + str([ status_str, int( returncode ) ]) )
    return [status_str, int( returncode) ]
