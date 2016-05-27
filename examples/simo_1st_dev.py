import time
import datetime
import numpy as np
import sys
from multiprocessing import Pool
sys.path.append("../backend/")

import materials
import objects
import mode_calcs
import integration
import plotting
from fortran import NumBAT


unitcell_x = 2.5*1550
inc_a_x = 314.7
unitcell_y = unitcell_x
inc_a_y = 0.9*inc_a_x
inc_shape = 'rectangular'

### Optical parameters
eps = 12.25

wl_nm = 1550
num_EM_modes = 30

### Acoustic parameters
s = 2330  # kg/m3

c_11 = 165.7  # GPa
c_12 = 63.9  # GPa
c_44 = 79.6  # GPa

p_11 = -0.044
p_12 = 0.017
p_44 = -0.051

eta_11 = 5.9  # m Pa s
eta_12 = 5.16  # m Pa s
eta_44 = 620  # mu Pa s

# wguide = objects.Struct(unitcell_x,inc_a_x,unitcell_y,inc_a_y,inc_shape,
#                         bkg_material=materials.Material(1.0 + 0.0j),
#                         inc_a_material=materials.Material(np.sqrt(eps)),
#                         lc_bkg=0.09, lc2=1.0, lc3=1.0, check_msh=False)

# sim_wguide = wguide.calc_modes(wl_nm, num_EM_modes)
# np.savez('wguide_data', sim_wguide=sim_wguide)
npzfile = np.load('wguide_data.npz')
sim_wguide = npzfile['sim_wguide'].tolist()

# betas = sim_wguide.k_z
# print 'k_z of EM wave \n', betas
# plotting.plot_EM_modes(sim_wguide)

# # Test overlap
# nel = sim_wguide.n_msh_el
# type_el = sim_wguide.type_el
# table_nod = sim_wguide.table_nod
x_arr = sim_wguide.x_arr
# nnodes = 6
# xel = np.zeros((2,nnodes))
# nod_el_p = np.zeros(nnodes)
# xx = [0,0]
# nquad = 16
# [wq, xq, yq] = integration.quad_triangle(nquad)

# integrand = 0.0
# print np.shape(sim_wguide.sol1)

# for ival in [0]:
# # for ival in range(len(sim_wguide.k_z)):
#     NumBAT.EM_mode_energy_int()

n_msh_el = sim_wguide.n_msh_el
type_el = sim_wguide.type_el
table_nod = sim_wguide.table_nod
n_msh_pts = sim_wguide.n_msh_pts
print 'n_msh_el', n_msh_el
print 'n_msh_pts', sim_wguide.n_msh_pts
print 'table_nod', np.shape(table_nod)
# print table_nod[0]
print 'x_arr', np.shape(x_arr)
print 'type_el', np.shape(type_el)

# find triangles associated with node
# find triangles type
# if types not all equal -> node on interface
# for node in range(1,sim_wguide.n_msh_pts+1):
#     print np

# bkg_el_type = 1
interface_nodes = []
edge_el_list = []
node_array = -1*np.ones(n_msh_pts)
### Find nodes that are in elements of various types
### and find elements that have multiple nodes of various types
### ie. are not single verticies on an interface.
for el in range(n_msh_el):
    el_type = type_el[el]
    for i in range(6):
        node = table_nod[i][el] 
        # Check if first time seen this node
        if node_array[node - 1] == -1: # adjust to python indexing
            node_array[node - 1] = el_type 
        else:
            if node_array[node - 1] != el_type:
                interface_nodes.append(node)
                ## line below is redundant because elements sorted by type w type 1 first
                # if el_type is not bkg_el_type: 
                edge_el_list.append(el)

interface_nodes = list(set(interface_nodes))
print interface_nodes
# print edge_el_list
# edge_els_multi_nodes = list(set(edge_els_multi_nodes))
from collections import Counter
edge_els_multi_nodes = [k for (k,v) in Counter(edge_el_list).iteritems() if v > 1]
print edge_els_multi_nodes

count = 0
for el in edge_els_multi_nodes:
    # neighbouring nodes
    for [n1,n2] in [[0,3],[3,1],[1,4],[4,2],[2,5],[5,0]]:
        node0 = table_nod[n1][el]
        node1 = table_nod[n2][el]
        if node0 in interface_nodes and node1 in interface_nodes:
            count += 1
            x1 = x_arr[0,table_nod[n1][el] - 1]
            y1 = x_arr[1,table_nod[n1][el] - 1]
            x2 = x_arr[0,table_nod[n2][el] - 1]
            y2 = x_arr[1,table_nod[n2][el] - 1]
            normal_vec = [y2-y1, -(x2-x1)]
            normal_vec_norm = normal_vec/np.linalg.norm(normal_vec)
            # print normal_vec
            all_el_w_node0 = np.where(table_nod[:] == node0)
            all_el_w_node1 = np.where(table_nod[:] == node1)
            all_el_w_node0 = [list(set(all_el_w_node0[0])), list(set(all_el_w_node0[1]))]
            all_el_w_node1 = [list(set(all_el_w_node1[0])), list(set(all_el_w_node1[1]))]
            all_el_w_node0 = [item for sublist in all_el_w_node0 for item in sublist]
            all_el_w_node1 = [item for sublist in all_el_w_node1 for item in sublist]
            all_el_w_nodes = all_el_w_node0 + all_el_w_node1
            all_el_w_node0_and_node1 = [k for (k,v) in Counter(all_el_w_nodes).iteritems() if v > 1]
            
            print el
            print all_el_w_node0_and_node1
            out_side_el = all_el_w_node0_and_node1.remove(el)
            print all_el_w_node0_and_node1


    # print count

# import matplotlib
# matplotlib.use('pdf')
# import matplotlib.pyplot as plt
# # plt.figure(figsize=(13,13))
# # count = 0
# interface_nodes2 = []
# for el in [0,1,2,3,4,5,6,7,8]:#edge_els_multi_nodes:
#     plt.clf()
#     # below is incorrect - need to include all possible combinations of the elements nodes
#     for i in range(0,6):
#         print table_nod[i][el] - 1
#         x = x_arr[0,table_nod[i][el] - 1]
#         y = x_arr[1,table_nod[i][el] - 1]
#         print 'x1 = ', x_arr[0,table_nod[i][el] - 1]
#         print 'y1 = ', x_arr[1,table_nod[i][el] - 1]
#         plt.plot(x, y, 'o')
#         plt.text(x+0.001, y+0.001, str(i))
#     plt.savefig('triangle_%i.png' %el)




### Calc Q_photoelastic Eq. 33
### Calc Q_deformation_pol Eq. 36
### Calc Q_moving_boundary Eq. 41 