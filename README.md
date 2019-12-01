# K Clique Percolation in Pyspark
Over the weekend, I implemented an **overlapping community detection** algorithm in **Pyspark**. Specifically, it is called **Clique Percolation Method** or **K-Clique Percolation Method** as described in the paper https://www.researchgate.net/publication/7797121_Uncovering_the_overlapping_community_structure_of_complex_networks_in_nature_and_society.

## Intuition
The K-Clique Percolation algorithm is based on the assumption that **internal edges of the community are likely to form cliques** while **intercommunity edges tend not to**. This algorithm first 
-	Step 1: Finds the maximal cliques with *networkx*
-	Step 2: Creates the clique overlap matrix -> Filters the matrix with the parameter **k** -> Coalesce the leftover overlapping cliques into communities. 

## How to use?
**Step 1**

We have to find the maximal cliques first.

```bash
python get_clique.py sample.csv clique_out
```

get_clique.py: Uses networkx library to find and write out the maximal cliques into clique_out.csv. You shouldn't encounter memory issue at here because the main function returns an iterator and avoids storing all cliques in memory by only keeping current candidate node lists in memory during its search.

sample.csv: Sample adjacency matrix

clique_out: Returns maximal cliques in lists for next step

**Step 2**

Pyspark implementation of step 2

```bash
spark-submit spark_k_clique.py clique_out 2 sample_out.csv
```

spark_k_clique.py: Pyspark implementation. Try to assign more driver memory because this implementation doesn't successfully parallelize everything. It works in a cluster for small to medium size graphs.

clique_out.csv: Output of step 1. To be used as input here.

2: The parameter k that is most important here. To understand k, please refer to the explanation here http://www.comp.nus.edu.sg/~leonghw/Courses/CS3230R/Talks/W11-Eugene-Clique-Percolation-Method.pptx

sample_out.csv: This returns key-value pairs with the clique ID as the key and community ID as the value. E.g. {"0": 0, "1": 0, "2": 0}. This means that clique ID "0", "1" and "2" belong to the same community ID 0.
