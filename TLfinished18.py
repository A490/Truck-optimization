# -*- coding: utf-8 -*-
"""
Created on Fri May 15 17:48:03 2020

@author: Alessandro Avolio & Leonardo Castellini
"""
#0-1 knapsack problem. We have a maximum number of avaiable trucks with a limited capacity.
# We have an Y demand of X products (sold in pallets) with their Z volume. We have to find
# the optimal number of trucks to being able to deliver all of our products.

import pyomo.environ as pe

####################### ABSTRACT MODEL #################################
TL = pe.AbstractModel (name = 'Truck loading')
#pallet set 
TL.pallet = pe.Set()
#pallet volume (cubic meters)
TL.vol = pe.Param (TL.pallet)
#pallets' demand
TL.qta = pe.Param (TL.pallet)
#tir set
TL.tir = pe.Set()
#trucks' maximum capacity (cubic meters)
TL.maxcap = pe.Param()
#0-1 variable for trucks (used/not used)
TL.y = pe.Var (TL.tir, within = pe.Binary)
#quantity matrix of i pallet in j truck, pallets being non partitionable
TL.x = pe.Var (TL.pallet, TL.tir, within = pe.NonNegativeIntegers)

#objective function, minimize trucks
def mintir_rule (m):
    return sum (m.y[j] for j in m.tir)
TL.mintir = pe.Objective (rule = mintir_rule)


#capacity constraint, each truck cannot be filled more than a given number.
def maxload_rule(m, j):
    return sum(m.x[i,j]*m.vol[i] for i in m.pallet) <= m.y[j]*m.maxcap
TL.maxload= pe.Constraint(TL.tir, rule= maxload_rule)

#quantity demand constraint, delivered pallets must be demanded pallets
def qtaric_rule(m, i):
    return sum(m.x[i,j] for j in m.tir)== m.qta[i]
TL.qtaric= pe.Constraint(TL.pallet, rule= qtaric_rule)

######################## MODEL INSTANTIATION AND SOLUTION ################
#instantiation
I_TL = TL.create_instance('TLDATIfinished.dat')

cap_nec= 0
num_truck=0
for j in I_TL.y:
    num_truck += 1
    
for i in I_TL.pallet:
    cap_nec += I_TL.qta[i]*I_TL.vol[i]
if cap_nec >= I_TL.maxcap*num_truck:
    print('Input not valid, add', round(cap_nec/I_TL.maxcap)-num_truck,
          'trucks or increase their capacity by', (cap_nec/num_truck)-I_TL.maxcap+1)
else:
    #solver call
    solver = pe.SolverFactory('glpk')
    solver.options["cuts"]=""
    res = solver.solve (I_TL)
    #res.write()
    #I_TL.pprint()
    ######################## PRINT DEVELOPMENT ###################################### 
    #creation of a dynamic list to index trucks, plus active trucks count
    name=[]
    cont=0
    for j in I_TL.tir:
        if I_TL.y[j].value==1:
            cont += 1
            name.append(str(cont))
    
    print('The optimal number of trucks is:',
          str(round(sum(I_TL.y[j].value for j in I_TL.tir))) +'.')
    
    #print and analysis of pallets and their quantity in each truck, with units and volume sum.
    cont2=0
    for j in I_TL.tir:
        if I_TL.y[j].value==1:
            print('Truck',name[cont2],'should carry:\n')
            for i in I_TL.pallet:
                if I_TL.x[i,j].value>0:
                    print(round(I_TL.x[i,j].value), 'units of', i)
            print('\nFor a total of', round(sum(I_TL.x[i,j].value for i in I_TL.pallet)),
                  'units, that occupy',
                  round(sum(I_TL.x[i,j].value*I_TL.vol[i] for i in I_TL.pallet), 2),
                  'cubic meters of volume.')
            cont2 += 1
            
    #print and analysis of total delivered volume sum, with utilization coefficent        
    somma = 0
    for j in I_TL.tir:
        if I_TL.y[j].value==1:
            somma += round(sum(I_TL.x[i,j].value*I_TL.vol[i] for i in I_TL.pallet), 3)
    c_ut= round(somma/(cont*I_TL.maxcap),3)
    print('\nTotal delivered volume is', str(round(somma,2))+
          'm3, with an utilization coefficent of', str(round(c_ut*100,2))+'%')
    
                
    
    



