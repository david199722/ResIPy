#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import time
#a = time.time()
print('importing pyqt')
from PyQt5.QtWidgets import (QMainWindow, QSplashScreen, QApplication, QPushButton, QWidget, 
    QAction, QTabWidget,QVBoxLayout, QGridLayout, QLabel, QLineEdit, QMessageBox,
    QListWidget, QFileDialog, QCheckBox, QComboBox, QTextEdit, QSlider, QHBoxLayout,
    QTableWidget, QFormLayout, QShortcut, QTableWidgetItem, QHeaderView, QProgressBar,
    QStackedLayout, QRadioButton, QGroupBox, QButtonGroup)
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QIntValidator, QDoubleValidator
from PyQt5.QtCore import QThread, pyqtSignal, QProcess, QSize
from PyQt5.QtCore import Qt

#%% General crash ERROR
import threading
import traceback

def errorMessage(etype, value, tb):
    print('ERROR begin:')
    traceback.print_exception(etype, value, tb)
    print('ERROR end.')
    errorMsg = traceback.format_exception(etype, value, tb,limit=None, chain=True)
    finalError =''
    for errs in errorMsg:
        finalError += errs
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("<b>Critical error:</b>")
    msg.setInformativeText('''Please see the detailed error below.<br>You can report the errors at:<p><a href='https://gitlab.com/hkex/pyr2/issues'>https://gitlab.com/hkex/pyr2/issues</a></p><br>''')
    msg.setWindowTitle("Error!")
#    msg.setWindowFlags(Qt.FramelessWindowHint)
    msg.setDetailedText('%s' % (finalError))
    msg.setStandardButtons(QMessageBox.Retry)
    msg.exec_()

def catchErrors():
    sys.excepthook = errorMessage
    threading.Thread.__init__

#%% Wine Check
import platform
from subprocess import PIPE, Popen

def wineCheck():
    #check operating system 
    OpSys=platform.system()    
    #detect wine
    if OpSys == 'Linux':
        p = Popen("wine --version", stdout=PIPE, shell=True)
        is_wine = str(p.stdout.readline())
        if is_wine.find("wine") == -1:
            wineMsgBox('Linux')
        else:
            pass
                
    elif OpSys == 'Darwin':
        try: 
            winePath = []
            wine_path = Popen(['which', 'wine'], stdout=PIPE, shell=False, universal_newlines=True)#.communicate()[0]
            for stdout_line in iter(wine_path.stdout.readline, ''):
                winePath.append(stdout_line)
            if winePath != []:
                is_wine = Popen(['%s' % (winePath[0].strip('\n')), '--version'], stdout=PIPE, shell = False, universal_newlines=True)
            else:
                is_wine = Popen(['/usr/local/bin/wine','--version'], stdout=PIPE, shell = False, universal_newlines=True)

        except:
            wineMsgBox('macOS')

def wineMsgBox(platform):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText('''<b>No "wine" is installed on your %s</b>''' % (platform))
    msg.setInformativeText('''pyR2 needs "wine" to run properly,<br>without "wine", no inversion or triangular meshing is possible.<br>''')
    msg.setWindowTitle('"Wine" is not detected!')
    bttnUpY = msg.addButton(QMessageBox.Yes)
    bttnUpY.setText('Learn more')
    bttnUpN = msg.addButton(QMessageBox.No)
    bttnUpN.setText('Continue')
    msg.setDefaultButton(bttnUpY)
    msg.exec_()
    if msg.clickedButton() == bttnUpY:
        webbrowser.open('https://gitlab.com/hkex/pyr2#linux-and-mac-user')

#%% Update checker
import urllib
import webbrowser

def updateChecker():
    #gets newest version from src/version.txt
    try:
        versionSource = urllib.request.urlopen('https://gitlab.com/hkex/pyr2/raw/master/src/version.txt?inline=false')
        versionCheck = str(versionSource.read())
        version = versionCheck.split('\\n')[1].replace("'",'') # assuming version number is in 2nd line of version.txt
        if pyR2_version not in versionCheck:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('''<b>pyR2 version %s is available</b>''' % (version))
            msg.setInformativeText('''Please download the latest version of pyR2 at:<p><a href='https://gitlab.com/hkex/pyr2#gui-for-r2-family-code'>https://gitlab.com/hkex/pyr2</a></p><br>''')
            msg.setWindowTitle("New version available")
            bttnUpY = msg.addButton(QMessageBox.Yes)
            bttnUpY.setText('Update')
            bttnUpN = msg.addButton(QMessageBox.No)
            bttnUpN.setText('Ignore')
            msg.setDefaultButton(bttnUpY)
            msg.exec_()
            if msg.clickedButton() == bttnUpY:
                webbrowser.open('https://gitlab.com/hkex/pyr2#gui-for-r2-family-code') # can add download link, when we have a direct dl link
    except: #if there is no internet connection!
        return False

#%%
QT_AUTO_SCREEN_SCALE_FACTOR = True # for high dpi display

#print('elpased', time.time()-a)

# small code to see where are all the directories
frozen = 'not'
if getattr(sys, 'frozen', False):
        # we are running in a bundle
        frozen = 'ever so'
        bundle_dir = sys._MEIPASS
else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
print( 'we are',frozen,'frozen')
print( 'bundle dir is', bundle_dir )
print( 'sys.argv[0] is', sys.argv[0] )
print( 'sys.executable is', sys.executable )
print( 'os.getcwd is', os.getcwd() )


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None, figure=None, navi=False, itight=True, threed=False):
        super(MatplotlibWidget, self).__init__(parent) # we can pass a figure but we can replot on it when
        # pushing on a button (I didn't find a way to do it) while with the axes, you can still clear it and
        # plot again on them
        self.itight = itight
        if figure is None:
            figure = Figure()
            self.canvas = FigureCanvasQTAgg(figure)
            if threed is True:
                axes = figure.add_subplot(111, projection='3d')
            else:
                axes = figure.add_subplot(111)
        else:
            axes = figure.get_axes()
        self.figure = figure
        self.axis = axes
        
        self.layoutVertical = QVBoxLayout(self)
        self.layoutVertical.addWidget(self.canvas)

        if navi is True:
            self.navi_toolbar = NavigationToolbar(self.canvas, self)
            self.navi_toolbar.setMaximumHeight(30)
            self.layoutVertical.addWidget(self.navi_toolbar)
    
    
    def setMinMax(self, vmin=None, vmax=None):
        coll = self.axis.collections[0]
#        print('->', vmin, vmax)
#        print('array ', coll.get_array())
        if vmin is None:
            vmin = np.nanmin(coll.get_array())
        else:
            vmin = float(vmin)
        if vmax is None:
            vmax = np.nanmax(coll.get_array())
        else:
            vmax = float(vmax)
#        print(vmin, vmax)
        coll.set_clim(vmin, vmax)
        self.canvas.draw()

    
    def plot(self, callback, threed=False):
        ''' call a callback plot function and give it the ax to plot to
        '''
#        print('plot is called')
        self.figure.clear() # need to clear the figure with the colorbar as well
        if threed is False:
            ax = self.figure.add_subplot(111)
        else:
            ax = self.figure.add_subplot(111, projection='3d')
        self.callback = callback
        callback(ax=ax)
        if threed is False:
            ax.set_aspect('auto')
            ax.set_autoscale_on(False)
        if self.itight is True:
            self.figure.tight_layout()
        self.canvas.draw()
    
    def setCallback(self, callback):
        self.callback = callback
        
    def replot(self, threed=False, **kwargs):
        self.figure.clear()        
        if threed is False:
            ax = self.figure.add_subplot(111)
        else:
            ax = self.figure.add_subplot(111, projection='3d')
        self.axis = ax
        self.callback(ax=ax, **kwargs)
        ax.set_aspect('auto')
        if self.itight is True:
            self.figure.tight_layout()
        self.canvas.draw()
    
    def clear(self):
        self.axis.clear()
        self.figure.clear()
        self.canvas.draw()
        
#
#    def draw(self, fig):
#        print('creating new figure')
#        self.figure = fig
#        self.figure.suptitle('hello')
#        self.canvas = FigureCanvasQTAgg(self.figure)
#        self.canvas.draw()
#        self.figure.canvas.draw()
#    
#    def drawAxes(self, ax):
#        print('draw Awes')
#        self.figure.clf()
#        self.figure.axes.append(ax)
##        self.canvas = FigureCanvasQTAgg(self.figure)
#        self.figure.canvas.draw()
#        self.canvas.draw()
    
#class ThreadSample(QThread):
#    newSample = pyqtSignal(list)
#    
#    def __init__(self, parent=None):
#        super(ThreadSample, self).__init__(parent)
#    
#    def run(self):
#        randomSample = random.sample(range(0, 10), 10)
#        
#        self.newSample.emit(randomSample)

class App(QMainWindow):
 
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle('pyR2')
        self.setGeometry(100,100,1100,600)
        self.newwd = os.path.join(bundle_dir, 'api', 'invdir')
        
        self.r2 = None
        self.typ = 'R2'
        self.parser = None
        self.fname = None
        self.iBatch = False
        self.iTimeLapse = False
        self.iBorehole = False
        self.iForward = False
        self.inputPhaseFlag = False
        self.iCropping = True # by default crop the mesh
        self.num_xy_poly = None # to store the values
        self.datadir = os.path.join(bundle_dir, 'api', 'test')
        
        self.table_widget = QWidget()
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        # app icon
#        self.setWindowIcon(QIcon(os.path.join(bundle_dir + 'logo.png')))
        
        def errorDump(text, flag=1):
            text = str(text)
            timeStamp = time.strftime('%H:%M:%S')
            if flag == 1: # error in red
                col = 'red'
            else:
                col = 'black'
            errorLabel.setText('<i style="color:'+col+'">['+timeStamp+']: '+text+'</i>')
        errorLabel = QLabel('<i style="color:black">Error messages will be displayed here</i>')
        QApplication.processEvents()

        
        def infoDump(text):
            errorDump(text, flag=0)
        
        
        #%% tab 1 importing data
        tabImporting = QTabWidget()
        tabs.addTab(tabImporting, 'Importing')
        
        tabImportingData = QWidget()
        tabImporting.addTab(tabImportingData, 'Data')
        tabImportingDataLayout = QVBoxLayout()
        
        # disable tabs if no survey is imported
        def activateTabs(val=True):
            if self.iForward is False:
                tabs.setTabEnabled(1,val)
                tabs.setTabEnabled(2,val)
                tabs.setTabEnabled(4,val)
                tabs.setTabEnabled(5,val)
                tabs.setTabEnabled(6,val)
            else:
                tabs.setTabEnabled(2,val)
#                tabs.setTabEnabled(4,val)
#                tabs.setTabEnabled(5,val)
#                tabs.setTabEnabled(6,val)
        
        # restart all new survey
        def restartFunc():
            print('------- creating new R2 object ----------')
            self.r2 = R2(self.newwd, typ=self.typ) # create new R2 instance
            '''actually we don't really need to instanciate a new object each
            time but it's save otherwise we would have to reset all attributes
            , delete all surveys and clear parameters
            '''
            self.r2.iBatch = self.iBatch
            self.r2.setBorehole(self.iBorehole)
            self.r2.iTimeLapse = self.iTimeLapse
            self.r2.iForward = self.iForward
            if self.iTimeLapse is True:
                reg_mode.setCurrentIndex(2)
            else:
                reg_mode.setCurrentIndex(0)
            # importing
            self.parser = None
            wdBtn.setText('Working directory:' + os.path.basename(self.r2.dirname))
            buttonf.setText('Import Data')
#            timeLapseCheck.setChecked(False)
#            boreholeCheck.setChecked(False)
#            batchCheck.setChecked(False)
            ipCheck.setChecked(False)
            ipCheck.setEnabled(False)
            tabImporting.setTabEnabled(1, False)
            mwPseudo.clear() # clearing figure
            elecTable.initTable(np.array([['',''],['','']]))
            topoTable.initTable(np.array([['',''],['','']]))
#            dimInverse.setChecked(True)

            # importing - IP stuff
            phiConvFactor.setEnabled(True)
            phiConvFactorlabel.setEnabled(True)
            if self.ftype != 'Syscal':
                phiConvFactor.setText('1')
            else:
                phiConvFactor.setText('1.2')
            if self.ftype == 'ProtocolIP':
                phiConvFactor.setText('-')
                phiConvFactor.setEnabled(False)
                phiConvFactorlabel.setEnabled(False)
                
            # pre-processing
            mwManualFiltering.clear()
            errFitType.currentIndexChanged.disconnect()
            errFitType.setCurrentIndex(0)
            errFitType.currentIndexChanged.connect(errFitTypeFunc)
            mwFitError.clear()
            mwIPFiltering.clear()
            iperrFitType.currentIndexChanged.disconnect()
            iperrFitType.setCurrentIndex(0)
            iperrFitType.currentIndexChanged.connect(iperrFitTypeFunc)
            phivminEdit.setText('0')
            phivmaxEdit.setText('25')
            dcaProgress.setValue(0)
            tabPreProcessing.setTabEnabled(0, True)
            tabPreProcessing.setTabEnabled(1, False)
            tabPreProcessing.setTabEnabled(2, False)
            tabPreProcessing.setTabEnabled(3, False)
#            tabPreProcessing.setTabEnabled(3, False)
            
            # mesh
            mwMesh.clear()
            regionTable.reset()
            
            # inversion options
            flux_type.setCurrentIndex(0)
            singular_type.setChecked(False)
            res_matrix.setCurrentIndex(1)
            scale.setText('1.0')
            patch_size_x.setText('1')
            patch_size_y.setText('1')
            inv_type.setCurrentIndex(1)
            data_type.setCurrentIndex(1)
            max_iterations.setText('10')
            error_mod.setCurrentIndex(1)
            alpha_aniso.setText('1.0')
            min_error.setText('0.01')
            a_wgt.setText('0.01')
            b_wgt.setText('0.02')
#            c_wgt.setText('1')
#            d_wgt.setText('2')
            rho_min.setText('-10e10')
            rho_max.setText('10e10')
            target_decrease.setText('0')
            helpSection2.setText('Click on the labels and help will be displayed here')
            
            # inversion
            self.pindex = 0
            self.rms = []
            self.rmsIndex = []
            self.rmsIP = []
            self.rmsIndexIP = []
            self.inversionOutput = ''
            logText.setText('')
            mwRMS.clear()
            try: # try because maybe the user hasn't inverted yet
                sectionId.currentIndexChanged.disconnect()
                sectionId.clear()
                attributeName.currentIndexChanged.disconnect()
                attributeName.clear()
            except:
                pass

            vminEdit.setText('')
            vmaxEdit.setText('')
            mwInvResult.clear()
            mwInvError.clear()
            mwInvError2.clear()


            
#        restartBtn = QPushButton('Reset UI')
#        restartBtn.setAutoDefault(True)
#        restartBtn.clicked.connect(restartFunc)
#        restartBtn.setToolTip('Press to reset all tabs and start a new survey.')
        
        def dimSurvey():
            if dimRadio2D.isChecked():
                self.typ = self.typ.replace('3t','2')
                if self.r2 is not None:
                    self.r2.typ = self.r2.typ.replace('3t','2')
                # importing tab
                elecTable.initTable(headers=['x','z','Buried'])
                topoTable.initTable(headers=['x','z'])
                elecDy.setEnabled(False)
                dimForward.setEnabled(True)
                dimForward.setChecked(False)
                boreholeCheck.setChecked(False)
                boreholeCheck.setEnabled(True)
                
                tabPreProcessing.setTabEnabled(0, True)

                # mesh tab
                meshQuadGroup.setVisible(True)
                meshTrianGroup.setVisible(True)
                meshTetraGroup.setVisible(False)
                instructionLabel.setVisible(True)
                
                # inversion settings
                show3DOptions(False)
                if self.r2 is not None:
                    showIpOptions(self.typ[0] == 'c')
                
                # inversion tab
                contourCheck.setVisible(True)
                edgeCheck.setVisible(True)
                sensCheck.setVisible(True)
                paraviewBtn.setVisible(False)
                sliceAxis.setVisible(False)
                print(self.typ)
            else:
                self.typ = self.typ.replace('2','3t')
                if self.r2 is not None:
                    self.r2.typ = self.r2.typ.replace('2', '3t')
                    
                # importing tab
                elecTable.initTable(headers=['x','y','z','Buried'])
                topoTable.initTable(headers=['x','y','z'])
                elecDy.setEnabled(True)
                dimForward.setChecked(False)
                dimForward.setEnabled(False)
                dimInverse.setChecked(True)
                boreholeCheck.setChecked(True) # to disable pseudo-section
                boreholeCheck.setEnabled(False)
                
                tabPreProcessing.setTabEnabled(0, False)

                # mesh tab
                meshQuadGroup.setVisible(False)
                meshTrianGroup.setVisible(False)
                meshTetraGroup.setVisible(True)
                instructionLabel.setVisible(False)
                
                # inversion settings
                show3DOptions(True)
                if self.r2 is not None:
                    showIpOptions(self.typ[0] == 'c')
                
                # inversion tab
                contourCheck.setVisible(False)
                edgeCheck.setVisible(False)
                sensCheck.setVisible(False)
                paraviewBtn.setVisible(True)
#                sliceAxis.setVisible(True)
                
        dimRadio2D = QRadioButton('2D')
        dimRadio2D.setChecked(True)
        dimRadio2D.toggled.connect(dimSurvey)
        dimRadio3D = QRadioButton('3D')
        dimRadio3D.setChecked(False)
#        dimRadio3D.setEnabled(False) # comment this to enable 3D
        dimRadio3D.toggled.connect(dimSurvey)
        dimLayout = QHBoxLayout()
        dimLayout.addWidget(dimRadio2D)
        dimLayout.addWidget(dimRadio3D)
        dimLayout.setContentsMargins(0,0,0,0)
        dimGroup = QGroupBox()
        dimGroup.setLayout(dimLayout)
        dimGroup.setFlat(True)
        dimGroup.setContentsMargins(0,0,0,0)
        dimGroup.setStyleSheet('QGroupBox{border: 0px;'
                                'border-style:inset;}')

        # meta data (title and date of survey)
        title = QLabel('Title')
        titleEdit = QLineEdit()
        titleEdit.setText('My beautiful survey')
        titleEdit.setToolTip('This title will be used in the ".in" file.')
        
        date = QLabel('Date')
        dateEdit = QLineEdit()
        dateEdit.setText(datetime.now().strftime('%Y-%m-%d')) # get today date
        dateEdit.setToolTip('This date will be used in the ".in" file.')
        
        def timeLapseCheckFunc(state):
            if state == Qt.Checked:
                self.iTimeLapse = True
                if self.r2 is not None: # if there is already an R2 object
                    restartFunc()
                    reg_mode.setCurrentIndex(2)
                buttonf.setText('Import Data Directory')
                buttonf.clicked.disconnect()
                buttonf.clicked.connect(getdir)
                ipCheck.setEnabled(False)
                batchCheck.setEnabled(False)
            else:
                self.iTimeLapse = False
                if self.r2 is not None:
                    restartFunc()
                    reg_mode.setCurrentIndex(0)
                buttonf.setText('Import Data')
                buttonf.clicked.disconnect()
                buttonf.clicked.connect(getfile)
                ipCheck.setEnabled(True)
                batchCheck.setEnabled(True)
                
        timeLapseCheck = QCheckBox('Time-lapse Survey')
        timeLapseCheck.stateChanged.connect(timeLapseCheckFunc)
        timeLapseCheck.setToolTip('Check to import time-lapse datasets and enable time-lapse inversion.')
        
        def boreholeCheckFunc(state):
            if state == Qt.Checked:
                self.iBorehole = True
                if self.r2 is not None:
                    self.r2.setBorehole(True)
            else:
                self.iBorehole = False
                if self.r2 is not None:
                    self.r2.setBorehole(False)
            if self.fname is not None:
                    plotPseudo()
        boreholeCheck = QCheckBox('Borehole Survey')
        boreholeCheck.stateChanged.connect(boreholeCheckFunc)
        boreholeCheck.setToolTip('Check if you have a borehole dataset. This will just change the pseudo-section.')

        def batchCheckFunc(state):
            if state == Qt.Checked:
                self.iBatch = True
                buttonf.setText('Import Data Directory')
                buttonf.clicked.disconnect()
                buttonf.clicked.connect(getdir)
                timeLapseCheck.setEnabled(False)
            else:
                self.iBatch = False
                buttonf.setText('Import Data')
                buttonf.clicked.disconnect()
                buttonf.clicked.connect(getfile)
                timeLapseCheck.setEnabled(True)
        batchCheck = QCheckBox('Batch Inversion')
        batchCheck.stateChanged.connect(batchCheckFunc)
        batchCheck.setToolTip('Check if you want to invert multiple surveys with the same settings.')
        
        # select inverse or forward model
        def dimForwardFunc():
            self.iForward = True
            fileType.setEnabled(False)
            spacingEdit.setReadOnly(True)
            dimInverse.setChecked(False)
            tabs.setTabEnabled(1,False)
            tabs.setTabEnabled(3, True)
            buttonf.setEnabled(False)
            timeLapseCheck.setEnabled(False)
            batchCheck.setEnabled(False)
