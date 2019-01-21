##! python3
##==============================================================================
##    Copyright (c) 2018 COMPAL Electronic Inc. All rights reserved.
##    This program contains proprietary and confidential information.
##    All rights reserved except as may be permitted by prior written consent.
##
##    Compal STiD NPSD Test Program Release Notification.
##
##    ModuleName:
##            Launcher.py
##
##    Abstract:
##            Check Local EXE dir and MDUT+.zip, then download it from server. 
##
##    Author:
##            25-Dec-2018 Sanchez
##
##    Revision History:
##            Rev 1.0.0.1 25-Dec-2018 Sanchez  Merry Xmas
##                    First create.
##==============================================================================
import os
import sys
import shutil
import filecmp
import pathlib
import subprocess
import configparser
from time     import strftime, localtime
from shutil   import copyfile
from datetime import datetime

g_strFileName = os.path.basename(__file__).rstrip('.py')
g_strVersion = "1.0.0.1" 
g_strLogPath, g_strINIPath = None, None

def check_ping(hostname):
    response = os.system("ping -n 1 " + hostname)
    if response == 0:
        return True
    else:
        return False

def compareINI(strServerINI,strLocalINI):
    Config = configparser.ConfigParser()
    Config.read(strServerINI)
    ServerConfig = Config.items('Checksum')
    
    Config2 = configparser.ConfigParser()
    Config2.read(strLocalINI)
    LocalConfig = Config2.items('Checksum')
    
    listFileNeedToCopy = []
    for i in ServerConfig:
        flag1 = False
        for j in LocalConfig:
            if i[0] == j[0]:
                if i[1] != j[1]:
                    printLog("[W][compareINI] Different sum: %s" % i[0])

                    listFileNeedToCopy.append(i[0])
                    flag1 = True
                else:
                    flag1 = True

        if flag1 == False:
            printLog("[W][compareINI] Missing: %s" % i[0])
            listFileNeedToCopy.append(i[0])
            
    return listFileNeedToCopy

def getDownLoadPath(strServerFilePath, strServerChkSumPath, listNeedDownload):
    Config = configparser.ConfigParser()
    Config.read(strServerChkSumPath) 
    listDownloadPath = []
    for item in listNeedDownload:
        strTmpPath = Config.get("Path", item)
        strTmpPath = strServerFilePath + strTmpPath.lstrip('.')
        printLog("[I][getDoenLoadPath] %s Path : %s" % (item,strTmpPath))
        listDownloadPath.append(strTmpPath)
    return listDownloadPath

#####################################################################
# copyfile : use shutil.copy() wich copy dir or file                #
#            without metadata, that will change modified time.      #
# copy2 : copy metadata too.                                        #
#####################################################################
def copyFileFromServer(strSourcePath,strDestPath,strCopyFileName):
    suffix = os.path.relpath(strCopyFileName,strSourcePath)
    if not os.path.exists(strDestPath + "\\" + suffix.rstrip(suffix.split('\\')[-1])[:-1]):
        os.makedirs(strDestPath + "\\" + suffix.rstrip(suffix.split('\\')[-1])[:-1])   
    copyfile(strCopyFileName, strDestPath + "\\" + suffix)

def copyZipFromServer(strSourcePath,strDestPath,strCopyFileName):
    suffix = os.path.relpath(strCopyFileName,strSourcePath)
    if not os.path.exists(strDestPath + "\\" + suffix.rstrip(suffix.split('\\')[-1])[:-1]):
        os.makedirs(strDestPath + "\\" + suffix.rstrip(suffix.split('\\')[-1])[:-1])   
    shutil.copy2(strCopyFileName, strDestPath + "\\" + suffix)


def readINI(strINIPath):
    if not os.path.exists(strINIPath):
        printLog("[E][readINI] INI file '%s' is not exist" % strINIPath)
        g_strFailReasonTemp = "INI file is not exist"
        return False

    try:
        config = configparser.ConfigParser()
        config.read(strINIPath)
        printLog("---------- INI ----------")
        strProjectName = config.get("MDUT_PLUS", 'ProjectName')
        printLog("[I][readINI] ProjectName = %s" % strProjectName)
        strServerPath = config.get("MDUT_PLUS", 'ServerPath')
        printLog("[I][readINI] ServerPath = %s" % strServerPath)

        printLog("---------- INI ----------")        
        return [strProjectName,strServerPath]
    except configparser.Error as err:
        printLog("[E][readINI] Read INI error: %s" %err)
        g_strFailReasonTemp = ("Read INI error: %s" % err)
        return False

def getDateTimeFormat():
    strDateTime = "[%s]" % (strftime("%m/%d %H:%M:%S", localtime()))
    return strDateTime
    
def printLog(strLog):
    print(strLog)
    fileLog = open(g_strLogPath, 'a')
    fileLog.write("%s%s\n" %(getDateTimeFormat(), strLog))
    fileLog.close()

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        print("Using copytree")
        print(s)
        print(d)
        print("==================")
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def getFileModifiedTime(strZipLocateDirPath, strProjectName):
    try:
        p = pathlib.Path(strZipLocateDirPath)
        for item in list(p.glob("*" + strProjectName + "*")):
            strLocalZipPath = str(item)
            printLog("[I][getFileModifiedTime] Zip Path: %s" % strLocalZipPath)

        timeLocalZipMod = datetime.fromtimestamp(os.path.getmtime(strLocalZipPath))
        printLog("[I][getFileModifiedTime] Zip Modified Time: %s" % timeLocalZipMod)
        return strLocalZipPath, timeLocalZipMod

    except:
        printLog("[W][getFileModifiedTime] Read Zip Failed!")
        timeLocalZipMod = None
        return None,None


