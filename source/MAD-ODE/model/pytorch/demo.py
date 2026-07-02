from statistics import median
from time import time
import pandas as pd
import numpy as np

# df = pd.read_csv('./data/swat/swat.csv',header=0,index_col=0)
# print(type(df1))
# df = pd.read_hdf('./data/pems-bay.h5')


X = [[0,1], [3,2], [1,1],[2,2],[3,4]]
from sklearn.neighbors import kneighbors_graph
A = kneighbors_graph(X, 2, metric='cosine',mode='distance')
print(type(A))
print(A)
print(A.toarray())