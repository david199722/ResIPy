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
    def __init__(self, parent=None, figure=None, navi=False, itight=True):
        super(MatplotlibWidget, self).__init__(parent) # we can pass a figure but we can replot on it when
        # pushing on a button (I didn't find a way to do it) while with the axes, you can still clear it and
        # plot again on them
        self.itight = itight
        if figure is None:
            figure = Figure()
            axes = figure.add_subplot(111)
        else:
            axes = figure.get_axes()
        self.axis = axes
        self.figure = figure
        self.canvas = FigureCanvasQTAgg(self.figure)
        
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

    
    def plot(self, callback):
        ''' call a callback plot function and give it the ax to plot to
        '''
#        print('plot is called')
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.axis = ax
        self.callback = callback
        callback(ax=ax)
        ax.set_aspect('auto')
        ax.set_autoscale_on(False)
        if self.itight == True:
            self.figure.tight_layout()
        self.canvas.draw()
    
    def setCallback(self, callback):
        self.callback = callback
        
    def replot(self, **kwargs):
#        print('replot:', kwargs)
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.axis = ax
        self.callback(ax=ax, **kwargs)
        ax.set_aspect('auto')
#        self.figure.tight_layout()
        self.canvas.draw()
    
    def clear(self):
#        print('clearing figure')
        self.axis.clear()
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
        if os.path.exists(self.newwd):
            shutil.rmtree(self.newwd)
        os.mkdir(self.newwd)
        
        self.r2 = None
        self.parser = None
        self.fname = None
        self.iBatch = False
        self.iTimeLapse = False
        self.iBorehole = False
        self.datadir = os.path.join(bundle_dir, 'api', 'test')
        
        self.table_widget = QWidget()
        layout = QVBoxLayout()
        tabs = QTabWidget()
        
        # app icon
        self.setWindowIcon(QIcon(os.path.join(bundle_dir + 'logo.png')))
        
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
        
        # restart all new survey
        def restartFunc():
            print('------- creating new R2 object ----------')
            self.r2 = R2(self.newwd) # create new R2 instance
            self.r2.iBatch = self.iBatch
            self.r2.setBorehole(self.iBorehole)
            self.r2.iTimeLapse = self.iTimeLapse
            if self.iTimeLapse is True:
                reg_mode.setCurrentIndex(2)
            else:
                reg_mode.setCurrentIndex(0)
            # importing
            wdBtn.setText('Working directory:' + self.r2.dirname + ' (Press to change)')
            buttonf.setText('Import Data')
#            timeLapseCheck.setChecked(False)
#            boreholeCheck.setChecked(False)
#            batchCheck.setChecked(False)
            ipCheck.setChecked(False)
            ipCheck.setEnabled(False)
            tabImporting.setTabEnabled(1, False)
            mwPseudo.clear() # clearing figure
            elecTable.clear()
            topoTable.initTable(np.array([['',''],['','']]))
#            dimInverse.setChecked(True)
            
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
            phivminEdit.setText('')
            phivmaxEdit.setText('')
            dcaProgress.setValue(0)
            tabPreProcessing.setTabEnabled(0, True)
            tabPreProcessing.setTabEnabled(1, False)
            tabPreProcessing.setTabEnabled(2, False)
            tabPreProcessing.setTabEnabled(3, False)
            
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
            data_type.setCurrentIndex(0)
            reg_mode.setCurrentIndex(0)
            max_iterations.setText('10')
            error_mod.setCurrentIndex(1)
            alpha_aniso.setText('1.0')
            a_wgt.setText('0.01')
            b_wgt.setText('0.02')
            c_wgt.setText('1')
            d_wgt.setText('2')
            rho_min.setText('-1000')
            rho_max.setText('1000')
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
                self.r2.typ = self.r2.typ.replace('3','2')
                elecTable.initTable(headers=['x','z','Buried'])
                topoTable.initTable(headers=['x','z'])
                elecDy.setEnabled(False)
                print(self.r2.typ)
            else:
                self.r2.typ = self.r2.typ.replace('2','3')
                elecTable.initTable(headers=['x','y','z','Buried'])
                topoTable.initTable(headers=['x','y','z'])
                elecDy.setEnabled(True)
                print(self.r2.typ)
                
        dimRadio2D = QRadioButton('2D')
        dimRadio2D.setChecked(True)
        dimRadio2D.toggled.connect(dimSurvey)
        dimRadio3D = QRadioButton('3D')
        dimRadio3D.setChecked(False)
        dimRadio3D.setEnabled(False)
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
        
        date = QLabel('Date')
        dateEdit = QLineEdit()
        dateEdit.setText(datetime.now().strftime('%Y-%m-%d')) # get today date
        
        
        def timeLapseCheckFunc(state):
            if state == Qt.Checked:
                self.iTimeLapse = True
                buttonf.setText('Import Data Directory')
                buttonf.clicked.disconnect()
                buttonf.clicked.connect(getdir)
                ipCheck.setEnabled(False)
                batchCheck.setEnabled(False)
            else:
                self.iTimeLapse = False
                buttonf.setText('Import Data')
                buttonf.clicked.disconnect()
                buttonf.clicked.connect(getfile)
                ipCheck.setEnabled(True)
                batchCheck.setEnabled(True)
                
        timeLapseCheck = QCheckBox('Time-lapse Survey')
        timeLapseCheck.stateChanged.connect(timeLapseCheckFunc)
        
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
        
        # select inverse or forward model
        def dimForwardFunc():
            fileType.setEnabled(False)
            spacingEdit.setReadOnly(True)
            dimInverse.setChecked(False)
            tabs.setTabEnabled(1,False)
            tabs.setTabEnabled(3, True)
            tabImporting.setTabEnabled(1, True)
            buttonf.setEnabled(False)
            timeLapseCheck.setEnabled(False)
            batchCheck.setEnabled(False)
            boreholeCheck.setEnabled(False)
            if self.r2 is None:
                self.r2 = R2(self.newwd)
            else:
                restartFunc() # let's first from previous inversion
        def dimInverseFunc():
            fileType.setEnabled(True)
            dimForward.setChecked(False)
            spacingEdit.setReadOnly(False)
            tabs.setTabEnabled(1,True)
            tabs.setTabEnabled(3, False)
            tabImporting.setTabEnabled(1, False)
            buttonf.setEnabled(True)
            timeLapseCheck.setEnabled(True)
            batchCheck.setEnabled(True)
            boreholeCheck.setEnabled(True)
        dimForward = QRadioButton('Forward')
        dimForward.setChecked(False)
        dimForward.toggled.connect(dimForwardFunc)
        dimInverse = QRadioButton('Inverse')
        dimInverse.setChecked(True)
        dimInverse.toggled.connect(dimInverseFunc)
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
                wdBtn.setText(fdir + ' (Press to change)')
            
        wdBtn = QPushButton('Working directory:' + self.newwd + ' (Press to change)')
        wdBtn.setAutoDefault(True)
        wdBtn.clicked.connect(getwd)
        wdBtn.setToolTip('The working directory will contains all files for the inversion (R2.in, R2.exe, protocol.dat, f001_res.vtk, ...)')
        
        self.ftype = 'Syscal' # by default
        
        def fileTypeFunc(index):
            if index == 0:
                self.ftype = 'Syscal'
            elif index == 1:
                self.ftype = 'Protocol'
            elif index == 2:
                self.ftype = 'Res2Dinv'
            elif index == 3:
                self.ftype = 'BGS Prime'
            elif index == 4:
                self.ftype = 'Custom'
                tabImporting.setCurrentIndex(2) # switch to the custom parser
            else:
                self.ftype = '' # let to be guessed
        fileType = QComboBox()
        fileType.addItem('Syscal')
        fileType.addItem('Protocol')
        fileType.addItem('Res2Dinv')
        fileType.addItem('BGS Prime')
        fileType.addItem('Custom')
        fileType.currentIndexChanged.connect(fileTypeFunc)
        fileType.setFixedWidth(150)
        
        spacingEdit = QLineEdit()
        spacingEdit.setValidator(QDoubleValidator())
        spacingEdit.setText('-1.0') # -1 let it search for the spacing
        spacingEdit.setFixedWidth(80)
        
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
                    buttonf.setText(os.path.basename(fdir) + ' (Press to change)')
                    plotPseudo()
                    elecTable.initTable(self.r2.elec)
                    tabImporting.setTabEnabled(1,True)
                    btnInvNow.setEnabled(True)
                    if all(self.r2.surveys[0].df['irecip'].values == 0):
                        pass
                    else:
                        tabPreProcessing.setTabEnabled(2, True)
                        plotError()
                except:
                    errorDump('File format not recognize or directory contains other files than .dat files')
            
        def getfile():
            print('ftype = ', self.ftype)
            fname, _ = QFileDialog.getOpenFileName(tabImportingData,'Open File', directory=self.datadir)
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
                except:
                    errorDump('File not recognized.')
                    pass
                print('ok passed import')
                if all(self.r2.surveys[0].df['irecip'].values == 0):
