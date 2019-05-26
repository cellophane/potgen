#reference : http://jwilson.coe.uga.edu/emt668/EMAT6680.F99/McCallum/WALLPA~1/SEVENT~1.HTM


import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import UnivariateSpline
import trimesh
import copy
import random
#random.seed(10204)
np.random.seed(10204)
##we would like to tile an arbitrary tube with n-ominos

##generate all n-ominos

def generateOminos(n,current_omino=set(),ominos = set(), depth=0):
    if depth == 0:
        ominos = set()
        current_omino = set([(0,0)])
        generateOminos(n,current_omino,ominos,1)
        return ominos
    if depth > 0:
        
        for element in current_omino:
            for x in [-1,0,1]:
                for y in [a for a in [-1,0,1] if abs(a)+abs(x)==1]:
                    
                
                    new_element = (element[0]+x,element[1]+y)
                    if new_element[0]==-10:
                        continue
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
    minX = 0
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
#function to tile a rectangle
placeCount = 0


def tileTube(size=[4,4],n=2,quantity=0, ominos = set(), grid = [], omino_list = [], omino_sets = set(), tried_set = set(), depth = 0):
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
                if tile[1]<0 or tile[1]>=size[1]:
                    canPlace = False
            if canPlace:
                grid = np.zeros(size,dtype=int)
                for tile in omino:
                    grid[tile[0]%size[0]][tile[1]]=1
                omino_list = [(i,(0,0))]
                tileTube(size,n,quantity,ominos,grid,omino_list,omino_sets, tried_set, 1)
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
                                if grid[checkX%size[0]][checkY] == 0 and checkY>=0:
                                    empty_neighbors.add((checkX%size[0],checkY))
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
                            if tile[1]+neighbor[1]<0:
                                tempCanPlace = False
                                break
                            if grid[(tile[0]+neighbor[0])%size[0]][tile[1]+neighbor[1]] != 0:
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
                            if tile[1]+neighbor[1]<0:
                                canPlace = False
                                break
                            if grid[(tile[0]+neighbor[0])%size[0]][tile[1]+neighbor[1]] != 0:
                                canPlace = False
                                break
                        except:
                            canPlace = False
                            break
                    if canPlace and not (i,neighbor) in tried_set:
                        #print("before")
                        #print(grid)
                        for tile in omino:
                            grid[(tile[0]+neighbor[0])%size[0]][tile[1]+neighbor[1]]=1
                        omino_list.append((i,neighbor))
                        #debug variable
                        global placeCount
                        placeCount+=1
                        if placeCount%5000 ==0:
                            print(grid)
                            print(countContiguousTube(grid,n))
                        if countContiguousTube(grid,n):
                            tileTube(size,n,quantity,ominos,grid,omino_list,omino_sets,tried_set, depth+1)
                        omino_list.pop()
                        for tile in omino:
                            grid[(tile[0]+neighbor[0])%size[0]][tile[1]+neighbor[1]]=0
                return
        if len(empty_neighbors)==0:
            omino_sets.add(frozenset(omino_list))

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
def countContiguous(grid,n):
    patchMembers = set()
    patchSizes = []
    
    size = np.shape(grid)
    for x in range(size[0]):
        for y in range(size[1]):
            if grid[x][y]!=0:
                continue
            if not (x,y) in patchMembers:
                patchMembers.add((x,y))
                patchSize = 1
                neighborList = []
                for xCheck in [-1,0,1]:
                    for yCheck in [y for y in[-1,0,1] if abs(y)+abs(xCheck)==1]:
                        xNeighbor = xCheck+x
                        yNeighbor = yCheck+y
                        if xNeighbor<0 or yNeighbor<0 or xNeighbor>=size[0] or yNeighbor>=size[1]:
                            continue
                        if grid[xNeighbor][yNeighbor] == 0:
                            neighborList.append((xNeighbor,yNeighbor))
                toCheck = neighborList.copy()
                neighborList.append((x,y))
                while len(toCheck)>0:
                    check = toCheck.pop()
                    if grid[check[0]][check[1]]==0:
                        patchSize+=1
                        patchMembers.add((check[0],check[1]))
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
                patchSize = 1
                neighborList = []
                for xCheck in [-1,0,1]:
                    for yCheck in [y for y in[-1,0,1] if abs(y)+abs(xCheck)==1]:
                        xNeighbor = xCheck+x
                        yNeighbor = yCheck+y
                        if yNeighbor<0 or yNeighbor>=size[1]:
                            continue
                        if grid[xNeighbor%size[0]][yNeighbor] == 0:
                            neighborList.append((xNeighbor%size[0],yNeighbor))
                toCheck = neighborList.copy()
                neighborList.append((x,y))
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
def printOminoSet(omino_set,size,n):
    print("Printing omino set.")
    ominoList = list(generateOminos(n))
    grid = np.zeros(size,dtype = int)
    count = 0
    characters = string.ascii_lowercase+string.ascii_uppercase
    for ominoIndex,coord in omino_set:
        count+=1
        omino = ominoList[ominoIndex]
        for tile in omino:
            if grid[tile[0]+coord[0]][tile[1]+coord[1]]!=0:
                print("problem")
                print(grid)
                
            grid[tile[0]+coord[0]][tile[1]+coord[1]] = count
    for x in range(size[0]):
        curString = ""
        for y in range(size[1]):
            
            curString+=characters[grid[x][y]%len(characters)]
        print(curString)

def printOminoSets(omino_sets,size,n):
    for omino_set in list(omino_sets):
        printOminoSet(omino_set,size,n)
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
            
            
        
size = [15,7]
n = 5
quantity = 10
omino_sets = tileRectangle(size,n,quantity)
set_list = list(omino_sets)
for i in range(0,len(set_list),max(int(len(set_list)/20),1)):
   plotOminoSet(set_list[i],size,n)
#printOminoSets(omino_sets,size,n)
