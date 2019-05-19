import numpy as np
from potgen import PotGen
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import UnivariateSpline
from numpy import random
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
import io
import os

filename = 'hello'
x = [0,5,7,8,12]
y = [2,3,1.75,1.5,3]
curve = UnivariateSpline(x, y)
pot = PotGen(curve,[32,6])
pot.generate()
pot.save(filename)
in_file = open(f"{filename}.stl","rb")
data = in_file.read()

in_file  = io.open(f"{filename}.stl","rb")    
data = in_file.read()
in_file.close()
size = os.path.getsize(f"{filename}.stl")
print(size)