#            boreholeCheck.setEnabled(False)
            tabImporting.setTabEnabled(2,False) # no custom parser needed
            restartFunc() # let's first from previous inversion
            nbElecEdit.setEnabled(True)
            tabImporting.setTabEnabled(1, True) # here because restartFunc() set it to False
            ipCheck.setEnabled(True)
            activateTabs(True)

        def dimInverseFunc():
            self.iForward = False
            fileType.setEnabled(True)
            dimForward.setChecked(False)
            spacingEdit.setReadOnly(False)
            tabs.setTabEnabled(1,True)
            tabs.setTabEnabled(3, False)
            tabImporting.setTabEnabled(1, False)
            buttonf.setEnabled(True)
            nbElecEdit.setEnabled(False)
            timeLapseCheck.setEnabled(True)
            ipCheck.setEnabled(False)
            tabImporting.setTabEnabled(2,True)
            batchCheck.setEnabled(True)
#            boreholeCheck.setEnabled(True)
            activateTabs(False)
        dimForward = QRadioButton('Forward')
        dimForward.setChecked(False)
        dimForward.toggled.connect(dimForwardFunc)
        dimForward.setToolTip('To create a model, a sequence and see what output you can obtain.')
        dimInverse = QRadioButton('Inverse')
        dimInverse.setChecked(True)
        dimInverse.toggled.connect(dimInverseFunc)
        dimInverse.setToolTip('To invert data that is already collected.')
        dimInvLayout = QHBoxLayout()
        dimInvLayout.addWidget(dimForward)
        dimInvLayout.addWidget(dimInverse)
        dimInvLayout.setContentsMargins(0,0,0,0)
        dimInvGroup = QGroupBox()
        dimInvGroup.setLayout(dimInvLayout)
        dimInvGroup.setFlat(True)
        dimInvGroup.setContentsMargins(0,0,0,0)
        dimInvGroup.setStyleSheet('QGroupBox{border: 0px;'
                                'border-style:inset;}')
        
        
        hbox1 = QHBoxLayout()
#        hbox1.addWidget(restartBtn)
        hbox1.addWidget(dimGroup)
        hbox1.addWidget(title)
        hbox1.addWidget(titleEdit)
        hbox1.addWidget(date)
        hbox1.addWidget(dateEdit)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(dimInvGroup)
        hbox2.addWidget(timeLapseCheck)
        hbox2.addWidget(batchCheck)
        hbox2.addWidget(boreholeCheck)
        

        # ask for working directory, and survey file to input
        def getwd():
            fdir = QFileDialog.getExistingDirectory(tabImportingData, 'Choose Working Directory')
            if fdir != '':
                self.newwd = fdir
                if self.r2 is not None:
                    self.r2.setwd(fdir)
                print('Working directory = ', fdir)
                wdBtn.setText(os.path.basename(self.newwd))
            
        wdBtn = QPushButton('Working directory:' + os.path.basename(self.newwd))
        wdBtn.setAutoDefault(True)
        wdBtn.clicked.connect(getwd)
        wdBtn.setToolTip('Select the working directory, containing your data\nThe working directory will automatically have all the necessary files for the inversion (e.g. R2.in, R2.exe, protocol.dat, f001_res.vtk, etc.)')
        
        self.ftype = 'Syscal' # by default
        self.fformat = 'Comma Separated Values (*.csv)' # default

        def fileTypeFunc(index):
            if index == 0:
                self.ftype = 'Syscal'
                self.fformat = 'Comma Separated Values (*.csv)'
            elif index == 1:
                self.ftype = 'Protocol'
                self.fformat = 'DAT (Tab delimited) (*.dat)'
            elif index == 2:
                self.ftype = 'ProtocolIP'
                self.fformat = 'DAT (Tab delimited) (*.dat)'
            elif index == 3:
                self.ftype = 'Res2Dinv'
                self.fformat = 'DAT (*.dat)'
            elif index == 4:
                self.ftype = 'BGS Prime'
                self.fformat = 'DAT (*.dat)'
            elif index == 5:
                self.ftype = 'Sting'
                self.fformat = ''
            elif index == 6:
                self.ftype = 'Custom'
                tabImporting.setCurrentIndex(2) # switch to the custom parser
            else:
                self.ftype = '' # let to be guessed
        fileType = QComboBox()
        fileType.addItem('Syscal')
        fileType.addItem('Protocol')
        fileType.addItem('Protocol w/ IP')
        fileType.addItem('Res2Dinv')
        fileType.addItem('BGS Prime')
        fileType.addItem('Sting')
        fileType.addItem('Custom')
        fileType.currentIndexChanged.connect(fileTypeFunc)
        fileType.setFixedWidth(150)
        fileType.setToolTip('Select data format.')
        
        spacingEdit = QLineEdit()
        spacingEdit.setValidator(QDoubleValidator())
        spacingEdit.setText('-1.0') # -1 let it search for the spacing
        spacingEdit.setFixedWidth(80)
        spacingEdit.setToolTip('Electrode spacing.')
        
        def getdir():
            fdir = QFileDialog.getExistingDirectory(tabImportingData, 'Choose the directory containing the data', directory=self.datadir)
            if fdir != '':
                restartFunc()
                self.datadir = os.path.dirname(fdir)
                try:
                    if self.r2.iBatch is False:
                        self.r2.createTimeLapseSurvey(fdir, ftype=self.ftype, dump=infoDump)
                        infoDump('Time-lapse survey created.')
                    else:
                        self.r2.createBatchSurvey(fdir, dump=infoDump)
                        infoDump('Batch survey created.')
                    fnamesCombo.clear()
                    for s in self.r2.surveys:
                        fnamesCombo.addItem(s.name)
#                    fnamesCombo.setEnabled(True)
                    fnamesCombo.show()
                    fnamesComboLabel.show()
                    buttonf.setText(os.path.basename(fdir) + ' (Press to change)')
                    plotPseudo()
                    elecTable.initTable(self.r2.elec)
                    tabImporting.setTabEnabled(1,True)
                    btnInvNow.setEnabled(True)
                    if all(self.r2.surveys[0].df['irecip'].values == 0):
                        pass # no reciprocals found
                    else:
#                        tabPreProcessing.setTabEnabled(1, True)
                        tabPreProcessing.setTabEnabled(2, True)
                        plotError()                                        
                        errHist()
                    plotManualFiltering()
                    activateTabs(True)
                except:
                    errorDump('File format is not recognized (or directory contains invalid input files)')
            
        def getfile():
            print('ftype = ', self.ftype)
            fname, _ = QFileDialog.getOpenFileName(tabImportingData,'Open File', self.datadir, self.fformat)
            if fname != '':
                restartFunc()
                self.datadir = os.path.dirname(fname)
                importFile(fname)
        
        def importFile(fname):            
            if len(self.r2.surveys) > 0:
                self.r2.surveys = []
            try:
                ipCheck.setEnabled(True)
                self.fname = fname
                buttonf.setText(os.path.basename(self.fname) + ' (Press to change)')
                if float(spacingEdit.text()) == -1:
                    spacing = None
                else:
                    spacing = float(spacingEdit.text())
                try:
                    self.r2.createSurvey(self.fname, ftype=self.ftype, spacing=spacing,
                                         parser=self.parser)
                    if 'magErr' in self.r2.surveys[0].df.columns:
                        a_wgt.setText('0.0')
                        b_wgt.setText('0.0')
                except:
                    errorDump('File is not recognized.')
                    pass
                print('ok passed import')
                if all(self.r2.surveys[0].df['irecip'].values == 0):
        #                    hbox4.addWidget(buttonfr)
                    buttonfr.show()
                    recipOrNoRecipShow(recipPresence = False)
                else:
                    recipOrNoRecipShow(recipPresence = True)
                    buttonfr.hide()
                    tabPreProcessing.setTabEnabled(2, True)
                    plotError()
                    errHist()
        #                generateMesh()
                if boreholeCheck.isChecked() is True:
                    self.r2.setBorehole(True)
                else:
                    self.r2.setBorehole(False)
                plotPseudo()
                plotManualFiltering()
                elecTable.initTable(self.r2.elec)
                tabImporting.setTabEnabled(1,True)
                if 'ip' in self.r2.surveys[0].df.columns:
                    if np.sum(self.r2.surveys[0].df['ip'].values) > 0 or np.sum(self.r2.surveys[0].df['ip'].values) < 0: # np.sum(self.r2.surveys[0].df['ip'].values) !=0 will result in error if all the IP values are set to NaN
                        ipCheck.setChecked(True)
        
                infoDump(fname + ' imported successfully')
                btnInvNow.setEnabled(True)
                activateTabs(True)
                nbElecEdit.setText(str(len(self.r2.elec)))
                elecDx.setText('%s' %(self.r2.elec[1,0]-self.r2.elec[0,0]))
#                fnamesCombo.setEnabled(False)
                fnamesCombo.hide()
                fnamesComboLabel.hide()
            except Exception as e:
                print(e)
                errorDump('Importation failed. File is not being recognized. \
                          Make sure you have selected the right file type.')
                pass
        
        buttonf = QPushButton('Import Data')
        buttonf.setAutoDefault(True)
        buttonf.clicked.connect(getfile)
        buttonf.setToolTip('Select input file (time-lapse: select the directory that contains the data).')
        
        def getfileR(): # import reciprocal file
            fnameRecip, _ = QFileDialog.getOpenFileName(tabImportingData,'Open File', self.datadir, self.fformat)
            if fnameRecip != '':
                buttonfr.setText(os.path.basename(fnameRecip))
                if float(spacingEdit.text()) == -1:
                    spacing = None
                else:
                    spacing = float(spacingEdit.text())
                self.r2.surveys[0].addData(fnameRecip, ftype=self.ftype, spacing=spacing, parser=self.parser)
                if all(self.r2.surveys[0].df['irecip'].values == 0) is False:
                    recipOrNoRecipShow(recipPresence = True)
                    tabPreProcessing.setTabEnabled(2, True) # no point in doing error processing if there is no reciprocal
                    plotError()
                    if ipCheck.checkState() == Qt.Checked:
                        tabPreProcessing.setTabEnabled(3, True)
                        recipfilt.setEnabled(True)
                        phaseplotError()
                        heatRaw()
                        heatFilter()
                    errHist()
                plotManualFiltering()

        buttonfr = QPushButton('If you have a reciprocal dataset upload it here')
        buttonfr.setAutoDefault(True)
        buttonfr.clicked.connect(getfileR)
        buttonfr.hide()
        buttonfr.setToolTip('Import file with reciprocal measurements (not mandatory).')
        
        def btnInvNowFunc():
            tabs.setCurrentIndex(5) # jump to inversion tab
            btnInvert.animateClick() # invert
        btnInvNow = QPushButton('Invert')
        btnInvNow.setStyleSheet('background-color: green')
        btnInvNow.setFixedWidth(150)
        btnInvNow.setAutoDefault(True)
        btnInvNow.clicked.connect(btnInvNowFunc)
        btnInvNow.setEnabled(False)
        btnInvNow.setToolTip('Invert with default settings. This will redirect you to the inversion tab.')
        
        hbox4 = QHBoxLayout()
        hbox4.addWidget(wdBtn)
        hbox4.addWidget(fileType)
#        hbox4.addWidget(spacingEdit)
        hbox4.addWidget(buttonf)
        hbox4.addWidget(buttonfr)
        hbox4.addWidget(btnInvNow)
        
        def ipCheckFunc(state):
            print('ipCheck', self.r2.typ)
            if state  == Qt.Checked:
                self.r2.typ = 'c' + self.r2.typ
                self.typ = 'c' + self.typ
                showIpOptions(True)
#                timeLapseCheck.setEnabled(False)
                if self.r2.iForward == True:
                    forwardPseudoIP.setVisible(True)
                else:
                    plotPseudoIP()
                    mwPseudoIP.setVisible(True)
                    tabPreProcessing.setTabEnabled(1, True)
                    if all(self.r2.surveys[0].df['irecip'].values == 0) is False:
                        phaseplotError()
                        tabPreProcessing.setTabEnabled(3, True) # no reciprocity = no IP error model
                        recipfilt.setEnabled(True)
                    heatRaw()
    #                self.r2.surveys[0].filterDataIP_plot = self.r2.surveys[0].filterDataIP_plotOrig
                    self.r2.surveys[0].filterDataIP = self.r2.surveys[0].df
                    heatFilter()
                regionTable.setColumnHidden(1, False)

            else:
                self.r2.typ = self.r2.typ[1:]
                self.typ = self.typ[1:]
                showIpOptions(False)
#                timeLapseCheck.setEnabled(True)
                mwPseudoIP.setVisible(False)
                tabPreProcessing.setTabEnabled(1, False)
                tabPreProcessing.setTabEnabled(3, False)
                regionTable.setColumnHidden(1, True)
                if self.r2.iForward == True:
                    forwardPseudoIP.setVisible(False)
            print('mode', self.r2.typ)

        ipCheck = QCheckBox('Induced Polarization')
        ipCheck.stateChanged.connect(ipCheckFunc)
        ipCheck.setEnabled(False)
        ipCheck.setToolTip('Check if you have IP data or want IP forward modeling')
        
        fnamesComboLabel = QLabel('Choose a dataset to plot:')
        fnamesComboLabel.hide()
        def fnamesComboFunc(index):
            mwPseudo.plot(self.r2.surveys[index].pseudo)
            if self.r2.typ[0] == 'c':
                mwPseudoIP.plot(self.r2.surveys[index].pseudoIP)
        fnamesCombo = QComboBox()
        fnamesCombo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        fnamesCombo.setMinimumWidth(150)
        fnamesCombo.currentIndexChanged.connect(fnamesComboFunc)
#        fnamesCombo.setEnabled(False)
        fnamesCombo.hide()
        
        hbox5 = QHBoxLayout()
        
        hbox5.setAlignment(Qt.AlignRight)
        hbox5.addWidget(ipCheck, Qt.AlignLeft)
        hbox5.addWidget(fnamesComboLabel)
        hbox5.addWidget(fnamesCombo)
        
        metaLayout = QVBoxLayout()
#        metaLayout.addLayout(topLayout)
        metaLayout.addLayout(hbox1)
        metaLayout.addLayout(hbox2)
#        metaLayout.addWidget(wdBtn)
        metaLayout.addLayout(hbox4)
        metaLayout.addLayout(hbox5)
        tabImportingDataLayout.addLayout(metaLayout, 40)

        
        def plotPseudo():
            mwPseudo.plot(self.r2.pseudo)
        
        def plotPseudoIP():
            mwPseudoIP.plot(self.r2.pseudoIP)
        
        pseudoLayout = QHBoxLayout()

        mwPseudo = MatplotlibWidget(navi=True)
        pseudoLayout.addWidget(mwPseudo)
                
        mwPseudoIP = MatplotlibWidget(navi=True)
        mwPseudoIP.setVisible(False)
        pseudoLayout.addWidget(mwPseudoIP)
        
        tabImportingDataLayout.addLayout(pseudoLayout, 60)
        tabImportingData.setLayout(tabImportingDataLayout)
        
        # topo informations
        tabImportingTopo = QWidget()
        tabImporting.addTab(tabImportingTopo, 'Electrodes (XYZ/Topo)')
        
        # electrode table
        class ElecTable(QTableWidget):
            def __init__(self, nrow=2, headers=['x','z','Buried'],
                         selfInit=False):
                """ if selfInit is true, it will automatically add rows if tt
                is bigger than the actual rows
                """
                ncol = len(headers)
                super(ElecTable, self).__init__(nrow, ncol)
                self.nrow = nrow
                self.ncol = ncol
                self.selfInit = selfInit
                self.initTable(np.array([['',''],['','']]), headers=headers)
#                self.headers = np.array(headers)
#                self.setHorizontalHeaderLabels(headers)
#                self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#                if 'Buried' in self.headers:
#                    self.setBuried()
#                    self.ncol = ncol-1
            
            def setBuried(self, vals=None):
                if vals is None:
                    vals = np.zeros(self.nrow, dtype=bool)
                j = np.where(np.array(self.headers) == 'Buried')[0][0]
                for i in range(len(vals)):
                    buriedCheck = QCheckBox()
                    buriedCheck.setChecked(bool(vals[i]))
                    self.setCellWidget(i, j, buriedCheck)
            
            def getBuried(self):
                j = np.where(self.headers == 'Buried')[0][0]
                self.buried = np.zeros(self.nrow, dtype=bool)
                for i in range(self.nrow):
                    buriedCheck = self.cellWidget(i, j)
                    if buriedCheck.isChecked() is True:
                        self.buried[i] = True
                return self.buried
                
            def keyPressEvent(self, e):
#                print(e.modifiers(), 'and', e.key())
                if (e.modifiers() == Qt.ControlModifier) & (e.key() == Qt.Key_V):
                    cell = self.selectedIndexes()[0]
                    c0, r0 = cell.column(), cell.row()
                    self.paste(c0, r0)
                elif e.modifiers() != Qt.ControlModifier: # start editing
#                    print('start editing...')
                    cell = self.selectedIndexes()[0]
                    c0, r0 = cell.column(), cell.row()
                    self.editItem(self.item(r0,c0))
                    
            def paste(self, c0=0, r0=0):
#                print('paste')
                # get clipboard
                text = QApplication.clipboard().text()
                # parse clipboard
                tt = []
                for row in text.split('\n'):
                    trow = row.split()
                    if len(trow) > 0:
                        tt.append(trow)
                tt = np.array(tt)
#                print('tt = ', tt)
#                    self.setItem(0,0,QTableWidgetItem('hlo'))
                if np.sum(tt.shape) > 0:
                    # get max row/columns
#                    cell = self.selectedIndexes()[0]
#                    c0, r0 = cell.column(), cell.row()
                    if self.selfInit is True:
                        self.initTable(tt)
                    else:
                        self.setTable(tt, c0, r0)
                    
            
            def initTable(self, tt=None, headers=None):
                self.clear()
                if headers is not None:
                    self.headers = np.array(headers)
                self.ncol = len(self.headers)
                self.setColumnCount(len(self.headers)) # +1 for buried check column
                self.setHorizontalHeaderLabels(self.headers)
                self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                if 'Buried' in self.headers:
                    self.ncol = self.ncol - 1
                if tt is None:
                    tt = np.zeros((10,len(self.headers)-1))
                self.setRowCount(tt.shape[0])
#                self.setColumnCount(tt.shape[1]) # +1 for buried check column
                self.nrow = tt.shape[0]
                self.setTable(tt)
                if 'Buried' in self.headers:
                    self.setBuried()
                
            def setTable(self, tt, c0=0, r0=0):
                # paste clipboard to qtableView
#                print('set table', self.nrow, self.ncol, tt.shape)
                for i in range(c0, min([self.ncol, c0+tt.shape[1]])):
                    for j in range(r0, min([self.nrow, r0+tt.shape[0]])):
                        self.setItem(j,i,QTableWidgetItem(str(tt[j-r0, i-c0])))
#                        print('item just ste', self.item(j,i).text())
                    
            def getTable(self):
                table = np.zeros((self.nrow, self.ncol))*np.nan
                for i in range(self.ncol):
                    for j in range(self.nrow):
                        if self.item(j,i) is not None:
                            item = self.item(j,i).text()
                            if item != '':
                                table[j,i] = float(item)
