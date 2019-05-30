


import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import UnivariateSpline
import trimesh
import copy
import random
#random.seed(10204)
np.random.seed(10204)
##we would like to tile an arbitrary tube with n-ominos

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
                            ominos.add(frozenset(new_omino))
#helper functions to display n-ominos
def printOminos(ominos):
    for omino in ominos:
        printOmino(omino)
        print("next omino")
def printOmino(omino):
    minX = min([x[0] for x in omino])
    minY = min([y[1] for y in omino])
    maxX = max([x[0] for x in omino])
    maxY = max([y[1] for y in omino])
    grid = np.zeros((maxX-minX+1,maxY-minY+1))
    for block in omino:
        grid[block[0]-minX][block[1]-minY]=1
 
    for x in range(len(grid)):
        cStr = ""
        for y in range(len(grid[0])):
            if grid[x][y]!=0:
                cStr+="X"
            else:
                cStr+="."
        print(cStr)

##debug variable to count how many times a tile has been placed
placeCount = 0

#tileTube and tileRectangle are basically the same function,
#tileTube allows for the tiles to wrap around in the x direction.

#size is the size of the tube we are trying to tile
#n is the number of tiles in the omino
#quantity is the number of solutions we are trying to find
#the rest of the variables are used during recursion
    #ominos is the set of all n-sided ominos
    #grid is the state of the tiling, with 0 being empty and 1 full. 
    # it is passed by reference
    #omino_list is the current list of tiles placed in the format:
    # (index of omino in ominos, coordinate)
    #omino_sets is the set of complete tilings.
    #tried_set is not used currently but it is intended to prevent the same 
    #tile from being used in the same place in different solutions
def tileTube(size=[4,4],n=2,quantity=0, ominos = set(), grid = [], omino_list = [], omino_sets = set(), tried_set = set(), depth = 0):
    #check whether we have enough solutions. find all solutions if quantity ==0
    if quantity>0:
        if len(omino_sets)>=quantity:
            return
    #setup
    if depth == 0:
        ominos = generateOminos(n)
        tried_set = set()
        #place the first omino
        for i,omino in enumerate(ominos):
            canPlace = True
            for tile in omino:
#we can place any omino as long as it does not leave the board on top or bottom
                if tile[1]<0 or tile[1]>=size[1]:
                    canPlace = False
            if canPlace:
                #setup a new grid. 
                grid = np.zeros(size,dtype=int)
                for tile in omino:
                    #make the grid reflect the current omino
                    #we are wrapping around so we mod index 0
                    grid[tile[0]%size[0]][tile[1]]=1
                omino_list = [(i,(0,0))]
                #start recursion
                tileTube(size,n,quantity,ominos,grid,omino_list,omino_sets, tried_set, 1)
        return omino_sets
    
    if depth>0:
        #update the empty neighbors. this should be passed by reference but 
        #i didn't do it that way. would be a big speedup to just keep it updated
        #instead of regenerating it on every iteration

        empty_neighbors = set()
        for x in range(size[0]):
            for y in range(size[1]):
                if grid[x][y] == 1:         
                    for neighborX in [-1,0,1]:
                        for neighborY in [y for y in [-1,0,1] if abs(neighborX)+abs(y)==1]:
                            checkX  = x+neighborX
                            checkY = y+neighborY
                            try:
                                if grid[checkX%size[0]][checkY] == 0 and checkY>=0:
                                    empty_neighbors.add((checkX%size[0],checkY))
                            except:
                                pass
                            
        #if we have any empty neighbors we aren't done yet.
        if len(empty_neighbors)>0:
            #count the number of choices in tile placement we have for every
            #empty neighbor. we will always place an omino in the space with the 
            #fewest options first. 
            tileChoices = [0]*len(empty_neighbors)
            for neighborIndex,neighbor in enumerate(empty_neighbors):
                #variable to check whether we can place any omino. if we can't
                #there is a contradiction and we drop down a level in recursion
                canPlace = False
                #count the choices we have at this space
                choiceCount  = 0
                for i,omino in enumerate(ominos):
                    #keep track of whether this omino could go here.
                    tempCanPlace = True
                    for tile in omino:
                        try:
                            #don't wrap around in the y direction
                            if tile[1]+neighbor[1]<0:
                                tempCanPlace = False
                                break
                            #check is the space this tile would go in is occupied
                            if grid[(tile[0]+neighbor[0])%size[0]][tile[1]+neighbor[1]] != 0:
                                tempCanPlace = False
                                break
                        except:
                            #bad array index
                            tempCanPlace = False
                            break
                    if tempCanPlace:
                        #we don't have a contradiction 
                        canPlace = True
                        #increment the amount of choices we have at neighbor
                        choiceCount+=1
                #no solution
                if canPlace == False:
                    return
                
                tileChoices[neighborIndex]=choiceCount
                #magical list comprehension to give a sorted list of the indexes
                #of the neighbors with the least choices. from stackexchange
                tileChoices = [i for i, v in sorted(enumerate(tileChoices), key=lambda iv: iv[1])]
            #go through the empty spaces and put in ominos
            for neighbor in [list(empty_neighbors)[x] for x in tileChoices]:
                for i,omino in enumerate(ominos):
                    canPlace = True
                    for tile in omino:
                        try:
                            if tile[1]+neighbor[1]<0:
                                canPlace = False
                                break
                            if grid[(tile[0]+neighbor[0])%size[0]][tile[1]+neighbor[1]] != 0:
                                canPlace = False
                                break
                        except:
                            canPlace = False
                            break
                    if canPlace:
                        #update the grid to place the new tile
                        for tile in omino:
                            grid[(tile[0]+neighbor[0])%size[0]][tile[1]+neighbor[1]]=1
                        #add the index and coordinate to the omino_list
                        omino_list.append((i,neighbor))
                        #display the grid every 5000 iterations
                        global placeCount
                        placeCount+=1
                        if placeCount%5000 ==0:
                            print(grid)
                            print(countContiguousTube(grid,n))
                        #check whether all the contiguous empty regions have 
                        #a multiple of the omino size in area. if they don't, 
                        #this solution is impossible and we don't go deeper
                        if countContiguousTube(grid,n):
                            tileTube(size,n,quantity,ominos,grid,omino_list,omino_sets,tried_set, depth+1)
                        #take the last added tile back out of the list
                        omino_list.pop()
                        for tile in omino:
                            #clear the space the omino occupied.
                            grid[(tile[0]+neighbor[0])%size[0]][tile[1]+neighbor[1]]=0
                return
        #if we have no empty neighbors we have tiled the tube!
        if len(empty_neighbors)==0:
            omino_sets.add(frozenset(omino_list))
            

