# classe abstraite, les classes JavaBasedLouvainClusterer et OurLouvainClusterer implémentent LouvainClusterer
# -> classe qui prend en entrée un ensemble de tweets et une matrice de similarité_ qui reste à définir_
# 			et on récupère en sortie un vecteur de correspondance qui associe a chaque tweet le cluster auquel il appartient

from abc import ABCMeta, abstractmethod

class LouvainClusterer :
     __metaclass__ = ABCMeta
     @abstractmethod
     def getClusters(self) :
          """
          input :
               the class should have a similarity matrix and the tweets
          output :
               vector of integer giving for each tweet its cluster id
               parallel to the vector of tweets
          """
          pass