#                print('table = ', table)
                if 'y' not in self.headers:
                    t = np.zeros((table.shape[0], 3))
                    t[:,[0,2]] = table
                    table = t
                return table
            
            def readTable(self, fname, nbElec=None):
                    df = pd.read_csv(fname, header=None)
                    tt = df.values
#                    tt = np.genfromtxt(fname)
                    if nbElec is not None:
                        if tt.shape[0] != nbElec:
                            errorDump('The file must have exactly ' + \
                                      str(nbElec) + ' lines (same number as number of electrodes).')
                            return
                    if 'Buried' in self.headers:
                        if len(np.unique(tt[:,-1])) == 2: #only 1 and 0
                            self.initTable(tt[:,:-1])
                            self.setBuried(tt[:,-1])
                        else:
                            self.initTable(tt)
                    else:
                        self.initTable(tt)
#                        if self.selfInit is True:
#                            self.initTable(tt)
#                        else:
#                            self.setTable(tt)    
        
        
        topoLayout = QVBoxLayout()
        
        elecTable = ElecTable(headers=['x','z','Buried'])
        elecLabel = QLabel('<i>Add electrode position. Use <code>Ctrl+V</code> to paste or import from CSV (no headers).\
                           The last column is 1 if checked (= buried electrode) and 0 if not (=surface electrode).\
                           You can also use the form below to generate \
                           regular electrode spacing.</i>')
        elecLabel.setWordWrap(True)
        
        def elecButtonFunc():
            fname, _ = QFileDialog.getOpenFileName(tabImportingTopo,'Open File', directory=self.datadir)
            if fname != '':
                if self.iForward is False:
                    nbElec = int(nbElecEdit.text())
                else:
                    nbElec = None
                elecTable.readTable(fname, nbElec=nbElec)
        elecButton = QPushButton('Import from CSV files (no headers)')
        elecButton.setAutoDefault(True)
        elecButton.clicked.connect(elecButtonFunc)
        nbElecEdit = QLineEdit()
        nbElecEdit.setValidator(QDoubleValidator())
        nbElecEdit.setEnabled(False)
        nbElecLabel = QLabel('Number of electrodes:')
        elecDx = QLineEdit('0.0')
        elecDx.setValidator(QDoubleValidator())
        elecDxLabel = QLabel('X spacing:')
        elecDy = QLineEdit('0.0')
        elecDy.setValidator(QDoubleValidator())
        elecDy.setEnabled(False)
        elecDyLabel = QLabel('Y spacing:')
        elecDz = QLineEdit('0.0')
        elecDz.setValidator(QDoubleValidator())
        elecDzLabel = QLabel('Z spacing:')
        def elecGenButtonFunc():
            nbElec = int(nbElecEdit.text())
            dx = float(elecDx.text())
            dy = float(elecDy.text())
            dz = float(elecDz.text())
            if 'y' in elecTable.headers: # 3D case
                electrodes = np.c_[np.linspace(0.0, (nbElec-1)*dx, nbElec),
                              np.linspace(0.0, (nbElec-1)*dy, nbElec),
                              np.linspace(0.0, (nbElec-1)*dz, nbElec)]
            else:
                electrodes = np.c_[np.linspace(0.0, (nbElec-1)*dx, nbElec),
                              np.linspace(0.0, (nbElec-1)*dz, nbElec)]
            elecTable.initTable(electrodes)
        elecGenButton = QPushButton('Generate')
        elecGenButton.setAutoDefault(True)
        elecGenButton.clicked.connect(elecGenButtonFunc)
        elecGenLayout = QHBoxLayout()
        elecGenLayout.addWidget(nbElecLabel)
        elecGenLayout.addWidget(nbElecEdit)
        elecGenLayout.addWidget(elecDxLabel)
        elecGenLayout.addWidget(elecDx)
        elecGenLayout.addWidget(elecDyLabel)
        elecGenLayout.addWidget(elecDy)
        elecGenLayout.addWidget(elecDzLabel)
        elecGenLayout.addWidget(elecDz)
        elecGenLayout.addWidget(elecGenButton)
        topoLayout.addWidget(elecLabel)
        topoLayout.addLayout(elecGenLayout)
        topoLayout.addWidget(elecButton)
        topoLayout.addWidget(elecTable)
        
        topoTable = ElecTable(headers=['x','z'], selfInit=True)
        topoTable.initTable(np.array([['',''],['','']]))
        topoLabel = QLabel('<i>Add additional surface points. \
                           You can use <code>Ctrl+V</code> to paste directly \
                           into a cell.</i>')
        def topoButtonFunc():
            fname, _ = QFileDialog.getOpenFileName(tabImportingTopo,'Open File', directory=self.datadir)
            if fname != '':
                topoTable.readTable(fname)
        topoButton = QPushButton('Import from CSV files (no headers)')
        topoButton.setAutoDefault(True)
        topoButton.clicked.connect(topoButtonFunc)
        topoLayout.addWidget(topoLabel)
        topoLayout.addWidget(topoButton)
        topoLayout.addWidget(topoTable)
        
        tabImportingTopo.setLayout(topoLayout)
        tabImporting.setTabEnabled(1, False)
        
        
        #%% sub tab for custom importing
        customParser = QWidget()
        tabImporting.addTab(customParser, 'Custom Parser')
        
        delimiterLabel = QLabel('Delimiter:')
        delimiterEdit = QLineEdit('')
        delimiterEdit.setToolTip(r'For tab delimited data use: \t')
        skipRowsLabel = QLabel('Number of header to skip:')
        skipRowsEdit = QLineEdit('0')
        skipRowsEdit.setValidator(QIntValidator())
        nrowsLabel = QLabel('Number of rows to read:')
        nrowsEdit = QLineEdit('')
        nrowsEdit.setValidator(QIntValidator())
        
        self.fnameManual = None
        def openFileBtnFunc(file):
            fname, _ = QFileDialog.getOpenFileName(tabImportingTopo,'Open File')
            if fname != '':
                self.fnameManual = fname
                openFileBtn.setText(fname + ' (Click to change)')
        openFileBtn = QPushButton('Open File')
        openFileBtn.setAutoDefault(True)
        openFileBtn.clicked.connect(openFileBtnFunc)

        def parseBtnFunc():
            if self.fnameManual is None:
                errorDump('Select a file to parse first.')
                return
            try:
                delimiter = delimiterEdit.text()
                delimiter = None if delimiter == '' else delimiter
                skipRows = skipRowsEdit.text()
                skipRows = None if skipRows == '' else int(skipRows)
                nrows = nrowsEdit.text()
                nrows = None if nrows == '' else int(nrows)
                parserTable.readTable(self.fnameManual, delimiter=delimiter,
                                          skiprows=skipRows, nrows=nrows)
                fillBoxes(boxes) # last one is elecSpacingEdit
                infoDump('Parsing successful.')
            except ValueError as e:
                errorDump('Parsing error:' + str(e))

        parseBtn = QPushButton('Import')
        parseBtn.setAutoDefault(True)
        parseBtn.clicked.connect(parseBtnFunc)
            
        # have qcombobox to be read for each columns
        aBoxLabel = QLabel('A (or C1):')
        bBoxLabel = QLabel('B (or C2):')
        mBoxLabel = QLabel('M (or P1):')
        nBoxLabel = QLabel('N (or P2):')
        vpBoxLabel = QLabel('Vp Potential Difference:')
        InBoxLabel = QLabel('In Current:')
        resistBoxLabel = QLabel('Transfer Resistance:')
#        ipStartBoxLabel = QLabel('IP start column') # we don't need these for now, since DCA only works with syscal files
#        ipEndBoxLabel = QLabel('IP end column')
        chargeabilityBoxLabel = QLabel('Chargeability:')
        phaseBoxLabel = QLabel('Phase shift:')
#        elecSpacingLabel = QLabel('Electrode spacing')
       
#        boxesLabels = [aBoxLabel, bBoxLabel, mBoxLabel, nBoxLabel, vpBoxLabel, InBoxLabel, resistBoxLabel, ipStartBoxLabel,
#                 ipEndBoxLabel, chargeabilityBoxLabel, phaseBoxLabel]#, elecSpacingLabel]
        boxesLabels = [aBoxLabel, bBoxLabel, mBoxLabel, nBoxLabel, vpBoxLabel, InBoxLabel, resistBoxLabel,
                       chargeabilityBoxLabel, phaseBoxLabel]#, elecSpacingLabel]
        
        aBox = QComboBox()
        bBox = QComboBox()
        mBox = QComboBox()
        nBox = QComboBox()
        vpBox = QComboBox()
        InBox = QComboBox()
        resistBox = QComboBox()
#        ipStartBox = QComboBox() # we don't need these for now, since DCA only works with syscal files
#        ipEndBox = QComboBox()
        chargeabilityBox = QComboBox()
        chargeabilityBox.setToolTip('input the column containing chargeability (mV/V) values')
        phaseBox = QComboBox()
        phaseBox.setToolTip('input the column containing phase shift (mRad) values')
#        elecSpacingEdit = QLineEdit('')
#        elecSpacingEdit.setEnabled(False)
#        elecSpacingEdit.setValidator(QDoubleValidator())
#        elecSpacingEdit.setFixedWidth(80)
#        elecSpacingEdit.setToolTip('Number to divide the selected columns to get electrode number.')
        
#        boxes = [aBox, bBox, mBox, nBox, vpBox, InBox, resistBox, ipStartBox,
#                 ipEndBox, chargeabilityBox, phaseBox]#, elecSpacingEdit]
        boxes = [aBox, bBox, mBox, nBox, vpBox, InBox, resistBox, 
                 chargeabilityBox, phaseBox]#, elecSpacingEdit]
                
        def fillBoxes(bs):
            for b in bs:
                b.clear()
                choices = parserTable.headers
                for i, choice in enumerate(choices):
                    if i == 0:
                        b.addItem('Select if available')
                    b.addItem(str(choice))
                    
        def getBoxes(bs):
            cols = []
            for b in bs:
                cols.append(b.currentIndex()-1) # -1 because of 1st item
            return np.array(cols)
        
        # add a qtableview or create a custom class
        class ParserTable(QTableWidget):
            def __init__(self, nrow=10, ncol=10):
                super(ParserTable, self).__init__(nrow, ncol)
                self.nrow = nrow
                self.ncol = ncol
                self.headers = []
#                self.horizontalHeader.hide()
            
            def readTable(self, fname='', delimiter=None, skiprows=None, nrows=None):
                if fname != '':
                    df = pd.read_csv(fname, delimiter=delimiter, skiprows=skiprows, nrows=nrows)
                    df = df.reset_index() # in case all parse columns goes into the index (don't know why)
                    self.setRowCount(df.shape[0])
                    self.setColumnCount(df.shape[1])
                    self.headers = df.columns.values.astype(str) # make sure it's string
                    self.setHorizontalHeaderLabels(self.headers)
                    tt = df.values
                    self.setTable(tt)            
                
            def setTable(self, tt):
                # paste clipboard to qtableView
                self.setRowCount(tt.shape[0])
                self.setColumnCount(tt.shape[1])
#                self.setHorizontalHeaderLabels(self.headers)
                self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                for i in range(tt.shape[1]):
                    for j in range(tt.shape[0]):
                        self.setItem(j,i,QTableWidgetItem(str(tt[j, i])))
        
            
        parserTable = ParserTable()
        
        def importBtnFunc():
            restartFunc()
            self.r2 = R2()
            print('importing data')
            colIndex = []
            newHeaders = []
            vals = getBoxes([aBox,bBox,mBox,nBox])
            if (np.sum(vals > 0) == 4) & (len(np.unique(vals)) == 4):
                colIndex.append(vals)
                newHeaders.append(['a','b','m','n'])
            else:
                errorDump('Please select columns for electrodes.')
                return
            vals = getBoxes([resistBox])
            if vals[0] > 0:
                colIndex.append(vals)
                newHeaders.append(['resist'])
            else:
                vals = getBoxes([vpBox,InBox])
                if all(vals > 0) is True:
                    colIndex.append(vals)
                    newHeaders.append(['vp','i'])
                else:
                    errorDump('Please select columns for Vp, In or Resist.')
                    return
            vals = getBoxes([chargeabilityBox])
            if vals[0] > 0:
                colIndex.append(vals)
                newHeaders.append(['ip'])
                phiConvFactor.setText('1')
                phiConvFactor.setEnabled(True)
                phiConvFactorlabel.setEnabled(True)
                self.inputPhaseFlag = False
            else:
                vals = getBoxes([phaseBox])
                if vals[0] > 0:
                    colIndex.append(vals)
                    newHeaders.append(['ip'])
                    phiConvFactor.setText('-')
                    phiConvFactor.setEnabled(False)
                    phiConvFactorlabel.setEnabled(False)
                    self.inputPhaseFlag = True
                else:
                    ipCheck.setChecked(False)
                    
            # TODO need to import the IP coluns as well
            
            colIndex = np.hstack(colIndex)
            newHeaders = np.hstack(newHeaders)
#            print(colIndex, newHeaders)

            def parserFunc(fname):
                # retrieve usefull values
                delimiter = delimiterEdit.text()
                delimiter = None if delimiter == '' else delimiter
                skipRows = skipRowsEdit.text()
                skipRows = None if skipRows == '' else int(skipRows)
                nrows = nrowsEdit.text()
                nrows = None if nrows == '' else int(nrows)
                espacing = None #if elecSpacingEdit.text() == '' else float(elecSpacingEdit.text())
                
                # parse
                print('delimiter=', delimiter)
                df = pd.read_csv(fname, delimiter=delimiter, skiprows=skipRows, nrows=nrows)
                df = df.reset_index() # solve issue all columns in index
                oldHeaders = df.columns.values[colIndex]
                df = df.rename(columns=dict(zip(oldHeaders, newHeaders)))
                if 'resist' not in df.columns:
                    df['resist'] = df['vp']/df['i']
                if 'ip' not in df.columns:
                    df['ip'] = 0
                elif self.inputPhaseFlag == True:
                    df['ip'] *= -1 # if the input ip values are already phase, in custom parser only!
                array = df[['a','b','m','n']].values.copy()
                arrayMin = np.min(np.unique(np.sort(array.flatten())))
                if arrayMin != 0:
                    array -= arrayMin
                if espacing is None:
                    espacing = np.unique(np.sort(array.flatten()))[1] - np.unique(np.sort(array.flatten()))[0]
                array = np.round(array/espacing+1).astype(int)
                df[['a','b','m','n']] = array
                imax = int(np.max(array))
#                if np.sum(array == 0) > 0:
#                    print('add 1 as there is electrodes at zeros')
#                    imax = imax+1
                elec = np.zeros((imax,3))
                elec[:,0] = np.arange(0,imax)*espacing
                nbElecEdit.setText('%s' % (len(elec)))
#                nbElecEdit.setEnabled(False)
                elecDx.setText('%s' % (espacing))
                return elec, df

            self.parser = parserFunc
            
            # test            
            elec, df = parserFunc(self.fnameManual)
            print('shapes = ', elec.shape, df.shape)
                
            
            if (self.r2.iTimeLapse is False) & (self.r2.iBatch is False):
                importFile(self.fnameManual)
            fileType.setCurrentIndex(7)
            tabImporting.setCurrentIndex(0)
                
                
        importBtn = QPushButton('Import Dataset')
        importBtn.setAutoDefault(True)
        importBtn.clicked.connect(importBtnFunc)
        
        
        # layout
        parserLayout = QVBoxLayout()
        parserOptions = QHBoxLayout()
        columnsAssign = QGridLayout()
        
        parserLayout.addWidget(openFileBtn)
        parserOptions.addWidget(delimiterLabel)
        parserOptions.addWidget(delimiterEdit)
        parserOptions.addWidget(skipRowsLabel)
        parserOptions.addWidget(skipRowsEdit)
        parserOptions.addWidget(nrowsLabel)
        parserOptions.addWidget(nrowsEdit)
        parserOptions.addWidget(parseBtn)
        parserLayout.addLayout(parserOptions)
        
        parserLayout.addWidget(parserTable)
        for i in range(len(boxes)):
            c = (i % 3)*2 # in 2*3 columns (with labels)
            r = int(i/3) 
            columnsAssign.addWidget(boxesLabels[i], r, c, Qt.AlignRight)
            columnsAssign.addWidget(boxes[i], r, c+1)
        parserLayout.addLayout(columnsAssign)
        parserLayout.addWidget(importBtn)
        
        customParser.setLayout(parserLayout)

        
        #%% tab 2 PRE PROCESSING
        tabPreProcessing = QTabWidget()
        tabs.addTab(tabPreProcessing, 'Pre-processing')
        tabs.setTabEnabled(1,False)
        
        def recipOrNoRecipShow(recipPresence = True): # changes the reciprocal filtering tab stuff
            if recipPresence == True:
                tabPreProcessing.setTabText(0, 'Reciprocal Filtering')
                recipErrorLabel.setText('<b>Remove datapoints that have reciprocal error larger than what you prefer.</b><br>Either select (<i>click on the dots to select them</i>) the points on the pseudo section below or choose a percentage threshold or both!</br>')
                recipErrorInputLabel.show()
                recipErrorInputLine.show()
                recipErrorInputLine.setText('-')
                recipErrorPltbtn.setText('Apply filters')
                recipErrorUnpairedBtn.show()
                recipErrorPltbtn.setToolTip('Removes measuremtns that have either greater reciprocal error than "Percent error threshold" or are manually selected or both!')
                recipErrorBottomTabs.setTabEnabled(1, True)
            if recipPresence == False:
                tabPreProcessing.setTabText(0, 'Manual Filtering')
                recipErrorLabel.setText('<b>Select datapoints to remove.</b><br><i>click on the dots to select them</i></br>')
                recipErrorInputLabel.hide()
                recipErrorInputLine.setText('-')
                recipErrorInputLine.hide()
                recipErrorUnpairedBtn.hide()
                recipErrorPltbtn.setText('Remove selected points')
                recipErrorPltbtn.setToolTip('Removes measuremtns that are manually selected!')
                recipErrorBottomTabs.setTabEnabled(1, False)              
                
        def plotManualFiltering():
            mwManualFiltering.plot(self.r2.surveys[0].manualFiltering)
            
        def errHist():
            if all(self.r2.surveys[0].df['irecip'].values == 0) is False:
                recipErrorPLot.plot(self.r2.errorDist)
            else:
                pass
        
        def recipFilter():
            try:
                numSelectRemoved = 0
                if self.r2.iTimeLapse or self.r2.iBatch: # only remove electrode not single measurements
                    self.r2.filterElec(np.where(self.r2.surveys[0].eselect)[0]+1)
                else:
                    numSelectRemoved += self.r2.surveys[0].filterData(~self.r2.surveys[0].iselect)
                if recipErrorInputLine.text() != '-':
                    percent = float(recipErrorInputLine.text())
                    numRecipRemoved = self.r2.filterRecip(percent=percent)
                    infoDump("%i measurements with greater than %3.1f%% reciprocal error and %i selected measurements removed!" % (numRecipRemoved,percent,numSelectRemoved))
                else:
                    infoDump("%i selected measurements removed!" % (numSelectRemoved))
                if ipCheck.checkState() == Qt.Checked:
                    for s in self.surveys:
                        s.dfPhaseReset = s.df
                        s.filterDataIP = s.df
                    heatFilter()
                    phaseplotError()
                errHist()
                plotManualFiltering()
                plotError()
            except ValueError as e:
                if ipCheck.checkState() != Qt.Checked:
                    errorDump(e)    
                else:
                    errorDump('Index error! Reciprocal Filtering cannot be done after Phase Filtering.\n'
                              'Reset the filters and redo the filterings, first reciprocity then phase.') 
            
        def resetRecipFilter():
            numRestored = len(self.r2.surveys[0].dfReset) - len(self.r2.surveys[0].df)
            for s in self.r2.surveys:
                s.df = s.dfReset.copy()
            if recipErrorInputLine.text() != '-':
                errHist()
                recipErrorInputLine.setText('-')
            if ipCheck.checkState() == Qt.Checked:
                for s in self.r2.surveys:
                    s.dfPhaseReset = s.dfReset.copy()
                    s.filterDataIP = s.dfReset.copy()
                heatFilter()
                phaseplotError()
            errHist()
            plotManualFiltering()
            plotError()
            infoDump('%i measurements restored!' % numRestored)

