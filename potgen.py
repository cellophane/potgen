import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import UnivariateSpline
import trimesh
import copy
#main class to generate the pot mesh
class PotGen:
    def __init__(self, curve, resolution = [16,16], height = 10):
        print("init")
        self.curve = curve
        # resolution is [zres,thetares]
        self.zRes = resolution[0]
        self.thetaRes = resolution[1]
        
        self.height = height
        self.triangles = []
        self.vertices = np.array([0,0,0])
    #save the output mesh
    def generate(self):
        self.makeVertices()
        self.spinVertices()
        self.makeTriangles()
        self.makeShell()
        self.displayMesh()
        self.solidifyMesh(.2)
        
    def save(self,filename = 'pot'):
        self.potMesh.export(filename+'.stl','stl')
    #take the profile curve and evaluate it to generate the initial vertices
    def makeVertices(self):
        self.vertices = np.array([[1*self.curve(self.height*z/self.zRes),0,z/(self.zRes-1)*(self.height)] for z in range(self.zRes)])
        return self.vertices
    #generate the rest of the vertices in the mesh
    def spinVertices(self):
        r = R.from_quat(([0,0,np.sin(np.pi/self.thetaRes),np.cos(np.pi/self.thetaRes)]))
        v1 = self.vertices
        for i in range(self.thetaRes-1):
            v1 = r.apply(v1)
            self.vertices = np.append(self.vertices,v1,0)
        return self.vertices
            
    #generate the triangles in the shell
    def makeTriangles(self):
        triangles = []
        vTotal = np.shape(self.vertices)[0]
        for i in range(vTotal):
            #the top rim should not have triangles added
            if (i+1)%self.zRes != 0:
                #add the two triangles to the upper right of the vertex
                triangles.append([i,(i+1)%vTotal,(i+self.zRes+1)%vTotal])
                triangles.append([i,(i+self.zRes+1)%vTotal,(self.zRes+i)%vTotal])
        self.triangles = triangles
        self.makeBottom()
    #generate the bottom of the pot
    def makeBottom(self):
        self.vertices = np.append(self.vertices,[[0,0,0]],0)
        triangles = []
        for i in range(self.thetaRes):
            triangles.append([i*self.zRes,((i+1)*self.zRes)%(np.shape(self.vertices)[0]-1),np.shape(self.vertices)[0]-1])
        self.triangles+=triangles
    #generate the initial mesh from the vertices and triangle data  
    def makeShell(self):
        self.potMesh= trimesh.Trimesh(self.vertices, self.triangles,process=False)
        
    #solidify the mesh
    def solidifyMesh(self, thickness=.1):
        
        self.newVertices =np.copy(self.vertices)
        normals = self.potMesh.vertex_normals
        shellMesh = self.potMesh.copy()
        for i,n in enumerate(normals):
            shellMesh.vertices[i]+=n*thickness
        
        shellMesh.invert()
        #trimesh does not preserve vertex ordering
        #so we have to find the top of the mesh again
        shellTopRing = {}
        for i,v in enumerate(shellMesh.vertices):
            if abs(v[2]-self.height)<self.height/self.zRes:
                shellTopRing[v] = i
        coreTopRing = {}

        for i,v in enumerate(self.potMesh.vertices):
            if abs(v[2]-self.height)<self.height/self.zRes/2:
                coreTopRing[v] = i

        print(len(shellTopRing))
        coreTopRing = set()
        self.shellMesh= shellMesh+self.potMesh
        self.shellMesh.export("test combined.stl",'stl')
    #display an image of the mesh
    
    def displayMesh(self):
        self.potMesh.show()
    