'''
Created on May 29, 2015

@author: bgray
'''

import tkinter as tk    #Python 3
#import Tkinter as tk    #Python 2

import Container
import Window
import StatusBar

class App():
    
    def __init__(self):
        self.container = Container.Container()
        self.container.wm_title('Steam Shortcut Creator')
        
        self.screenSize = self.container.getScreenDimensions()
        self.windowedWidth = self.screenSize[0]/3
        self.windowedHeight = self.screenSize[1]/3
        self.container.setMinSize(self.windowedWidth, self.windowedHeight)
        
        self.container.focus_set()
        self.container.bind('<Key>', self.keyBind)
        
        self.container.gridConfig(0, 20)
        self.container.gridConfig(1, 10)
        self.container.gridConfig(2, 1, 0, 1)
        
        self.bgdWindow = Window.Window(self.container, bgColor='BLACK')
        self.bgdWindow.gridConfig(None, None, 0, 1)
        self.bgdWindow.gridConfig(0, 1, 1, 20)
        self.container.addWindow(self.bgdWindow, 0, 0, 'nsew')
        
        self.msgWindow = Window.Window(self.bgdWindow, bgColor='GRAY')
        self.msgWindow.windowCustomize(1, tk.RAISED)
        
        self.procWindow = Window.Window(self.bgdWindow, bgColor='GRAY')
        self.procWindow.windowCustomize(1, tk.RAISED)
        
        self.btmWindow = Window.Window(self.container, bgColor='BLACK')
        self.btmWindow.windowCustomize(1, tk.RAISED)
        
        self.statusBar = StatusBar.StatusBar(self.container, '', '')
        
    def startApp(self):
        self.container.startLoop()
        
    def endApp(self):
        self.container.endLoop()
        
    def keyBind(self, event):
        self.inputProcess(event.keysym)
    
    def inputProcess(self, event):
        if event=='Escape':
            self.container.endLoop()
        if event=='F11':
            self.container.toggleFullScreen()
    