#        manualLayout = QVBoxLayout()
          
#        def btnDoneFunc():
#            self.r2.surveys[0].filterData(~self.r2.surveys[0].iselect)
#            infoDump('Data have been manually filtered.')
#            plotManualFiltering()
#            plotError()

#        manualTopLayout = QVBoxLayout()
#        manualTopLayout.setAlignment(Qt.AlignTop)
#        notice = QLabel('Click on the dots to select them. Press "Apply" to remove them.')
#        manualTopLayout.addWidget(notice)
#        
#        btnLayout = QHBoxLayout()
        
#        btnStart = QPushButton('Start')
#        btnStart.setAutoDefault(True)
#        btnStart.clicked.connect(plotManualFiltering)
#        btnStart.setToolTip('Plot a clickable pseudo section with electrodes.')
#        btnLayout.addWidget(btnStart)
#        btnDone = QPushButton('Apply')
#        btnDone.setAutoDefault(True)
#        btnDone.clicked.connect(btnDoneFunc)
#        btnDone.setToolTip('This will erase all selected quadrupoles definitively.')
#        btnLayout.addWidget(btnDone)
#        manualTopLayout.addLayout(btnLayout)
#        manualLayout.addLayout(manualTopLayout, 0) # number is stretch factor
     
        recipErrorLayout = QVBoxLayout()
        recipErrorTopLayout = QVBoxLayout()
        
        recipErrorLabel = QLabel('<b>Remove datapoints that have reciprocal error larger than what you prefer.</b><br>Either select (<i>click on the dots to select them</i>) the points on the pseudo section below or choose a percentage threshold or both!</br>')
        recipErrorTopLayout.addWidget(recipErrorLabel)
        
        
        recipErrorInputlayout = QHBoxLayout()
        
        recipErrorInputLeftlayout = QHBoxLayout()
        recipErrorInputLeftlayout.setAlignment(Qt.AlignLeft)
        
        recipErrorInputLeftlayoutL = QHBoxLayout()
        recipErrorInputLeftlayoutL.setAlignment(Qt.AlignRight)
        recipErrorInputLabel = QLabel('Percent error threshold:')
        recipErrorInputLeftlayoutL.addWidget(recipErrorInputLabel)
        recipErrorInputLeftlayout.addLayout(recipErrorInputLeftlayoutL)
        
        recipErrorInputLineLayout = QHBoxLayout()
        recipErrorInputLineLayout.setAlignment(Qt.AlignLeft)
        
        recipErrorInputLine = QLineEdit('-')
        recipErrorInputLine.setFixedWidth(100)
        recipErrorInputLine.setValidator(QDoubleValidator())
        recipErrorInputLineLayout.addWidget(recipErrorInputLine)
        recipErrorInputLeftlayout.addLayout(recipErrorInputLineLayout)
        recipErrorInputlayout.addLayout(recipErrorInputLeftlayout)
            
        recipErrorBtnLayout = QHBoxLayout()
        recipErrorBtnLayout.setAlignment(Qt.AlignRight)
        
        def recipErrorUnpairedFunc():
            numRemoved = self.r2.removeUnpaired()
            if ipCheck.checkState() == Qt.Checked:
                for s in self.surveys:
                    s.dfPhaseReset = s.df
                    s.filterDataIP = s.df
                heatFilter()
                phaseplotError()
            errHist()
            plotManualFiltering()
            plotError()
            infoDump('%i unpaired quadrupoles removed!' % numRemoved)

        recipErrorUnpairedBtn = QPushButton('Remove Unpaired')
        recipErrorUnpairedBtn.setFixedWidth(150)
        recipErrorUnpairedBtn.setToolTip('Remove quadrupoles without reciprocals')
        recipErrorUnpairedBtn.clicked.connect(recipErrorUnpairedFunc)
        recipErrorBtnLayout.addWidget(recipErrorUnpairedBtn)
        
        recipErrorPltbtn = QPushButton('Apply filters')
        recipErrorPltbtn.setToolTip('Removes measuremtns that have either greater reciprocal error than "Percent error threshold" or are manually selected or both!')
        recipErrorPltbtn.clicked.connect(recipFilter)
        recipErrorPltbtn.setFixedWidth(150)
        recipErrorBtnLayout.addWidget(recipErrorPltbtn)
        
        recipErrorResetbtn = QPushButton('Reset')
        recipErrorResetbtn.setStyleSheet("color: red")
        recipErrorResetbtn.setToolTip('This will restore all deleted measurements at this stage')
        recipErrorResetbtn.clicked.connect(resetRecipFilter)
        recipErrorResetbtn.setFixedWidth(150)
        recipErrorBtnLayout.addWidget(recipErrorResetbtn)
        
        
        recipErrorInputlayout.addLayout(recipErrorBtnLayout, 1)
        recipErrorTopLayout.addLayout(recipErrorInputlayout)
        
        recipErrorLayout.addLayout(recipErrorTopLayout, 0) # number is stretch factor
        
        recipErrorPlotLayout = QVBoxLayout()
        recipErrorPLot = MatplotlibWidget(navi=True)
        recipErrorPlotLayout.addWidget(recipErrorPLot)
               
        recipErrorBottomLayout = QVBoxLayout()
        
        recipErrorBottomTabs = QTabWidget() 
        
        recipErrorPseudoPlotLayout = QVBoxLayout()
        mwManualFiltering = MatplotlibWidget(navi=True)
        recipErrorPseudoPlotLayout.addWidget(mwManualFiltering)
#        manualPseudoPlotLayout.setLayout(manualBottomLayout)
        pseudoSectionPlotTab = QWidget()
        pseudoSectionPlotTab.setLayout(recipErrorPseudoPlotLayout)
        recipErrorBottomTabs.addTab(pseudoSectionPlotTab, 'Pseudo Section')
        
        errorHistogramPlotTab = QWidget()
        errorHistogramPlotTab.setLayout(recipErrorPlotLayout)
        recipErrorBottomTabs.addTab(errorHistogramPlotTab, 'Error Histogram')
        
        recipErrorBottomLayout.addWidget(recipErrorBottomTabs)
#        manualBottomLayout.addWidget(mwManualFiltering)
        recipErrorLayout.addLayout(recipErrorBottomLayout, 1) # '1' to keep the plot in largest strech
        
        # Resistance error tab
        errorLayout = QVBoxLayout()
        
        def errorModelSpecified():
            a_wgt.setText('0.0')
            a_wgtFunc()
            b_wgt.setText('0.0')
            b_wgtFunc()
        
        def plotError():
            mwFitError.plot(self.r2.plotError)
            self.r2.err = False
            
#        def fitLinError():
#            mwFitError.plot(self.r2.linfit)
#            self.r2.errTyp = 'lin'
#            
#        def fitLmeError():
#            print('NOT READY YET')
#            mwFitError.plot(self.r2.lmefit)
#            self.r2.errTyp = 'lme'
#        
#        def fitpwl():
#            mwFitError.plot(self.r2.pwlfit)
#            self.r2.errTyp = 'pwl'

        def errFitTypeFunc(index):
#            print(index)
            if index == 0:
                plotError()
            elif index == 1:
                mwFitError.plot(self.r2.linfit)
                self.r2.err = True
            elif index == 2:
                mwFitError.plot(self.r2.pwlfit)
                self.r2.err = True
            elif index == 3:
                mwFitError.plot(self.r2.lmefit)
                self.r2.err = True
            else:
                print('NOT IMPLEMENTED YET')
            if index == 0:
                a_wgt.setText('0.01')
                a_wgtFunc()
                b_wgt.setText('0.02')
                b_wgtFunc()
            else:
                a_wgt.setText('0.0')
                a_wgtFunc()
                b_wgt.setText('0.0')
                b_wgtFunc()
        
        errFitType = QComboBox()
        errFitType.addItem('Observed Errors')
        errFitType.addItem('Linear')
        errFitType.addItem('Power-law')
        errFitType.addItem('Linear Mixed Effect (requires R and the lme4 package, dc surveys only for now)')
        errFitType.currentIndexChanged.connect(errFitTypeFunc)
        errFitType.setToolTip('Select an error model to use.')
        errorLayout.addWidget(errFitType)
        
        mwFitError = MatplotlibWidget(navi=True)
        errorLayout.addWidget(mwFitError)
       
        
        ipLayout = QVBoxLayout()
        
        def phaseplotError():
            mwIPFiltering.plot(self.r2.phaseplotError)
        
#        def phasePLerr():
#            mwIPFiltering.plot(self.r2.plotIPFit)
#            self.r2.errTypIP = 'pwlip'
            
        def iperrFitTypeFunc(index):
#            print(index)
            if index == 0:
                phaseplotError()
            elif index == 1:
                mwIPFiltering.plot(self.r2.plotIPFit)
                self.r2.err = True
            elif index == 2:
                mwIPFiltering.plot(self.r2.plotIPFitParabola)
                self.r2.err = True
            else:
                print('NOT IMPLEMENTED YET')
            if index == 0:
                a_wgt.setText('0.02')
                a_wgtFunc()
                b_wgt.setText('2')
                b_wgtFunc()
#                b_wgt.setText('0.02')
#                b_wgtFunc()
#                c_wgt.setText('1.0')
#                c_wgtFunc()
            else:
                a_wgt.setText('0')
                a_wgtFunc()
                b_wgt.setText('0')
                b_wgtFunc()
#                a_wgt.setText('0.01')
#                a_wgtFunc()
#                b_wgt.setText('0.0')
#                b_wgtFunc()
#                c_wgt.setText('0.0')
#                c_wgtFunc()
            
            
        iperrFitType = QComboBox()
        iperrFitType.addItem('Observed discrepancies') ##### BY default does not show!! should be selected after the power law (don't know why!!!)
        iperrFitType.addItem('Power law')
        iperrFitType.addItem('Parabola')
        iperrFitType.currentIndexChanged.connect(iperrFitTypeFunc)
        iperrFitType.setToolTip('Select an error model for IP.')
        ipLayout.addWidget(iperrFitType)
        
        mwIPFiltering = MatplotlibWidget(navi=True)
        ipLayout.addWidget(mwIPFiltering)

        phasefiltlayout = QVBoxLayout()
        
        def phirange():
            self.r2.iprangefilt(float(phivminEdit.text()),
                                float(phivmaxEdit.text()))
            heatFilter()
            
        def removerecip():
            self.r2.removerecip()
            heatFilter()
        
        def removenested():
            self.r2.removenested()
            heatFilter()
            
        def convFactK():
            self.r2.surveys[0].kFactor = float(phiConvFactor.text())
            heatFilter()
            
        phitoplayout = QHBoxLayout()
        phiConvFactorlabel = QLabel('Conversion factor k (φ = -kM):')
        phiConvFactorlabel.setToolTip('Assuming linear relationship.\nk = 1.2 is for IRIS Syscal devices\nThis equation is not used when importing phase data')
        phiConvFactor = QLineEdit()
        phiConvFactor.setFixedWidth(50)
        phiConvFactor.setValidator(QDoubleValidator())
        phiConvFactor.setText('1.2')
        phiConvFactor.setToolTip('Assuming linear relationship.\nk = 1.2 is for IRIS Syscal devices\nThis equation is not used when importing phase data')
        phiConvFactor.editingFinished.connect(convFactK)
        rangelabel = QLabel('     Phase range filtering:')
        phivminlabel = QLabel('-φ min:')
        phivminEdit = QLineEdit()
        phivminEdit.setValidator(QDoubleValidator())
        phivmaxlabel = QLabel('-φ max:')
        phivmaxEdit = QLineEdit()
        phivmaxEdit.setValidator(QDoubleValidator())
        phivminEdit.setText('0')
        phivmaxEdit.setText('25')
        rangebutton = QPushButton('Apply')
        rangebutton.setAutoDefault(True)
        rangebutton.clicked.connect(phirange)
        
        recipfilt = QPushButton('Remove reciprocals')
        recipfilt.setToolTip('Reciprocal measurements will not be considered for inversion in pyR2.\nThis filter just visualize the removal')
        recipfilt.setAutoDefault(True)
        recipfilt.setEnabled(False)
        recipfilt.clicked.connect(removerecip)

        nestedfilt = QPushButton('Remove nested')
        nestedfilt.setToolTip('Measurments where M and/or N are inbetween A and B will be removed.\nNOTE: Wenner like arrays will also be affected')
        nestedfilt.setAutoDefault(True)
        nestedfilt.clicked.connect(removenested)        
        
        phitoplayout.addWidget(phiConvFactorlabel)
        phitoplayout.addWidget(phiConvFactor)
        phitoplayout.addWidget(rangelabel)
        phitoplayout.addWidget(phivminlabel)
        phitoplayout.addWidget(phivminEdit)
        phitoplayout.addWidget(phivmaxlabel)
        phitoplayout.addWidget(phivmaxEdit)
        phitoplayout.addWidget(rangebutton)
        phitoplayout.addWidget(recipfilt)
        phitoplayout.addWidget(nestedfilt)
        
        phasefiltlayout.addLayout(phitoplayout,0)
        
        def filt_reset():
            self.r2.surveys[0].filterDataIP = self.r2.surveys[0].dfPhaseReset.copy()
            self.r2.surveys[0].df = self.r2.surveys[0].dfPhaseReset.copy()
            heatFilter()
            dcaProgress.setValue(0)
            infoDump('All phase filteres are now reset!')
            
        def phiCbarRange():
            self.r2.surveys[0].phiCbarmin = float(phiCbarminEdit.text())
            self.r2.surveys[0].phiCbarMax = float(phiCbarMaxEdit.text())
            heatFilter()
            heatRaw()
        
        def phiCbarDataRange():
            minDataIP = np.min(self.r2.surveys[0].dfOrigin['ip'])
            maxDataIP = np.max(self.r2.surveys[0].dfOrigin['ip'])
            if self.ftype == 'ProtocolIP':
                self.r2.surveys[0].phiCbarmin = -maxDataIP
                self.r2.surveys[0].phiCbarMax = -minDataIP
            else:
                self.r2.surveys[0].phiCbarmin = minDataIP
                self.r2.surveys[0].phiCbarMax = maxDataIP
            heatFilter()
            heatRaw()
        
        resetlayout = QHBoxLayout()
        filtreset = QPushButton('Reset all "phase" filters')
        filtreset.setStyleSheet("color: red")
        filtreset.setToolTip('Reset all the filtering.\nk factor is not affected')
        filtreset.setAutoDefault(True)
        filtreset.clicked.connect(filt_reset)
        phiCbarminlabel = QLabel('Colorbar min: ')
        phiCbarminEdit = QLineEdit()
#        phiCbarminEdit.setFixedWidth(80)
        phiCbarminEdit.setValidator(QDoubleValidator())
        phiCbarminEdit.setText('0')
        phiCbarMaxlabel = QLabel('Colorbar Max: ')
        phiCbarMaxEdit = QLineEdit()
#        phiCbarMaxEdit.setFixedWidth(80)
        phiCbarMaxEdit.setValidator(QDoubleValidator())
        phiCbarMaxEdit.setText('25')
        phiCbarrangebutton = QPushButton('Apply')
        phiCbarrangebutton.setToolTip('This is not a filtering step.')
        phiCbarrangebutton.setAutoDefault(True)
        phiCbarrangebutton.clicked.connect(phiCbarRange)
        phiCbarDatarangebutton = QPushButton('Scale to raw data range')
        phiCbarDatarangebutton.setToolTip('This is not a filtering step.')
        phiCbarDatarangebutton.setAutoDefault(True)
        phiCbarDatarangebutton.clicked.connect(phiCbarDataRange)
        resetlayout.addWidget(phiCbarminlabel)
        resetlayout.addWidget(phiCbarminEdit)
        resetlayout.addWidget(phiCbarMaxlabel)
        resetlayout.addWidget(phiCbarMaxEdit)
        resetlayout.addWidget(phiCbarrangebutton)
        resetlayout.addWidget(phiCbarDatarangebutton)
        resetlayout.addWidget(filtreset)
#        recipfilt.clicked.connect("add function")
        
        
        ipfiltlayout = QHBoxLayout()
        
        def heatRaw():
#            self.r2.surveys[0].phiCbarmin = float(phiCbarminEdit.text())
#            self.r2.surveys[0].phiCbarMax = float(phiCbarMaxEdit.text())
            self.r2.surveys[0].filt_typ = 'Raw'
#            self.r2.surveys[0].cbar = False
            raw_hmp.plot(self.r2.heatmap)
            
        def heatFilter():
            self.r2.surveys[0].filt_typ = 'Filtered'
#            self.r2.surveys[0].cbar = True
            filt_hmp.plot(self.r2.heatmap)
            
        raw_hmp = MatplotlibWidget(navi=True)
        filt_hmp = MatplotlibWidget(navi=True)
        ipfiltlayout.addWidget(raw_hmp)
        ipfiltlayout.addWidget(filt_hmp)           

        
        def dcaDump(val):
            dcaProgress.setValue(val)
            QApplication.processEvents()
            
        def dcaFiltering():
            try:
                self.r2.surveys[0].dca(dump=dcaDump)
                heatFilter()
            except:
                errorDump('No decay curves found or incomplete set of decay curves! Export the data from "Prosys" with M1, M2, ... , M20 and TM1 tabs enabled.')         
            
        dcaLayout = QHBoxLayout()
        dcaButton = QPushButton('DCA filtering')
        dcaButton.setToolTip('Decay Curve Analysis filtering.\nFor more see: Flores Orozco, et al. (2017), Decay curve analysis for data error quantification in\ntime-domain induced polarization imaging')
        dcaButton.setAutoDefault(True)
        dcaButton.clicked.connect(dcaFiltering)
        dcaProgress = QProgressBar()
        dcaLayout.addWidget(dcaButton)
        dcaLayout.addWidget(dcaProgress)
        
        phasefiltlayout.addLayout(dcaLayout, 1)
        phasefiltlayout.addLayout(resetlayout, 2)
        phasefiltlayout.addLayout(ipfiltlayout, 3)
            
#        manualWidget = QWidget()
#        manualWidget.setLayout(manualLayout)
#        tabPreProcessing.addTab(manualWidget, 'Reciprocal Filtering')
        
        recipErrorWidget = QWidget()
        recipErrorWidget.setLayout(recipErrorLayout)
        tabPreProcessing.addTab(recipErrorWidget, 'Reciprocal error analysis')
        
        ipfiltWidget = QWidget()
#        ipfiltWidget.setVisible(False)
        ipfiltWidget.setLayout(phasefiltlayout)
        tabPreProcessing.addTab(ipfiltWidget, 'Phase Filtering')
        errorWidget = QWidget()
        errorWidget.setLayout(errorLayout)
        tabPreProcessing.addTab(errorWidget, 'Resistance Error Model')
        ipWidget = QWidget()
        ipWidget.setVisible(False)
        ipWidget.setLayout(ipLayout)
        tabPreProcessing.addTab(ipWidget, 'Phase Error Model')

        tabPreProcessing.setTabEnabled(0, True) # Reciprocal filter
        tabPreProcessing.setTabEnabled(1, False) # IP filter
        tabPreProcessing.setTabEnabled(2, False) # resistivity error model
        tabPreProcessing.setTabEnabled(3, False) # IP error model        
        
        #%% tab MESH
        tabMesh= QWidget()
        tabs.addTab(tabMesh, 'Mesh')
        tabs.setTabEnabled(2, False)
                
        meshLayout = QVBoxLayout()
        
        def replotMesh():
            regionTable.reset()
            def func(ax):
                self.r2.createModel(ax=ax, addAction=regionTable.addRow)
            mwMesh.plot(func)
            mwMesh.canvas.setFocusPolicy(Qt.ClickFocus) # allows the keypressevent to go to matplotlib
            mwMesh.canvas.setFocus() # set focus on the canvas
            
        def meshQuadFunc():
            elec = elecTable.getTable()
            buried = elecTable.getBuried()
            surface = topoTable.getTable()
            if not np.isnan(surface[0,0]):
                surface_flag = True
            else:
                surface_flag = False
            if np.sum(~np.isnan(elec[:,0])) == 0:
                errorDump('Please first import data or specify electrodes in the "Electrodes (XYZ/Topo)" tab.')
                return
            else:
                self.r2.setElec(elec)