#i'm not going to write comments for this function. it's the same in every way as tileTube but without allowing x wraparound.
def tileRectangle(size=[4,4],n=2,quantity=0, ominos = set(), grid = [], omino_list = [], omino_sets = set(), tried_set = set(), depth = 0):
    #if depth = 0, setup board
    if quantity>0:
        if len(omino_sets)>=quantity:
            return
    if depth == 0:
        ominos = generateOminos(n)
        tried_set = set()
        for i,omino in enumerate(ominos):
            canPlace = True
            for tile in omino:
                if tile[0]<0 or tile[0]>=size[0] or tile[1]<0 or tile[1]>=size[1]:
                    canPlace = False
            if canPlace:
                grid = np.zeros(size,dtype=int)
                for tile in omino:
                    grid[tile[0]][tile[1]]=1
                omino_list = [(i,(0,0))]
                tileRectangle(size,n,quantity,ominos,grid,omino_list,omino_sets, tried_set, 1)
        return omino_sets
    if depth>0:

        empty_neighbors = set()
        for x in range(size[0]):
            for y in range(size[1]):
                if grid[x][y] == 1:         
                    for neighborX in [-1,0,1]:
                        for neighborY in [y for y in [-1,0,1] if abs(neighborX)+abs(y)==1]:
                            checkX  = x+neighborX
                            checkY = y+neighborY
                            try:
                                if grid[checkX][checkY] == 0 and checkX>=0 and checkY>=0:
                                    empty_neighbors.add((checkX,checkY))
                            except:
                                pass
        if len(empty_neighbors)>0:
            tileChoices = [0]*len(empty_neighbors)
            for neighborIndex,neighbor in enumerate(empty_neighbors):
                canPlace = False
                choiceCount  = 0
                for i,omino in enumerate(ominos):
                    tempCanPlace = True
                    for tile in omino:
                        try:
                            if tile[0]+neighbor[0]<0 or tile[1]+neighbor[1]<0:
                                tempCanPlace = False
                                break
                            if grid[tile[0]+neighbor[0]][tile[1]+neighbor[1]] != 0:
                                tempCanPlace = False
                                break
                        except:
                            tempCanPlace = False
                            break
                    if tempCanPlace:
                        canPlace = True
                        choiceCount+=1
                        
                if canPlace == False:
                    return
                tileChoices[neighborIndex]=choiceCount
                tileChoices = [i for i, v in sorted(enumerate(tileChoices), key=lambda iv: iv[1])]
            for neighbor in [list(empty_neighbors)[x] for x in tileChoices]:
                for i,omino in enumerate(ominos):
                    canPlace = True
                    for tile in omino:
                        try:
                            if tile[0]+neighbor[0]<0 or tile[1]+neighbor[1]<0:
                                canPlace = False
                                break
                            if grid[tile[0]+neighbor[0]][tile[1]+neighbor[1]] != 0:
                                canPlace = False
                                break
                        except:
                            canPlace = False
                            break
                    if canPlace and not (i,neighbor) in tried_set:
                        #print("before")
                        #print(grid)
                        for tile in omino:
                            grid[tile[0]+neighbor[0]][tile[1]+neighbor[1]]=1
                        omino_list.append((i,neighbor))
                        #debug variable
                        global placeCount
                        placeCount+=1
                        if placeCount%5000 ==0:
                            print(grid)
                            print(countContiguous(grid,n))
                        if countContiguous(grid,n):
                            tileRectangle(size,n,quantity,ominos,grid,omino_list,omino_sets,tried_set, depth+1)
                        omino_list.pop()
                        for tile in omino:
                            grid[tile[0]+neighbor[0]][tile[1]+neighbor[1]]=0
                return
        if len(empty_neighbors)==0:
            #printOminoSet(frozenset(omino_list),size,n)
            omino_sets.add(frozenset(omino_list))
            