#                    hbox4.addWidget(buttonfr)
                    buttonfr.show()
                else:
                    buttonfr.hide()
                    tabPreProcessing.setTabEnabled(2, True)
                    plotError()
#                generateMesh()
                if boreholeCheck.isChecked() is True:
                    self.r2.setBorehole(True)
                else:
                    self.r2.setBorehole(False)
                plotPseudo()
#                plotManualFiltering()
                elecTable.initTable(self.r2.elec)
                tabImporting.setTabEnabled(1,True)
                if 'ip' in self.r2.surveys[0].df.columns:
                    if np.sum(self.r2.surveys[0].df['ip'].values) > 0:
                        ipCheck.setChecked(True)
                infoDump(fname + ' imported successfully')
                btnInvNow.setEnabled(True)
            except Exception as e:
                print(e)
                errorDump('Importation failed. File is not being recognized. \
                          Make sure you selected the right file type.')
                pass
        
        buttonf = QPushButton('Import Data')
        buttonf.setAutoDefault(True)
        buttonf.clicked.connect(getfile)
        
        def getfileR():
            fnameRecip, _ = QFileDialog.getOpenFileName(tabImportingData,'Open File', directory=self.datadir)
            if fnameRecip != '':
                buttonfr.setText(os.path.basename(fnameRecip))
                if float(spacingEdit.text()) == -1:
                    spacing = None
                else:
                    spacing = float(spacingEdit.text())
                self.r2.surveys[0].addData(fnameRecip, ftype=self.ftype, spacing=spacing)
                if all(self.r2.surveys[0].df['irecip'].values == 0) is False:
                    tabPreProcessing.setTabEnabled(2, True) # no point in doing error processing if there is no reciprocal
                    plotError()
#                plotManualFiltering()

        buttonfr = QPushButton('If you have reciprocals upload them here')
        buttonfr.setAutoDefault(True)
        buttonfr.clicked.connect(getfileR)
        buttonfr.hide()
        
        def btnInvNowFunc():
            tabs.setCurrentIndex(5) # jump to inversion tab
            btnInvert.animateClick() # invert
        btnInvNow = QPushButton('Invert')
        btnInvNow.setStyleSheet('background-color: green')
        btnInvNow.setFixedWidth(150)
        btnInvNow.setAutoDefault(True)
        btnInvNow.clicked.connect(btnInvNowFunc)
        btnInvNow.setEnabled(False)
        
        hbox4 = QHBoxLayout()
        hbox4.addWidget(fileType)
        hbox4.addWidget(spacingEdit)
        hbox4.addWidget(buttonf)
        hbox4.addWidget(buttonfr)
        hbox4.addWidget(btnInvNow)
        
        def ipCheckFunc(state):
            if state  == Qt.Checked:
                self.r2.typ = 'cR2'
#                timeLapseCheck.setEnabled(False)
                plotPseudoIP()
                phaseplotError()
                showIpOptions(True)
                mwPseudoIP.setVisible(True)
                tabPreProcessing.setTabEnabled(1, True)
                tabPreProcessing.setTabEnabled(3, True)
                heatRaw()
#                self.r2.surveys[0].filterDataIP_plot = self.r2.surveys[0].filterDataIP_plotOrig
                self.r2.surveys[0].filterDataIP = self.r2.surveys[0].df
                heatFilter()
            else:
                self.r2.typ = 'R2'
                showIpOptions(False)
