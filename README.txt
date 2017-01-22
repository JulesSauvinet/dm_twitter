*************************************************
* 		PROJET DATA MINING      	*
*						*
*     Detection d'evenement a partir de tweets  *
*						*
*						*
*  Date : 22 janvier 2015			*
*  Auteurs : Marine Ruiz			*
*	     Gregory Howard			*
*	     Jules Sauvinet			*
*						*
*  Lien GitHub : 				*
*  https://github.com/JulesSauvinet/dm_twitter	*
*						*
*************************************************

-------- /docs ------- 
Rapport_HOWARD_RUIZ_SAUVINET.pdf :
le rapport du projet

dmkd2015.pdf :
l'article de recherche sur la detection d'evenement multi scalaire a l'origine du developpement du module de detection que nous utilisons


-------- /video ------- 
VideoPresentation.mp4 :
-> la vidéo de présentation du projet


-------- /tweetmining ------- 

/tweetmining/data :
-> nos fichiers de donnees
/tweetmining/src :
-> le code Python et le module d'execution
/tweetmining/vizu :
-> tous les elements necessaires a la visualisation de nos donnees

---------  /tweetmining/src  ------------- 

/eventDetectionFromTwitter :
-> contient tout le code que nous avons recuperes et modifies
/scikitlearn :
-> contient nos tests et essais avec DBScan
/SortieFile :
-> contient toutes nos sorties de fichiers pour nos tests avec les options d'elasticite et de geolocalisation notamment
/SortieFileResultat :
-> contenant les sorties de détection d'evenement sur le gros fichiers de tweets


----------- /knime ------------

robotFilter.knwf : 
-> suppression des plus gros utilisateurs avec la 1ere succession de noeuds
-> puis suppression des tweets non geolocalises apres la jointure

tweetClusteringWithKMeans.knwf:
un premier test d'un clustering géographique sur les tweets avec la méthode des kmeans


----------- L'execution  ----------- 

Nous chargons nos donnees de tweets a partir de la base de donnees MongoDB
Il faut donc pour commencer lancer mongoD.exe puis mongo.exe.

On ouvre le module tweetmining du dossier src. Ce module execute deux algorithmes :
	- le clustering sans pretraitement ni filtre sur les donnees
	- le clustering avec le filtre sur loi de Pearson et la blackList

ATTENTION : il faut verifier sur quel jeu de donnees l'execution va se faire avant d'executer le fichier



---------------------------------------------------------- Projet.py (scikitlearn) ---------------------------------------------------------- 

Prend en entrée un fichier de tweet nommé "smallTweets3.csv" et affiche ensuite les clusteurs qu'il a trouvé
Il utilise une fonction de distance expliquée dans le rapport.
Il faut que le fichier soit correct en entrée (même nombre de colonne dans chaque ligne et donc présence de guillemet pour le lancer "python projet.py"



--------------------------------------------------------- Visualisation du resultat --------------------------------------------------------- 
ou est-ce-que l'on peut visualiser les resultats ? 
	-> de deux manieres differents a deux endroits differents

- dans le dossier src plusieurs fichiers sont crees :
	- clustering & evenements avec _clusterAvecTraitement.txt et _clusterSansPreTraitement.txt
	- la blacklist avec _blackList.txt
	- les utilisateurs supprimes avec _userDeleted.txt

  les autres fichiers textes doivent etre transformes en fichier csv pour la partie suivante de la visualisation des resultats

- affichage de nos resultats avec notre visualisation d'evenements
	- il faut aller dans le dossier vizu 
	- ouvrir le fichier displayEvents.js
	- aller a la ligne 293 pour changer le csv des evenements (csv qui doit etre dans le dossier vizu)
	- aller a la ligne 295 pour changer le csv des tweets originaux (csv qui doit etre dans le dossier vizu)

	pour lancer le serveur, il faut taper la commande suivante :
	- python -m SimpleHTTPServer pour python 2.7 
	- python -m http.server pour Python 3.X

	puis ouvrir un navigateur et charger la page : localhost:8000/vizuEvents.html
	on peut alors voir :
		- la carte des d'evenements a gauche
		- la carte des tweets a droite
		- le slider pour changer la date en haut a gauche