#this function finds all the regions of empty space in the grid and 
#checks whether their area is a multiple of the domino size.
#a solution is only possible if this is the case
def countContiguous(grid,n):
    #this keeps track of the empty squares so that they are not double counted
    patchMembers = set()
    #this is a list of the sizes of the patches found.
    patchSizes = []
    
    #iterate over every space on the grid.
    size = np.shape(grid)
    for x in range(size[0]):
        for y in range(size[1]):
            #skip over spaces that are already full.
            if grid[x][y]!=0:
                continue
            #if we haven't counted this empty cell yet, start a new patch 
            #and add it to the set of cells we have seen.
            if not (x,y) in patchMembers:
                patchMembers.add((x,y))
                patchSize = 0
                #toCheck is the list of cells we need to look around
                toCheck = [(x,y)]
                #neighborList is the list of cells we have noticed already
                neighborList = [(x,y)]
                while len(toCheck)>0:
                    check = toCheck.pop()
                    #check if we found another cell in the empty patch
                    if grid[check[0]][check[1]]==0:
                        patchSize+=1
                        #keep track of it so we don't count it again
                        patchMembers.add((check[0],check[1]))
                        #check the orthogonal neighbors
                        for xCheck in [-1,0,1]:
                            for yCheck in [y for y in[-1,0,1] if abs(y)+abs(xCheck)==1]:
                                xNeighbor = xCheck+check[0]
                                yNeighbor = yCheck+check[1]
                                if xNeighbor<0 or yNeighbor<0 or xNeighbor>=size[0] or yNeighbor>=size[1]:
                                    continue
                                
                                if grid[xNeighbor][yNeighbor] == 0 and not (xNeighbor,yNeighbor) in neighborList:
                                    neighborList.append((xNeighbor,yNeighbor))
                                    toCheck.append((xNeighbor,yNeighbor))
                                    
                patchSizes.append(patchSize)
    for patchSize in patchSizes:
        if patchSize%n != 0:
            return False
    return True
#basically the same as countContiguous but with a wraparound
def countContiguousTube(grid,n):
    global placeCount
    if placeCount == 10000:
        print(grid)
    patchMembers = set()
    patchSizes = []
    
    size = np.shape(grid)
    for x in range(size[0]):
        for y in range(size[1]):
            if grid[x][y]!=0:
                continue
            if not (x,y) in patchMembers:
                patchMembers.add((x,y))
                patchSize = 0
                toCheck = [(x,y)]
                neighborList = [(x,y)]
                while len(toCheck)>0:
                    check = toCheck.pop()
                    if grid[check[0]%size[0]][check[1]]==0:
                        patchSize+=1
                        patchMembers.add((check[0]%size[0],check[1]))
                        for xCheck in [-1,0,1]:
                            for yCheck in [y for y in[-1,0,1] if abs(y)+abs(xCheck)==1]:
                                xNeighbor = xCheck+check[0]
                                yNeighbor = yCheck+check[1]
                                if yNeighbor<0 or yNeighbor>=size[1]:
                                    continue
                                if grid[xNeighbor%size[0]][yNeighbor] == 0 and not (xNeighbor%size[0],yNeighbor) in neighborList:
                                    neighborList.append((xNeighbor%size[0],yNeighbor))
                                    toCheck.append((xNeighbor%size[0],yNeighbor))
                                    
                patchSizes.append(patchSize)
    if placeCount%5000 == 0:
        print(patchSizes)
        print(placeCount)
    for patchSize in patchSizes:
        if patchSize%n != 0:
            return False
    
    return True                    
                    
            
