#! python2
#coding:utf-8
##==============================================================================
##    Copyright (c) 2017 COMPAL Electronic Inc. All rights reserved.
##    This program contains proprietary and confidential information.
##    All rights reserved except as may be permitted by prior written consent.
##
##    Compal STiD NPSD Test Program Release Notification.
##
##    ModuleName:
##            Python_Package_Install_Tool.py
##
##    Abstract:
##            Python Package Installation UI.
##
##    Author:
##            28-Dec-2017 Sanche Peng
##
##    Revision History:
##            Rev 1.0.0.3 14-May-2018 Sanchez Peng
##                    1, Hide requiredment of install package
##                    2, Add ini to set requirement
##                    3, Auto-detect packagefile at both showlist and requirement directory
##                    4, Add support to .tar.gz file
##            Rev 1.0.0.2 02-May-2018 Sanchez Peng 
##                    Add support to some specific package
##            Rev 1.0.0.1 28-Dec-2017 Sanchez Peng
##                    First create.
##==============================================================================
import io
import os
import time
import struct
import threading
import subprocess
import ConfigParser
import tkMessageBox
import Tkinter as tk
from os import walk
from Tkinter import *
from ftplib import FTP
from subprocess import Popen, PIPE
from ScrolledText import ScrolledText
from time import strftime, localtime, sleep
from distutils.dir_util import copy_tree

g_strVersion = "1.0.0.3"
g_strLogPath, PythonBitVersion, g_PIPFileName = None, None, None
nWindowsWidth, nWindowsHeight = None, None
PackageShowList, RefinePackageShowList ,CheckVar = [],[],[]
g_strCurrentDirectory = None
g_PackageRequirementList, RequirementList = [],[]

def getDateTimeFormat():
    strDateTime = "[%s]" % (strftime("%Y/%m/%d %H:%M:%S", localtime()))
    return strDateTime

def printLog(strPrintLine):
    fileLog = open("Python_Package_Install_Tool.log", 'a')
    print strPrintLine
    fileLog.write("%s%s\n" % (getDateTimeFormat(), strPrintLine))
    fileLog.close()

def readINI(strINIPath):
    global g_strFailReasonTemp, g_nRecordSec, g_strEC, g_strdBUpperLimit, g_strdbLowerLimit, g_strplayingfile,RefinePackageShowList
    global g_nMicIndex,g_PackageRequirementList
    if not os.path.exists(strINIPath):
        printLog("[E][readINI] INI file '%s' is not exist" % strINIPath)
        g_strFailReasonTemp = "INI file is not exist"
        return False

    try:
        config = ConfigParser.ConfigParser()
        config.read(strINIPath)
        printLog("---------- INI ----------")
        for index in range(len(RefinePackageShowList)):
            if config.has_option('SanchezHandsome',RefinePackageShowList[index][0]):
                g_PackageRequirementList.append([RefinePackageShowList[index][0],config.get('SanchezHandsome',RefinePackageShowList[index][0]).split(',')])     
        for index in range(len(g_PackageRequirementList)):
            printLog("[I][readINI] " + g_PackageRequirementList[index][0] + " = " + str(g_PackageRequirementList[index][1]))

        printLog("---------- INI ----------")        
        return True

    except ConfigParser.Error, err:
        printLog("[E][readINI] Read INI error: %s" %err)
        g_strFailReasonTemp = ("Read INI error: %s" % err)
        return False

def removeNotSupportPackage():
    global PackageShowList, g_PIPFileName, RequirementList

    # Define what is going to remove. 
    RemoveList = []
    if PythonBitVersion == 32:
        for i in range(len(PackageShowList)):
            if "amd64" in PackageShowList[i]:
                RemoveList.append(PackageShowList[i])
            if "pip-" in PackageShowList[i]:
                g_PIPFileName = PackageShowList[i]
                printLog("[I][removeNotSupportPackage]" + g_PIPFileName)
                RemoveList.append(PackageShowList[i])

    elif PythonBitVersion == 64:
        for i in range(len(PackageShowList)):
            if "win32" in PackageShowList[i]:
                RemoveList.append(PackageShowList[i])
            if "pip-" in PackageShowList[i]:
                g_PIPFileName = PackageShowList[i]
                RemoveList.append(PackageShowList[i])

    # Remove
    for item in range(len(RemoveList)):
        PackageShowList.remove(RemoveList[item])

    printLog("[I][removeNotSupportPackage] Remove Showlist unsupported package success!")

    # Define what is going to remove. 
    RemoveList = []
    if PythonBitVersion == 32:
        for i in range(len(RequirementList)):
            if "amd64" in RequirementList[i]:
                RemoveList.append(RequirementList[i])

    elif PythonBitVersion == 64:
        for i in range(len(RequirementList)):
            if "win32" in RequirementList[i]:
                RemoveList.append(RequirementList[i])


    # Remove
    for item in range(len(RemoveList)):
        RequirementList.remove(RemoveList[item])

    printLog("[I][removeNotSupportPackage] Remove Requirement unsupported package success!")