#            nnodes = int(nnodesEdit.text())
#            if nnodes < 4:
#                nnodesEdit.setText('4')
#                nnodes = 4
#                errorDump('There need to be at least 4 elements between two electrodes.')
#            if nnodes > 10:
#                nnodesEdit.setText('10')
#                nnodes = 10
#                errorDump('Sorry no more than 10 elements between electrodes.')
            nnodes = nnodesSld.value()
            try:
                if surface_flag:
                    print("quad mesh + topo")
                    self.r2.createMesh(typ='quad', buried = buried, elemx=nnodes, surface_x=surface[:,0], surface_y=surface[:,2])
                else:
                    print("quad mesh no topo")
                    self.r2.createMesh(typ='quad', buried = buried, elemx=nnodes)
                scale.setVisible(False)
                scaleLabel.setVisible(False)
                meshOutputStack.setCurrentIndex(1)
                replotMesh()
            except Exception as e:
                errorDump('Error creating the mesh: ' + str(e))
        meshQuad = QPushButton('Quadrilateral Mesh')
        meshQuad.setAutoDefault(True)
        meshQuad.clicked.connect(meshQuadFunc)
        meshQuad.setToolTip('Generate quadrilateral mesh.')
        
        def meshTrianFunc():
            elec = elecTable.getTable()
            if np.sum(~np.isnan(elec[:,0])) == 0:
                errorDump('Please first import data or specify electrodes in the "Electrodes (XYZ/Topo)" tab.')
                return
            else:
                self.r2.setElec(elec)
            meshOutputStack.setCurrentIndex(0)
            QApplication.processEvents()
            meshLogText.clear()
            elecSpacing = np.sqrt((self.r2.elec[0,0]-self.r2.elec[1,0])**2+
                                  (self.r2.elec[0,2]-self.r2.elec[1,2])**2)
            cl = float(clSld.value())/10*(elecSpacing-elecSpacing/8)
            cl_factor = clFactorSld.value()
#            cl = float(clEdit.text())
#            cl_factor = float(cl_factorEdit.text())
            buried = elecTable.getBuried()
            surface = topoTable.getTable()
#            print('buried = ', buried)
#            print('surface = ', surface)
#            print('electrode = ', elec)
            inan = ~np.isnan(surface[:,0])
            if np.sum(~inan) == surface.shape[0]:
                surface = None
            else:
                surface = surface[inan,:]
            self.r2.createMesh(typ='trian', buried=buried, surface=surface,
                               cl=cl, cl_factor=cl_factor, dump=meshLogTextFunc)
            scale.setVisible(True)
            scaleLabel.setVisible(True)
            replotMesh()
            meshOutputStack.setCurrentIndex(1)
            
        meshTrian = QPushButton('Triangular Mesh')
        meshTrian.setAutoDefault(True)
        meshTrian.clicked.connect(meshTrianFunc)
        meshTrian.setToolTip('Generate triangular mesh.')
              
        
        def meshTetraFunc():
            elec = elecTable.getTable()
            if np.sum(~np.isnan(elec[:,0])) == 0:
                errorDump('Please first import data or specify electrodes in the "Electrodes (XYZ/Topo)" tab.')
                return
            else:
                self.r2.setElec(elec)
            meshOutputStack.setCurrentIndex(0)
            QApplication.processEvents()
            meshLogText.clear()
            cl = float(cl3Edit.text())
            cl_factor = float(cl3FactorEdit.text())
            buried = elecTable.getBuried()
            surface = topoTable.getTable()
            inan = ~np.isnan(surface[:,0])
            if np.sum(~inan) == surface.shape[0]:
                surface = None
            else:
                surface = surface[inan,:]
            self.r2.createMesh(typ='tetra', buried=buried, surface=surface,
                               cl=cl, cl_factor=cl_factor, dump=meshLogTextFunc)
            mwMesh3D.plot(self.r2.showMesh, threed=True)
            meshOutputStack.setCurrentIndex(2)

        meshTetra = QPushButton('Tetrahedral Mesh')
        meshTetra.setAutoDefault(True)
        meshTetra.clicked.connect(meshTetraFunc)
        meshTetra.setToolTip('Generate tetrahedral mesh.')

        
        # additional options for quadrilateral mesh
        nnodesLabel = QLabel('Number of nodes between electrode (4 -> 10):')
#        nnodesEdit = QLineEdit()
#        nnodesEdit.setValidator(QIntValidator())
#        nnodesEdit.setText('4')
        nnodesSld = QSlider(Qt.Horizontal)
        nnodesSld.setMinimum(4)
        nnodesSld.setMaximum(10)

        # additional options for triangular mesh
        clLabel = QLabel('Characteristic Length:')
#        clEdit = QLineEdit()
#        clEdit.setValidator(QDoubleValidator())
#        clEdit.setText('-1')
        clGrid = QGridLayout()
        clFineLabel = QLabel('Fine')
        clFineLabel.setStyleSheet('font:12px;')
        clCoarseLabel = QLabel('Coarse')
        clCoarseLabel.setStyleSheet('font:12px;')
        clSld = QSlider(Qt.Horizontal)
        clSld.setMinimum(1) # TODO this will depend of electrode spacing
        clSld.setMaximum(10)
        clSld.setValue(5)
        clGrid.addWidget(clSld, 0, 0, 1, 2)
        clGrid.addWidget(clFineLabel, 1,0,1,1)
        clGrid.addWidget(clCoarseLabel, 1,1,1,1)
        clFactorLabel = QLabel('Growth factor:')
#        clFactorEdit = QLineEdit()
#        clFactorEdit.setValidator(QDoubleValidator())
#        clFactorEdit.setText('2')
        clFactorSld = QSlider(Qt.Horizontal)
        clFactorSld.setMinimum(1)
        clFactorSld.setMaximum(10)
        clFactorSld.setValue(4)
  
        # additional options for tetrahedral mesh
        cl3Label = QLabel('Characteristic Length:')
        cl3Edit = QLineEdit()
        cl3Edit.setValidator(QDoubleValidator())
        cl3Edit.setText('-1')
        cl3FactorLabel = QLabel('Growth factor:')
        cl3FactorEdit = QLineEdit()
        cl3FactorEdit.setValidator(QDoubleValidator())
        cl3FactorEdit.setText('2')
        def openMeshParaviewFunc():
            print('Writing mesh to .vtk first...', end='')
            meshVTK = os.path.join(self.r2.dirname, 'mesh.vtk')
            self.r2.mesh.write_vtk(meshVTK)
            print('done')
            try:
                Popen(['paraview', meshVTK])
            except Exception as e:
                errorDump('Error opening Paraview:' + str(e))
        openMeshParaview = QPushButton('Open in Paraview')
        openMeshParaview.clicked.connect(openMeshParaviewFunc)
        
        def importCustomMeshFunc():
            fname, _ = QFileDialog.getOpenFileName(tabImportingData,'Open File', self.datadir)
            if fname != '':
                try:
                    self.r2.importMesh(fname)
                    mwMesh3D.plot(self.r2.showMesh, threed=True)
                    meshOutputStack.setCurrentIndex(2)
                except Exception as e:
                    errorDump('Error importing mesh' + str(e))
        importCustomMeshBtn = QPushButton('Import Custom Mesh')
        importCustomMeshBtn.clicked.connect(importCustomMeshFunc)
        
        # layout
        meshOptionQuadLayout = QHBoxLayout()
        meshOptionQuadLayout.addWidget(nnodesLabel)
#        meshOptionQuadLayout.addWidget(nnodesEdit)
        meshOptionQuadLayout.addWidget(nnodesSld)
        
        meshOptionTrianLayout = QHBoxLayout()
        meshOptionTrianLayout.addWidget(clLabel)
#        meshOptionTrianLayout.addWidget(clSld)
        meshOptionTrianLayout.addLayout(clGrid)
#        meshOptionTrianLayout.addWidget(clEdit)
        meshOptionTrianLayout.addWidget(clFactorLabel)
#        meshOptionTrianLayout.addWidget(clFactorEdit)
        meshOptionTrianLayout.addWidget(clFactorSld)

        meshOptionTetraLayout = QHBoxLayout()
        meshOptionTetraLayout.addWidget(cl3Label)
        meshOptionTetraLayout.addWidget(cl3Edit)
        meshOptionTetraLayout.addWidget(cl3FactorLabel)
        meshOptionTetraLayout.addWidget(cl3FactorEdit)
        meshOptionTetraLayout.addWidget(openMeshParaview)
        meshOptionTetraLayout.addWidget(importCustomMeshBtn)
        meshChoiceLayout = QHBoxLayout()
        meshQuadLayout = QVBoxLayout()
        meshTrianLayout = QVBoxLayout()
        meshTetraLayout = QVBoxLayout()
        meshQuadGroup = QGroupBox()
        meshQuadGroup.setStyleSheet("QGroupBox{padding-top:1em; margin-top:-1em}")
        meshTrianGroup = QGroupBox()
        meshTrianGroup.setStyleSheet("QGroupBox{padding-top:1em; margin-top:-1em}")
        meshTetraGroup = QGroupBox()
        meshTetraGroup.setStyleSheet("QGroupBox{padding-top:1em; margin-top:-1em}")
        
        meshQuadLayout.addLayout(meshOptionQuadLayout)
        meshQuadLayout.addWidget(meshQuad)
        meshQuadGroup.setLayout(meshQuadLayout)
        meshChoiceLayout.addWidget(meshQuadGroup)
        
        meshTrianLayout.addLayout(meshOptionTrianLayout)
        meshTrianLayout.addWidget(meshTrian)
        meshTrianGroup.setLayout(meshTrianLayout)
        meshChoiceLayout.addWidget(meshTrianGroup)
        
        meshTetraLayout.addLayout(meshOptionTetraLayout)
        meshTetraLayout.addWidget(meshTetra)
        meshTetraGroup.setLayout(meshTetraLayout)
        meshChoiceLayout.addWidget(meshTetraGroup)
        meshTetraGroup.setHidden(True)
        
        meshLayout.addLayout(meshChoiceLayout, 20)
        
        
        class RegionTable(QTableWidget):
            def __init__(self, nrow=1, ncol=4):
                super(RegionTable, self).__init__(nrow, ncol)
                self.nrow = nrow
                self.ncol = ncol
                self.setColumnCount(self.ncol)
                self.setRowCount(self.nrow)
                self.headers = ['|Z| [Ohm.m]', 'φ [mrad]', 'Zones', 'Fixed']
                self.setHorizontalHeaderLabels(self.headers)
                self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.setItem(0,0,QTableWidgetItem('100.0')) # resistivity [Ohm.m]
                self.setItem(0,1,QTableWidgetItem('0')) # phase [mrad]
                self.setItem(0,2,QTableWidgetItem('1')) # zone
                self.setCellWidget(0,3, QCheckBox())
                    
            def addRow(self):
                self.nrow = self.nrow + 1
                self.setRowCount(self.nrow)
                self.setItem(self.nrow-1, 0, QTableWidgetItem('100.0'))
                self.setItem(self.nrow-1, 1, QTableWidgetItem('0'))
                self.setItem(self.nrow-1, 2, QTableWidgetItem('1'))
                self.setCellWidget(self.nrow-1, 3, QCheckBox())
                
            def getTable(self):
                res0 = np.zeros(self.nrow)
                phase0 = np.zeros(self.nrow)
                zones = np.zeros(self.nrow, dtype=int)
                fixed = np.zeros(self.nrow, dtype=bool)
                for j in range(self.nrow):
                    res0[j] = float(self.item(j,0).text())
                    phase0[j] = float(self.item(j,1).text())
                    zones[j] = int(self.item(j,2).text())
                    fixed[j] = self.cellWidget(j,3).isChecked()
                return res0, phase0, zones, fixed
            
            def reset(self):
                self.nrow = 1
                self.setRowCount(1)
        
        
        instructionLabel = QLabel('To define a region, just click on the mesh'
           ' to draw a polygon. Close the polygon using a right click. Once done'
           ', you can define the region resistivity in the table. To define a'
           ' new region, just press \'e\'')
        instructionLabel.setWordWrap(True)
        meshLayout.addWidget(instructionLabel)
        
        mwMesh = MatplotlibWidget(navi=True)
        mwMesh3D = MatplotlibWidget(threed=True, navi=True)
        
        meshLogText = QTextEdit()
        meshLogText.setReadOnly(True)
        def meshLogTextFunc(text):
            cursor = meshLogText.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(text + '\n')
            meshLogText.ensureCursorVisible()
            QApplication.processEvents()
#            if len(text.split()) > 2:
#                if text.split()[2] == 'Stopped':
#                    meshOutputStack.setCurrentIndex(1) # switch to graph

        regionTable = RegionTable()
        regionTable.setColumnHidden(1, True)
        
        regionLayout = QVBoxLayout()
        regionLayout.addWidget(regionTable)
        
        meshPlot = QWidget()
        meshPlotLayout = QHBoxLayout()
        meshPlotLayout.addWidget(mwMesh, 70)
        meshPlotLayout.addLayout(regionLayout, 30)
        meshPlot.setLayout(meshPlotLayout)
        
        meshPlot3D = QWidget()
        meshPlot3DLayout = QHBoxLayout()
        meshPlot3DLayout.addWidget(mwMesh3D)
        meshPlot3D.setLayout(meshPlot3DLayout)
        
        meshOutputStack = QStackedLayout()
        meshOutputStack.addWidget(meshLogText)
        meshOutputStack.addWidget(meshPlot)
        meshOutputStack.addWidget(meshPlot3D)
        meshOutputStack.setCurrentIndex(0)
        
        meshLayout.addLayout(meshOutputStack, 80)
        
        
        # TODO add layout for 3D (button for automatic 3D generation+
        # matplotlib widget for visuallization) and otherbutton to import mesh?
        # and the possible a table to paste the note electrode relationship...)
        
        
        
        '''
        def changeValue(value):
            print(value)
            self.r2.createMesh(elemy=value)
            plotQuadMesh()
            
        def plotQuadMesh():
            print('plotQuadMesh')
            mwqm.plot(self.r2.mesh.show)
        
        def genQuadMesh():
            self.r2.createMesh()
            
        btn = QPushButton('QuadMesh')
        btn.clicked.connect(genQuadMesh)
        grid.addWidget(btn, 3, 0)
        
        sld = QSlider(Qt.Horizontal)
        sld.setGeometry(30, 40, 100, 30)
        sld.valueChanged[int].connect(changeValue)
        grid.addWidget(sld, 4, 0)
        
        mwqm = MatplotlibWidget(navi=True)
        grid.addWidget(mwqm, 5, 0)
        '''

        tabMesh.setLayout(meshLayout)
        
        #%% tab Forward model
        tabForward = QWidget()
        tabs.addTab(tabForward, 'Forward model')
        tabs.setTabEnabled(3, False)
        
        # add table for sequence generation
        seqLabel = QLabel('Define the number of skip and levels in the table.'
                          'Take into account the specifications of your instrument to'
                          ' obtain realistic simulation results. You can copy-paste '
                          'your custom sequence as well. '
                          '<b>Mouse over the sequence title for more help.</b>')
        seqLabel.setWordWrap(True)
        
        class SequenceTable(QTableWidget):
            def __init__(self, headers, selfInit=False):
                nrow, ncol = 10, len(headers)
                super(SequenceTable, self).__init__(nrow, ncol)
                self.nrow = nrow
                self.ncol = ncol
                self.selfInit = selfInit
                self.setColumnCount(self.ncol)
                self.setRowCount(self.nrow)
                self.headers = headers
                self.setHorizontalHeaderLabels(self.headers)
                self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#                self.setItem(0,0,QTableWidgetItem(''))
#                self.setItem(0,1,QTableWidgetItem(''))

            def addRow(self):
                self.nrow = self.nrow + 1
                self.setRowCount(self.nrow)
			
            def keyPressEvent(self, e):
                if (e.modifiers() == Qt.ControlModifier) & (e.key() == Qt.Key_V):
                    cell = self.selectedIndexes()[0]
                    c0, r0 = cell.column(), cell.row()
                    self.paste(c0, r0)
                elif e.modifiers() != Qt.ControlModifier: # start editing
#                    print('start editing...')
                    cell = self.selectedIndexes()[0]
                    c0, r0 = cell.column(), cell.row()
                    self.editItem(self.item(r0,c0))
                    
            def paste(self, c0=0, r0=0):
                # get clipboard
                text = QApplication.clipboard().text()
                # parse clipboard
                tt = []
                for row in text.split('\n'):
                    trow = row.split()
                    if len(trow) > 0:
                        tt.append(trow)
                tt = np.array(tt)

                if np.sum(tt.shape) > 0:
                    # get max row/columns
                    if self.selfInit is True:
                        self.initTable(tt)
                    else:
                        self.setTable(tt, c0, r0)
						
            def initTable(self, tt=None, headers=None):
                self.clear()
                if headers is not None:
                    self.headers = np.array(headers)
                self.ncol = len(self.headers)
                self.setColumnCount(len(self.headers))
                self.setHorizontalHeaderLabels(self.headers)
                self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                if tt is None:
                    tt = np.zeros((10,len(self.headers)-1))
                self.setRowCount(tt.shape[0])
                self.nrow = tt.shape[0]
                self.setTable(tt)
                
            def setTable(self, tt, c0=0, r0=0):
                # paste clipboard to qtableView
                for i in range(c0, min([self.ncol, c0+tt.shape[1]])):
                    for j in range(r0, min([self.nrow, r0+tt.shape[0]])):
                        self.setItem(j,i,QTableWidgetItem(str(tt[j-r0, i-c0])))
                
            def getTable(self):
                table = -np.ones((self.nrow, self.ncol), dtype=int)
                for i in range(self.ncol):
                    for j in range(self.nrow):
                        if self.item(j,i) is not None:
                            try:
                                table[j,i] = int(self.item(j,i).text())
                            except:
                                pass
                return table
            
            def reset(self):
                self.nrow = 1
                self.setRowCount(1)
        
        seqDipDipLabel = QLabel('Dipole-Dipole')
        seqDipDipLabel.setToolTip('<img src="image/dipdip.png">')
        seqDipDip = SequenceTable(['a','n'])
        seqDipDip.setItem(0,0,QTableWidgetItem('1')) #confuses user. user should define the sequence.
        seqDipDip.setItem(0,1,QTableWidgetItem('8'))
        
        seqWennerLabel = QLabel('Wenner')
        seqWennerLabel.setToolTip('<img src="image/wenner.png">')
#        pixmap = QPixmap('image/wenner.png').scaledToWidth(250)
#        seqWennerLabel.setPixmap(pixmap)
        