#                timeLapseCheck.setEnabled(True)
                mwPseudoIP.setVisible(False)
                tabPreProcessing.setTabEnabled(1, False)
                tabPreProcessing.setTabEnabled(3, False)

        ipCheck = QCheckBox('Induced Polarization')
        ipCheck.stateChanged.connect(ipCheckFunc)
        ipCheck.setEnabled(False)
        hbox5 = QHBoxLayout()
        hbox5.addWidget(ipCheck)
        
        metaLayout = QVBoxLayout()
#        metaLayout.addLayout(topLayout)
        metaLayout.addLayout(hbox1)
        metaLayout.addLayout(hbox2)
        metaLayout.addWidget(wdBtn)
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
        tabImporting.addTab(tabImportingTopo, 'Topography')
        
        # electrode table
        class ElecTable(QTableWidget):
            def __init__(self, nrow=10, headers=['x','z','Buried'],
                         visible=True, selfInit=False):
                """ if selfInit is true, it will automatically add rows if tt
                is bigger than the actual rows
                """
                ncol = len(headers)
                super(ElecTable, self).__init__(nrow, ncol)
                self.setVisible(visible)
                self.nrow = nrow
                self.ncol = ncol
                self.selfInit = selfInit
                self.initTable(np.zeros((nrow, ncol)), headers=headers)
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
#                    print('rename headers = ', headers)
                    self.headers = np.array(headers)
#                else:
#                    print('will use ', self.headers)
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
                        item = self.item(j,i).text()
                        if item != '':
                            table[j,i] = float(item)
#                print('table = ', table)
                return table
            
            def readTable(self):
                fname, _ = QFileDialog.getOpenFileName(tabImportingTopo,'Open File')
                if fname != '':
                    df = pd.read_csv(fname, header=None)
                    tt = df.values
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
        
        elecTable = ElecTable(visible=True, headers=['x','z','Buried'])
        elecLabel = QLabel('<i>Add electrode position. Use <code>Ctrl+V</code> to paste or import from CSV (no headers).\
                           The last column is 1 if checked (= buried electrode) and 0 if not (=surface electrode).\
                           You can also use the form below to generate \
                           regular electrode spacing.</i>')
        elecLabel.setWordWrap(True)
        elecButton = QPushButton('Import from CSV files (no headers)')
        elecButton.setAutoDefault(True)
        elecButton.clicked.connect(elecTable.readTable)
        nbElecEdit = QLineEdit()
        nbElecEdit.setValidator(QIntValidator())
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
        
        topoTable = ElecTable(visible=True, headers=['x','z'], selfInit=True)
        topoTable.initTable(np.array([['',''],['','']]))
        topoLabel = QLabel('<i>Add additional surface points. \
                           You can use <code>Ctrl+V</code> to paste directly \
                           into a cell.</i>')
        topoButton = QPushButton('Import from CSV files (no headers)')
        topoButton.setAutoDefault(True)
        topoButton.clicked.connect(topoTable.readTable)
        topoLayout.addWidget(topoLabel)
        topoLayout.addWidget(topoButton)
        topoLayout.addWidget(topoTable)
        
        tabImportingTopo.setLayout(topoLayout)
        tabImporting.setTabEnabled(1, False)
        
        
        #%% sub tab for custom importing
        customParser = QWidget()
        tabImporting.addTab(customParser, 'Custom Parser')
        
        delimiterLabel = QLabel('Delimiter')
        delimiterEdit = QLineEdit('')
        skipRowsLabel = QLabel('Number of header to skip')
        skipRowsEdit = QLineEdit('0')
        skipRowsEdit.setValidator(QIntValidator())
        nrowsLabel = QLabel('Number of rows to read')
        nrowsEdit = QLineEdit('')
        nrowsEdit.setValidator(QIntValidator())
        
        def openFileBtnFunc(file):
            fname, _ = QFileDialog.getOpenFileName(tabImportingTopo,'Open File')
            if fname != '':
                self.fnameManual = fname
                openFileBtn.setText(fname + ' (Click to change)')
        openFileBtn = QPushButton('Open File')
        openFileBtn.setAutoDefault(True)
        openFileBtn.clicked.connect(openFileBtnFunc)

        def parseBtnFunc():
            try:
                delimiter = delimiterEdit.text()
                delimiter = None if delimiter == '' else delimiter
                skipRows = skipRowsEdit.text()
                skipRows = None if skipRows == '' else int(skipRows)
                nrows = nrowsEdit.text()
                nrows = None if nrows == '' else int(nrows)
                parserTable.readTable(self.fnameManual, delimiter=delimiter,
                                          skiprows=skipRows, nrows=nrows)
                fillBoxes(boxes[:-1]) # last one is elecSpacingEdit
            except ValueError as e:
                errorDump('Import error:', e)

        parseBtn = QPushButton('Import')
        parseBtn.setAutoDefault(True)
        parseBtn.clicked.connect(parseBtnFunc)
            
        # have qcombobox to be read for each columns
        aBoxLabel = QLabel('A (or C1)')
        bBoxLabel = QLabel('B (or C2)')
        mBoxLabel = QLabel('M (or P1)')
        nBoxLabel = QLabel('N (or P2)')
        vpBoxLabel = QLabel('Vp Potential Difference')
        InBoxLabel = QLabel('In Current')
        resistBoxLabel = QLabel('Transfer Resistance')
        ipStartBoxLabel = QLabel('IP start column')
        ipEndBoxLabel = QLabel('IP end column')
        chargeabilityBoxLabel = QLabel('Chargeability')
        elecSpacingLabel = QLabel('Electrode spacing')
       
        boxesLabels = [aBoxLabel, bBoxLabel, mBoxLabel, nBoxLabel, vpBoxLabel, InBoxLabel, resistBoxLabel, ipStartBoxLabel,
                 ipEndBoxLabel, chargeabilityBoxLabel, elecSpacingLabel]
        
        aBox = QComboBox()
        bBox = QComboBox()
        mBox = QComboBox()
        nBox = QComboBox()
        vpBox = QComboBox()
        InBox = QComboBox()
        resistBox = QComboBox()
        ipStartBox = QComboBox()
        ipEndBox = QComboBox()
        chargeabilityBox = QComboBox()
        elecSpacingEdit = QLineEdit('')
        elecSpacingEdit.setValidator(QDoubleValidator())
        elecSpacingEdit.setFixedWidth(80)
        elecSpacingEdit.setToolTip('Number to divide the selected columns to get electrode number.')
        
        boxes = [aBox, bBox, mBox, nBox, vpBox, InBox, resistBox, ipStartBox,
                 ipEndBox, chargeabilityBox, elecSpacingEdit]
                
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
                    self.headers = df.columns.values
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
                espacing = None if elecSpacingEdit.text() == '' else float(elecSpacingEdit.text())
                
                # parse
                df = pd.read_csv(fname, delimiter=delimiter, skiprows=skipRows, nrows=nrows)
                df = df.reset_index() # solve issue all columns in index
                oldHeaders = df.columns.values[colIndex]
                df = df.rename(columns=dict(zip(oldHeaders, newHeaders)))
                if 'resist' not in df.columns:
                    df['resist'] = df['vp']/df['i']
                if 'ip' not in df.columns:
                    df['ip'] = 0
                array = df[['a','b','m','n']].values.copy()
                if espacing is None:
                    espacing = np.unique(np.sort(array.flatten()))[1]
                array = np.round(array/espacing+1).astype(int)
                df[['a','b','m','n']] = array
                imax = int(np.max(array))
