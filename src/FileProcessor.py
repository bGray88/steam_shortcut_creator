'''
Created on May 29, 2015

@author: bgray
'''

import os
import site
import re
import requests
import sys
import LogFile
import Database
import win32com.client
import shutil
import PIL

from os.path import normpath
from os.path import join
from os.path import isfile
from multiprocessing import Queue
from PIL import Image
from PIL import PngImagePlugin
from PIL import JpegImagePlugin
from PIL import TgaImagePlugin

class FileProcessor():
    
    def __init__(self, mDirectory, sDirectory):
        self.mainDirectory = mDirectory
        self.saveDirectory = sDirectory
        self.processComplete = False
        self.processSuccess = True
        self.logFile = LogFile.LogFile(self.saveDirectory, '_Steam_Shortcuts')
        self.dbFile = Database.Database(self.getDataFile(filename='_Steam_Data'), '_Steam_Data')
        
        self.iconUrlPrefix = 'https://steamdb.info/app/'
        self.iconUrlGet = 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/'
        self.dirMediaPath = 'steam\games'
        self.dirGamePath = 'Steam\SteamApps'
        self.dirRunPath = "steam://run/"
        self.iconExt = '.ico'
        self.jpgExt = '.jpg'
        self.tgaExt = '.tga'
        self.gameExt = '.acf'
        self.cutExt = '.lnk'
        
        self.gamefiles = []
        self.iconfiles = []
        self.gamedbAppend = []
        
        self.dictSteamIds = {}
        
    def processFiles(self):
        self.logFile.logMsg('\n-----------------\n'
                            'Created Shortcuts\n'
                            '-----------------\n')
        for (dirPath, dirNames, fileNames) in os.walk(self.mainDirectory):
            dirPath = dirPath.replace('/', '\\')
            if dirPath.endswith(self.dirMediaPath):
                for file in fileNames:
                    if file.lower().endswith(self.iconExt):
                        self.iconfiles.append(dirPath + '\\' + file)
                    if file.lower().endswith(self.tgaExt):
                        self.iconfiles.append(dirPath + '\\' + file)
                self.iconfiles.sort()
            if dirPath.endswith(self.dirGamePath):
                for file in fileNames:
                    if file.lower().endswith(self.gameExt):
                        self.gamefiles.append(dirPath + '\\' + file)
                self.gamefiles.sort()
                
        self.logFile.logMsg('Finished_Searching')
        
        # Create SteamApp ID's; Format Dict-[SteamID]:(GameName, IconName)
        for appId in self.gamefiles:
            self.arrSteamTitles = []
            
            appIdIdx = appId.find('_')
            steamId = appId[(appIdIdx + 1):len(appId)]
            steamId = steamId.replace(self.getExtension(steamId), '')
            
            self.logFile.logMsg('\nProcessing- ' + steamId)
            
            if not steamId.isnumeric():
                failTag = 'steam_id_num'
                self.logError(failTag)
                return (str(self.processSuccess), failTag)
            else:
                self.arrSteamTitles.append(self.processGameName(appId))
                self.arrSteamTitles.append(self.processSteamIcon(steamId))
                self.dictSteamIds[steamId] = self.arrSteamTitles
                
        self.logFile.logMsg('Finished_Sorting')
        
        # Filenames to Write to Database
        for app in self.gamedbAppend:
            self.dbFile.dataEntryAppend(app) 
        
        # Create Shortcut Files
        if len(self.dictSteamIds) is 0:
            failTag = 'steam_id_count'
            self.logError(failTag)
            return (str(self.processSuccess), failTag)
        else:
            for gameId in self.dictSteamIds.keys():
                gameTitle = str(self.dictSteamIds[gameId][0]).title()
                gameIcon = self.dictSteamIds[gameId][1]
                
                if not isfile((normpath(join(self.mainDirectory, self.dirMediaPath, 
                                             gameIcon)))) and gameIcon != '':
                    self.getUrlFile(self.iconUrlGet + gameId + '/' + gameIcon, gameIcon)
                    if self.getExtension(gameIcon) != self.iconExt and isfile((normpath(join(self.mainDirectory, self.dirMediaPath, 
                                                       gameIcon)))):
                        self.convertImg((normpath(join(self.mainDirectory, self.dirMediaPath, 
                                                       gameIcon))))
                        os.remove((normpath(join(self.mainDirectory, self.dirMediaPath, 
                                                 gameIcon))))
                        gameIconExt = self.getExtension(gameIcon)
                        gameIcon = gameIcon.replace(gameIconExt, self.iconExt)
                self.createShortcut((normpath(join(self.saveDirectory, 
                                                   gameTitle + self.cutExt))), 
                                    (self.dirRunPath + gameId), '', 
                                    (normpath(join(self.mainDirectory, 
                                                   self.dirMediaPath, 
                                                   gameIcon))))
                self.logFile.logMsg(gameTitle + ' - ' + gameId + '\n')
        return (str(self.processSuccess), '')
        
        self.logFile.logMsg('Finished_Program')
    
    def processGameName(self, docPath):
        doc = open(docPath, 'r')
        for line in doc:
            if line.find('name') is not -1:
                gamename = line.replace('name', '')
                gamename = gamename.replace('"', '')
                gamename = gamename.replace('\:', '\-')
                gamename = gamename.strip(' \t\n\r')
                gamename = re.sub('[^a-zA-Z0-9\- ]', '', gamename)
                return gamename
                
    def processSteamIcon(self, steamId):
        clientIconName = ''
        dbAppend = True
        
        if isfile(self.getDataFile(filename='_Steam_Data') + '.db'):
            arrDbLines = self.dbFile.readLines()
            for line in arrDbLines:
                if line.find('-' + steamId + '-') is not -1:
                    clientIconName = line.replace('-' + steamId + '-', '')
                    clientIconName = clientIconName.replace('-', '')
                    clientIconName = clientIconName.strip(' \t\n\r')
                    dbAppend = False
                    break
        else:
            self.dbFile.printHeader('_Steam_Data')
        if (clientIconName == '') or (self.getExtension(clientIconName) == None):
            clientIconName = self.getClientIcon(steamId, 'clienticon', self.iconExt, dbAppend)
            if (clientIconName == '') or (self.getExtension(clientIconName) == None):
                clientIconName = self.getClientIcon(steamId, '>icon<', self.jpgExt, dbAppend)
                if (clientIconName == '') or (self.getExtension(clientIconName) == None):
                    clientIconName = self.getClientIcon(steamId, 'clienttga', self.tgaExt, dbAppend)
        return clientIconName
        
    def convertImg(self, path):
        img = Image.open(path)
        ext = self.getExtension(path)
        path = path.replace(ext, self.iconExt)
        img.save(path)
        
    def createShortcut(self, path, target=None, wDir=None, icon=None):
        if self.getExtension(path) == '.url':
            shortcut = win32com.client.Dispatch.file(path, 'w')
            shortcut.write('[InternetShortcut]\n')
            shortcut.write('URL=%s' % target)
            shortcut.close()
        else:
            win32com.client.pythoncom.CoInitialize()
            winShell = win32com.client.Dispatch('WScript.Shell')
            shortcut = winShell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            if icon == '':
                pass
            else:
                shortcut.IconLocation = icon
            shortcut.save()
            
    def getDataFile(self, path='', filename=''):
        if getattr(sys, 'frozen', False):
            datadir = os.path.dirname(sys.executable)
        else:
            datadir = os.path.join(site.getsitepackages()[0], path)
        return (normpath(join(datadir, filename)))
        
    def getUrlResponse(self, steamId, findStr):
        response = requests.get(self.iconUrlPrefix + steamId, 
                                verify=self.getDataFile(path=os.path.join('Lib', 
                                                                          'site-packages', 
                                                                          'requests'), 
                                                        filename='cacert.pem'))
        clientIconIdx = str(response.content).find(findStr)
        clientIconName = str(response.content)[clientIconIdx:len(response.content)]
        clientIconName = clientIconName[0:clientIconName.find('</a>')]
        clientIconName = clientIconName[(clientIconName.find('nofollow">') + 
                                         len('nofollow">')):len(clientIconName)]
        return clientIconName
        
    def getUrlFile(self, path, filename):
        response = requests.get(path, stream=True, 
                                verify=self.getDataFile(path=os.path.join('Lib', 
                                                                          'site-packages', 
                                                                          'requests'), 
                                                        filename='cacert.pem'))
        with open((normpath(join(self.mainDirectory, self.dirMediaPath, 
                                 filename))), 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        
    def getClientIcon(self, steamId, identifier, iconExt, append=False):
        clientIconName = self.getUrlResponse(steamId, identifier)
        if clientIconName is not '':
            clientIconName = clientIconName.strip(' \t\n\r')
            clientIconName = clientIconName + iconExt
            if append:
                self.gamedbAppend.append('-' + steamId + '-' + '-' + clientIconName + '-\n')
        return clientIconName
        
    def getExtension(self, filename):
        i = 0
        strIndex = 0
        fileExt = filename
        if fileExt.find('.', i) is not -1:
            while i is not len(fileExt):
                if fileExt.find('.', i) is not -1:
                    strIndex = fileExt.find('.', i)
                if strIndex > i:
                    i = strIndex
                else:
                    i = i + 1
            fileExt = fileExt[strIndex:len(fileExt)]
        else:
            fileExt = None
        return fileExt
            
    def logError(self, failtag):
        self.processSuccess = False
        self.logFile.logMsg('\n\n**************************************\n'
                            '-THE PROCESS HAS FAILED-' + failtag + '\n'
                            '**************************************\n')
        return
        