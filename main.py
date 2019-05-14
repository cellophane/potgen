from potgen import PotGen
import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import UnivariateSpline
from numpy import random
x = [0,5,7,8,12]
y = [2,3,1.75,1.5,3]
curve = UnivariateSpline(x, y)
pot = PotGen(curve)
print(pot.makeVertices())