#                if np.sum(array == 0) > 0:
#                    print('add 1 as there is electrodes at zeros')
#                    imax = imax+1
                elec = np.zeros((imax,3))
                elec[:,0] = np.arange(0,imax)*espacing
                return elec, df

            self.parser = parserFunc
            
            # test            
            elec, df = parserFunc(self.fnameManual)
            print('shapes = ', elec.shape, df.shape)
                
            
            if (self.r2.iTimeLapse is False) & (self.r2.iBatch is False):
                importFile(self.fnameManual)
            
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
            columnsAssign.addWidget(boxesLabels[i], r, c)
            columnsAssign.addWidget(boxes[i], r, c+1)
        parserLayout.addLayout(columnsAssign)
        parserLayout.addWidget(importBtn)
        
        customParser.setLayout(parserLayout)

        
        #%% tab 2 PRE PROCESSING
        tabPreProcessing = QTabWidget()
        tabs.addTab(tabPreProcessing, 'Pre-processing')
        
        manualLayout = QVBoxLayout()
        
        def plotManualFiltering():
            mwManualFiltering.plot(self.r2.surveys[0].manualFiltering)
        
        def btnDoneFunc():
            self.r2.surveys[0].filterData(~self.r2.surveys[0].iselect)
            print('Data have been manually filtered')
            plotManualFiltering()
            plotError()
            
        notice = QLabel('Click on the dots to select them. Press "Apply" to remove them.')
        manualLayout.addWidget(notice)
        
        btnLayout = QHBoxLayout()
        btnStart = QPushButton('Start')
        btnStart.setAutoDefault(True)
        btnStart.clicked.connect(plotManualFiltering)
        btnLayout.addWidget(btnStart)
        btnDone = QPushButton('Apply')
        btnDone.setAutoDefault(True)
        btnDone.clicked.connect(btnDoneFunc)
        btnDone.setToolTip('This will erase all selected quadrupoles definitively.')
        btnLayout.addWidget(btnDone)
        manualLayout.addLayout(btnLayout)
        
        
        mwManualFiltering = MatplotlibWidget(navi=True)
        manualLayout.addWidget(mwManualFiltering)
        
        
        errorLayout = QVBoxLayout()
        
        def errorModelSpecified():
            a_wgt.setText('0.0')
            a_wgtFunc()
            b_wgt.setText('0.0')
            b_wgtFunc()
        
        def plotError():
            mwFitError.plot(self.r2.plotError)
            self.r2.errTyp = 'none'
            
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
                self.r2.errTyp = 'lin'
            elif index == 2:
                mwFitError.plot(self.r2.pwlfit)
                self.r2.errTyp = 'pwl'
            elif index == 3:
                print('NOT READY YET')
                mwFitError.plot(self.r2.lmefit)
                self.r2.errTyp = 'lme'
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
        errFitType.addItem('Linear Mixed Effect')
        errFitType.currentIndexChanged.connect(errFitTypeFunc)
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
                self.r2.errTypIP = 'pwlip'
            else:
                print('NOT IMPLEMENTED YET')
            if index == 0:
                b_wgt.setText('0.02')
                b_wgtFunc()
                c_wgt.setText('1.0')
                c_wgtFunc()
            else:
                a_wgt.setText('0.01')
                a_wgtFunc()
                b_wgt.setText('0.0')
                b_wgtFunc()
                c_wgt.setText('0.0')
                c_wgtFunc()
            
            
        iperrFitType = QComboBox()
        iperrFitType.addItem('Observed discrepancies') ##### BY default does not show!! should be selected after the power law (don't know why!!!)
        iperrFitType.addItem('Power law')
        iperrFitType.currentIndexChanged.connect(iperrFitTypeFunc)
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
        phiConvFactorlabel = QLabel('Conversion factor k (φ = -kM)')
        phiConvFactor = QLineEdit()
        phiConvFactor.setFixedWidth(50)
        phiConvFactor.setValidator(QDoubleValidator())
        phiConvFactor.setText('1.2')
        phiConvFactor.editingFinished.connect(convFactK)
        rangelabel = QLabel('  |  Phase range filtering:')
        phivminlabel = QLabel('-φ min: ')
        phivminEdit = QLineEdit()
        phivminEdit.setValidator(QDoubleValidator())
        phivmaxlabel = QLabel('-φ max: ')
        phivmaxEdit = QLineEdit()
        phivmaxEdit.setValidator(QDoubleValidator())
        rangebutton = QPushButton('Apply')
        rangebutton.setAutoDefault(True)
        rangebutton.clicked.connect(phirange)
        
        recipfilt = QPushButton('Remove reciprocals')
        recipfilt.setAutoDefault(True)
        recipfilt.clicked.connect(removerecip)

        nestedfilt = QPushButton('Remove nested')
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
            self.r2.surveys[0].filterDataIP = self.r2.surveys[0].dfphasereset.copy()
            self.r2.surveys[0].df = self.r2.surveys[0].dfphasereset.copy()
            heatFilter()
            dcaProgress.setValue(0)
            
        def phiCbarRange():
            self.r2.surveys[0].phiCbarmin = float(phiCbarminEdit.text())
            self.r2.surveys[0].phiCbarMax = float(phiCbarMaxEdit.text())
            heatFilter()
            heatRaw()
        
        resetlayout = QHBoxLayout()
        filtreset = QPushButton('Reset all "phase" filters')
        filtreset.setStyleSheet("background-color: red")
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
        phiCbarrangebutton.setAutoDefault(True)
        phiCbarrangebutton.clicked.connect(phiCbarRange)
        resetlayout.addWidget(phiCbarminlabel)
        resetlayout.addWidget(phiCbarminEdit)
        resetlayout.addWidget(phiCbarMaxlabel)
        resetlayout.addWidget(phiCbarMaxEdit)
        resetlayout.addWidget(phiCbarrangebutton)
        resetlayout.addWidget(filtreset)