if __name__ == '__main__':
    strLocalPath = os.path.dirname(os.path.abspath(__file__))
    g_strLogPath = strLocalPath + "\\Launcher.log"
    printLog("==================== Start ====================")
    printLog("[I][main] Python " + sys.version)
    printLog("[I][main] %s.py %s" %(g_strFileName, g_strVersion))

#################################################################################
    # step 1: read ini 
    g_strINIPath = strLocalPath + "\\Launcher.ini"
    tmpResult = readINI(g_strINIPath)
    if (tmpResult == False):
        printLog("[E][Main] Read INI Failed!")
        sys.exit(1)
    else:
        strProjectName = tmpResult[0]
        strServerPath = tmpResult[1]    

#################################################################################
    # step 2: check connection with server
    strServerIP = strServerPath.lstrip('\\').split('\\')[0]
    printLog("[I][Main] ServerIP = %s" % strServerIP)
    if(check_ping(strServerIP)):
        printLog("[I][Main] Ping server success")
    else:
        printLog("[E][Main] Ping server failed")
        sys.exit(1)

#################################################################################
    # step 3: Local makesum if possible
    p = pathlib.Path(strServerPath)
    bFullDownload = False
    strLocalMakeSumPath = ""

    for i in list(p.glob("*" + strProjectName + "*")):
        strFileName = str(i).split('\\')[-1]

    strLocalMakeSumPath = strLocalPath + "\\" + strFileName + "\\MDUT+_MakeChkSum.exe"
  
    if os.path.isfile(strLocalMakeSumPath):
        os.chdir(strLocalPath + "\\" + strFileName)
        printLog("[I][LocalMakeSum] MakeSum.exe exist, now makesum...")
        tmp = subprocess.call([strLocalMakeSumPath,"/maklocalsum"],shell=True)
        if(tmp == 0):
            printLog("[E][LocalMakeSum] MakeSum failed!")
            sys.exit(1)
    else:
        printLog("[I][LocalMakeSum] No local file, start fullldownload...")
        bFullDownload = True

#################################################################################
    # step 4 : FullDownload or INIcompare and download
    ## FullDownload
    strServerFilePath = strServerPath + "\\" + strFileName
    strServerChkSumPath = strServerFilePath + "\\EXE\\ChkSum.txt"
    strLocalFilePath = strLocalPath + "\\" + strFileName
    strLocalChkSumPath = strLocalFilePath + "\\EXE\\ChkSum.txt"

    if bFullDownload:
        try:
            os.makedirs(strLocalFilePath)
        except:
            pass
        copytree(strServerFilePath,strLocalFilePath)

    ## INIcompare and download
    ########################### EXE ###########################
    else:
        printLog("[I][Main] Now CheckSum for EXE ...")
        listNeedDownload = compareINI(strServerChkSumPath, strLocalChkSumPath)
        
        if not listNeedDownload:
            printLog("[I][Main] EXE CheckSum Pass!")

        else:
            printLog("[I][Main] Now Start download missing or different file.")
            listDownLoadPath = getDownLoadPath(strServerFilePath, strServerChkSumPath, listNeedDownload)
            for item in listDownLoadPath:
                copyFileFromServer(strServerPath,strLocalPath,item)

    ########################### ZIP ###########################
        printLog("[I][Main] Now check modified time of the zip...")
        strLocalZipPath, timeLocalZipMod = getFileModifiedTime(strLocalFilePath,strProjectName)
        strServerZipPath, timeServerZipMod = getFileModifiedTime(strServerFilePath,strProjectName)

        if (timeLocalZipMod is None) or (timeLocalZipMod != timeServerZipMod) or (strLocalZipPath.split('\\')[-1] != strServerZipPath.split('\\')[-1]):
            printLog("[I][Main] Zip need download...")
            try:
                os.remove(strLocalZipPath)
            except:
                pass
            copyZipFromServer(strServerPath,strLocalPath,strServerZipPath)

        else:
            printLog("[I][Main] Zip CheckSum Pass!")

#################################################################################
    # step 5 : Double CheckSum
    printLog("[I][Main] Now CheckSum Twice......")
    os.chdir(strLocalFilePath)
    tmp = subprocess.call([strLocalMakeSumPath,"/maklocalsum"],shell=True)
    if(tmp == 0):
        printLog("[E][LocalMakeSum] MakeSum failed!")
        sys.exit(1)
    listdNeedDownload = compareINI(strServerChkSumPath, strLocalChkSumPath)
    if not listdNeedDownload:
        printLog("[I][Main] Double CheckSum Pass!")

    else:
        printLog("[E][Main] Double CheckSum Failed!")

        listdDownLoadPath = getDownLoadPath(strServerFilePath, strServerChkSumPath, listdNeedDownload)
        for item in listdDownLoadPath:
            printLog("[E][Main] Problemfile: %s" % item)

        sys.exit(1)