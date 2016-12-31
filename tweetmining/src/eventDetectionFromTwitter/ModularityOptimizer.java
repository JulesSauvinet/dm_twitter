/**
 * ModularityOptimizer
 *
 * @author Ludo Waltman
 * @author Nees Jan van Eck
 * @version 1.3.0, 08/31/15
 */

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.Console;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;
import java.util.Random;

public class ModularityOptimizer
{
	/*
	Main a 9 arguments :
		inputFileName = nom du fichier d'entrée pour le clustering
		outputFileName = nom du fichier de sortie contenant les matrices de correspondance
		modularityFunction = (1 : standard  2 : alternative)
		resolution = 
		algorithm = (1 = Louvain; 2 = Louvain with multilevel refinement; 3 = smart local moving)
		nRandomStarts = 
		nIterations = nombre d'iterations pour construire les clusters
		randomSeed = seed pour le random
		printOutput = verbose 
	*/
    public static void main(String[] args) throws IOException
    {
        boolean printOutput, update;
        Clustering clustering;
        Console console;
        double modularity, maxModularity, resolution, resolution2;
        int algorithm, i, j, modularityFunction, nIterations, nRandomStarts;
        long beginTime, endTime, randomSeed;
        Network network;
        Random random;
        String inputFileName, outputFileName;
        VOSClusteringTechnique VOSClusteringTechnique;

	/* ------------------------------------- recuperation des 9 arguments necessaires a l'execution ------------------------------------- */
        if (args.length == 9)
        {
            inputFileName = args[0];
            outputFileName = args[1];
            modularityFunction = Integer.parseInt(args[2]);
            resolution = Double.parseDouble(args[3]);
            algorithm = Integer.parseInt(args[4]);
            nRandomStarts = Integer.parseInt(args[5]);
            nIterations = Integer.parseInt(args[6]);
            randomSeed = Long.parseLong(args[7]);
            printOutput = (Integer.parseInt(args[8]) > 0);

            if (printOutput)
            {
                System.out.println("Modularity Optimizer version 1.3.0 by Ludo Waltman and Nees Jan van Eck");
                System.out.println();
            }
        }
        else
        {
            console = System.console();
            System.out.println("Modularity Optimizer version 1.3.0 by Ludo Waltman and Nees Jan van Eck");
            System.out.println();
            inputFileName = console.readLine("Input file name: ");
            outputFileName = console.readLine("Output file name: ");
            modularityFunction = Integer.parseInt(console.readLine("Modularity function (1 = standard; 2 = alternative): "));
            resolution = Double.parseDouble(console.readLine("Resolution parameter (e.g., 1.0): "));
            algorithm = Integer.parseInt(console.readLine("Algorithm (1 = Louvain; 2 = Louvain with multilevel refinement; 3 = smart local moving): "));
            nRandomStarts = Integer.parseInt(console.readLine("Number of random starts (e.g., 10): "));
            nIterations = Integer.parseInt(console.readLine("Number of iterations (e.g., 10): "));
            randomSeed = Long.parseLong(console.readLine("Random seed (e.g., 0): "));
            printOutput = (Integer.parseInt(console.readLine("Print output (0 = no; 1 = yes): ")) > 0);
            System.out.println();
        }

		/* ----------------------------------- fin recuperation des 9 arguments necessaires a l'execution ----------------------------------- */
		
        if (printOutput)
        {
            System.out.println("Reading input file...");
            System.out.println();
        }

        network = readInputFile(inputFileName, modularityFunction);

        if (printOutput)
        {
            System.out.format("Number of nodes: %d%n", network.getNNodes());
            System.out.format("Number of edges: %d%n", network.getNEdges());
            System.out.println();
            System.out.println("Running " + ((algorithm == 1) ? "Louvain algorithm" : ((algorithm == 2) ? "Louvain algorithm with multilevel refinement" : "smart local moving algorithm")) + "...");
            System.out.println();
        }

        resolution2 = ((modularityFunction == 1) ? (resolution / (2 * network.getTotalEdgeWeight() + network.totalEdgeWeightSelfLinks)) : resolution);

        beginTime = System.currentTimeMillis();
        clustering = null;
        maxModularity = Double.NEGATIVE_INFINITY;
        random = new Random(randomSeed);
        for (i = 0; i < nRandomStarts; i++)
        {
            if (printOutput && (nRandomStarts > 1))
                System.out.format("Random start: %d%n", i + 1);

            VOSClusteringTechnique = new VOSClusteringTechnique(network, resolution2);

            j = 0;
            update = true;
			/*
				tant que on fait des modifications et tant que on n'a pas fait le bon nombre d'iterations
			*/
            do
            {
                if (printOutput && (nIterations > 1))
                    System.out.format("Iteration: %d%n", j + 1);

                if (algorithm == 1)
                    update = VOSClusteringTechnique.runLouvainAlgorithm(random);
                else if (algorithm == 2)
                    update = VOSClusteringTechnique.runLouvainAlgorithmWithMultilevelRefinement(random);
                else if (algorithm == 3)
                    VOSClusteringTechnique.runSmartLocalMovingAlgorithm(random);
                j++;

                modularity = VOSClusteringTechnique.calcQualityFunction();

                if (printOutput && (nIterations > 1))
                    System.out.format("Modularity: %.4f%n", modularity);
            }
            while ((j < nIterations) && update);

			/*
				on ne garde que le clustering qui maximise la modularité
			*/
            if (modularity > maxModularity)
            {
                clustering = VOSClusteringTechnique.getClustering();
                maxModularity = modularity;
            }

            if (printOutput && (nRandomStarts > 1))
            {
                if (nIterations == 1)
                    System.out.format("Modularity: %.4f%n", modularity);
                System.out.println();
            }
        }
        endTime = System.currentTimeMillis();

        if (printOutput)
        {
            if (nRandomStarts == 1)
            {
                if (nIterations > 1)
                    System.out.println();
                System.out.format("Modularity: %.4f%n", maxModularity);
            }
            else
                System.out.format("Maximum modularity in %d random starts: %.4f%n", nRandomStarts, maxModularity);
            System.out.format("Number of communities: %d%n", clustering.getNClusters());
            System.out.format("Elapsed time: %d seconds%n", Math.round((endTime - beginTime) / 1000.0));
            System.out.println();
            System.out.println("Writing output file...");
            System.out.println();
        }

        writeOutputFile(outputFileName, clustering);
    }

