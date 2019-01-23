#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 11:34:56 2019

@author: jkl

RUN ALL SECTION ON THE TEST AND CHECK THE GRAPH PRODUCED
"""

import numpy as np
import os
import matplotlib.pyplot as plt

testdir = 'api/test/image/'

#%% testing the Survey class
from api.Survey import Survey




#%% testing the meshTools class
import api.meshTools as mt

print(' -------------- Testing importing vtk --------------')
fresults = os.path.join('./api/test/f001.vtk')
mesh = mt.vtk_import(fresults)#makes a dictionary of a mesh 
assert mesh.elm_centre[0][0] == 16.442
assert np.array(mesh.con_matrix).shape[1] == 1362
mesh.show()



#%% testing the R2 class
from api.R2 import R2

print('-------------Testing simple 2D inversion ------------')
k = R2()
assert k.typ == 'R2'
k.createSurvey('./api/test/syscalFile.csv', ftype='Syscal')
assert len(k.surveys) == 1
assert k.surveys[0].df.shape == (308, 18)
assert np.sum(k.elec[:,2]) == 0 # no z topography by default
assert np.sum(k.elec[:,1]) == 0 # no y topography by default
k.pseudo(contour=True)
topo = np.genfromtxt('./api/test/elecTopo.csv', delimiter=',')
k.elec[:,[0,2]] = topo[:,[0,1]]
k.createMesh(typ='quad',cl=0.1, cl_factor=5)
k.showMesh()
k.createMesh(typ='trian')
k.showMesh()
k.pwlfit()
k.linfit()
#k.lmefit(iplot=True)
k.write2in()
k.write2protocol(errTyp='pwl', errTot=True)
k.invert()
k.showResults()

#%%
print('-------------Testing borehole------------')
k = R2()
k.createSurvey('./api/test/protocolXbh.dat', ftype='Protocol')
x = np.genfromtxt('./api/test/elecXbh.csv', delimiter=',')
k.elec[:,[0,2]] = x[:,:2]
buried = x[:,2].astype(bool)
k.createMesh('trian', buried=buried, cl=0.5, cl_factor=20)
k.showMesh()
k.createMesh('quad', buried=buried, elemx=12)
k.showMesh()
k.invert()
k.showIter(index=0)
k.showIter(index=1)
k.showResults(sens=False)

#%% test for IP

print('-------------Testing IP ------------')
k = R2(typ='cR2')
#k.createSurvey('api/test/IP/rifleday8.csv', ftype='Syscal')
k.createSurvey('api/test/IP/syscalFileIP.csv')
k.createMesh('quad')
k.invert()
k.showResults(attr='Magnitude(Ohm-m)', sens=False)
k.showResults(attr='Phase(mrad)', sens=False)
k.pseudoError()

#%% test for timelapse inversion

print('-------------Testing Time-lapse in // ------------')
k = R2()
k.createTimeLapseSurvey('api/test/testTimelapse')
k.linfit()
k.pwlfit()
k.errTyp = 'pwl'
k.param['a_wgt'] = 0
k.param['b_wgt'] = 0
k.invert(iplot=False, parallel=True)
k.saveInvPlots(attr='difference(percent)')
k.showResults(index=3)
k.showResults(index=1)


#%% test for batch inversion

print('-------------Testing Batch Inversion ------------')
k = R2()
k.createBatchSurvey('api/test/testTimelapse')
k.invert(parallel=True)
k.showResults(index=3)
k.showResults(index=1)


#%% test mesh with buried electrodes
#
#print('-------------Testing Buried electrodes Inversion ------------')
#k = R2()
#k.createSurvey('api/test/syscalFile.csv', ftype='Syscal')
#k.elec[:,2] = np.tile(np.arange(0,-12,-1),2)
#k.elec[:,0] = np.repeat([0,8], 12)
#k.elec[1:11,:2] = np.c_[np.ones(10)*2, np.linspace(0,-4,10)]
#buried = np.ones(k.elec.shape[0], dtype=bool)
#buried[[0,12]] = False
#surface = np.array([[-2,0],[10,0]])
#k.createMesh(typ='quad')
#k.showMesh()
#k.createMesh(typ='trian', buried=buried, cl=0.5, cl_factor=5) # works well
#k.showMesh()
#k.invert()
#k.showResults()
#
##%%
#k = R2()
#k.createSurvey('./api/test/syscalFile.csv')
#k.elec[3,1] = -1
#buried = np.zeros(k.elec.shape[0], dtype=bool)
#buried[3] = True
#k.createMesh('quad', buried=buried)
#k.invert()

#%% forward modelling

print('-------------Testing Forward Modelling ------------')
k = R2(typ='R2')
k.createSurvey('api/test/syscalFile.csv')
k.elec = np.c_[np.linspace(0,5.75, 24), np.zeros((24, 2))]
k.createMesh(typ='trian')
#
## full API function
k.addRegion(np.array([[1,0],[2,0],[2,-0.5],[1,-0.5],[1,0]]), 10, -3)
k.addRegion(np.array([[3,-0.5],[3.5,-0.5],[3.5,-1],[3,-1],[3,-0.5]]), 20, blocky=True, fixed=True)
k.addRegion(np.array([[4,0],[5,0],[5,-0.5],[4,-0.5],[4,0]]), 30, blocky=True, fixed=False)

## full GUI function
#k.createModel() # manually define 3 regions
#k.assignRes0({1:500, 2:20, 3:30}, {1:1, 2:2, 3:1}, {1:False, 2:False, 3:True})

k.forward(iplot=True, noise=0.05)
k.invert(iplot=True)

# the forward initial model
k.showResults(index=0, attr='Resistivity(Ohm-m)', sens=False) # not for cR2
k.showResults(index=0, attr='Phase(mrad)')
k.showResults(index=0, attr='Magnitude(Ohm-m)')

# the inverted
k.showResults(index=1, attr='Resistivity(Ohm-m)', sens=False) # not for cR2
k.showResults(index=1, attr='Phase(mrad)')
k.showResults(index=1, attr='Magnitude(Ohm-m)')


#%% test Paul River

print('-------------Testing Buried Electrodes in Fixed River ------------')
k = R2()
k.createSurvey('./api/test/primeFile.dat', ftype='BGS Prime')
x = np.genfromtxt('./api/test/primePosBuried.csv', delimiter=',')
k.elec[:,[0,2]] = x[:,:2]
surface = np.array([[0.7, 92.30],[10.3, 92.30]])
buried = x[:,2].astype(bool)
k.createMesh(typ='trian', buried=buried, surface=surface, cl=0.2, cl_factor=10)
#k.createMesh(typ='quad',buried=buried)
k.showMesh()
xy = k.elec[1:21,[0,2]]
k.addRegion(xy, res0=18, blocky=True, fixed=False)
k.param['b_wgt'] = 0.04 # doesn't work
k.invert()
k.showResults(sens=False)


#%% 3D testing

print('-------------Testing 3D inversion ------------')
k = R2(typ='R3t')
k.createSurvey('api/test/protocol3D.dat', ftype='Protocol')
elec = np.genfromtxt('api/test/electrodes3D.dat')
k.setElec(elec)
k.createMesh(cl=2)
k.invert()
k.showResults() 
k.meshResults[0].showSlice(axis='z')
k.meshResults[0].showSlice(axis='x')
k.meshResults[0].showSlice(axis='y')