import string
#turn an omino set into an array
def ominoArray(omino_set,size,n):
    ominoList = list(generateOminos(n))
    grid = np.zeros(size,dtype = int)
    count = 0
    
    for ominoIndex,coord in omino_set:
        count+=1
        omino = ominoList[ominoIndex]
        for tile in omino:
            grid[tile[0]+coord[0]][tile[1]+coord[1]] = count
    return grid

#print an ascii representation of the tiling
def printOminoSet(omino_set,size,n):
    print("Printing omino set.")
    grid = ominoArray(omino_set,size,n)
    characters = string.ascii_lowercase+string.ascii_uppercase
    for x in range(size[0]):
        curString = ""
        for y in range(size[1]):
            curString+=characters[grid[x][y]%len(characters)]
        print(curString)
#print all the tilings in a set of solutions
def printOminoSets(omino_sets,size,n):
    for omino_set in list(omino_sets):
        printOminoSet(omino_set,size,n)
#use matplotlib to plot a representation of a tiling
def plotOminoSet(omino_set,size,n):
    import numpy as np
    
    import matplotlib.pyplot as plt
    import matplotlib
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    yMin = 0
    xMin= 0
    yMax = size[1]
    xMax = size[0]
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    #plt.axes().set_aspect('equal')
    patches = []
    ominoList = list(generateOminos(n))
    for ominoIndex,coord in omino_set:
        omino = ominoList[ominoIndex]
        color=np.random.rand(3,)
        
        for tile in omino:
            center = ((tile[0]+coord[0])%size[0],tile[1]+coord[1])
            rect = Rectangle(center,1,1,color=color)
            patches.append(rect)
            ax.add_artist(rect)
    p = PatchCollection(patches)

    plt.ylim(yMin,yMax)
    plt.xlim(xMin,xMax)

    ax.add_collection(p)
    plt.show()
#Function to turn an n-omino tiling on a tube into a beveled mesh. 
#We will consider our coordinates to be the bottom left side of the square tiles.
#The bevel should exist on sides without a neighboring tile in the pentomino.
def createMesh(size, n, omino_set):
    ominos = generateOminos(n)
    vertices = []
    triangles = []
    baseTriangles = [(i,(i+1)%4,(i+1)%4+4) for i in range(4)]+[(i,(i+1)%4+4,i+4) for i in range(4)]+[(5,6,7),(5,7,4)]
    for i in range(len(omino_set)*5):
        for triangle in baseTriangles:
            triangles.append((triangle[0]+8*i,triangle[1]+8*i,triangle[2]+8*i))
    sideLength = 7
    bevelWidth = .2
    bevelHeight = .2
    for ominoIndex, coord in omino_set:
        omino = list(ominos)[ominoIndex]
        for tile in omino:
            bevelSides = []
            
            for x in [-1,0,1]:
                for y in [y for y in [-1,0,1] if abs(x)+abs(y)==1]:
                    if not (tile[0]+x,tile[1]+y) in omino:
                        bevelSides.append((x,y))
                        
            for x,y in [(0,0),(0,1),(1,1),(1,0)]:
                vertices.append((x+coord[0]+tile[0],y+coord[1]+tile[1],0))
            for x,y in [(0,0),(0,1),(1,1),(1,0)]:
                xOffset = 0
                yOffset = 0
                if x == 0:
                    if (-1,0) in bevelSides:
                        xOffset = bevelWidth
                elif (1,0) in bevelSides:
                    xOffset = -bevelWidth
                if y == 0:
                    if (0,-1) in bevelSides:
                        yOffset = bevelWidth
                elif (0,1) in bevelSides:
                    yOffset = -bevelWidth
                if xOffset == 0 and yOffset == 0:
                    if not (tile[0]+[-1,1][x],tile[1]+[-1,1][y]) in omino:
                        xOffset = [1,-1][x]*bevelWidth
                        yOffset = [1,-1][y]*bevelWidth
                vertices.append((x+xOffset+coord[0]+tile[0],y+yOffset+coord[1]+tile[1],bevelHeight))
    for i,vertex in enumerate(vertices):
        vertices[i]=[vertex[0]*sideLength,vertex[1]*sideLength,vertex[2]]
    mesh = trimesh.Trimesh(vertices=vertices,faces=triangles)
    mesh.export("test.stl")