#        recipfilt.clicked.connect("add function")
        
        
        ipfiltlayout = QHBoxLayout()
        
        def heatRaw():
            self.r2.surveys[0].phiCbarmin = float(phiCbarminEdit.text())
            self.r2.surveys[0].phiCbarMax = float(phiCbarMaxEdit.text())
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
            self.r2.surveys[0].dca(dump=dcaDump)
            heatFilter()
            
        dcaLayout = QHBoxLayout()
        dcaButton = QPushButton('DCA filtering')
        dcaButton.setAutoDefault(True)
        dcaButton.clicked.connect(dcaFiltering)
        dcaProgress = QProgressBar()
        dcaLayout.addWidget(dcaButton)
        dcaLayout.addWidget(dcaProgress)
        
        phasefiltlayout.addLayout(dcaLayout, 1)
        phasefiltlayout.addLayout(resetlayout, 2)
        phasefiltlayout.addLayout(ipfiltlayout, 3)
            
        manualWidget = QWidget()
        manualWidget.setLayout(manualLayout)
        tabPreProcessing.addTab(manualWidget, 'Manual Filtering')
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

        
        tabPreProcessing.setTabEnabled(3, False)
        tabPreProcessing.setTabEnabled(2, False)
        tabPreProcessing.setTabEnabled(1, False)
        
        
        #%% tab MESH
        tabMesh= QWidget()
        tabs.addTab(tabMesh, 'Mesh')
        meshLayout = QVBoxLayout()
        
        def replotMesh():
            regionTable.reset()
            def func(ax):
                self.r2.createModel(ax=ax, addAction=regionTable.addRow)
            mwMesh.plot(func)
            mwMesh.canvas.setFocusPolicy(Qt.ClickFocus) # allows the keypressevent to go to matplotlib
            mwMesh.canvas.setFocus() # set focus on the canvas
            
        def meshQuadFunc():
            self.r2.elec[:,[0,2]] = elecTable.getTable()
            nnodes = int(nnodesEdit.text())
            try:
                self.r2.createMesh(typ='quad', elemx=nnodes)
                scale.setVisible(False)
                scaleLabel.setVisible(False)
                meshOutputStack.setCurrentIndex(1)
                replotMesh()
            except Exception as e:
                errorDump('Error creating the mesh: ' + str(e))
        meshQuad = QPushButton('Quadrilateral Mesh')
        meshQuad.setAutoDefault(True)
        meshQuad.clicked.connect(meshQuadFunc)
        
        def meshTrianFunc():
            meshOutputStack.setCurrentIndex(0)
            QApplication.processEvents()
            meshLogText.clear()
#            try:
            self.r2.elec[:,[0,2]] = elecTable.getTable()
            cl = float(clEdit.text())
            cl_factor = float(cl_factorEdit.text())
            buried = elecTable.getBuried()
            surface = topoTable.getTable()
            inan = ~np.isnan(surface[:,0])
            if np.sum(inan) == surface.shape[0]:
                surface = None
            else:
                surface = surface[inan,:]
            self.r2.createMesh(typ='trian', buried=buried, surface=surface,
                               cl=cl, cl_factor=cl_factor, dump=meshLogTextFunc)
            scale.setVisible(True)
            scaleLabel.setVisible(True)
            replotMesh()
            meshOutputStack.setCurrentIndex(1)
