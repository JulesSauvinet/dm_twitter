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



------------------------------------------------------ L'execution de notre algorithme ------------------------------------------------------ 

Nous chargons nos donnees de tweets a partir de la base de donnees MongoDB
Il faut donc pour commencer lancer mongoD.exe puis mongo.exe.


on ouvre le module tweetmining du dossier src. Ce module execute deux algorithmes :
	- le clustering sans pretraitement ni filtre sur les donnees
	- le clustering avec le filtre sur loi de Pearson et la blackList

ATTENTION : il faut verifier sur quel jeu de donn?es du dossier data on veut faire l'ex?cution

----------------------------------------------------------------------------------


---------------------------------------------------------- Projet.py (scikitlearn) ---------------------------------------------------------- 

Prend en entrée un fichier de tweet nommé "smallTweets3.csv" et affiche ensuite les clusteurs qu'il a trouvé
Il utilise une fonction de distance expliquée dans le rapport.
Il faut que le fichier soit correct en entrée (même nombre de colonne dans chaque ligne et donc présence de guillemet pour le lancer "python projet.py"







----------------------------------------------------------------------------------
-> expliquer et justifier notre approche

d?tection d'?v?venents ? partir d'un fichier de 1,7 Go comportant 10 982 005 tweets 
	- r?cup?r?s sur Twitter. 
	- post?s dans l'agglom?ration newyorkaise ou par des utilisateurs newyorkais 
	- du 21 juillet 2015 au 16 novembre 2015

---> Montrer l'int?rieur du fichier avec les colonnes et le contenu

pr?traitement des donn?es avec Knime 
	- suppression des plus gros utilisateurs
	- suppression des tweets non g?olocalis?s

---> Montrer le workflow avec la succession de noeuds
----------------------------------------------------------------------------------



----------------------------------------------------------------------------------
-> comment on lance le projet

lancer mongoD.exe
lancer mongo.exe



on lance ---- montrer ce que on obtient quand tout est fini
----------------------------------------------------------------------------------



----------------------------------------------------------------------------------
-> ou est-ce-que l'on peut visualiser les r?sultats

affichage de nos r?sultats avec notre visualisation de donn?es
	- la carte des clusters
	- la carte des tweets
	- le slider pour changer la date

---> Montrer la visualisation, o? mettre les fichiers et o? les remplacer dans le JavaScript

affichage des r?sultats :
	- clustering & evenements
	- la blacklist
	- les utilisateurs supprim?s

---> Montrer o? trouver ses fichiers dans le dossier
----------------------------------------------------------------------------------