def refinePackageShowList():
    global RefinePackageShowList

    # Making two-dimension array of[package name][package version] to make checkbox. 
    RefinePackageShowList = [[None for x in range(2)] for y in range(len(PackageShowList))] 
    for index in range(len(PackageShowList)):
        TempPackageName = PackageShowList[index]
        RefinePackageShowList[index][0] = TempPackageName.split('-')[0]
        RefinePackageShowList[index][1] = TempPackageName.split('-')[1]
    printLog("[I][refinePackageShowList] CheckBox Name refine success!")

def installPackage(PackageName):
    printLog("[I][installPackage] Installing " + PackageName)
    bNotInRequirementDirectory = False

    if PackageName == "pyadb-0.1.4":
        strPyadbPath = g_strCurrentDirectory + '\\' + PackageName
        copy_tree(strPyadbPath, "C:\\Python27\\Lib\\site-packages\\pyadb")
    elif 'olefile' in PackageName:
        printLog("[I][startInstalling] olefile starting install...")
        os.chdir("./PythonPackageRequirement/olefile-0.45.1")
        strolefilePath = g_strCurrentDirectory + '\\' + PackageName + '\\setup.py' 
        PackageInstallProcess=subprocess.call(["python",strolefilePath,"install"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        printLog("[I][startInstalling] olefile installed.")
        os.chdir("../../")

    else:
        # InstalledState: 0 = successfully installed ; 1 = Already installed; 2 = Not support in this platform.
        InstalledState=0
        PackageInstallProcess=subprocess.Popen(['pip', 'install', './PythonPackageRequirement/' + PackageName], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        # Read console error and message 
        while True:
            errorline=PackageInstallProcess.stderr.readline()
            if errorline != '':
                # If Package is not in PythonPackageRequirement directory
                if 'looks like a filename, but the file does not exist' in errorline:
                    bNotInRequirementDirectory = True
                    break
                # Find if package not support in this platform
                if "is not a supported" in errorline:
                    InstalledState = 2
                    printLog("[W][installPackage] " + errorline.rstrip('\n'))
                    break

            line = PackageInstallProcess.stdout.readline()
            if line != '':
                # Find if package already installed
                if "Requirement already satisfied" in line:
                    InstalledState = 1
                    printLog("[W][installPackage] " + line.rstrip('\n'))
                else:
                    InstalledState = 0
                    printLog("[I][installPackage] " + line.rstrip('\n'))
                    
            else:
                break
        
        # Not in PythonPackageRequirement Directory, Now try yo use PythonPackageShowList Directory
        if bNotInRequirementDirectory:
            InstalledState=0
            PackageInstallProcess=subprocess.Popen(['pip', 'install', './PythonPackageShowList/' + PackageName], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            
            # Read console error and message 
            while True:
                errorline=PackageInstallProcess.stderr.readline()
                if errorline != '':
                    # Find if package not support in this platform
                    if "is not a supported" in errorline:
                        InstalledState = 2
                        printLog("[W][installPackage] " + errorline.rstrip('\n'))
                        break

                line = PackageInstallProcess.stdout.readline()
                if line != '':
                    # Find if package already installed
                    if "Requirement already satisfied" in line:
                        InstalledState = 1
                        printLog("[W][installPackage] " + line.rstrip('\n'))
                    else:
                        InstalledState = 0
                        printLog("[I][installPackage] " + line.rstrip('\n'))
                        
                else:
                    break




        if InstalledState == 1:
            PackageInstallDlg.printResult("[W] Already installed!\n")
            printLog("[W][installPackage] " + PackageName.split('-')[0] + " final state: Already installed!")
        elif InstalledState == 2:
            PackageInstallDlg.printResult("[E] Wrong version!!\n")
            printLog("[E][installPackage] " + PackageName.split('-')[0] + " final state: Wrong version!")
        else:
            PackageInstallDlg.printResult("[I] Successfully Insalled!\n")
            printLog("[I][installPackage] " + PackageName.split('-')[0] + " final state: Successfully Insalled!")

def installPIP():

    PIPInstalledState = 0
    PackageInstallProcess=subprocess.Popen(['pip', 'install', './PythonPackageShowList/' + g_PIPFileName], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    while True:
        time.sleep(0.5)
        errorline=PackageInstallProcess.stderr.readline()
        if errorline != '':
            # Find if package not support in this platform
            if "is not a supported" in errorline:
                PIPInstalledState = 2
                printLog("[W][installPackage] " + errorline.rstrip('\n'))
                break

        line = PackageInstallProcess.stdout.readline()
        if line != '':
            # Find if package already installed
            if "Requirement already satisfied" in line:
                PIPInstalledState = 1
                printLog("[W][installPackage] " + line.rstrip('\n'))
            else:
                PIPInstalledState = 0
                printLog("[I][installPackage] " + line.rstrip('\n'))
                
        else:
            break

    if PIPInstalledState == 1:
        PackageInstallDlg.printResult("[I] PIP already installed correctly!\n")
        printLog("[I][installPackage] PIP is already installed correctly!")
    elif PIPInstalledState == 2:
        PackageInstallDlg.printResult("[E] PIP Version ERROR!!!!\n")
        printLog("[E][installPackage] PIP Version Not Support!!")      
    else:
        PackageInstallDlg.printResult("[I] PIP upgrade successfully!\n")
        printLog("[I][installPackage] PIP upgrade successfully!")  

    PackageInstallDlg.inputControl("Unlock")
    PackageInstallDlg.changeRunningState("Ready")


class PackageInstallDlg(Frame):
    def __init__(self, master = None, width=0, height=0):
        Frame.__init__(self, master)
        self.createPackageInstallDlg()

    def createPackageInstallDlg(self):
        global nWindowsWidth, nWindowsHeight
        printLog("[I][createLTENoiseParserDlg] Create Windows.")

        #Windows title
        self.master.title('PythonPackageInstall_Tool %s' % (g_strVersion));
        self.pack(fill = BOTH, expand = 1);
        self.master.iconbitmap(r'Compal.ico')
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        nWindowsWidth, nWindowsHeight = (self.winfo_screenwidth() * 3 / 4), (self.winfo_screenheight() * 3 / 4)
        nWindowsPosX = (self.winfo_screenwidth() / 2) - (nWindowsWidth / 2)
        nWindowsPosY = (self.winfo_screenheight() / 2) - (nWindowsHeight / 2)

        self.master.minsize(width = nWindowsWidth, height = nWindowsHeight)
        self.master.maxsize(width = nWindowsWidth, height = nWindowsHeight)
        self.master.geometry("+%d+%d" % (nWindowsPosX, nWindowsPosY))
        self.showReportBox()
        self.showExitBtn()
        self.showCheckFrame()
        self.showPackageCheckBox()
        self.showInstallBtn()
        self.showStatus()
        self.checkPIP()

    def checkPIP(self):
        self.printResult("[I] Checking PIP version...\n")
        self.inputControl("Lock")
        self.changeRunningState("Running")
        threading.Thread(target=installPIP).start()


    def showStatus(self):
        self.StatusText = Label(self, text = "State: ",foreground="#000080")
        self.StatusText['font'] = ("Microsoft JhengHei", 26,"bold")
        self.StatusText.place(x = nWindowsWidth * 2 / 80, y = nWindowsHeight * 1 / 80, width = nWindowsWidth * 8 / 80, height = nWindowsHeight * 8 / 80)

        self.StatusLabel = Label(self, text = "Ready......  ", bg = "green")
        self.StatusLabel['font'] = ("Microsoft JhengHei", 26,"bold")
        self.StatusLabel.place(x = nWindowsWidth * 10 / 80, y = nWindowsHeight * 1 / 80, width = nWindowsWidth * 16 / 80, height = nWindowsHeight * 8 / 80)

    def showCheckFrame(self):
        self.CheckFrame = LabelFrame(self, text="~*~^~*~Package List ~*~^~*~", labelanchor="n", foreground="orange")
        self.CheckFrame['font'] = ("Microsoft JhengHei", 16,"bold")
        self.CheckFrame.place(x = nWindowsWidth * 2 / 80, y = nWindowsHeight * 10 / 80, width = nWindowsWidth * 37 / 80, height = nWindowsHeight * 65 / 80)

    def showPackageCheckBox(self):
        global CheckVar
        CheckVar = []
        self.ListCheckbox = []
        for PackageShowListIndex in range(len(PackageShowList)):
            self.var = IntVar()
            self.ListCheckbox.append(Checkbutton(self, text = str(RefinePackageShowList[PackageShowListIndex][0]) + ", version: " + str(RefinePackageShowList[PackageShowListIndex][1]), variable = self.var, anchor = "w"))
            CheckVar.append(self.var)
            self.ListCheckbox[PackageShowListIndex].place(x = nWindowsWidth * 3 / 80 , y = (nWindowsHeight * 13 / 80) + (PackageShowListIndex * nWindowsHeight * 7 / 320), width = nWindowsWidth * 17 / 80, height = nWindowsHeight * 2 / 80)
        printLog("[I][showPackageCheckBox] Checkbox successfully generate")

    def on_closing(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to close the windows?"):
            printLog("[I][on_closing] The windows had been closed.")
            self.master.destroy()

    def showExitBtn(self):
        self.ExitBtn = Button(self,text = "Exit" ,command = self.exitPackageInstallDlg, foreground="#000080")
        self.ExitBtn.place(x = nWindowsWidth * 62 / 80, y = nWindowsHeight * 69 / 80, width = nWindowsWidth * 15 / 80, height = nWindowsHeight * 8 / 80)
        self.ExitBtn['font'] = ("Microsoft JhengHei", 18,"bold")

    def exitPackageInstallDlg(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to close the windows?"):
            printLog("[I][exitPackageInstallDlg] The windows had been Exit.")
            self.master.destroy()

    def showReportBox(self):
        self.ResultBoxLabel = Label( self, text = "Log:" ,anchor = "w",foreground="#000080")
        self.ResultBoxLabel['font'] = ( "Microsoft JhengHei", 16, "bold" )
        self.ResultBoxLabel.place( x = nWindowsWidth * 40 / 80, y = nWindowsHeight * 2 / 80, width = nWindowsWidth * 40 / 80,height = nWindowsHeight * 4 / 80)
        self.ResultBox = ScrolledText( self,state=DISABLED, foreground="#000080")
        self.ResultBox.place( x = nWindowsWidth * 40 / 80, y = nWindowsHeight * 6 / 80, width = nWindowsWidth * 39 / 80, height = nWindowsHeight * 60 / 80 )

    def printResult(self,strInfo):
        self.ResultBox.configure(state='normal')
        self.ResultBox.insert(END,strInfo)
        self.ResultBox.configure(state='disabled')    

    def showInstallBtn(self):
        self.checkAllBtn = Button(self,text = "Select All" ,command = self.checkAll, foreground="#000080")
        self.checkAllBtn.place(x = nWindowsWidth * 4 / 80, y = nWindowsHeight * 65 / 80 ,width = nWindowsWidth * 15 / 80 ,height = nWindowsHeight * 8 / 80)
        self.checkAllBtn['font'] = ("Microsoft JhengHei", 18, "bold")

        self.uncheckAllBtn = Button(self, text = "Unselect All", command = self.uncheckAll, foreground="#000080")
        self.uncheckAllBtn.place(x = nWindowsWidth * 22 / 80, y = nWindowsHeight * 65 / 80, width = nWindowsWidth * 15 / 80, height = nWindowsHeight * 8 / 80)
        self.uncheckAllBtn['font'] = ("Microsoft JhengHei", 18,"bold")

        self.InstallBtn = Button(self,text = "Start Install" ,command = self.installBtn, foreground="#af0000")
        self.InstallBtn.place(x = nWindowsWidth * 43 / 80, y = nWindowsHeight * 69 / 80, width = nWindowsWidth * 15 / 80, height = nWindowsHeight * 8 / 80)
        self.InstallBtn['font'] = ("Microsoft JhengHei", 18, "bold")

    def checkAll(self):
        for i in self.ListCheckbox:
            i.select()

    def uncheckAll(self):
        for i in self.ListCheckbox:
            i.deselect()

    def installBtn(self):
        # State labe change
        self.changeRunningState("Running")

        # Disable all button except exit
        self.inputControl("Lock")

        # Start installing thread
        threading.Thread(target=self.startInstalling).start()

    def changeRunningState(self,RunningOrReady):
        if RunningOrReady == "Running":
            self.StatusLabel.destroy()
            self.StatusLabel = Label(self, text = "Running...", bg = "red")
            self.StatusLabel['font'] = ("Microsoft JhengHei", 26, "bold")
            self.StatusLabel.place(x = nWindowsWidth * 5 / 40, y = nWindowsHeight * 1 / 80, width = nWindowsWidth * 8 / 40)
        if RunningOrReady == "Ready":
            self.StatusLabel.destroy()
            self.StatusLabel = Label(self, text = "Ready",bg = "green")
            self.StatusLabel['font'] = ("Microsoft JhengHei", 26,"bold")
            self.StatusLabel.place(x = nWindowsWidth * 5 / 40, y = nWindowsHeight * 1 / 80, width = nWindowsWidth * 8 / 40)
        if RunningOrReady == "Finish":
            self.StatusLabel.destroy()
            self.StatusLabel = Label(self, text = "Finish",bg = "blue" )
            self.StatusLabel['font'] = ("Microsoft JhengHei", 26,"bold")
            self.StatusLabel.place(x = nWindowsWidth * 5 / 40, y = nWindowsHeight * 1 / 80, width = nWindowsWidth * 8 / 40)

    def startInstalling(self):
        for i in range(len(PackageShowList)):

            if CheckVar[i].get()==1:
                PackageInstallDlg.printResult( "[I] Searching " + PackageShowList[i] + " requirement...\n")
                for index in range(len(g_PackageRequirementList)):
                    if g_PackageRequirementList[index][0] in PackageShowList[i]:
                        for innerindex in range(len(g_PackageRequirementList[index][1])):
                            for j in range(len(RequirementList)):
                                if g_PackageRequirementList[index][1][innerindex] in RequirementList[j]:
                                    PackageInstallDlg.printResult( "[I] Installing: " + RequirementList[j] + "\n")
                                    installPackage(RequirementList[j])
                PackageInstallDlg.printResult( "[I] Installing: " + PackageShowList[i] + "\n")
                installPackage(PackageShowList[i])
                print "end"

        # State labe change
        self.changeRunningState("Finish")
        self.printResult("╔═══════════════╗\n")
        self.printResult("║         F i n i s h !        ║\n")
        self.printResult("╚═══════════════╝\n")


    def inputControl(self,LockOrUnlock):

        if LockOrUnlock == "Lock":
            for item in self.ListCheckbox:
                item['state'] = 'disabled'
            self.checkAllBtn['state'] = 'disabled'
            self.uncheckAllBtn['state'] = 'disabled'
            self.InstallBtn['state'] = 'disabled'
        elif LockOrUnlock == "Unlock":
            for item in self.ListCheckbox:
                item['state'] = 'normal'
            self.checkAllBtn['state'] = 'normal'
            self.uncheckAllBtn['state'] = 'normal'
            self.InstallBtn['state'] = 'normal'


if __name__ == '__main__':
    printLog("========== Start Python_Package_Install_Tool ==========")
    printLog("[I][Main] Python " + sys.version)
    printLog("[I][Main] Version = %s" % g_strVersion)

    # Get Python Bit Version (32bit or 64bit)
    PythonBitVersion = struct.calcsize("P") * 8
    # Get Current Working Directory
    g_strCurrentDirectory = os.path.dirname(os.path.abspath(__file__)) + "\\PythonPackageShowList"

    for (dirpath, dirnames, filenames) in walk(g_strCurrentDirectory):
        PackageShowList.extend(filenames)
        break       
    for (dirpath, dirnames,filenames) in walk(g_strCurrentDirectory):
        PackageShowList.extend(dirnames)
        break

    g_strCurrentDirectory = os.path.dirname(os.path.abspath(__file__)) + "\\PythonPackageRequirement"
    for (dirpath, dirnames, filenames) in walk(g_strCurrentDirectory):
        RequirementList.extend(filenames)
        break       
    for (dirpath, dirnames,filenames) in walk(g_strCurrentDirectory):
        RequirementList.extend(dirnames)
        break
    # Remove not supported package under current Bit version
    removeNotSupportPackage()
    refinePackageShowList()


    strINIPath = os.path.dirname(os.path.abspath(__file__)) + "\\Python_Package_Install_Tool.ini"
    readINI(strINIPath)

    # Main window create
    cTk = Tk()
    PackageInstallDlg  = PackageInstallDlg(master = cTk)
    PackageInstallDlg.mainloop()
    printLog("=========== End Python_Package_Install_Tool ===========")


