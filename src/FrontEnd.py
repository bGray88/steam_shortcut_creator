'''
Created on May 29, 2015

@author: bgray
'''

import tkinter as tk    #Python 3
#import Tkinter as tk    #Python 2

import App
import os
import FileProcessor
import threading

from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkinter.constants import DISABLED, NORMAL

#from PIL import Image    #Canvas
#from PIL import ImageTk    #Canvas

class FrontEnd(App.App):
    
    def __init__(self):
        super().__init__()
        
        self.fileDirSelected = None
        self.saveDirSelected = None
        self.returnsuccess = None
        self.returnMsg = None
        
        self.container.setFrameIcon('steam.ico')
        self.introWindow()
        self.btnWindow()
        self.statusBarWindow()
        
    def checkProcessThread(self):
        if self.processThread.is_alive():
            self.container.after(1, self.checkProcessThread)
        else:
            self.completeProcess()
            self.progressBar.stop()
        
    def runFileProcess(self):
        self.returnsuccess, self.returnMsg = self.fileProcessor.processFiles()
        
    def startProcess(self):
        if self.fileDirSelected:
            if self.saveDirSelected:
                self.prepareProcess()
                self.processWindow()
                self.progressBar.start()
                self.fileProcessor = FileProcessor.FileProcessor(self.fileDirSelected, 
                                                         self.saveDirSelected)
                self.processThread = threading.Thread(target=self.runFileProcess)
                self.processThread.daemon = True
                self.processThread.start()
                self.container.after(1, self.checkProcessThread)
            else:
                tk.messagebox.showwarning('Open file', 
                                          'Please select a valid save directory')
        else:
            tk.messagebox.showwarning('Open file', 
                                      'Please select a valid steam directory')
        
    def prepareProcess(self):
        self.browseMainButton.config(state=DISABLED)
        self.browseSaveButton.config(state=DISABLED)
        self.processButton.config(state=DISABLED)
        self.exitButton.config(state=DISABLED)
                
    def completeProcess(self):
        self.exitButton.config(state=NORMAL)
        unsuccessfulMsg = ('The process has finished unsuccessfully\n')
        successfulMsg = ('The process has finished successfully\n')
        suffixUnMsg = ('Please check your setup and attempt the process again\n')
        suffixMsg = ('Enjoy all of the newly created shortcuts\n')
        
        if self.returnMsg is 'steam_id_num':
            completeMsg = (unsuccessfulMsg + 'The Steam ID\'s in the selected '
            'directory may be invalid\n' + suffixUnMsg)
        elif self.returnMsg is 'steam_id_count':
            completeMsg = (unsuccessfulMsg + 'The selected directory does not '
            'contain any valid Steam game files\n' + suffixUnMsg)
        else:
            completeMsg = (successfulMsg + suffixMsg)
            
        self.procMessage.config(text=completeMsg)
        
    def setMainDir(self):
        rootDir = self.getRootDir()
        self.container.withdraw()
        self.fileDirSelected = self.browseForFolder('Select the Steam Directory', True, 
                                                    os.path.normpath(rootDir))
        self.container.deiconify()
        
    def setSaveDir(self):
        rootDir = self.getRootDir()
        self.container.withdraw()
        self.saveDirSelected = self.browseForFolder('Select the Shortcut Save Directory', True, 
                                                    os.path.normpath(rootDir))
        self.container.deiconify()
        
    def browseForFolder(self, title, mustexist, initialdir):
        return tk.filedialog.askdirectory(title=title, 
                                                          mustexist=mustexist, 
                                                          initialdir=initialdir)
        
    def getFolderSelected(self):
        return self.fileDirSelected
    
    def getRootDir(self):
        rootDir = os.path.expanduser("~")
        rootIdx = rootDir.find(os.path.normpath('/'))
        while rootDir.find(os.path.normpath('/'), (rootIdx + 1)) is not -1:
            rootDir = os.path.dirname(rootDir)
        return (os.path.dirname(rootDir))
        
    def configWindows(self, window, *args):
        for coords in args:
            for rx, rw, cx, cw in coords:    
                window.gridConfig(rx, rw, cx, cw)
        
    def introWindow(self):
        self.labelFont = ('sans', 12, 'bold')
        self.introMessage = tk.Label(self.msgWindow, width=0, height=0, 
                                   background='GRAY', foreground='WHITE', font=self.labelFont,
                                   text='\nWelcome to the Steam Shortcut Creator\n'
                                   'Simply browse to your Steam root folder to begin\n'
                                   'Also select a suitable save location\n'
                                   'And then process your files\n')
        self.msgGridConfig = [[0,1,None,None], [1,1,None,None], 
                              [2,1,None,None], [3,1,None,None],
                              [4,1,0,1]]
        self.configWindows(self.msgWindow, self.msgGridConfig)
        self.msgWindow.addWindow(self.introMessage, 1, 0, 'nsew')
        self.bgdWindow.addWindow(self.msgWindow, 0, 0, 'nsew', 2)
        
    def processWindow(self):
        self.labelFont = ('sans', 12, 'bold')
        self.procMessage = tk.Label(self.procWindow, width=0, height=0, 
                                   background='GRAY', foreground='WHITE', font=self.labelFont,
                                   text='\nThe program will now create shortcuts based\n'
                                   'on the Steam apps installed\n')
        self.progressBar = tk.ttk.Progressbar(self.procWindow, orient="horizontal",
                                        length=(int(self.windowedWidth / 2)), 
                                        mode="indeterminate")
        self.procGridConfig = [[0,1,None,None], [1,1,None,None], 
                              [2,1,None,None], [3,1,None,None],
                              [4,1,0,1]]
        self.configWindows(self.procWindow, self.procGridConfig)
        self.procWindow.addWindow(self.procMessage, 1, 0, 'nsew')
        self.procWindow.addWindow(self.progressBar, 3, 0)
        self.bgdWindow.addWindow(self.procWindow, 0, 0, 'nsew', 2)
        
    def btnWindow(self):
        BROWSE_MAIN_CMD = self.setMainDir
        self.browseMainButton = self.btmWindow.createButton('Browse Steam', 'GRAY', 
                                                   'WHITE', BROWSE_MAIN_CMD, '2', '15')
        BROWSE_SAVE_CMD = self.setSaveDir
        self.browseSaveButton = self.btmWindow.createButton('Browse Save', 'GRAY', 
                                                   'WHITE', BROWSE_SAVE_CMD, '2', '15')
        PROCESS_COMMAND = self.startProcess
        self.processButton = self.btmWindow.createButton('Process', 'GRAY', 
                                                 'WHITE', PROCESS_COMMAND, '2', '15')
        EXIT_COMMAND = self.endApp
        self.exitButton = self.btmWindow.createButton('Exit', 'GRAY', 
                                                 'WHITE', EXIT_COMMAND, '2', '15')
        self.btmGridConfig = [[None,None,0,1], [None,None,1,2], 
                              [None,None,2,2], [0,1,3,2],
                              [1,1,4,2], [2,1,5,1]]
        self.configWindows(self.btmWindow, self.btmGridConfig)
        self.btmWindow.placeButton(self.browseMainButton, 1, 1, 'nsew')
        self.btmWindow.placeButton(self.browseSaveButton, 1, 2, 'nsew')
        self.btmWindow.placeButton(self.processButton, 1, 3, 'nsew')
        self.btmWindow.placeButton(self.exitButton, 1, 4, 'nsew')
        self.container.addWindow(self.btmWindow, 1, 0, 'nsew', 2)
        
    def statusBarWindow(self):
        self.statusBar.setTitle('Steam Shortcut Creator')
        self.statusBar.setScreen('Menu')
        self.statusBar.padConfig(1, 1)
        self.statGridConfig = [[None,None,0,5], [None,None,1,5], 
                              [None,None,2,5], [None,None,3,5],
                              [0,1,4,3]]
        self.configWindows(self.statusBar, self.statGridConfig)
        self.container.addWindow(self.statusBar, 2, 0, 'nsew', 2)
        