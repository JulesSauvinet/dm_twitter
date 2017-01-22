------------------------------------------------------------ Dossier tweetmining ------------------------------------------------------------ 

On trouve plusieurs sous-dossiers dans ce dossier :
	un dossier data avec tous nos fichiers de donnees
	un dossier docs contenant l'architecture et les captures d'ecran pour le rapport latex 
	un dossier src contenant tout le code Python et le module d'execution
	un dossier vizu contenant tous les elements necessaires a la visualisation de nos donnees



---------------------------------------------------------------- Dossier src ---------------------------------------------------------------- 

On trouve plusieurs sous-dossiers dans ce dossier :
	un dossier eventDetectionFromTwitter contenant tout le code que nous avons recuperes et modifies
	un dossier scikitlearn contenant nos tests et essais avec DBScan
	un dossier SortieFile contenant toutes nos sorties de fichiers pour nos tests avec les booleens d'elasticite et de geolocalisation
	un dossier SortieFileResultat contenant les sorties fichiers sur le gros fichiers de tweets



------------------------------------------------------------------- Knime ------------------------------------------------------------------- 

on fait un pretraitement des donnees avec Knime 
	- suppression des plus gros utilisateurs avec la 1ere succession de noeuds
	- puis suppression des tweets non geolocalises apres la jointure



------------------------------------------------------ L'execution de notre algorithme ------------------------------------------------------ 

Nous chargons nos donnees de tweets a partir de la base de donnees MongoDB
Il faut donc pour commencer lancer mongoD.exe puis mongo.exe.


on ouvre le module tweetmining du dossier src. Ce module execute deux algorithmes :
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
