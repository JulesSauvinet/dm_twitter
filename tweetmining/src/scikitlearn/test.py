from sklearn.cluster import DBSCAN
from scipy.sparse import csr_matrix
A = csr_matrix([[1, 2, 0, 1],
                [0, 0, 1, 1],
                [4, 7, 0, 0],
                [5, -1, 1, 1],
                [7, 1, 0, 1],
                [6, 9, 1, 1],
                [2, 3, 1, 0],
                [1, 4, 1, 0],
                [8, 5, 0, 1],
                [4, 1, 1, 0],
                [-5,-9, 1, 0],
                [8, -8, 1, 1]])
def distanceCalc(a,b):
    return 1
    #return np.sqrt(np.sum((a-b)**2))
               
db = DBSCAN(eps=0.3, min_samples=10).fit(A)
