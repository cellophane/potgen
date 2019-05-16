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

    def generate(self):
        self.makeVertices()
        self.spinVertices()
        self.makeTriangles()
        self.makeShell()
        self.solidifyMesh(.2)
    #save the output mesh
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
        self.shellMesh = self.potMesh.copy()
        for i,n in enumerate(normals):
            self.shellMesh.vertices[i]+=n*thickness
        #flip the normals of the other side of the pot
        self.shellMesh.invert()
        #concatenate the two halve of the mesh
        self.shellMesh= self.shellMesh+self.potMesh
        
        #stitch the two halves together
        for i in range(self.thetaRes):
            size = self.thetaRes*self.zRes
            a = self.zRes-1+i*self.zRes
            b = (self.zRes-1+(i+1)*self.zRes)%size
            c = (size+1)+(self.zRes-1 + (i+1)*self.zRes)%size
            self.shellMesh.faces = np.append(self.shellMesh.faces,[[a,c,b]],0)
            
            
            a = self.zRes-1+i*self.zRes
            b = (size+1)+self.zRes-1 + i*self.zRes
            c = (size+1)+(self.zRes-1 + (i+1)*self.zRes)%size
            self.shellMesh.faces = np.append(self.shellMesh.faces,[[a,b,c]],0)
           
            self.potMesh = self.shellMesh
    #display an image of the mesh
    
    def displayMesh(self):
        self.potMesh.show()
    