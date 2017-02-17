#!/usr/bin/python

from gurobipy import *

try:

    # Create a new model
    m = Model("Generalized Cable Trench Problem")

    # ---- Define INPUT ----

    cp = 1.0 # Cable Price
    tp = 0.5 # Trench Price

    #Number of Verticies ( V1 == ROOT )
    v = 7

    # e = Edges
    e = [(1, 2), (1, 3), (1, 7), (2, 4), (3, 4), (3, 5), (3, 6), (3, 7), (4, 5), (5, 6), (6, 7)]

    #To be used in the Generalized CTP ( Use wy = wt in the simple version )
    #Trench Distances ( cost_edge_trench)
    wt = [50, 60, 60, 30, 30, 40, 40, 10, 30, 30, 39]
    wy = wt #Cable Distances cost_edge_cable

    # ---- Create Variables ----

    #  Create variables X ( For the Cables ) 0
    x = tupledict()

    for (i,j) in e:
        x[i,j] = m.addVar(name='x[%d,%d]'%(i,j))
        if i != 1:
            x[j,i] = m.addVar(name='x[%d,%d]'%(j,i))


    #  Create variables Y ( For the Trenches ) 1
    y = tupledict()

    for (i,j) in e:
        y[i,j] = m.addVar(vtype=GRB.BINARY, name='y[%d,%d]'%(i,j))

    # ---- Set objective ----

    # ( Edge(i,j) + Edge(j,i)) * cost_edge_cable(i,j)
    cableFactor = quicksum((x[e[i][0],e[i][1]] + (0 if e[i][0] == 1 else x[e[i][1],e[i][0]])) * wy[i] for i in range(len(e)))

    # Edge(i,j) * cost_edge_trench(i,j)
    trenchFactor = quicksum(y[e[i][0],e[i][1]] * wt[i] for i in range(len(e)))

    # ( cablePrice * sumCable ) + ( trenchPrice * sumTrench )
    m.setObjective( cp*(cableFactor) + tp*(trenchFactor), GRB.MINIMIZE)


    # ---- Add constraint ----

    #C.2
    sum_X_1j = x.sum(1,'*')
    m.addConstr(sum_X_1j == v - 1, "c.2[1]")

    #C.3
    for i in range(2,v+1):
        sum_X_ij = x.sum(i,'*')
        sum_X_ki = x.sum('*',i)
        m.addConstr(sum_X_ij - sum_X_ki == -1, name='c.3[%d]'%(i))

    #C.4
    sum_Y_ij = y.sum()
    m.addConstr(sum_Y_ij == v - 1, "c.4")

    #C.5
    for (i,j) in e:
        m.addConstr( (v - 1) * y[i,j] - x[i,j] - (0 if i == 1 else x[j,i])  >= 0 , name='c.5[%d]'%(i))

    #C.6
    for (i,j) in e:
        m.addConstr(x[i,j] >= 0, name='c.6[%d,%d]'%(i,j))
        if i != 1:
            m.addConstr(x[j,i] >= 0, name='c.6[%d,%d]'%(j,i))

    m.optimize()

    for v in m.getVars():
        print('%s %g' % (v.varName, v.x))

    print('Obj: %g' % m.objVal)

except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')
