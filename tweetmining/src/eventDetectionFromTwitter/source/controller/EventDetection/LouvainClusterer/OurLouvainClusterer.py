# cette classe hérite de LouvainClusterer
# quand on arrive dans cette classe, la matrice de similarité est déjà faite bien qu'on la mette à jour ici
# on réalise le clustering en essayant de maximiser la similiratiré inter-cluster et donc minimiser la similiratiré intra-cluster
#

import numpy as np
from scipy.sparse import dok_matrix,coo_matrix,csr_matrix
from LouvainClusterer import LouvainClusterer

class OurLouvainClusterer(LouvainClusterer) :
    def __init__(self,tweets,similarityMatrix) :
        self.tweets=tweets
        self.similarityMatrix=similarityMatrix 

	# cette méthode permet de construire les clusters à partir de la matrice de similarité
	# on obtient le nombre de clusters final après de maintes reprises de réduction
    def getClusters(self) :
        PASS=1
        
        matrix=csr_matrix(self.similarityMatrixBuilder)
        continu=True
        realClusters=[]
        clusters=[]
        nextMatrix=[]
        firstRound=True
		
        while continu :
            print "-"*40
            print "PASS #{0}".format(PASS)
            PASS+=1
			# on recupere le nombre de clusters et le vecteur de mapping obtenus a l'aide de la matrice de similarité 
            clustersNumber,clusters=LouvainClusterer.getOnePassLouvainCommunities(matrix)
			
			# on charge nos donnees de clusters dans realClusters
            if firstRound :
                firstRound=False
                realClusters=clusters
            else :
                LouvainClusterer.updateRealClusters(realClusters,clusters)
				
			# on regarde si on a reussi a reduire le nombre de clusters
			# si oui on réitère en modifiant la matrice de travail 
			# et ce jusqu'à ne plus arriver à réduire le nbr de clusters
            if (clustersNumber==matrix.shape[0]) :
                continu=False
            else :
                nextMatrix=LouvainClusterer.buildNewSimilarityMatrix(matrix,clusters,clustersNumber)
                matrix=nextMatrix
        return np.array(realClusters)

# ------------------------------------------------------- Méthodes de manipulation des clusters ------------------------------------------------------- #
    @staticmethod
	# on fait une maj de realClusters
	# clusters est comme une map qui associe a chaque numero de cluster les tweets associés
	# on charge donc le contenu de clusters dans realClusters
    def updateRealClusters(realClusters,clusters) :
        for i in range(0,len(realClusters)) :
            realClusters[i]=clusters[realClusters[i]]

    @staticmethod
	# cette méthode permet de construire une matrice de similarité a partir d'un ensemble de clusters 
    def buildNewSimilarityMatrix(matrix,clusters,clustersNumber) :
        nextMatrix=dok_matrix((clustersNumber,clustersNumber),dtype=np.float)
        for i in range(0,clustersNumber) :
            for j in range(i,clustersNumber) :
                nextMatrix[i,j]=LouvainClusterer.getSimilarityOf2Clusters(matrix,clusters,i,j)
        return csr_matrix(nextMatrix)

    @staticmethod
	# retourne la similarité entre deux clusters calculé à partir de la similarité de chaque cluster
	# il me semble que c'est la somme des similarités
    def getSimilarityOf2Clusters(matrix,clusters,clusterI,clusterJ) :
        iVertices=np.where(clusters == clusterI)[0]
        jVertices=np.where(clusters == clusterJ)[0]
        sumOfWeights=0
        for k in iVertices :
            for l in jVertices :
                sumOfWeights+=LouvainClusterer.getFromMatrix(matrix,k,l)
        return sumOfWeights

    @staticmethod
	# méthode d'acces dans la matrice
	# le min et le max permettent d'ordonner l'accès dans la matrice
    def getFromMatrix(matrix,i,j) :
        return matrix[min(i,j),max(i,j)]

		
