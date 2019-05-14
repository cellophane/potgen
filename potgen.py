import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import UnivariateSpline
#main class to generate the pot mesh
class PotGen:
    def __init__(self, curve, resolution = [16,16], height = 10):
        print("init")
        self.curve = curve
        # resolution is [zres,thetares]
        self.zRes = resolution[0]
        self.thetaRes = resolution[1]
        self.height = height
        
    #save the output mesh
    def save(self,filename = 'pot.obj'):
        pass
    #take the profile curve and evaluate it to generate the initial vertices
    def makeVertices(self):
        self.vertices = np.array([[1*self.curve(self.height*z/self.zRes),0,z/(self.zRes-1)*(self.height)] for z in range(self.zRes)])
        return self.vertices
    #generate the rest of the vertices in the mesh
    def spinVertices(self):
        r = R.from_quat(([0,0,np.sin(2*np.pi/self.thetaRes),np.cos(2*np.pi/self.thetaRes)]))
        v1 = self.vertices
        for i in range(self.thetaRes):
            v1 = r.apply(v1)
            self.vertices = np.append(self.vertices,v1,0)
        return self.vertices
            
    #generate the triangles in the shell
    def makeTriangles(self):
        pass
    #generate the initial mesh from the vertices and triangle data  
    def makeShell(self):
        pass
        
    #solidify the mesh
    def solidifyMesh(self, thickness):
        pass
    
    #display an image of the mesh
    def displayMesh(self):
        pass
        
    