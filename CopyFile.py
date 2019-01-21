import glob, os, shutil
from datetime import datetime

def scanDirectory(strEXEpath):
    # nowtime = datetime.now()
    os.chdir(strEXEpath)
    lSource=[]
    mypath = "EXE\\*"
    glob_list = glob.glob(mypath)
    for entry in glob.iglob(mypath + "*", recursive=True):
        if os.path.isfile(entry):
            timeSourceFile = str(datetime.fromtimestamp(os.path.getmtime(entry)))
            lSource.append([entry,timeSourceFile])
    # timegap = datetime.now() - nowtime
    # print("[I][scanDirectory] Scan %s time: %s" % (strEXEpath,str(timegap)))
    print("[I][scanDirectory] Scan %s finish." % strEXEpath)
    return lSource

def compareScanResult(lSource, lDest):
    lNeedCopy = []
    for strSourcePath in lSource:
        if len(lDest) == 0:
            lNeedCopy.append(strSourcePath[0])
        else:
            flag=False
            for indexDest in range(len(lDest)):
                if strSourcePath[0] in lDest[indexDest]:
                    if lDest[indexDest][1] != strSourcePath[1]:
                        print("%s Modified time not match!" % strSourcePath[0])
                        lNeedCopy.append(strSourcePath[0])
                        flag=True
                        break
                    else:
                        flag=True
                        break
            if flag is False:
                print("%s Not exist!" % strSourcePath[0])
                lNeedCopy.append(strSourcePath[0])
    print("[I][compareScanResult] Compare two timelist complete.")
    return lNeedCopy        

def checkMTimeAndCopy(strEXEPath, nMMDUTCount):
    nowtime = datetime.now()
    strOriginWorkingDirectory = os.getcwd()
    print("[I][checkMTimeAndCopy] Origin Working Directory : %s" % strOriginWorkingDirectory)

    print("[I][checkMTimeAndCopy] Now scan %s." % strEXEPath)
    lSource = scanDirectory(strEXEPath)

    if os.path.exists(strEXEPath + "\\Portfile") is False:
        os.mkdir(strEXEPath + "\\Portfile")
    for i in range(nMMDUTCount):
        strPortfilePath = strEXEPath + "\\Portfile\\" + str(nMMDUTCount)
        if os.path.exists(strEXEPath + "\\Portfile\\" + str(nMMDUTCount)) is False:
            os.mkdir(strEXEPath + "\\Portfile\\" + str(nMMDUTCount))

        print("[I][checkMTimeAndCopy] Now scan %s." % strPortfilePath)
        lDest = scanDirectory(strPortfilePath)

        print("[I][checkMTimeAndCopy] Now compare two scan and get need-copy list.")
        lNeedCopy = compareScanResult(lSource, lDest)
        
        if len(lNeedCopy) is 0:
            print("[I][checkMTimeAndCopy] No file need to copy.")
        else:
            print("[I][checkMTimeAndCopy] Now copy file if needed.")
            for i in lNeedCopy:
                strPath = ""
                for j in range(len(i.split('\\'))-1):
                    strPath = strPath + '\\' + i.split('\\')[j]
                strAbsEXEPath = strEXEPath + '\\' + i
                strAbsDirPath = strPortfilePath + strPath
                strAbsDestPath = strPortfilePath + '\\' + i

                if not os.path.exists(strAbsDirPath):
                    os.makedirs(strAbsDirPath)
                shutil.copy2(strAbsEXEPath, strAbsDestPath)

    os.chdir(strOriginWorkingDirectory)
    print("[I][checkMTimeAndCopy] Change Back to Origin Working Directory.")
    timegap = datetime.now() - nowtime
    print("[I][checkMTimeAndCopy] Total use time: %s" % timegap)