#        from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
#        seqWennerMap = QSvgWidget('image/proto.svg')
#        renderer = QSvgRenderer('image/proto.svg')
#        seqWennerLabel.resize(renderer.defaultSize())
        
        seqWenner = SequenceTable(['a'])
        
        seqSchlumLabel = QLabel('Schlumberger')
        seqSchlumLabel.setToolTip('<img src="image/schlum.png">')
        seqSchlum = SequenceTable(['a','n'])
        
        seqMultiLabel = QLabel('Multigradient')
        seqMultiLabel.setToolTip('<img src="image/gradient.png">')
        seqMulti = SequenceTable(['a','n','s'])
		
        seqCustomLabel = QLabel('Custom Sequence')
        seqCustomLabel.setToolTip('paste your custom sequence using ctrl+v in here\na: C+, b: C-, m: P+, n: P-')
        seqCustom = SequenceTable(['a','b','m','n'], selfInit=True)
        
        seqTables = {'dpdp1' : seqDipDip,
                     'wenner_alpha' : seqWenner,
                     'schlum1' : seqSchlum,
                     'multigrad' : seqMulti,
                     'custSeq' : seqCustom}
        
        seqs = [[seqDipDipLabel, seqDipDip],
                [seqWennerLabel, seqWenner],
                [seqSchlumLabel, seqSchlum],
                [seqMultiLabel, seqMulti],
                [seqCustomLabel, seqCustom]]
        
        def seqCreateFunc():
            if self.r2.elec is None:
                errorDump('Input electrode positions in the "Electrodes (XYZ/Topo)" tab first.')
                return
            else:
                self.r2.elec = elecTable.getTable()
            params = []
            counter = 0 #temp loop counter
            for key in seqTables:
                p = seqTables[key].getTable()
                ie = (p != -1).all(1)
                p = p[ie,:]
                if len(p) > 0:
                    if key == 'custSeq':
                        self.r2.sequence = seqCustom.getTable()
                        seq_typ = ' imported'
                    else:
                        for i in range(p.shape[0]):
                            params.append((key, *p[i,:]))
                else:
                    counter += 1
            print(params)
            print(counter)
            if params:
                self.r2.createSequence(params=params)
                seq_typ = ' generated'
                
            text_default = ''
            array_typ = ''
            if counter == 5: # creats a default DpDp1 if user doesn't specify the sequence
                self.r2.createSequence()
                text_default = 'Default '
                array_typ = ' Dipole - Dipole'
                seq_typ = ' generated'
                
            seqOutputLabel.setText(text_default + str(len(self.r2.sequence)) + array_typ + ' quadrupoles' + seq_typ)
        
        seqOutputLabel = QLabel('')
    
        # add noise possibility
        noiseLabel = QLabel('Resistivity noise [%]:')
        noiseEdit = QLineEdit('2')
        noiseEdit.setValidator(QDoubleValidator())
        
        # add IP noise
        noiseLabelIP = QLabel('Phase noise [mrad]:')
        noiseEditIP = QLineEdit('2')
        noiseEditIP.setValidator(QDoubleValidator())
        
        # add a forward button
        def forwardBtnFunc():
            if self.r2.mesh is None: # we need to create mesh to assign starting resistivity
                errorDump('Please specify a mesh and an initial model first.')
                return
            seqCreateFunc()
            forwardOutputStack.setCurrentIndex(0)
            forwardLogText.clear()
            QApplication.processEvents()
            # apply region for initial model
            
            x, phase0, zones, fixed = regionTable.getTable()
            regid = np.arange(len(x)) + 1 # region 0 doesn't exist
            self.r2.assignRes0(dict(zip(regid, x)),
                               dict(zip(regid, zones)),
                               dict(zip(regid, fixed)),
                               dict(zip(regid, phase0)))
            noise = float(noiseEdit.text()) / 100 #percentage to proportion
            noiseIP = float(noiseEditIP.text())
            self.r2.forward(noise=noise, noiseIP=noiseIP, iplot=False, dump=forwardLogTextFunc)
            forwardPseudo.plot(self.r2.surveys[0].pseudo)
            tabs.setTabEnabled(4, True)
            tabs.setTabEnabled(5, True)
            tabs.setTabEnabled(6, True)
            if self.r2.typ[0] == 'c':
                forwardPseudoIP.plot(self.r2.surveys[0].pseudoIP)
        forwardBtn = QPushButton('Forward Modelling')
        forwardBtn.setAutoDefault(True)
        forwardBtn.clicked.connect(forwardBtnFunc)
        forwardBtn.setStyleSheet('background-color: green')
                
        forwardPseudo = MatplotlibWidget(navi=True)
        forwardPseudoIP = MatplotlibWidget(navi=True)
        forwardPseudoIP.setVisible(False)
        
        forwardLogText = QTextEdit()
        forwardLogText.setReadOnly(True)
        def forwardLogTextFunc(text):
            cursor = forwardLogText.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(text + '\n')
            forwardLogText.ensureCursorVisible()
            QApplication.processEvents()
            if text == 'Forward modelling done.':
                forwardOutputStack.setCurrentIndex(1) # switch to graph

        
        # layout
        forwardLayout = QVBoxLayout()
        seqLayout = QHBoxLayout()
        noiseLayout = QHBoxLayout()
        
        for seq in seqs:
            qgroup = QGroupBox()
            qgroup.setStyleSheet("QGroupBox{padding-top:1em; margin-top:-1em}")
            qlayout = QVBoxLayout()
            for a in seq:
                qlayout.addWidget(a)
            qgroup.setLayout(qlayout)
            seqLayout.addWidget(qgroup)
        
        noiseLayout.addWidget(noiseLabel)
        noiseLayout.addWidget(noiseEdit)
        noiseLayout.addWidget(noiseLabelIP)
        noiseLayout.addWidget(noiseEditIP)
        noiseLayout.addWidget(seqOutputLabel)
        
        forwardLayout.addWidget(seqLabel, 5)
        forwardLayout.addLayout(seqLayout, 30)
        forwardLayout.addLayout(noiseLayout, 2)
        forwardLayout.addWidget(forwardBtn, 3)
        
        forwardPseudoLayout = QHBoxLayout()
        forwardPseudoLayout.addWidget(forwardPseudo)
        forwardPseudoLayout.addWidget(forwardPseudoIP)
        forwardPseudoIP.hide()
        
        forwardPseudos = QWidget()
        forwardPseudos.setLayout(forwardPseudoLayout)
        
        forwardOutputStack = QStackedLayout()
        forwardOutputStack.addWidget(forwardLogText)
        forwardOutputStack.addWidget(forwardPseudos)
        forwardOutputStack.setCurrentIndex(0)
        
        forwardLayout.addLayout(forwardOutputStack, 60)
        
        tabForward.setLayout(forwardLayout)
        
        #%% tab INVERSION SETTINGS
        tabInversionSettings = QTabWidget()
        tabs.addTab(tabInversionSettings, 'Inversion settings')
        tabs.setTabEnabled(4,False)

        # general tab
        generalSettings = QWidget()
        generalLayout = QHBoxLayout()
        invForm = QFormLayout()
        
        # advanced tab
        advancedSettings = QWidget()
        advancedLayout = QHBoxLayout()
        advForm = QFormLayout()
        
#        def showIpOptions(arg):
#            opts = [c_wgt, c_wgtLabel, d_wgt, d_wgtLabel,
#                    singular_type, singular_typeLabel,
#                    res_matrix, res_matrixLabel]
#            activeState = np.array([1, 1, 1, 1, 0, 0, 0, 0], dtype=bool)
#            if arg == True:
#                iopts = activeState
#            else:
#                iopts = ~activeState
#            [o.setVisible(io) for o, io in zip(opts, iopts)]
        def showIpOptions(arg):
            if arg == True:
                a_wgt.setText('0.02')
                b_wgt.setText('2')
                if self.r2.iForward is False:
                    if 'magErr' in self.r2.surveys[0].df.columns:
                        a_wgt.setText('0.0')
                        b_wgt.setText('0.0')
                if self.r2.typ == 'cR3t':
                    c_wgt.setText('1')
                    c_wgt.setVisible(True)
                    c_wgtLabel.setVisible(True)
                min_error.setVisible(True)
                min_errorLabel.setVisible(True)
                data_type.setVisible(False)
                data_typeLabel.setVisible(False)
            else:
                a_wgt.setText('0.01')
                b_wgt.setText('0.02')
                if self.r2.typ == 'cR3t':
                    c_wgt.setVisible(False)
                    c_wgtLabel.setVisible(False)
                min_error.setVisible(False)
                min_errorLabel.setVisible(False)
                data_type.setVisible(True)
                data_typeLabel.setVisible(True)
        
        def show3DOptions(arg):
            settings3D = [no_improveLabel, no_improve,
                          inv_type3DLabel, inv_type3D,
                          alpha_sLabel, alpha_s,
                          cginv_toleranceLabel, cginv_tolerance,
                          cginv_maxitsLabel, cginv_maxits,
                          alpha_maxLabel, alpha_max,
                          num_alpha_stepsLabel, num_alpha_steps,
                          min_stepLabel, min_step]
            settings2D = [flux_typeLabel, flux_type,
                          inv_typeLabel, inv_type,
                          min_errorLabel, min_error,
                          reg_modeLabel, reg_mode,
                          rho_minLabel, rho_min,
                          rho_maxLabel, rho_max,
                          target_decreaseLabel, target_decrease]
            if arg is True:
                [s.setVisible(True) for s in settings3D]
                [s.setVisible(False) for s in settings2D]                
            else:
                [s.setVisible(False) for s in settings3D]
                [s.setVisible(True) for s in settings2D]
        
        # help sections
        def showHelp(arg): # for general tab
            if arg not in r2help:
                helpSection.setText('SORRY NOT IN HELP')
            else:
                helpSection.setHtml(r2help[arg])
        
        def showHelp2(arg): # for advanced tab
            if arg not in r2help:
                helpSection2.setText('SORRY NOT IN HELP')
            else:
                helpSection2.setHtml(r2help[arg])
        
        
#        def job_typeFunc(index):
#            self.r2.param['job_type'] = index
#        job_type = QComboBox()
#        job_type.addItem('Inversion [1]')
#        job_type.addItem('Forward [0]')
#        job_type.currentIndexChanged.connect(job_typeFunc)
#        invForm.addRow(QLabel('Job Type:'), job_type)
        
        self.parallel = False
        def parallelFunc(state):
            if state == Qt.Checked:
                self.parallel = True
            else:
                self.parallel = False
        parallelLabel = QLabel('<a href="parallel">Parallel inversion</a>')
        parallelLabel.linkActivated.connect(showHelp2)
        parallelCheck = QCheckBox()
        parallelCheck.stateChanged.connect(parallelFunc)
        advForm.addRow(parallelLabel, parallelCheck)
        
        def modErrFunc(state):
            if state == Qt.Checked:
                self.modErr = True
            else:
                self.modErr = False
        modErrLabel = QLabel('<a href="modErr">Compute Modelling Error</a>')
        modErrLabel.linkActivated.connect(showHelp2)
        modErr = QCheckBox()
        modErr.stateChanged.connect(modErrFunc)
        advForm.addRow(modErrLabel, modErr)
        self.modErr = False
        
        def notCroppingFunc(state):
            if state == Qt.Checked:
                self.iCropping = False
                if 'num_xy_poly' in self.r2.param:
                    self.num_xy_poly = self.r2.param['num_xy_poly'] # store value
            else:
                self.iCropping = True # default
                if ('num_xy_poly' in self.r2.param) and (self.num_xy_poly is not None):
                    self.r2.param['num_xy_poly'] = self.num_xy_poly # restore value
        notCroppingLabel = QLabel('<a href="notCropping">Do not crop the output vtk</a>')
        notCroppingLabel.linkActivated.connect(showHelp2)
        notCropping = QCheckBox()
        notCropping.stateChanged.connect(notCroppingFunc)
        advForm.addRow(notCroppingLabel, notCropping)
        
        def flux_typeFunc(index):
            if index == 0:
                self.r2.param['flux_type'] = 3
            else:
                self.r2.param['flux_type'] = 2
        flux_typeLabel = QLabel('<a href="flux_type">Flux Type</a>:')
        flux_typeLabel.linkActivated.connect(showHelp)
        flux_type = QComboBox()
        flux_type.addItem('3D')
        flux_type.addItem('2D')
        flux_type.currentIndexChanged.connect(flux_typeFunc)
        invForm.addRow(flux_typeLabel, flux_type)
        
        def singular_typeFunc(state):
            if state == Qt.Checked:
                self.r2.param['singular_type'] = 1
            else:
                self.r2.param['singular_type'] = 0
        singular_typeLabel = QLabel('<a href="singular_type">Remove Singularity</a>')
        singular_typeLabel.linkActivated.connect(showHelp)
        singular_type = QCheckBox()
        singular_type.stateChanged.connect(singular_typeFunc)
        invForm.addRow(singular_typeLabel, singular_type)
        
        def res_matrixFunc(index):
            self.r2.param['res_matrix'] = index
        res_matrixLabel = QLabel('<a href="res_matrix">Value for <code>res_matrix</code><a/>')
        res_matrixLabel.linkActivated.connect(showHelp2)
        res_matrix = QComboBox()
        res_matrix.addItem('No sensisitivity/resolution matrix [0]')
        res_matrix.addItem('Sensitivity matrix [1]')
        res_matrix.addItem('True Resolution Matrix [2]')
        res_matrix.addItem('Sensitivity map [3]')
        res_matrix.setCurrentIndex(1)
        res_matrix.currentIndexChanged.connect(res_matrixFunc)
        advForm.addRow(res_matrixLabel, res_matrix)
        
        def scaleFunc():
            self.r2.param['scale'] = float(scale.text())
        scaleLabel = QLabel('<a href="scale"> Scale for triangular mesh</a>:')
        scaleLabel.linkActivated.connect(showHelp)
        scaleLabel.setVisible(False)
        scale = QLineEdit()
        scale.setValidator(QDoubleValidator())
        scale.setText('1.0')
        scale.editingFinished.connect(scaleFunc)
        scale.setVisible(False)
        invForm.addRow(scaleLabel, scale)
        
        # put in adv
        def patch_size_xFunc():
            self.r2.param['patch_size_x'] = int(patch_size_x.text())
        patch_size_xLabel = QLabel('<a href="patch">Patch size x<a/>:')
        patch_size_xLabel.linkActivated.connect(showHelp2)
        patch_size_x = QLineEdit()
        patch_size_x.setValidator(QIntValidator())
        patch_size_x.setText('1')
        patch_size_x.editingFinished.connect(patch_size_xFunc)
        advForm.addRow(patch_size_xLabel, patch_size_x)

        # put in adv
        def patch_size_yFunc():
            self.r2.param['patch_size_y'] = int(patch_size_y.text())
        patch_size_yLabel = QLabel('<a href="patch">Patch size y<a/>:')
        patch_size_yLabel.linkActivated.connect(showHelp2)
        patch_size_y = QLineEdit()
        patch_size_y.setValidator(QIntValidator())
        patch_size_y.setText('1')
        patch_size_y.editingFinished.connect(patch_size_yFunc)
        advForm.addRow(patch_size_yLabel, patch_size_y)
        
        def inv_typeFunc(index):
            self.r2.param['inverse_type'] = index
            opts = [data_typeLabel, data_type,
                    reg_modeLabel, reg_mode,
                    toleranceLabel, tolerance,
                    max_iterationsLabel, max_iterations,
                    error_modLabel, error_mod,
                    alpha_anisoLabel, alpha_aniso,
                    a_wgtLabel, a_wgt,
                    b_wgtLabel, b_wgt]
            if index == 3: # qualitative solution
                [o.setVisible(False) for o in opts]
            else:
                [o.setVisible(True) for o in opts]
        inv_typeLabel = QLabel('<a href="inverse_type">Inversion Type</a>:')
        inv_typeLabel.linkActivated.connect(showHelp)
        inv_type = QComboBox()
        inv_type.addItem('Pseudo Marquardt [0]')
        inv_type.addItem('Regularized Inversion with Linear Filtering [1]')
        inv_type.addItem('Regularized Inversion with Quadratic Filtering [2]')
        inv_type.addItem('Qualitative Solution [3]')
        inv_type.addItem('Blocked Linear Regularized Inversion [4]')
        inv_type.setCurrentIndex(1)
        inv_type.currentIndexChanged.connect(inv_typeFunc)
        invForm.addRow(inv_typeLabel, inv_type)
        
        def inv_type3DFunc(index):
            self.param['inverse_type'] = index
            if index > 0:
                alpha_sLabel.setVisible(True)
                alpha_s.setVisible(True)
            else:
                alpha_sLabel.setVisible(False)
                alpha_s.setVisible(False)
        inv_type3DLabel = QLabel('<a href="inv_type3D">Inversion Type</a>:')
        inv_type3DLabel.linkActivated.connect(showHelp)
        inv_type3D = QComboBox()
        inv_type3D.addItem('Normal Regularisation [0]')
        inv_type3D.addItem('Background Regularisation [1]')
        inv_type3D.addItem('Difference Regularisation [2]')
        inv_type3D.currentIndexChanged.connect(inv_type3DFunc)
        invForm.addRow(inv_type3DLabel, inv_type3D)
        inv_type3DLabel.setVisible(False)
        inv_type3D.setVisible(False)
        
        def data_typeFunc(index):
            self.r2.param['data_type'] = index
        data_typeLabel = QLabel('<a href="data_type">Data type</a>:')
        data_typeLabel.linkActivated.connect(showHelp)
        data_type = QComboBox()
        data_type.addItem('Normal [0]')
        data_type.addItem('Logarithmic [1]')
        data_type.setCurrentIndex(1)
        data_type.currentIndexChanged.connect(data_typeFunc)
        invForm.addRow(data_typeLabel, data_type)
        
        def reg_modeFunc(index):
            self.r2.param['reg_mode'] = index
        reg_modeLabel = QLabel('<a href="reg_mode">Regularization mode</a>:')
        reg_modeLabel.linkActivated.connect(showHelp)
        reg_mode = QComboBox()
        reg_mode.addItem('Normal regularization [0]')
        reg_mode.addItem('Regularization from initial model [1]')
        reg_mode.addItem('Regularization from difference inversion [2]')
        reg_mode.currentIndexChanged.connect(reg_modeFunc)
        invForm.addRow(reg_modeLabel, reg_mode)
        
        def toleranceFunc():
            self.r2.param['tolerance'] = float(tolerance.text())
        toleranceLabel = QLabel('<a href="tolerance">Value for tolerance</a>:')
        toleranceLabel.linkActivated.connect(showHelp)
        tolerance = QLineEdit()
        tolerance.setValidator(QDoubleValidator())
        tolerance.setText('1.0')
        tolerance.editingFinished.connect(toleranceFunc)
        invForm.addRow(toleranceLabel, tolerance)
        
        def no_improveFunc():
            self.r2.param['no_improve'] = float(no_improve.text())
        no_improveLabel = QLabel('<a href="no_improve">Stop criteria</a>')
        no_improveLabel.linkActivated.connect(showHelp)
        no_improve = QLineEdit()
        no_improve.setValidator(QDoubleValidator())
        no_improve.setText('1.0')
        no_improve.editingFinished.connect(no_improveFunc)
        invForm.addRow(no_improveLabel, no_improve)
        no_improveLabel.setVisible(False)
        no_improve.setVisible(False)
        
        def max_iterationsFunc():
            self.r2.param['max_iter'] = int(max_iterations.text())
        max_iterationsLabel = QLabel('<a href="max_iterations">Maximum number of iterations</a>:')
        max_iterationsLabel.linkActivated.connect(showHelp)
        max_iterations = QLineEdit()
        max_iterations.setValidator(QIntValidator())
        max_iterations.setText('10')
        max_iterations.editingFinished.connect(max_iterationsFunc)
        invForm.addRow(max_iterationsLabel, max_iterations)
        
        def error_modFunc(index):
            self.r2.param['error_mod'] = index
        error_modLabel = QLabel('<a href="error_mod">Update the weights</a>:')
        error_modLabel.linkActivated.connect(showHelp2)
        error_mod = QComboBox()
        error_mod.addItem('Keep the same weights [0]')
        error_mod.addItem('Update the weights [1]')
        error_mod.addItem('Update the weights (recommended) [2]')
        error_mod.setCurrentIndex(2)
        error_mod.currentIndexChanged.connect(error_modFunc)
        advForm.addRow(error_modLabel, error_mod)
        
        