#            except Exception as e:
#                errorDump('Error creating the mesh: ' + str(e))

        meshTrian = QPushButton('Triangular Mesh')
        meshTrian.setAutoDefault(True)
        meshTrian.clicked.connect(meshTrianFunc)
        
        # additional options for quadrilateral mesh
        nnodesLabel = QLabel('Number of nodes between electrode:')
        nnodesEdit = QLineEdit()
        nnodesEdit.setValidator(QIntValidator())
        nnodesEdit.setText('4')

        # additional options for triangular mesh
        clLabel = QLabel('Characteristic Length:')
        clEdit = QLineEdit()
        clEdit.setValidator(QDoubleValidator())
        clEdit.setText('-1')
        cl_factorLabel = QLabel('Growth factor:')
        cl_factorEdit = QLineEdit()
        cl_factorEdit.setValidator(QDoubleValidator())
        cl_factorEdit.setText('2')
        
        meshOptionQuadLayout = QHBoxLayout()
        meshOptionQuadLayout.addWidget(nnodesLabel)
        meshOptionQuadLayout.addWidget(nnodesEdit)
        
        meshOptionTrianLayout = QHBoxLayout()
        meshOptionTrianLayout.addWidget(clLabel)
        meshOptionTrianLayout.addWidget(clEdit)
        meshOptionTrianLayout.addWidget(cl_factorLabel)
        meshOptionTrianLayout.addWidget(cl_factorEdit)
        
        meshChoiceLayout = QHBoxLayout()
        meshQuadLayout = QVBoxLayout()
        meshTrianLayout = QVBoxLayout()
        meshQuadGroup = QGroupBox()
        meshQuadGroup.setStyleSheet("QGroupBox{padding-top:1em; margin-top:-1em}")
        meshTrianGroup = QGroupBox()
        meshTrianGroup.setStyleSheet("QGroupBox{padding-top:1em; margin-top:-1em}")
        
        meshQuadLayout.addLayout(meshOptionQuadLayout)
        meshQuadLayout.addWidget(meshQuad)
        meshQuadGroup.setLayout(meshQuadLayout)
        meshChoiceLayout.addWidget(meshQuadGroup)
        
        meshTrianLayout.addLayout(meshOptionTrianLayout)
        meshTrianLayout.addWidget(meshTrian)
        meshTrianGroup.setLayout(meshTrianLayout)
        meshChoiceLayout.addWidget(meshTrianGroup)
        
        meshLayout.addLayout(meshChoiceLayout, 20)
        
        
        class RegionTable(QTableWidget):
            def __init__(self, nrow=1, ncol=3):
                super(RegionTable, self).__init__(nrow, ncol)
                self.nrow = nrow
                self.ncol = ncol
                self.setColumnCount(self.ncol)
                self.setRowCount(self.nrow)
                self.headers = ['Resistivity [Ohm.m]', 'Zones', 'Fixed']
                self.setHorizontalHeaderLabels(self.headers)
                self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.setItem(0,0,QTableWidgetItem('100.0'))
                self.setItem(0,1,QTableWidgetItem('1'))
                self.setCellWidget(0,2, QCheckBox())
                    
            def addRow(self):
                self.nrow = self.nrow + 1
                self.setRowCount(self.nrow)
                self.setItem(self.nrow-1, 0, QTableWidgetItem('100.0'))
                self.setItem(self.nrow-1, 1, QTableWidgetItem('1'))
                self.setCellWidget(self.nrow-1, 2, QCheckBox())
                
            def getTable(self):
                res0 = np.zeros(self.nrow)
                zones = np.zeros(self.nrow, dtype=int)
                fixed = np.zeros(self.nrow, dtype=bool)
                for j in range(self.nrow):
                    res0[j] = float(self.item(j,0).text())
                    zones[j] = int(self.item(j,1).text())
                    fixed[j] = self.cellWidget(j,2).isChecked()
                return res0, zones, fixed
            
            def reset(self):
                self.nrow = 1
                self.setRowCount(1)
        
        
        instructionLabel = QLabel('To define a region, just click on the mesh'
           ' to draw a polygon. Close the polygon using a left click. Once done'
           ', you can define the region resistivity in the table. To define a'
           ' new region, just press \'e\'')
        instructionLabel.setWordWrap(True)
        meshLayout.addWidget(instructionLabel)
        
        mwMesh = MatplotlibWidget(navi=True)
        
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
        
        regionLayout = QVBoxLayout()
        regionLayout.addWidget(regionTable)
        
        meshPlot = QWidget()
        meshPlotLayout = QHBoxLayout()
        meshPlotLayout.addWidget(mwMesh, 80)
        meshPlotLayout.addLayout(regionLayout, 20)
        meshPlot.setLayout(meshPlotLayout)
        
        meshOutputStack = QStackedLayout()
        meshOutputStack.addWidget(meshLogText)
        meshOutputStack.addWidget(meshPlot)
        meshOutputStack.setCurrentIndex(0)
        
        meshLayout.addLayout(meshOutputStack, 80)
        
        
        
        
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
                          'obtain realistic simulation results.')
        seqLabel.setWordWrap(True)
        
        class SequenceTable(QTableWidget):
            def __init__(self):
                nrow, ncol = 1, 2
                super(SequenceTable, self).__init__(nrow, ncol)
                self.nrow = nrow
                self.ncol = ncol
                self.setColumnCount(self.ncol)
                self.setRowCount(self.nrow)
                self.headers = ['Skip', 'Levels']
                self.setHorizontalHeaderLabels(self.headers)
                self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.setItem(0,0,QTableWidgetItem('0'))
                self.setItem(0,1,QTableWidgetItem('10'))

            
            def addRow(self):
                self.nrow = self.nrow + 1
                self.setRowCount(self.nrow)
                
            def getTable(self):
                table = np.zeros((self.nrow, self.ncol))
                for i in range(self.ncol):
                    for j in range(self.nrow):
                        table[j,i] = int(self.item(j,i).text())
                return table
            
            def reset(self):
                self.nrow = 1
                self.setRowCount(1)
        
        seqTable = SequenceTable()
        seqReset = QPushButton('Reset')
        seqReset.setAutoDefault(True)
        seqReset.clicked.connect(seqTable.reset)
        seqAddRow = QPushButton('Add Row')
        seqAddRow.setAutoDefault(True)
        seqAddRow.clicked.connect(seqTable.addRow)
        def seqCreateFunc():
            skipDepths = [tuple(a) for a in list(seqTable.getTable())]
            print(skipDepths)
            self.r2.createSequence(skipDepths=skipDepths)
            seqOutputLabel.setText(str(len(self.r2.sequence)) + ' quadrupoles generated')
        seqCreate = QPushButton('Create Sequence')
        seqCreate.setAutoDefault(True)
        seqCreate.clicked.connect(seqCreateFunc)
        seqOutputLabel = QLabel('')
    
        # add noise possibility
        noiseLabel = QLabel('Guassian noise to be added to the simulated data:')
        noiseEdit = QLineEdit('0.05')
        noiseEdit.setValidator(QDoubleValidator())
        
        # add a forward button
        def forwardBtnFunc():
            forwardOutputStack.setCurrentIndex(0)
            forwardLogText.clear()
            QApplication.processEvents()
            # apply region for initial model
            if self.r2.mesh is None: # we need to create mesh to assign starting resistivity
                self.r2.createMesh()
            x, zones, fixed = regionTable.getTable()
            regid = np.arange(len(x))
            self.r2.assignRes0(dict(zip(regid, x)),
                               dict(zip(regid, zones)),
                               dict(zip(regid, fixed)))
            noise = float(noiseEdit.text())
            self.r2.forward(noise=noise, iplot=False, dump=forwardLogTextFunc)
            forwardPseudo.plot(self.r2.surveys[0].pseudo)
        forwardBtn = QPushButton('Forward Modelling')
        forwardBtn.setAutoDefault(True)
        forwardBtn.clicked.connect(forwardBtnFunc)
                
        forwardPseudo = MatplotlibWidget(navi=True)
        
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
        seqBtnLayout = QVBoxLayout()
        seqBtnLayoutH = QHBoxLayout()
        noiseLayout = QHBoxLayout()
        
        seqBtnLayoutH.addWidget(seqAddRow)
        seqBtnLayoutH.addWidget(seqReset)
        
        seqBtnLayout.addLayout(seqBtnLayoutH)
        seqBtnLayout.addWidget(seqCreate)
        seqBtnLayout.addWidget(seqOutputLabel)
        
        seqLayout.addWidget(seqTable)
        seqLayout.addLayout(seqBtnLayout)
        
        noiseLayout.addWidget(noiseLabel)
        noiseLayout.addWidget(noiseEdit)
        
        forwardLayout.addWidget(seqLabel, 5)
        forwardLayout.addLayout(seqLayout, 15)
        forwardLayout.addLayout(noiseLayout, 5)
        forwardLayout.addWidget(forwardBtn, 5)
        
        forwardOutputStack = QStackedLayout()
        forwardOutputStack.addWidget(forwardLogText)
        forwardOutputStack.addWidget(forwardPseudo)
        forwardOutputStack.setCurrentIndex(0)
        
        forwardLayout.addLayout(forwardOutputStack, 70)
        
        tabForward.setLayout(forwardLayout)
        
        #%% tab INVERSION SETTINGS
        tabInversionSettings = QTabWidget()
        tabs.addTab(tabInversionSettings, 'Inversion settings')

        # general tab
        generalSettings = QWidget()
        generalLayout = QHBoxLayout()
        invForm = QFormLayout()
        
        # advanced tab
        advancedSettings = QWidget()
        advancedLayout = QHBoxLayout()
        advForm = QFormLayout()
        
        def showIpOptions(arg):
            opts = [c_wgt, c_wgtLabel, d_wgt, d_wgtLabel,
                    singular_type, singular_typeLabel,
                    res_matrix, res_matrixLabel]
            activeState = np.array([1, 1, 1, 1, 0, 0, 0, 0], dtype=bool)
            if arg == True:
                iopts = activeState
            else:
                iopts = ~activeState
            [o.setVisible(io) for o, io in zip(opts, iopts)]
        
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
        
        def modErrFunc(state):
            if state == Qt.Checked:
                self.modErr = True
            else:
                self.modErr = False
        modErrLabel = QLabel('<a href="modErr">Compute Modelling Error</a>')
        modErrLabel.linkActivated.connect(showHelp)
        modErr = QCheckBox()
        modErr.stateChanged.connect(modErrFunc)
        invForm.addRow(modErrLabel, modErr)
        self.modErr = False
        
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
        
        def data_typeFunc(index):
            self.r2.param['data_type'] = index
        data_typeLabel = QLabel('<a href="data_type">Data type</a>:')
        data_typeLabel.linkActivated.connect(showHelp)
        data_type = QComboBox()
        data_type.addItem('Normal [0]')
        data_type.addItem('Logarithmic [1]')
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
        
        def max_iterationsFunc():
            self.r2.param['max_iterations'] = int(max_iterations.text())
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
        error_mod.setCurrentIndex(1)
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
        
        def d_wgtFunc():
            self.r2.param['d_wgt'] = float(d_wgt.text())
        d_wgtLabel = QLabel('<a href="errorParam"><code>d_wgt</code></a>:')
        d_wgtLabel.linkActivated.connect(showHelp)
        d_wgtLabel.setVisible(False)
        d_wgt = QLineEdit()
        d_wgt.setValidator(QDoubleValidator())
        d_wgt.setText('2')
        d_wgt.editingFinished.connect(d_wgtFunc)
        d_wgt.setVisible(False)
        invForm.addRow(d_wgtLabel, d_wgt)
        
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
                                mwInvResult.plot(self.r2.showIter)
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
#                            print('new processing detected')
                            self.pindex = self.pindex + 1
