# cette classe hérite de LouvainClusterer
# on réalise le clustering ici grace a ModularityOptimizer.jar
#

import sys,subprocess,numpy as np
from scipy.sparse import dok_matrix
from LouvainClusterer import LouvainClusterer

class JavaBasedLouvainClusterer(LouvainClusterer) :
    def __init__(self,tweets,similarityMatrix) :
        self.tweets=tweets
        self.similarityMatrix=similarityMatrix
        
	# dans cette fonction on ecrit la matrice de similarité dans le fichier input
	# et on appelle clusterFromSimilarityFile avec comme entrée le fichier input et ouput
    def getClusters(self) :
        """
        This method use ModularityOptimizer.jar
        """
		#on initialise la matrice et on recupere sa taille
        similarityMatrix=self.similarityMatrix
        matrixSize=similarityMatrix.shape[0]
        
        realClusters=[]
        weightsFilePath="input.txt"
        clusterFilePath="output.txt"

        # write the weights file
		#x = [1, 2, 3], y = [4, 5, 6]
		#zipped = zip(x, y)
		#zipped = [(1, 4), (2, 5), (3, 6)]
		# la matrice de similarité est donc une matrice carré
		
        print "   Writing similarity matrix into File ..."
        l = sorted(zip(similarityMatrix.row, similarityMatrix.col, similarityMatrix.data))
        if (l[-1][1] < matrixSize-1) : 
			l.append((matrixSize-2,matrixSize-1,0))
		
		# on ecrit dans lines tous les triplets de l puis on les ecrit dans le fichier weightsFilePath qui est le fichier input.txt
        lines="\n".join(["{0}\t{1}\t{2}".format(i,j,v) for i,j,v in l])
        with open(weightsFilePath, 'w') as weightsFile :
            weightsFile.write(lines)
            
        return clusterFromSimilarityFile(weightsFilePath=weightsFilePath,clusterFilePath=clusterFilePath)

		
# cette méthode appelle  "java -jar ModularityOptimizer.jar {0} {1} 1 0.5 2 10 10 0 0" ------> comprendre les arguments du jar
# mais on peut supposer que c'est ce jar qui réalise le clustering
def clusterFromSimilarityFile(weightsFilePath="input.txt",clusterFilePath="output.txt") :
    # execute the command
    print "\tClustering ..."
    command = "java -jar ModularityOptimizer.jar {0} {1} 1 0.5 2 10 10 0 0".format(weightsFilePath,clusterFilePath)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return getClusterFromOutputFile(clusterFilePath)
	
    
# cette méthode récupère le fichier output.txt grace à la méthode précédente
# on recupere tous les lignes du fichier rempli grace a ModularityOptimizer.jar ----> a compendre ce que cela contient
# et on renvoie un tableau de liste qui pour chaque cluster contient les tweets contenus dans ce cluster
def getClusterFromOutputFile(clusterFilePath="input.txt") :
    # get clusters from clusterFile (output of the command)
    print "\tReading clusters from a file ..."
    with open(clusterFilePath) as f :
        realClusters=map(int,f.readlines())
        return np.array(realClusters)
    
        
        
            