#        def createLabel(helpTag, title): # doesn't seem to work
#            ql = QLabel('<a href="' + helpTag + '>' + title + '</a>:')
#            ql.linkActivated.connect(showHelp)
#            return ql

        def alpha_anisoFunc():
            self.r2.param['alpha_aniso'] = float(alpha_aniso.text())
        alpha_anisoLabel = QLabel('<a href="alpha_aniso">Value for <code>alpha_aniso</code></a>:')
        alpha_anisoLabel.linkActivated.connect(showHelp2)
        alpha_aniso = QLineEdit()
        alpha_aniso.setValidator(QDoubleValidator())
        alpha_aniso.setText('1.0')
        alpha_aniso.editingFinished.connect(alpha_anisoFunc)
        advForm.addRow(alpha_anisoLabel, alpha_aniso)
        
        def alpha_sFunc():
            self.r2.param['alpha_s'] = float(alpha_s.text())
        alpha_sLabel = QLabel('<a href="alpha_s"><code>alpha_s</code></a>:')
        alpha_sLabel.linkActivated.connect(showHelp2)
        alpha_s = QLineEdit()
        alpha_s.setValidator(QDoubleValidator())
        alpha_s.setText('1.0')
        alpha_s.editingFinished.connect(alpha_sFunc)
        advForm.addRow(alpha_sLabel, alpha_s)
        alpha_sLabel.setVisible(False)
        alpha_s.setVisible(False)
        
        def cginv_toleranceFunc():
            self.r2.param['cginv_tolerance'] = float(cginv_tolerance.text())
        cginv_toleranceLabel = QLabel('<a href="cginv_tolerance"><code>cginv_tolerance</code></a>:')
        cginv_toleranceLabel.linkActivated.connect(showHelp2)
        cginv_tolerance = QLineEdit()
        cginv_tolerance.setValidator(QDoubleValidator())
        cginv_tolerance.setText('0.0001')
        cginv_tolerance.editingFinished.connect(cginv_toleranceFunc)
        advForm.addRow(cginv_toleranceLabel, cginv_tolerance)
        cginv_toleranceLabel.setVisible(False)
        cginv_tolerance.setVisible(False)
        
        def cginv_maxitsFunc():
            self.r2.param['cginv_maxits'] = int(cginv_maxits.text())
        cginv_maxitsLabel = QLabel('<a href="cginv_maxits"><code>cginv_maxits</code></a>:')
        cginv_maxitsLabel.linkActivated.connect(showHelp2)
        cginv_maxits = QLineEdit()
        cginv_maxits.setValidator(QDoubleValidator())
        cginv_maxits.setText('500')
        cginv_maxits.editingFinished.connect(cginv_maxitsFunc)
        advForm.addRow(cginv_maxitsLabel, cginv_maxits)
        cginv_maxitsLabel.setVisible(False)
        cginv_maxits.setVisible(False)
        
        def alpha_maxFunc():
            self.r2.param['alpha_max'] = float(alpha_max.text())
        alpha_maxLabel = QLabel('<a href="alpha_max">Maximum alpha</a>:')
        alpha_maxLabel.linkActivated.connect(showHelp2)
        alpha_max = QLineEdit()
        alpha_max.setValidator(QIntValidator())
        alpha_max.setText('1.0')
        alpha_max.editingFinished.connect(alpha_maxFunc)
        advForm.addRow(alpha_maxLabel, alpha_max)
        alpha_maxLabel.setVisible(False)
        alpha_max.setVisible(False)
        
        def num_alpha_stepsFunc():
            self.r2.param['num_alpha_steps'] = float(num_alpha_steps.text())
        num_alpha_stepsLabel = QLabel('<a href="alpha_max">Number of alpha steps</a>:')
        num_alpha_stepsLabel.linkActivated.connect(showHelp2)
        num_alpha_steps = QLineEdit()
        num_alpha_steps.setValidator(QDoubleValidator())
        num_alpha_steps.setText('10')
        num_alpha_steps.editingFinished.connect(num_alpha_stepsFunc)
        advForm.addRow(num_alpha_stepsLabel, num_alpha_steps)
        num_alpha_stepsLabel.setVisible(False)
        num_alpha_steps.setVisible(False)
        
        def min_stepFunc():
            self.r2.param['min_step'] = float(min_step.text())
        min_stepLabel = QLabel('<a href="min_step">Minimium Step Length</a>:')
        min_stepLabel.linkActivated.connect(showHelp2)
        min_step = QLineEdit()
        min_step.setValidator(QDoubleValidator())
        min_step.setText('0.001')
        min_step.editingFinished.connect(min_stepFunc)
        advForm.addRow(min_stepLabel, min_step)
        min_stepLabel.setVisible(False)
        min_step.setVisible(False)
        
        def min_errorFunc():
            self.r2.param['min_error'] = float(min_error.text())
        min_errorLabel = QLabel('<a href="errorParam"><code>min_error</code></a>:')
        min_errorLabel.linkActivated.connect(showHelp)
        min_errorLabel.setVisible(False)
        min_error = QLineEdit()
        min_error.setText('0.01')
        min_error.editingFinished.connect(min_errorFunc)
        min_error.setVisible(False)
        invForm.addRow(min_errorLabel, min_error)
        
        def a_wgtFunc():
            self.r2.param['a_wgt'] = float(a_wgt.text())
        a_wgtLabel = QLabel('<a href="errorParam"><code>a_wgt</code></a>:')
        a_wgtLabel.linkActivated.connect(showHelp)
        a_wgt = QLineEdit()
        a_wgt.setValidator(QDoubleValidator())
        a_wgt.setText('0.01')
        a_wgt.editingFinished.connect(a_wgtFunc)
        invForm.addRow(a_wgtLabel, a_wgt)
        
        def b_wgtFunc():
            self.r2.param['b_wgt'] = float(b_wgt.text())
        b_wgtLabel = QLabel('<a href="errorParam"><code>b_wgt</code></a>:')
        b_wgtLabel.linkActivated.connect(showHelp)
        b_wgt = QLineEdit()
        b_wgt.setValidator(QDoubleValidator())
        b_wgt.setText('0.02')
        b_wgt.editingFinished.connect(b_wgtFunc)
        invForm.addRow(b_wgtLabel, b_wgt)
        
        def c_wgtFunc():
            self.r2.param['c_wgt'] = float(c_wgt.text())
        c_wgtLabel = QLabel('<a href="errorParam"><code>c_wgt</code></a>:')
        c_wgtLabel.linkActivated.connect(showHelp)
        c_wgtLabel.setVisible(False)
        c_wgt = QLineEdit()
        c_wgt.setValidator(QDoubleValidator())
        c_wgt.setText('1')
        c_wgt.editingFinished.connect(c_wgtFunc)
        c_wgt.setVisible(False)
        invForm.addRow(c_wgtLabel, c_wgt)
#        
#        def d_wgtFunc():
#            self.r2.param['d_wgt'] = float(d_wgt.text())
#        d_wgtLabel = QLabel('<a href="errorParam"><code>d_wgt</code></a>:')
#        d_wgtLabel.linkActivated.connect(showHelp)
#        d_wgtLabel.setVisible(False)
#        d_wgt = QLineEdit()
#        d_wgt.setValidator(QDoubleValidator())
#        d_wgt.setText('2')
#        d_wgt.editingFinished.connect(d_wgtFunc)
#        d_wgt.setVisible(False)
#        invForm.addRow(d_wgtLabel, d_wgt)
        
        def rho_minFunc():
            self.r2.param['rho_min'] = float(rho_min.text())
        rho_minLabel = QLabel('<a href="errorParam">Minimum apparent resistivity</a>:')
        rho_minLabel.linkActivated.connect(showHelp)
        rho_min = QLineEdit()
        rho_min.setValidator(QDoubleValidator())
        rho_min.setText('-1000')
        rho_min.editingFinished.connect(rho_minFunc)
        invForm.addRow(rho_minLabel, rho_min)

        def rho_maxFunc():
            self.r2.param['rho_max'] = float(rho_max.text())
        rho_maxLabel = QLabel('<a href="errorParam">Maximum apparent resistivity</a>:')
        rho_maxLabel.linkActivated.connect(showHelp)
        rho_max = QLineEdit()
        rho_max.setValidator(QDoubleValidator())
        rho_max.setText('1000')
        rho_max.editingFinished.connect(rho_maxFunc)
        invForm.addRow(rho_maxLabel, rho_max)        
        
        def target_decreaseFunc():
            self.r2.param['target_decrease'] = float(target_decrease.text())
        target_decreaseLabel = QLabel('<a href="target_decrease">Target decrease</a>:')
        target_decreaseLabel.linkActivated.connect(showHelp)
        target_decrease = QLineEdit()
        target_decrease.setValidator(QDoubleValidator())
        target_decrease.setText('0')
        target_decrease.editingFinished.connect(target_decreaseFunc)
        invForm.addRow(target_decreaseLabel, target_decrease)
                
        
        generalLayout.addLayout(invForm)
        
        helpSection = QTextEdit('Help will be display here')
        helpSection.setReadOnly(True)
        helpSection.setText('Click on the labels and help will be displayed here')
        generalLayout.addWidget(helpSection)
        
        generalSettings.setLayout(generalLayout)
        tabInversionSettings.addTab(generalSettings, 'General')
        
        
        advancedLayout.addLayout(advForm)
        
        helpSection2 = QTextEdit('Help will be display here')
        helpSection2.setReadOnly(True)
        helpSection2.setText('Click on the labels and help will be displayed here')
        advancedLayout.addWidget(helpSection2)
        
        advancedSettings.setLayout(advancedLayout)
        tabInversionSettings.addTab(advancedSettings, 'Advanced')

        
        #%% tab 5 INVERSION
        
        tabInversion = QWidget()
#        tabInversion.setStyleSheet('background-color:red')
        tabs.addTab(tabInversion, '&Inversion')
        tabs.setTabEnabled(5, False)
        
        invLayout = QVBoxLayout()

#        def callback(ax):
#            ax.plot(np.random.randn(20,5), '*-')
#            ax.set_title('Random data')
#        
#        def updateGraph():
#            mw.plot(callback)
#
#        btn = QPushButton('Draw random sample')
#        btn.clicked.connect(updateGraph)
#        mw = MatplotlibWidget()
#        
#        grid.addWidget(btn, 1, 0)
#        grid.addWidget(mw, 2, 0)
        
        self.pindex = 0
        self.rms = []
        self.rmsIndex = []
        self.rmsIP = []
        self.rmsIndexIP = []
        self.inversionOutput = ''
        self.end = False
        
        def parseRMS(tt):
            newFlag = False
            if len(tt) > 1:
                for i in range(len(tt)):
                    a = tt[i].split()
                    if len(a) > 0:
                        if a[0] == 'Initial':
                            try:
                                newFlag = True
                                self.rms.append(float(a[3]))
                                self.rmsIndex.append(self.pindex)
                            except ValueError as e:
                                print('parseRMS error:', e)
                                pass
                            if a[1] == 'Phase':
                                self.rmsIP.append(float(a[4]))
                                self.rmsIndexIP.append(self.pindex)
                        if a[0] == 'Processing':
                            self.pindex = self.pindex + 1
                        if a[0] == 'End':
                            self.end = True
                        if a[0] == 'Iteration':
                            mwInvResult.plot(self.r2.showIter)
            return newFlag

        def plotRMS(ax):
            if len(self.rms) > 0:
                rms = np.array(self.rms)
                rmsIndex = np.array(self.rmsIndex)
                xx = np.arange(len(rms))
                iindex = np.unique(rmsIndex)
#                    print('iidnex', iindex)
                for ii in iindex:
                    ie = rmsIndex == ii
                    ax.plot(xx[ie], rms[ie], 'o-')
            if len(self.rmsIP) > 0:
                rms = np.array(self.rmsIP)
                rmsIndex = np.array(self.rmsIndexIP)
                xx = np.arange(len(rms))
                iindex = np.unique(rmsIndex)
#                    print('iidnex', iindex)
#                    ax.axvline(xx[0]-0.5)
                ax.set_prop_cycle(None)
                for ii in iindex:
                    ie = rmsIndex == ii
                    ax.plot(xx[ie], rms[ie], '*--')
                        
            ax.set_xticks([])
            ax.set_xticklabels([],[])
            ax.set_xlabel('Iterations', fontsize=8)
            ax.tick_params(axis='both', which='major', labelsize=8)
            ax.set_ylabel('RMS', fontsize=8)
#            ax.figure.tight_layout()
                
        # run R2
#        def dataReady():
#            cursor = logText.textCursor()
#            cursor.movePosition(cursor.End)
#            text = str(self.processes[-1].readAll(), 'utf-8')
#            cursor.insertText(text)
#            logText.ensureCursorVisible()
#
#            # plot RMS graph
#            text = self.inversionOutput
#            tt = text.split('\n')
#            newFlag = parseRMS(tt)
#            if newFlag:
#                mwRMS.plot(plotRMS)
#        
#        self.processes = []
        
#        def runR2(dirname=''):
#            # run R2
#            if dirname == '':
#                dirname = self.r2.dirname
#            exeName = self.r2.typ + '.exe'
#            if frozen == 'not':
#                shutil.copy(os.path.join('api','exe', exeName),
#                    os.path.join(dirname, exeName))
#            else:
#                shutil.copy(os.path.join(bundle_dir, 'api', 'exe', exeName),
#                    os.path.join(dirname, exeName))
#            process = QProcess(self)
#            process.setWorkingDirectory(dirname)
#            # QProcess emits `readyRead` when there is data to be read
#            process.readyRead.connect(dataReady)
#            if OS == 'Linux':
#                process.start('wine ' + exeName)
#            else:
#                wdpath = "\"" + os.path.join(self.r2.dirname, exeName).replace('\\','/') + "\""
#                print('wdpath = ', wdpath)
#                try:
#                    process.start(wdpath) # need absolute path and escape quotes (if space in the path)
#                except Exception as e:
#                    print(e)
#                    pass
#            self.processes.append(process)
        
        def logInversion():
            self.end = False
            outStackLayout.setCurrentIndex(0)
            mwInvResult.clear()
            self.r2.param['lineTitle'] = titleEdit.text()
            if self.r2.mesh is None:
                meshQuadFunc() # generate default mesh

            def func(text):
#                print('t', text)
                self.inversionOutput = text + '\n'
                cursor = logText.textCursor()
                cursor.movePosition(cursor.End)
                cursor.insertText(text+'\n')
                logText.ensureCursorVisible()
                # plot RMS graph
                text = self.inversionOutput
                tt = text.split('\n')
                newFlag = parseRMS(tt)
                if newFlag:
                    mwRMS.plot(plotRMS)
                QApplication.processEvents()
            
            def funcLogOnly(text): #for // processing
                self.inversionOutput = text + '\n'
                cursor = logText.textCursor()
                cursor.movePosition(cursor.End)
                cursor.insertText(text+'\n')
                logText.ensureCursorVisible()
                QApplication.processEvents()
            
            # don't crop the mesh if that's what we'e chosen
            if self.iCropping is True:
                if self.num_xy_poly is not None:
                    self.r2.param['num_xy_poly'] = self.num_xy_poly
            else:
                self.r2.param['num_xy_poly'] = 0
            
            # apply region for initial model
            if self.r2.mesh is None: # we need to create mesh to assign starting resistivity
                self.r2.createMesh()
            x, phase0, zones, fixed = regionTable.getTable()
            regid = np.arange(len(x)) + 1 # 1 is the background (no 0)
            self.r2.assignRes0(dict(zip(regid, x)),
                               dict(zip(regid, zones)),
                               dict(zip(regid, fixed)),
                               dict(zip(regid, phase0)))
            
#            f = print if self.parallel is True else func
            if self.parallel is True:
                self.r2.invert(iplot=False, dump=print, parallel=True)
                with open(os.path.join(self.r2.dirname, self.r2.typ + '.out'),'r') as f:
                    text = f.read()
                func(text)
            else:
                self.r2.invert(iplot=False, dump=func, modErr=self.modErr)#, parallel=self.parallel)
            self.r2.proc = None
            try:
                sectionId.currentIndexChanged.disconnect()
                sectionId.clear()
            except:
#                print('no method connected to sectionId yet')
                pass
            
            # displaying results or error
            def printR2out():
                print('--------INVERSION FAILED--------')
                outStackLayout.setCurrentIndex(1)
                with open(os.path.join(self.r2.dirname, self.r2.typ + '.out'),'r') as f:
                    text = f.read()
                r2outEdit.setText(text)
                btnInvert.setText('Invert')
                btnInvert.setStyleSheet("background-color: green")
                btnInvert.clicked.disconnect()
                btnInvert.clicked.connect(btnInvertFunc)
                frozeUI(False)
                
           
            if self.end is True:
                try:
                    # this could failed if we invert homogeneous model -> vtk
                    #file size = 0 -> R2.getResults() -> vtk_import failed
                    plotSection()
                    if self.iForward is True:
                        sectionId.addItem('Initial Model')
                    for i in range(len(self.r2.surveys)):
                        sectionId.addItem(self.r2.surveys[i].name)
                    outStackLayout.setCurrentIndex(0)
                    showDisplayOptions(True)
                    btnInvert.setText('Invert')
                    btnInvert.setStyleSheet("background-color: green")
                    btnInvert.clicked.disconnect()
                    btnInvert.clicked.connect(btnInvertFunc)
                    frozeUI(False)
                    if self.iForward is True:
                        sectionId.setCurrentIndex(1)
                except Exception as e:
                    print('Error when plotting:', e)
                    pass
                    printR2out()
                    
            else:
                printR2out()
                
                
        def plotSection():
            if self.r2.typ[-1] == '2': # 2D
                mwInvResult.setCallback(self.r2.showResults)
                resultStackLayout.setCurrentIndex(0)
            else:
                mwInvResult3D.setCallback(self.r2.showResults)
                resultStackLayout.setCurrentIndex(1)
#                mwInvResult.setCallback(self.r2.showSlice)
            if self.r2.iBorehole is False:
                try:
                    plotInvError()
                except Exception as e:
                    print('plotInvError FAILED:', e)
                    pass
            try:
                plotInvError2()
            except Exception as e:
                errorDump(e)
                pass
            if self.r2.typ[0] != 'c':
                defaultAttr = 'Resistivity(log10)'
            if self.r2.typ[0] == 'c':
                defaultAttr = 'Sigma_real(log10)'
            self.displayParams = {'index':0,'edge_color':'none',
                                  'sens':True, 'attr':defaultAttr,
                                  'contour':False, 'vmin':None, 'vmax':None}
            contourCheck.setChecked(False)
            sensCheck.setChecked(True)
            edgeCheck.setChecked(False)
            vminEdit.setText('')
            vmaxEdit.setText('')
            self.r2.getResults()
            displayAttribute(arg=defaultAttr)
            # graph will be plotted because changeSection will be called
            sectionId.currentIndexChanged.connect(changeSection)
#            attributeName.currentIndexChanged.connect(changeAttribute)
                
        
        def replotSection(): # main plotting function
            index = self.displayParams['index']
            edge_color = self.displayParams['edge_color']
            sens = self.displayParams['sens']
            attr = self.displayParams['attr']
            contour = self.displayParams['contour']
            vmin = self.displayParams['vmin']
            vmax = self.displayParams['vmax']
            if self.r2.typ[-1] == '2':
                mwInvResult.replot(threed=False, index=index, edge_color=edge_color,
                                   contour=contour, sens=sens, attr=attr,
                                   vmin=vmin, vmax=vmax)
            else:
                mwInvResult3D.replot(threed=True, index=index, attr=attr,
                                     vmin=vmin, vmax=vmax)
                    
        def msgBox(text):
            msg = QMessageBox()
            msg.setText(text)
            
        def setCBarLimit():
            vmax = vmaxEdit.text()
            vmin = vminEdit.text()
            vmax = None if vmax == '' else float(vmax)
            vmin = None if vmin == '' else float(vmin)
            self.displayParams['vmin'] = vmin
            self.displayParams['vmax'] = vmax
            if (contourCheck.isChecked() is True) or (self.r2.typ[-1] != '2'):
                replotSection()
            else:
                mwInvResult.setMinMax(vmin=vmin, vmax=vmax) 
        
        def frozeUI(val=True): # when inversion is running
            n = tabs.count()
            if val == True: # froze them
                showDisplayOptions(False)
                self.tabState = np.array([tabs.isTabEnabled(i) for i in range(n)])
                for i in range(n):
                    if i != 5:
                        tabs.setTabEnabled(i, False)
            else: # unfrozing
                for i in range(n):
                    tabs.setTabEnabled(i, self.tabState[i])
        
        def btnInvertFunc():
            frozeUI()
            btnInvert.setText('Kill')
            btnInvert.setStyleSheet("background-color: red")
            btnInvert.clicked.disconnect()
            btnInvert.clicked.connect(btnKillFunc)
            QApplication.processEvents()
            logInversion()
            
        def btnKillFunc():
            if self.r2.proc is not None:
                btnInvert.setText('Invert')
                btnInvert.setStyleSheet("background-color: green")
                btnInvert.clicked.disconnect()
                btnInvert.clicked.connect(btnInvertFunc)
                QApplication.processEvents()
                self.r2.proc.kill()
                frozeUI(False)

        btnInvert = QPushButton('Invert')
        btnInvert.setStyleSheet("background-color: green")
        btnInvert.setAutoDefault(True)
        btnInvert.clicked.connect(btnInvertFunc)
        btnInvert.setToolTip('Click to invert. This could take a while.')
        invLayout.addWidget(btnInvert)
        
        logLayout = QHBoxLayout()
        
        logText = QTextEdit()
        logText.setReadOnly(True)
        logLayout.addWidget(logText)
        
        mwRMS = MatplotlibWidget(navi=False, itight=False)
        logLayout.addWidget(mwRMS)

        logLayout.setStretch(0, 60)
        logLayout.setStretch(1, 40)        
        invLayout.addLayout(logLayout, 25)
        
        # option for display
        def displayAttribute(arg='Resistivity(log10)'):
            self.attr = list(self.r2.meshResults[self.displayParams['index']].attr_cache)
            resistIndex = 0
            c = -1
            try:
                attributeName.currentIndexChanged.disconnect() # avoid unwanted plotting
            except:
                print('no method connected yet to attribute name')
                pass
            attributeName.clear() # delete all items (after disconnect otherwise it triggers it !)
            for i in range(len(self.attr)):
                if self.attr[i] == 'Resistivity(log10)':
                    resistIndex = i
                if self.attr[i] == arg:
                    c = i