#                            print('index = ', self.pindex)
                        if a[0] == 'End':
                            self.end = True
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
                
            # apply region for initial model
            if self.r2.mesh is None: # we need to create mesh to assign starting resistivity
                self.r2.createMesh()
            x, zones, fixed = regionTable.getTable()
            regid = np.arange(len(x))
            self.r2.assignRes0(dict(zip(regid, x)),
                               dict(zip(regid, zones)),
                               dict(zip(regid, fixed)))
            
            self.r2.invert(iplot=False, dump=func, modErr=self.modErr)
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
           
            if self.end is True:
#                try:
                plotSection()
                for i in range(len(self.r2.surveys)):
                    sectionId.addItem(self.r2.surveys[i].name)
                outStackLayout.setCurrentIndex(0)
                showDisplayOptions(True)
                btnInvert.animateClick() # simulate a click
#                except:
#                    pass
#                    printR2out()
            else:
                printR2out()
            
        
        def plotSection():
            mwInvResult.setCallback(self.r2.showResults)
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
            if self.r2.typ == 'R2':
                defaultAttr = 'Resistivity(log10)'
            if self.r2.typ == 'cR2':
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
                
        
        def replotSection():
#            print('replotSection')
            index = self.displayParams['index']
            edge_color = self.displayParams['edge_color']
            sens = self.displayParams['sens']
            attr = self.displayParams['attr']
            contour = self.displayParams['contour']
            vmin = self.displayParams['vmin']
            vmax = self.displayParams['vmax']
            mwInvResult.replot(index=index, edge_color=edge_color,
                               contour=contour, sens=sens, attr=attr,
                               vmin=vmin, vmax=vmax)
                    
        def msgBox(text):
            msg = QMessageBox()
            msg.setText(text)
            
        def setCBarLimit():
#            print('setCBarLimit')
            vmax = vmaxEdit.text()
            vmin = vminEdit.text()
            # ternary operations
            vmax = None if vmax == '' else float(vmax)
            vmin = None if vmin == '' else float(vmin)
            self.displayParams['vmin'] = vmin
            self.displayParams['vmax'] = vmax
            if contourCheck.isChecked() is True:
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
            self.r2.proc.kill()
            frozeUI(False)
            btnInvert.setText('Invert')
            btnInvert.setStyleSheet("background-color: green")
            btnInvert.clicked.disconnect()
            btnInvert.clicked.connect(btnInvertFunc)
            QApplication.processEvents()
        btnInvert = QPushButton('Invert')
        btnInvert.setStyleSheet("background-color: green")
        btnInvert.setAutoDefault(True)
        btnInvert.clicked.connect(btnInvertFunc)
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
#            print('displayAttribute arg = ', arg)
            self.attr = list(self.r2.meshResults[self.displayParams['index']].attr_cache)
#            print('list of attributes availables', self.attr)
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
#            print('end of displayAttribute')
        
        def changeAttribute(index):