#function to create a list of clockwise edges for an n-omino
def generateEdge(omino, coord = [0,0]):
    edges = set([])
    #start with a vertical edge
    for tile in omino:
        #look left
        if not (tile[0]-1,tile[1]) in omino:
            edges.add((tile,(tile[0],tile[1]+1)))
        #look up
        if not (tile[0],tile[1]+1) in omino:
            edges.add(((tile[0],tile[1]+1),(tile[0]+1,tile[1]+1)))
        #look right
        if not (tile[0]+1,tile[1]) in omino:
            edges.add(((tile[0]+1,tile[1]+1),(tile[0]+1,tile[1])))
        #look down
        if not (tile[0],tile[1]-1) in omino:
            edges.add(((tile[0]+1,tile[1]),(tile[0],tile[1])))
    collapsedEdges = []
    edgeStarts = [edge[0] for edge in list(edges)]
    edgeEnds = [edge[1] for edge in list(edges)]
    foundEnds = [edgeStarts[0],edgeEnds[0]]
    foundStarts = []
    currentEdge = list(edges)[0]
    #keep looking for edges that start with the end of the current edge.
    #if the new edge is in the same direction as the current edge, replace the
    #current edge to reflect that. otherwise append the finished edge to the list
    #and continue looking
    while len(foundEnds)>0:
        end = foundEnds.pop()
        for i, start in enumerate(edgeStarts):
            if start == end and not start in foundStarts:
                checkEdge = list(edges)[i]
                cXDiff = abs(currentEdge[0][0]-currentEdge[1][0])>0
                cYDiff = abs(currentEdge[0][1]-currentEdge[1][1])>0
                nXDiff = abs(checkEdge[0][0]-checkEdge[1][0])>0
                nYDiff = abs(checkEdge[0][1]-checkEdge[1][1])>0
                if cXDiff == nXDiff and cYDiff == nYDiff:
                    currentEdge = (currentEdge[0],checkEdge[1])
                    foundEnds.append(checkEdge[1])
                    foundStarts.append(edgeStarts[i])
                    break
                else:
                    collapsedEdges.append(currentEdge)
                    currentEdge = checkEdge
                    foundEnds.append(checkEdge[1])
                    foundStarts.append(edgeStarts[i])
                    break
    #connect the final edge
    currentEdge = (collapsedEdges[-1][1],collapsedEdges[0][0])
    checkEdge = collapsedEdges[0]
    cXDiff = abs(currentEdge[0][0]-currentEdge[1][0])>0
    cYDiff = abs(currentEdge[0][1]-currentEdge[1][1])>0
    nXDiff = abs(checkEdge[0][0]-checkEdge[1][0])>0
    nYDiff = abs(checkEdge[0][1]-checkEdge[1][1])>0
    if cXDiff == nXDiff and cYDiff == nYDiff:
        collapsedEdges[0] = (collapsedEdges[-1][1],collapsedEdges[0][1])
    else:
        collapsedEdges.append(currentEdge)
    return collapsedEdges
    
#a function to return a triangulated polygon
def triangulate(edges):
    def area(a,b,c):
        return abs((a[0]*(b[1]-c[1])+b[0]*(c[1]-a[1])+c[0]*(a[1]-b[1]))/2)
    def inside(triangle,point):
        a1 = area(triangle[0],triangle[1],point)
        a2 = area(triangle[1],triangle[2],point)
        a3 = area(triangle[2],triangle[0],point)
        a = area(triangle[0],triangle[1],triangle[2])
        if a1+a2+a3==a:
            return True
        return False
    vertices = []
    for edge in edges:
        vertices.append(edge[0])
    vertices.pop()
    print(vertices)
    triangles = []
    while len(vertices)>3:
        for i in range(len(vertices)):
            v1 = vertices[i]
            v2 = vertices[(i+1)%len(vertices)]
            v3 = vertices[(i+2)%len(vertices)]
            noneInside = True
            for check in [v for v in vertices if v!=v1 and v!=v2 and v!=v3]:
                if inside([v1,v2,v3],check):
                    print(f"[{v1},{v2},{v3}],{check}")
                    noneInside = False
                    break
            if noneInside:
                print(triangles)
                triangles.append([v1,v2,v3])
                print(triangles)
                vertices.pop(i)
                break
    triangles.append([vertices])
    print(triangles)
    return triangles
                
                    
    
            
size = [15,7]
n = 5
quantity = 10
ominos = generateOminos(5)
edges  = generateEdge(list(ominos)[1])
lines = list(edges)
triangles = triangulate(lines)