# ------------------------------------------- Méthodes qui permettent de construire la matrice de similarité ------------------------------------------- #
    @staticmethod
	# méthode qui permet à partir de la matrice de tweet de créer des clusters
	# on renvoie donc le nombre de clusters créés et un vecteur de correspondance qui pour chaque ligne de la matrice associe un numéro de cluster
    def getOnePassLouvainCommunities(matrix) :
        ITER=1
        
        matrixSize=matrix.shape[0]
		# on somme les valeurs en colonnes et en lignes pour chaque cluster de la matrice
		# sumsOfWeights -> liste de matrixSize valeurs
        sumsOfWeights=np.array([sum(matrix.getrow(i).data)+sum(matrix.getcol(i).data) for i in range(matrixSize)])
		
		# totalSumOfWeight -> somme de toutes les valeurs
        totalSumOfWeight=sum(sumsOfWeights)
		
		# on crée une liste de matrixSize valeurs pour representer les clusters
		# au début on a autant de clusteur que d'elements de la matrice
        clusters=np.array(range(0,matrixSize))
        modified=True
		
		# boucle pour agglomérer les elements entre eux 
        while modified :
            print "  ITER #{0}".format(ITER)
            ITER+=1
            modified=False
            for i in range(0,matrixSize) :
                newCluster=LouvainClusterer.getArgMaxModularity(matrix,clusters,sumsOfWeights,totalSumOfWeight,i)
                if (newCluster!=-1) :
                    modified=True
                    clusters[i]=newCluster

		# on aplique un reduce sur le vecteur clusters pour avoir les vrais clusters
		# newClusterIdentifiers est une map d'association entre les clusters du vecteur cluster et les nouveaux clusters
        newClusterIdentifiers={}
        clustersNumber=0
        for i in range(0,len(clusters)) :
            if (clusters[i] in newClusterIdentifiers) :
                clusters[i]=newClusterIdentifiers[clusters[i]]
            else :
                newClusterIdentifiers[clusters[i]]=clustersNumber
                clusters[i]=clustersNumber
                clustersNumber+=1
        print "End of a Pass"
        print "-"*40
        return clustersNumber, clusters
		

    @staticmethod
	# on prend en entrée la matrice de clusters, les clusters et le cluster de travail i
	# le but est de renvoyer le cluster j qui maximise la différence DMCEJ - DMCEI
	# si toutes les diffences valent 0, alors il n'y a pas de clusters à renvoyer et on renvoie -1
    def getArgMaxModularity(matrix,clusters,sumsOfWeights,totalSumOfWeight,i) :
        """
        This function returns -1 if there is no optimization of modularity 
        """
		
        DMCE = LouvainClusterer.getDeltaModularityCalculElements(matrix,clusters,sumsOfWeights,totalSumOfWeight,i)
        DMCEI=DMCE[clusters[i]]
        maxDelta=0
        maxJ=-1

        for j in matrix.getrow(i).indices :
            delta=DMCE[clusters[j]]-DMCEI
            if (delta>maxDelta) :
                maxDelta,maxJ=delta,j

        for j in matrix.getcol(i).indices :
            delta=DMCE[clusters[j]]-DMCEI
            if (delta>maxDelta) :
                maxDelta,maxJ=delta,j
        
        if (maxDelta==0) :
            return -1

        return clusters[maxJ]

    @staticmethod
	# -> on renvoie une Map qui associe a chaque cluster k de la matrice son coefficient de "corrélation" avec le cluster de travail i
    def getDeltaModularityCalculElements(matrix,clusters,sumsOfWeights,totalSumOfWeight,i) :
        matrixSize = matrix.shape[0]
        sumOfWeightsI = sumsOfWeights[i]
        modularityPerCluster = {clusters[i]:0}
        delta=0
		
		# ensuite on parcourt la matrice de [0,i] à [i,i] compris en ligne uniquement 
		# on calcule une valeur que l'on pourrait comparer un calcul de covariance entre i et k
		# reste a creuser -> determiner le vrai sens du calcul
        for k in range(i+1) :
            value=(matrix[k,i]-sumOfWeightsI*sumsOfWeights[k]/(2*totalSumOfWeight))
            try:
                modularityPerCluster[clusters[k]]+= value
            except KeyError:
                modularityPerCluster[clusters[k]] = value
		
		# ensuite on parcourt la matrice de [i,i+1] à [i,matrixSize] compris en ligne uniquement 
		# on calcule une valeur que l'on pourrait comparer un calcul de covariance entre i et k
        for k in range(i+1,matrixSize) :
            value=(matrix[i,k]-sumOfWeightsI*sumsOfWeights[k]/(2*totalSumOfWeight))
            try:
                modularityPerCluster[clusters[k]]+= value
            except KeyError:
                modularityPerCluster[clusters[k]] = value
        return modularityPerCluster