    private static Network readInputFile(String fileName, int modularityFunction) throws IOException
    {
        BufferedReader bufferedReader;
        double[] edgeWeight1, edgeWeight2, nodeWeight;
        int i, j, nEdges, nLines, nNodes;
        int[] firstNeighborIndex, neighbor, nNeighbors, node1, node2;
        Network network;
        String[] splittedLine;

        bufferedReader = new BufferedReader(new FileReader(fileName));

		/* on compte le nbr de lignes que le fichier d'entrées contient */
        nLines = 0;
        while (bufferedReader.readLine() != null)
            nLines++;

        bufferedReader.close();

        bufferedReader = new BufferedReader(new FileReader(fileName));

        node1 = new int[nLines];
        node2 = new int[nLines];
        edgeWeight1 = new double[nLines];
        i = -1;
        for (j = 0; j < nLines; j++)
        {
			/* 
			pour chaque ligne du ficher d'entrée que l'on split, 
			node1 contient la 1ere valeur de la ligne (le 1er tweet) & node2 contient la 2eme valeur de la ligne (le 2eme tweet)
				-> on met dans i la valeur maximale de toutes les valeurs que l'on croise
			si on a une 3 eme valeur sur la ligne, on la met dans edgeWeight1, sinon on met 1 (valeur de la similarité)
			*/
            splittedLine = bufferedReader.readLine().split("\t");
            node1[j] = Integer.parseInt(splittedLine[0]);
            if (node1[j] > i)
                i = node1[j];
            node2[j] = Integer.parseInt(splittedLine[1]);
            if (node2[j] > i)
                i = node2[j];
            edgeWeight1[j] = (splittedLine.length > 2) ? Double.parseDouble(splittedLine[2]) : 1;
        }
        nNodes = i + 1;

        bufferedReader.close();

		/*
		on crée un tableau de la taille maximale recuperee en faisant le parcours du fichier d'entrée _ (nbr de tweets)
		on parcourt nos deux tableaux node1 et node2 et si node1 < node2 alors node1 et node2 sont voisins pour le futur graphe
		avec node1 < node2 on ne lit qu'une partie de la matrice symétrique
		*/
        nNeighbors = new int[nNodes];
        for (i = 0; i < nLines; i++)
            if (node1[i] < node2[i])
            {
                nNeighbors[node1[i]]++;
                nNeighbors[node2[i]]++;
            }

		/*
		on met dans firstNeighborIndex un equivalent d'un effectif cumules du nombre de noeuds voisins traités
		ce qui equivaut au nombre d'aretes dans un graphe a un moment ou l'on a i noeuds
		*/
        firstNeighborIndex = new int[nNodes + 1];
        nEdges = 0;
        for (i = 0; i < nNodes; i++)
        {
            firstNeighborIndex[i] = nEdges;
            nEdges += nNeighbors[i];
        }
        firstNeighborIndex[nNodes] = nEdges;

		/*
		si node1 < node2 :
			on met dans j le nombre d'arete que l'on aura après avoir pris en compte le noeud qui se trouve dans node1
			on met donc a cet indice dans neighbor la valeur de node2
			on egale edgeWeight2 et edgeWeight1 pour ce meme indice
			on remplace j par le nombre d'arete que l'on aura après avoir pris en compte le noeud qui se trouve dans node2
			on met donc a cet indice dans neighbor la valeur de node1		
			on incremente a nouveau dans nNeighbors le nombre de voisins pour node1 et node2
		*/
        neighbor = new int[nEdges];
        edgeWeight2 = new double[nEdges];
        Arrays.fill(nNeighbors, 0);
        for (i = 0; i < nLines; i++)
            if (node1[i] < node2[i])
            {
                j = firstNeighborIndex[node1[i]] + nNeighbors[node1[i]];
                neighbor[j] = node2[i];
                edgeWeight2[j] = edgeWeight1[i];
                nNeighbors[node1[i]]++;
                j = firstNeighborIndex[node2[i]] + nNeighbors[node2[i]];
                neighbor[j] = node1[i];
                edgeWeight2[j] = edgeWeight1[i];
                nNeighbors[node2[i]]++;
            }

        if (modularityFunction == 1)
			/* 
			on met par defaut nodeWeight = null
			on appelle getTotalEdgeWeightPerNode où un calcul est réalisé
			*/
            network = new Network(nNodes, firstNeighborIndex, neighbor, edgeWeight2);
        else
        {
            nodeWeight = new double[nNodes];
            Arrays.fill(nodeWeight, 1);
            network = new Network(nNodes, nodeWeight, firstNeighborIndex, neighbor, edgeWeight2);
        }

        return network;
    }

	/*
		affiche pour chaque element du graphe au rang i, le cluste auquel il appartient -> semblable a une matrice de passage
	*/
    private static void writeOutputFile(String fileName, Clustering clustering) throws IOException
    {
        BufferedWriter bufferedWriter;
        int i, nNodes;

        nNodes = clustering.getNNodes();

        clustering.orderClustersByNNodes();

        bufferedWriter = new BufferedWriter(new FileWriter(fileName));

        for (i = 0; i < nNodes; i++)
        {
            bufferedWriter.write(Integer.toString(clustering.getCluster(i)));
            bufferedWriter.newLine();
        }

        bufferedWriter.close();
    }
}