#            print('changeAttribute', index)
            self.displayParams['attr'] = self.attr[index]
            vminEdit.setText('')
            vmaxEdit.setText('')
            replotSection()


        def changeSection(index):
#            print('changeSection')
            self.displayParams['index'] = index
            displayAttribute(arg=self.displayParams['attr'])
            replotSection()
            # find a way to keep the current display settings between section
            # without just replotting it here
#            mwInvResult.replot()
        
        displayOptions = QHBoxLayout()
            
        sectionId = QComboBox()
        displayOptions.addWidget(sectionId, 20)
        
        attributeName = QComboBox()
        displayOptions.addWidget(attributeName, 20)
        
        vminLabel = QLabel('Min:')
        vminEdit = QLineEdit()
        vminEdit.setValidator(QDoubleValidator())
#        vminEdit.textChanged.connect(setCBarLimit)
        vmaxLabel = QLabel('Max:')
        vmaxEdit = QLineEdit()
#        vmaxEdit.textChanged.connect(setCBarLimit)
        vmaxEdit.setValidator(QDoubleValidator())
        vMinMaxApply = QPushButton('Apply')
        vMinMaxApply.setAutoDefault(True)
        vMinMaxApply.clicked.connect(setCBarLimit)
        
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
        displayOptions.addWidget(sensCheck)
        
        def btnSaveGraphs():
            edge_color = self.displayParams['edge_color']
            sens = self.displayParams['sens']
            attr = self.displayParams['attr']
            contour = self.displayParams['contour']
            vmin = self.displayParams['vmin']
            vmax = self.displayParams['vmax']
            self.r2.saveInvPlots(edge_color=edge_color,
                               contour=contour, sens=sens, attr=attr,
                               vmin=vmin, vmax=vmax)
            infoDump('All graphs saved successfully in the working directory.')

        btnSave = QPushButton('Save graphs')
        btnSave.clicked.connect(btnSaveGraphs)
        displayOptions.addWidget(btnSave)
        
        def showDisplayOptions(val=True):
            opts = [sectionId, attributeName, vminEdit, vmaxEdit, vMinMaxApply, 
                    edgeCheck, contourCheck, sensCheck, btnSave]
            [o.setEnabled(val) for o in opts]
        
        showDisplayOptions(False) # hidden by default
        
        resultLayout = QVBoxLayout()
        resultLayout.addLayout(displayOptions, 20)
        
        mwInvResult = MatplotlibWidget(navi=True)
        resultLayout.addWidget(mwInvResult, 90)
        
#        invLayout.addLayout(resultLayout, 70)
        
        # in case of error, display R2.out
        r2outLayout = QVBoxLayout()

        r2outTitle = QLabel('<b>The Inversion did not succeeded. Please see below for more details.</b>')
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
        
        invError = QWidget()
        tabPostProcessing.addTab(invError, 'Inversion Errors (1)')
        invErrorLayout = QVBoxLayout()
        
        def plotInvError():
            mwInvError.plot(self.r2.pseudoError)
            
        mwInvError = MatplotlibWidget(navi=True)
        invErrorLayout.addWidget(mwInvError)
        invError.setLayout(invErrorLayout)

        
        invError2 = QWidget()
        tabPostProcessing.addTab(invError2, 'Inversion Errors (2)')
        invErrorLayout2 = QVBoxLayout()
        
        def plotInvError2():
            mwInvError2.plot(self.r2.showInversionErrors)
        mwInvError2 = MatplotlibWidget(navi=True)
        invErrorLayout2.addWidget(mwInvError2)
        invError2.setLayout(invErrorLayout2)
        
        
        #%% About tab
        
        tabAbout = QTabWidget()
        tabs.addTab(tabAbout, 'About')
        
        infoLayout = QVBoxLayout()
        aboutText = QLabel()
        aboutText.setText('''<h1>About pyR2</h1> \
                          <p><i>pyR2 is a free and open source software for inversion of geoelectrical data (DC and IP)</i></p> \
                          <p>If you encouter issues or would like to submit a feature request, please raise an issue on gitlab:</p> \
                          <p><a href="https://gitlab.com/sagitta1618/r2gui/issues">https://gitlab.com/sagitta1618/r2gui/issues</a></p> \
                          <p>pyR2 uses R2 and cR2 code from Andrew Binley:</p> \
                          <p><a href="http://www.es.lancs.ac.uk/people/amb/Freeware/R2/R2.htm">http://www.es.lancs.ac.uk/people/amb/Freeware/R2/R2.htm</a></p> \
                          <p>For generation of triangular mesh, pyR2 uses "Gmsh" software:</p> \
                          <p><a href="http://gmsh.info/">http://gmsh.info/</a></p>\
                          <p>Python packages used: scipy, numpy, pandas, matplotlib.
<ul>
<li>Jones E, Oliphant E, Peterson P, <em>et al.</em>
<strong>SciPy: Open Source Scientific Tools for Python</strong>, 2001-,
<a class="reference external" href="http://www.scipy.org/">http://www.scipy.org/</a> [Online; accessed 2018-10-02].
</li>
<li>
 Wes McKinney.
<strong>Data Structures for Statistical Computing in Python</strong>,
Proceedings of the 9th Python in Science Conference, 51-56 (2010)
(<a class="reference external" href="http://conference.scipy.org/proceedings/scipy2010/mckinney.html">publisher link</a>)
</li>
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
<br/>
                          <p><strong>pyR2's core developers: Guillaume Blanchy, Sina Saneiyan and Jimmy Boyd.<strong></p>''')
        aboutText.setOpenExternalLinks(True)
        aboutText.setWordWrap(True)
        aboutText.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        infoLayout.addWidget(aboutText)
        
        tabAbout.setLayout(infoLayout)
        
        #%% general Ctrl+Q shortcut + general tab layout
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
    progressBar.setValue(2)
    app.processEvents()

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
    
    from api.R2 import R2
    from api.r2help import r2help
    progressBar.setValue(10)
    app.processEvents()
    
    ex = App()
    splash.hide() # hiding the splash screen when finished
    
    sys.exit(app.exec_())



#%%
#table = QTableWidget(10, 3)
#table.setVisible(False)
#table.setItem(0,0,QTableWidgetItem('4.3'))
#table.setItem(1,1,QTableWidgetItem('2.3'))
#print(table.item(0,0).text())
