#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 30 20:09:24 2018

@author: jkl
"""

import numpy as np


def write2in(param, dirname):
    ''' write R2.in file
    param = dictionnary of the parameters
    '''
    
    # check
    if 'mesh' not in param:
        raise Exception('Need mesh to write configuration file')
    
    # default
    dparam = {
            'lineTitle':'My beautiful survey',
            'job_type':1,
            'mesh_type':4, # meshx, meshy, topo should be defined
            'flux_type':3,
            'singular_type':1,
            'res_matrix':1,
            'scale':1, # only used for triangular mesh
            'num_regions':1,
            'regions':None, # should be defined by the number of element in the mesh
            'patchx':1,
            'patchy':1,
            'inverse_type':1,
            'target_decrease':1,    
            'data_type':0,
            'reg_mode':1,
            'tol':1e-5,
            'max_iter':10,
            'error_mod':0,
            'alpha_aniso':1,
            'a_wgt':0.01,
            'b_wgt':0.02,
            'rho_min':-1000,
            'rho_max':-1000,
            'num_poly':5,
            'xy_poly_table':np.zeros((5,2)),
            'num_elec':None, #should be define when importing data
            'elec_node':None # should be define when building the mesh
            }
    
    
    # check if values are missing
    for a in dparam:
        if a not in param: # parameter missing
            param[a] = dparam[a]
    
    
    # create text for R2.in
    content = ''
    content = content + '{}\n\n'.format(param['lineTitle'])
    content = content + '{}\t{}\t{}\t{}\t{}\n\n'.format(
                        param['job_type'],
                        param['mesh_type'],
                        param['flux_type'],
                        param['singular_type'],
                        param['res_matrix'])
    if param['mesh_type'] == 4: # quadrilateral mesh
        meshx = param['meshx']
        meshy = param['meshy']
        topo = param['topo']
        content = content + '\t{}\t{}\t<< numnp_x, numnp_y\n\n'.format(
                len(meshx), len(meshy))
        content = content + '\t' + ' '.join(['{:.4f}']*len(meshx)).format(*meshx) + '<< xx \n\n'
        content = content + '\t' + ' '.join(['{:.4f}']*len(topo)).format(*topop) + '<< topo \n\n'        
        content = content + '\t' + ' '.join(['{:.4f}']*len(meshy)).format(*meshy) + '<< yy \n\n'
    elif param['mesh_type'] == 3:
        content = content + '{}  << scale for triangular mesh\n\n'.format(param['scale'])
    else:
        print('NOT IMPLEMENTED')
    content = content + '{} << num_regions\n'.format(param['num_regions'])
    if param['num_regions'] > 0:
        content = content + ''.join(['\t{}\t{}\t{} << elem_1, elem_2, value\n']*len(param['regions'])).format(param['regions'].flatten())
    if param['job_type'] == 1 & param['mesh_type'] == 4|5:
        content = content + '\t{}\t{}\t<< no. patches in x, no. patches in z\n\n'.format(
                param['patchx'], param['patchy'])
    
    content = content + '{}\t{}\t<< inverse_type, target_decrease\n\n'.format(
            param['inverse_type'],
            param['target_decrease'])    
    content = content + '{}\t{}\t<< data type (0=normal;1=log), regularization type\n\n'.format(
            param['data_type'],
            param['reg_mode'])
    content = content + '{}\t{}\t{}\t{}\t<< tolerance, max_iterations, error_mod, alpha_aniso\n\n'.format(
            param['tol'],
            param['max_iter'],
            param['error_mod'],
            param['alpha_aniso'])
    content = content + '{}\t{}\t{}\t{}\t<<  a_wgt, b_wgt, rho_min, rho_max\n\n'.format(
            param['a_wgt'],
            param['b_wgt'],
            param['rho_min'],
            param['rho_max'])
    content = content + '{}\t<< num_poly\n'.format(param['num_xy_poly'])
    content = content + ''.join(['{}\t{}\n']*len(param['xy_poly_table'])).format(
            param['xy_poly_table'].flatten())
    content = content + '{}\t<< num_electrodes\n'.format(param['num_elec'])
    content = content + ''.join(['{}\t{}\n']*len(param['node_elec'])).format(
            param['node_elec'].flatten())
    content = content + '\n'
    

    # write configuration file
    with open(dirname + '/R2.in','w') as f:
        f.write(content)
    
    
    return content


#%% test code
content = write2in(param={}, dirname='.')

