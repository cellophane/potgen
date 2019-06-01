# -*- coding: utf-8 -*-
"""
Created on Fri May 31 22:36:21 2019

@author: jules
"""
import numpy as np
import numpy.ma as ma
import string
##generate all n-ominos. every rotation will be saved as its own omino. 
##returns a set
def generateOminos(n,current_omino=set(),ominos = set(), depth=0):
    if depth == 0:
        ominos = set()
        current_omino = set([(0,0)])
        generateOminos(n,current_omino,ominos,1)
        return ominos
    if depth > 0:
        #for each tile in the current omino, add a tile to all neighbors
        #recursively proceed until the omino is finished and add it to the set of all ominos
        for element in current_omino:
            for x in [-1,0,1]:
                #exclude diagonals from neighbors
                for y in [a for a in [-1,0,1] if abs(a)+abs(x)==1]:
                    new_element = (element[0]+x,element[1]+y)
                    if not new_element in current_omino:
                        new_omino = current_omino.copy()
                        new_omino.add(new_element)
                        if depth<n-1:
                            generateOminos(n,new_omino,ominos,depth+1)
                        if depth == n-1:
                            minX = 0
                            minY = 0
                            for aTile in new_omino:
                                minX = min(minX,aTile[0])
                                minY = min(minY,aTile[1])
                            add_omino = set()
                            for tile in new_omino:
                                add_omino.add((tile[0]-minX,tile[1]-minY))
                            ominos.add(frozenset(add_omino))
#generate an array with a row for each possible tile placement
#returns possibilityArray, a size[0]*size[1] X number of choices array,
  #rowIndices, the corresponding indexes and locations of the placement [ominoIndex, (x,y)]
  #columnCounts, a tally of how many nonzero elements there are in each column
         
def generatePossibilityArray(ominos,size,forTube=True):
    numColumns = size[0]*size[1]
    possibilityArray = []
    rowIndices = {}
    columnCounts = [0]*numColumns
    count  = 0
    for ominoIndex, omino in enumerate(list(ominos)):
        print(f"{ominoIndex} next omino in {len(ominos)}")
        for x in range(size[0]):
            for y in range(size[1]):
                
                canPlace = True
                
                for tile in omino:
                    if y+tile[1]>=size[1] or y+tile[1]<0:
                        canPlace = False
                    if forTube ==False:
                        if x+tile[0]>=size[0] or x+tile[0]<0:
                            canPlace = False
                if canPlace ==False:
                    continue
                row = [0]*numColumns
                rowIndices[count] = (ominoIndex,(x,y))
                count+=1
                for tile in omino:
                    
                    x1 = (x+tile[0])%size[0]
                    y1 = y+tile[1]
                    columnCounts[x1+y1*size[0]]+=1
                    row[x1+y1*size[0]]=1
                possibilityArray +=row
    possibilityArray = np.reshape(possibilityArray,(int(len(possibilityArray)/numColumns),numColumns))
    return possibilityArray,rowIndices,columnCounts
def findSolution1(possibilityArray,columnCounts,activeRows=[],activeColumns=[],choices =[],depth=0, solutions = set()):
    #print(depth)
    if depth ==0:
        solutions = set()
        shape = np.shape(possibilityArray)
        activeColumns = [0]*shape[1]
        activeRows = [0]*shape[0]
        choices = []
        findSolution1(possibilityArray, columnCounts, activeRows,activeColumns, choices,1, solutions)
        return solutions
    if depth>0:
        #solution found
        if min(activeColumns)==1:
            solutions.add(tuple(choices))
            print(choices)
            print(len(solutions))
            return
        if min(activeRows)==1:
            return
        #choose the active column with the least number of ones in it 
        possibleChoice = ma.masked_array(columnCounts,mask=activeColumns)
        columnChoice = np.argmin(possibleChoice)
        #set the column choice to no longer be active
        rowChoices = [i for i,r in enumerate(activeRows) if r==0]
        #iterate through the active rows, we will choose each of them in succession
        for row in rowChoices:
            #if the cell has a one, we pick it
            if possibilityArray[row][columnChoice] ==1:
                
                #any row that has a 1 in the column we chose cannot be considered, since that column is covered
                rowsToRemove = []
                for i in [i for i,r in enumerate(possibilityArray[:,columnChoice]) if r==1]:
                    if activeRows[i]==0:
                        rowsToRemove.append(i)
                        activeRows[i] = 1
                    #decrement the column count for the eliminated rows
                        for c in [j for j,c in enumerate(possibilityArray[i,:]) if c==1]:
                            if activeColumns[c]==0:
                                columnCounts[c]-=1
                #any column that is covered by the chosen row cannot be considered
                columnsToRemove = []
                for i in [i for i,c in enumerate(possibilityArray[row,:]) if c==1]:
                    if activeColumns[i]==0:
                        columnsToRemove.append(i)
                        activeColumns[i] = 1
                    #any row in a column covered by the row also cannot be considered
                    for r in [i for i,r in enumerate(possibilityArray[:,i]) if r==1]:
                        if activeRows[r]==0:
                            rowsToRemove.append(r)
                            activeRows[r] = 1
                            for c in [j for j,c in enumerate(possibilityArray[r,:]) if c==1]:
                                if activeColumns[c]==0: 
                                    columnCounts[c]-=1
                choices.append(row)
                #recursively choose the next row
                findSolution1(possibilityArray,columnCounts,activeRows,activeColumns,choices,depth+1, solutions)
                #undo the last choice
                choices.pop()
                for r in rowsToRemove:
                    activeRows[r] = 0
                    for i in [i for i,c in enumerate(possibilityArray[r,:]) if c==1]:
                        columnCounts[i]+=1
                for c in columnsToRemove:
                    activeColumns[c] = 0
        
                    
        
        
            

#print an ascii representation of the tiling
def printOminoSet(omino_set,size,n):
    #print("Printing omino set.")
    grid = ominoArray(omino_set,size,n)
    characters = string.ascii_lowercase+string.ascii_uppercase
    for x in range(size[0]):
        curString = ""
        for y in range(size[1]):
            if grid[x][y]==0:
                print('bad')
                return
            curString+=characters[grid[x][y]%len(characters)]
        print(curString)


#turn an omino set into an array
def ominoArray(omino_set,size,n):
    ominoList = list(generateOminos(n))
    grid = np.zeros(size,dtype = int)
    count = 1
    
    for ominoIndex,coord in omino_set:
        count+=1
        omino = ominoList[ominoIndex]
        for tile in omino:
            grid[(tile[0]+coord[0])%size[0]][tile[1]+coord[1]] = count
    return grid                   
ominoSize = 5
size = [10,10]
ominos=generateOminos(ominoSize)    
possibilityArray,rowIndices,columnCounts = generatePossibilityArray(ominos,size)
print(len(columnCounts))
solutions = findSolution1(possibilityArray,columnCounts)

for omino_set in solutions:
    
    
    ominos = set()
    for i in omino_set:
        ominos.add(rowIndices[i])
    if len(ominos)==size[0]*size[1]/ominoSize:
        printOminoSet(ominos,size,ominoSize)