#                    print('found attribute ', arg)
                attributeName.addItem(self.attr[i])
            if c != -1: # we found the same attribute
                resistIndex = c
#            else:
#                print('sorry same attribute not found')
            self.displayParams['attr'] = self.attr[resistIndex]
            attributeName.setCurrentIndex(resistIndex)
            attributeName.currentIndexChanged.connect(changeAttribute)
            #sectionId.setCurrentIndex(0)
        
        def changeAttribute(index):
            self.displayParams['attr'] = self.attr[index]
            vminEdit.setText('')
            vmaxEdit.setText('')
            self.displayParams['vmin'] = None
            self.displayParams['vmax'] = None
            replotSection()


        def changeSection(index):
            self.displayParams['index'] = index
            displayAttribute(arg=self.displayParams['attr'])
            replotSection()
        
        displayOptions = QHBoxLayout()
            
        sectionId = QComboBox()
        sectionId.setToolTip('Change survey or see initial model.')
        displayOptions.addWidget(sectionId, 20)
        
        attributeName = QComboBox()
        attributeName.setToolTip('Change attribute to display.')
        displayOptions.addWidget(attributeName, 20)
        
        vminLabel = QLabel('Min:')
        vminEdit = QLineEdit()
        vminEdit.setToolTip('Set mininum for current scale.')
        vminEdit.setValidator(QDoubleValidator())
        vmaxLabel = QLabel('Max:')
        vmaxEdit = QLineEdit()
        vmaxEdit.setToolTip('Set maximum for current color scale.')
        vmaxEdit.setValidator(QDoubleValidator())
        vMinMaxApply = QPushButton('Apply')
        vMinMaxApply.setAutoDefault(True)
        vMinMaxApply.clicked.connect(setCBarLimit)
        vMinMaxApply.setToolTip('Apply limits on current color scale.')
        
        displayOptions.addWidget(vminLabel)
        displayOptions.addWidget(vminEdit, 10)
        displayOptions.addWidget(vmaxLabel)
        displayOptions.addWidget(vmaxEdit, 10)
        displayOptions.addWidget(vMinMaxApply)
        
        def showEdges(status):
            if status == Qt.Checked:
                self.displayParams['edge_color'] = 'k'
            else:
                self.displayParams['edge_color'] = 'none'
            replotSection()
        edgeCheck= QCheckBox('Show edges')
        edgeCheck.setChecked(False)
        edgeCheck.setToolTip('Show edges of each mesh cell.')
        edgeCheck.stateChanged.connect(showEdges)
        displayOptions.addWidget(edgeCheck)
        
        def contourCheckFunc(state):
            if state == Qt.Checked:
                edgeCheck.setEnabled(False)
                self.displayParams['contour'] = True
            else:
                edgeCheck.setEnabled(True)
                self.displayParams['contour'] = False
            replotSection()
        contourCheck = QCheckBox('Contour')
        contourCheck.stateChanged.connect(contourCheckFunc)
        contourCheck.setToolTip('Grid and contour the data.')
        displayOptions.addWidget(contourCheck)
        
        def showSens(status):
            if status == Qt.Checked:
                self.displayParams['sens'] = True
            else:
                self.displayParams['sens'] = False
            replotSection()
        sensCheck = QCheckBox('Sensitivity overlay')
        sensCheck.setChecked(True)
        sensCheck.stateChanged.connect(showSens)
        sensCheck.setToolTip('Overlay a semi-transparent white sensivity layer.')
        displayOptions.addWidget(sensCheck)
        
        def sliceAxisFunc(index):
            self.displayParams['axis'] = index
        sliceAxis = QComboBox()
        sliceAxis.addItem('x')
        sliceAxis.addItem('y')
        sliceAxis.addItem('z')
        sliceAxis.setToolTip('Define axis slice.')
        sliceAxis.setVisible(False)
        displayOptions.addWidget(sliceAxis)
        
        def paraviewBtnFunc():
            self.r2.showInParaview(self.displayParams['index'])
        paraviewBtn = QPushButton('Open in Paraview')
        paraviewBtn.clicked.connect(paraviewBtnFunc)
        paraviewBtn.setVisible(False)
        displayOptions.addWidget(paraviewBtn)
            
        def btnSaveGraphs():
            fdir = QFileDialog.getExistingDirectory(tabImportingData, 'Choose the directory to export graphs and .vtk', directory=self.datadir)
            if fdir != '':
                if self.r2.typ[-1] == '2':
                    edge_color = self.displayParams['edge_color']
                    sens = self.displayParams['sens']
                    attr = self.displayParams['attr']
                    contour = self.displayParams['contour']
                    vmin = self.displayParams['vmin']
                    vmax = self.displayParams['vmax']
                    self.r2.saveInvPlots(outputdir=fdir, edge_color=edge_color,
                                       contour=contour, sens=sens, attr=attr,
                                       vmin=vmin, vmax=vmax)
                self.r2.saveVtks(fdir)
            
            infoDump('All graphs saved successfully in the working directory.')

        btnSave = QPushButton('Save graphs')
        btnSave.clicked.connect(btnSaveGraphs)
        btnSave.setToolTip('Save current graph to the working directory.')
        displayOptions.addWidget(btnSave)
        
        def showDisplayOptions(val=True):
            opts = [sectionId, attributeName, vminEdit, vmaxEdit, vMinMaxApply, 
                    edgeCheck, contourCheck, sensCheck, sliceAxis, paraviewBtn, btnSave]
            [o.setEnabled(val) for o in opts]
        
        showDisplayOptions(False) # hidden by default
        
        resultLayout = QVBoxLayout()
        resultLayout.addLayout(displayOptions, 20)
        
        mwInvResult = MatplotlibWidget(navi=True, itight=False)        
        mwInvResult3D = MatplotlibWidget(navi=True, threed=True)

        resultStackLayout = QStackedLayout()
        resultStackLayout.addWidget(mwInvResult)
        resultStackLayout.addWidget(mwInvResult3D)
        resultLayout.addLayout(resultStackLayout, 90)
                
        # in case of error, display R2.out
        r2outLayout = QVBoxLayout()

        r2outTitle = QLabel('<b>The inversion was unsuccessful. Please see below for more details.</b>')
        r2outLayout.addWidget(r2outTitle)
        
        r2outEdit = QTextEdit()
        r2outEdit.setReadOnly(True)
        r2outLayout.addWidget(r2outEdit)
        
        r2outWidget = QWidget()
        r2outWidget.setLayout(r2outLayout)
        resultWidget = QWidget()
        resultWidget.setLayout(resultLayout)
        
        outStackLayout  = QStackedLayout()
        outStackLayout.addWidget(resultWidget)
        outStackLayout.addWidget(r2outWidget)
        outStackLayout.setCurrentIndex(0)
        
        invLayout.addLayout(outStackLayout, 75)
        
        
        tabInversion.setLayout(invLayout)
                    
        
        #%% tab 6 POSTPROCESSING
        tabPostProcessing = QTabWidget()
        tabs.addTab(tabPostProcessing, 'Post-processing')
        tabs.setTabEnabled(6,False)
        
        invError = QWidget()
        tabPostProcessing.addTab(invError, 'Pseudo Section Error')
        invErrorLayout = QVBoxLayout()
        
        def plotInvError():
            mwInvError.plot(self.r2.pseudoError)
            
        mwInvError = MatplotlibWidget(navi=True)
        invErrorLayout.addWidget(mwInvError, Qt.AlignCenter)
        invError.setLayout(invErrorLayout)
        
        invError2 = QWidget()
        tabPostProcessing.addTab(invError2, 'Normalised Errors')
        invErrorLayout2 = QVBoxLayout()
        invErrorLayout2Plot = QVBoxLayout()
        
        def plotInvError2():
            mwInvError2.plot(self.r2.showInversionErrors)
        mwInvError2 = MatplotlibWidget(navi=True)
        invErrorLabel = QLabel('All errors should be between +/- 3% (Binley at al. 1995). '
                               'If it\'s not the case try to fit an error model or '
                               'manually change the a_wgt and b_wgt in inversion settings.')
        invErrorLayout2Plot.addWidget(mwInvError2, Qt.AlignCenter)
        invErrorLayout2.addLayout(invErrorLayout2Plot, 1)
        invErrorLayout2.addWidget(invErrorLabel)
        invError2.setLayout(invErrorLayout2)
        
        
        #%% Help tab
        tabHelp = QTabWidget()
        tabs.addTab(tabHelp, 'Help')
        
        helpLayout = QVBoxLayout()
        helpText = QLabel() # NOTE: YOU'LL NEED TO SET THE VERSION NUMBER IN HERE TOO
        helpText.setText('''
           <h1>General help</h1>\
           <p>Below are simple instructions to guide you to through the software.</p>
           <ul>
           <li>In the "Importing" tab:
           <ul>
           <li>Select if you want a 2D/3D survey, an inverse/forward solution and check if you have borehole/timelapse/batch data.</li>
           <li>Modify the default working directory if you want to keep the outputed files afterwards.</li>
           <li>Select the file type. You can choose "Custom" if you file type is not available and you will be redirected to the custom parser tab.</li>
           <li>If your survey has topography, you can import it in the "Electrodes(XZY/Topo)" tab.</li>
           <li>Then one can choose to directly invert with all the default settings or go through the other tabs on the rights.</li>
           <ul></li>
           <li>In the "Pre-processing" tab:
           <ul>
           <li>The first tab offers manual filtering option based on reciprocal measurements in the dataset (if any).</li>
           <li>The "Phase Filtering" tab is only enable for IP data and allows precise filtering of IP data (range filtering, removing of nested measuremetns, DCA, ...).</li>
           <li>The "Resistance Error Model" tab allows to fit a power-law or linear error model to resistance data.</li>
           <li>The "Phase Error Model" tab allows to fit a power-law or parabolic error model to phase data.</li>
           </ul></li>
           <li>In the "Mesh" tab you can create a quadrilateral or triangular mesh (2D) or a tetrahedral mesh (3D). For 2D mesh you can specify different\
           region of given resistivity/phase and if they need to be fixed or not during inversion. For forward modelling this mesh serves as the initial model.</li>
           <li>In the "Forward model" tab (only available in forward mode) you can design your sequence and add noise. The resulting synthetic measurements will be\
           automatically added to as an actual survey in pyR2 and can be inverted directly.</li>
           <li>In the "Inversion Settings" tab, you can modify all settings for the inversion. Help is available by clicking on the label of each item. The help\
           generally refers to the document present in the R2/cR3/R3t/cR3t respective manuals.</li>
           <li>In the "Inversion" tab, you can invert your survey and see the output in real time. if you have selected parallel inversion in "Inversion Settings">"Advanced",\
           then nothing will be printed out until the inversion finished. When the inversion finished you will be able to see the inverted section, open it with Paraview (mainly for 3D)\
           and save the outputed .vtk file and graphs using the "Save Graphs" button.</li>
           <li>The "Post-processing" tab displays the errors from the invesrion. It helps to assess the quality of the inversion.</li>
           </ul>
        ''')
        helpText.setOpenExternalLinks(True)
        helpText.setWordWrap(True)
        helpLayout.addWidget(helpText)
        tabHelp.setLayout(helpLayout)
        
        
        #%% About tab
        
        tabAbout = QTabWidget()
        tabs.addTab(tabAbout, 'About')
        
        infoLayout = QVBoxLayout()
        aboutText = QLabel() # NOTE: YOU'LL NEED TO SET THE VERSION NUMBER IN HERE TOO
        aboutText.setText('''<h1>About pyR2</h1> \
                          <p><b>Version: %s</b></p> \
                          <p><i>pyR2 is a free and open source software for inversion of geoelectrical data (Resistivity and IP)</i></p> \
                          <p>If you encouter any issues or would like to submit a feature request, please raise an issue on our gitlab repository at:</p> \
                          <p><a href="https://gitlab.com/hkex/pyr2/issues">https://gitlab.com/hkex/pyr2/issues</a></p> \
                          <p>pyR2 uses R2 and cR2 codes developed by Andrew Binley:</p> \
                          <p><a href="http://www.es.lancs.ac.uk/people/amb/Freeware/R2/R2.htm">http://www.es.lancs.ac.uk/people/amb/Freeware/R2/R2.htm</a></p> \
                          <p>For generation of triangular mesh, pyR2 uses "Gmsh" software:</p> \
                          <p><a href="http://gmsh.info/">http://gmsh.info/</a></p>\
                          <p>Python packages used: numpy, pandas, matplotlib.
<ul>
<li>
John D. Hunter.
<strong>Matplotlib: A 2D Graphics Environment</strong>,
Computing in Science &amp; Engineering, <strong>9</strong>, 90-95 (2007),
<a class="reference external" href="https://doi.org/10.1109/MCSE.2007.55">DOI:10.1109/MCSE.2007.55</a> 
</li>
<li>Travis E, Oliphant. <strong>A guide to NumPy</strong>,
USA: Trelgol Publishing, (2006).
</li>
</ul>
</p>
<p><strong>pyR2's core developers: Guillaume Blanchy, Sina Saneiyan, Jimmy Boyd and Paul McLachlan.<strong></p>
'''%pyR2_version)
#        aboutText.setText('''<h1>About pyR2</h1> \
#                          <p><b>Version: %s</b></p> \
#                          <p><i>pyR2 is a free and open source software for inversion of geoelectrical data (Resistivity and IP)</i></p> \
#                          <p>If you encouter any issues or would like to submit a feature request, please raise an issue on our gitlab repository at:</p> \
#                          <p><a href="https://gitlab.com/hkex/pyr2/issues">https://gitlab.com/hkex/pyr2/issues</a></p> \
#                          <p>pyR2 uses R2 and cR2 codes developed by Andrew Binley:</p> \
#                          <p><a href="http://www.es.lancs.ac.uk/people/amb/Freeware/R2/R2.htm">http://www.es.lancs.ac.uk/people/amb/Freeware/R2/R2.htm</a></p> \
#                          <p>For generation of triangular mesh, pyR2 uses "Gmsh" software:</p> \
#                          <p><a href="http://gmsh.info/">http://gmsh.info/</a></p>\
#                          <p>Python packages used: scipy, numpy, pandas, matplotlib.
#<ul>
#<li>Jones E, Oliphant E, Peterson P, <em>et al.</em>
#<strong>SciPy: Open Source Scientific Tools for Python</strong>, 2001-,
#<a class="reference external" href="http://www.scipy.org/">http://www.scipy.org/</a> [Online; accessed 2018-10-02].
#</li>
#<li>
# Wes McKinney.
#<strong>Data Structures for Statistical Computing in Python</strong>,
#Proceedings of the 9th Python in Science Conference, 51-56 (2010)
#(<a class="reference external" href="http://conference.scipy.org/proceedings/scipy2010/mckinney.html">publisher link</a>)
#</li>
#<li>
#John D. Hunter.
#<strong>Matplotlib: A 2D Graphics Environment</strong>,
#Computing in Science &amp; Engineering, <strong>9</strong>, 90-95 (2007),
#<a class="reference external" href="https://doi.org/10.1109/MCSE.2007.55">DOI:10.1109/MCSE.2007.55</a> 
#</li>
#<li>Travis E, Oliphant. <strong>A guide to NumPy</strong>,
#USA: Trelgol Publishing, (2006).
#</li>
#</ul>
#</p>
#<p><strong>pyR2's core developers: Guillaume Blanchy, Sina Saneiyan, Jimmy Boyd and Paul McLachlan.<strong></p>
#'''%pyR2_version)
        aboutText.setOpenExternalLinks(True)
        aboutText.setWordWrap(True)
        aboutText.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        infoLayout.addWidget(aboutText)
        
        tabAbout.setLayout(infoLayout)
        
        #%% general Ctrl+Q shortcut + general tab layout
        if OS == 'Darwin':
            metaLayout.setSpacing(4)
            btnInvNow.setStyleSheet('background-color: green; margin-left: 5px; padding: 2px')
            phasefiltlayout.setSpacing(4)
            
        layout.addWidget(tabs)
        layout.addWidget(errorLabel)
        self.table_widget.setLayout(layout)
        self.setCentralWidget(self.table_widget)
        self.show()


    def keyPressEvent(self, e):
        if (e.modifiers() == Qt.ControlModifier) & (e.key() == Qt.Key_Q):
            self.close()
        if (e.modifiers() == Qt.ControlModifier) & (e.key() == Qt.Key_W):
            self.close()
    
    
''' 
class MyTableWidget(QWidget):        
 
    def __init__(self, parent):   
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
 
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()	
        self.tab2 = QWidget()
        self.tabs.resize(300,200) 
 
        # Add tabs
        self.tabs.addTab(self.tab1,"Tab 1")
        self.tabs.addTab(self.tab2,"Tab 2")
 
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.pushButton1 = QPushButton("PyQt5 button")
        self.tab1.layout.addWidget(self.pushButton1)
        self.tab1.setLayout(self.tab1.layout)
 
        # Add tabs to widget        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
 
'''

if __name__ == '__main__':
    catchErrors()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(bundle_dir, 'logo.png'))) # that's the true app icon
    print(os.path.join(bundle_dir, 'logo.png'))
    splash_pix = QPixmap(os.path.join(bundle_dir, 'logo.png'))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)
    # splash = QSplashScreen(splash_pix)
    # adding progress bar
    progressBar = QProgressBar(splash)
    progressBar.setMaximum(10)
    progressBar.setGeometry(0, splash_pix.height() - 50, splash_pix.width(), 20)

    # splash.setMask(splash_pix.mask())
    from api.R2 import pyR2_version
    
    splash.show()
    splash.showMessage("Loading libraries", Qt.AlignBottom, Qt.white)
    app.processEvents()    

    # in this section all import are made except the one for pyQt
    
    progressBar.setValue(1)    
    app.processEvents()

    print('importing matplotlib')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import axes3d
    progressBar.setValue(2)
    app.processEvents()
    
#    import matplotlib.pyplot as plt # this does work
#    fig = plt.figure()
#    fig.add_subplot(111, projection='3d')
#    fig.show()
    
    print('importing numpy')
    import numpy as np
    progressBar.setValue(4)
    app.processEvents()
    print ('importing pandas')
    import pandas as pd
    progressBar.setValue(6)
    app.processEvents()
    print('importing python libraries')
    import shutil
    import platform
    OS = platform.system()
    from datetime import datetime
    progressBar.setValue(8)
    app.processEvents()
    from matplotlib import rcParams
    rcParams.update({'font.size': 13}) # CHANGE HERE for graph font size
    from subprocess import Popen # used for opening paraview
    
    from api.R2 import R2
    from api.r2help import r2help
    progressBar.setValue(10)
    app.processEvents()

    ex = App()
    splash.hide() # hiding the splash screen when finished
    wineCheck()
    updateChecker()
    sys.exit(app.exec_())



#%%
#table = QTableWidget(10, 3)
#table.setVisible(False)
#table.setItem(0,0,QTableWidgetItem('4.3'))
#table.setItem(1,1,QTableWidgetItem('2.3'))
#print(table.item(0,0).text())
