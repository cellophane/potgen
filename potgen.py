#main class to generate the pot mesh
class PotGen:
	def __init__(self):
		print("init")
		pass
	#save the output mesh
	def save(self,filename = 'pot.obj'):
		pass
	#take the profile curve and evaluate it to generate the initial vertices
	def makeVertices(self):
		pass
	#generate the rest of the vertices in the mesh
	def spinVertices(self):
		pass
	
	#generate the triangles in the shell
	def makeTriangles(self):
		pass
	#generate the initial mesh from the vertices and triangle data  
	def makeShell(self):
		pass
		
	#solidify the mesh
	def solidifyMesh(self):
		pass
	
	#display an image of the mesh
	def displayMesh(self):
		pass
		
	