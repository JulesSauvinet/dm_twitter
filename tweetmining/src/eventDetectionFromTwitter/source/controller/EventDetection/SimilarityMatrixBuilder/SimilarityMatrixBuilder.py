# cette classe abstraite permet de construire la matrice de similarité entre n tweets 
# on renvoie donc une matrice en théorie symétrique de taille n x n

from abc import ABCMeta, abstractmethod

class SimilarityMatrixBuilder :
     __metaclass__ = ABCMeta
     @abstractmethod
     def build(self,tweets) :
          """
          input :
               tweets : list of tweet of size n
          output :
               Matrix : similarity matrix of dimension n x n
          """
          pass
