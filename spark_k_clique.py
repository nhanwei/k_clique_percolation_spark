from collections import defaultdict
import sys
from pyspark import SparkContext, SparkConf
import json
# from networkx.algorithms.clique import find_cliques
# import networkx as nx
# import pandas as pd
# import time

# def get_clique(datafile):
#       df = pd.read_csv(datafile, delimiter="\t", skiprows = 3, header=0, names=["from","to"], engine='python')
#       # df = pd.read_csv("C:\\Users\\nhanw\\OneDrive\\Desktop\\graph_proj\\sample.csv", names =['from', 'to'])
#       # pandas to graph
#       G = nx.from_pandas_edgelist(df, source='from', target='to')
#       count = 1
#       start = time.time()
#       clique_list = []
#       for i in find_cliques(G):
#               clique_list.append(i)
#               if count % 100 == 0:
#                       print("Written out ", count, "cliques")
#                       print("Time elapsed ", time.time() - start)
#               count += 1
#       return clique_list

if __name__ == "__main__":

        # create Spark context with Spark configuration
        conf = SparkConf().setAppName("clique_percolation")
        sc = SparkContext(conf=conf)

        # clique_list = get_clique(sys.argv[1])
        data = sc.textFile(sys.argv[1]).filter(lambda x: x!= '').map(lambda x: eval(x))
        data = data.map(lambda x: sorted(x)) # sort the list so that we can use it to compare
        data = data.zipWithIndex()

        # Get all combination of cliques
        carte_rdd = data.cartesian(data)

        # count the length of both cliques and their intersection
        lengths_rdd = carte_rdd.map(lambda x: (x[0][0], x[0][1], x[1][0], x[1][1],
                                                                len(x[0][0]), len(x[1][0]), len(set(x[0][0]).intersection(set(x[1][0])))))
        # in each row, we have clique1, clique1_id, clique2, clique2_id, size(clique1), size(clique2), overlap of clique 1 and 2

        lengths_rdd.persist()
        # see the powerpoint by Eugene
        diag_rdd = lengths_rdd.filter(lambda x: x[1] == x[3])
        triangle_rdd = lengths_rdd.filter(lambda x: x[1] != x[3])

        ## Let's say k = 4
        k = int(sys.argv[2])

        # remove if size of overlap is less than k
        triangle_rdd_filtered = triangle_rdd.filter(lambda x: x[6] >= k-1)
        # out: [([1, 2, 3, 4, 5], 0, [3, 4, 5, 6], 1, 5, 4, 3), ([3, 4, 5, 6], 1, [1, 2, 3, 4, 5], 0, 4, 5, 3), ([1, 2, 3, 4, 5], 0, [1, 2, 3, 9], 3, 5, 4, 3), ([1, 2, 3, 9], 3, [1, 2, 3, 4, 5], 0, 4, 5, 3)]
        print("diag_rdd", diag_rdd.collect())

        # remove if size of clique is less than k
        # clique_list contains the cliques that will be in a community
        clique_list = diag_rdd.filter(lambda x: x[6] >= k).map(lambda x: x[1]).collect()
        # out: [0, 1, 2, 3]
        # unprocessed_clique_list contains the cliques that haven't been processed
        community_dict = defaultdict(int)
        community_counter = 0
        # key value pair -> 

        # looping through the all the cliques
        print("clique_list", clique_list)
        for i in clique_list:
                print('Processing', i)
                # get the cliques who are in a community with clique i
                clique_community = triangle_rdd_filtered.filter(lambda x: (x[1] == i ) | (x[3]  == i))
                clique_community.collect()
                if clique_community.collect() == []: # if the clique i is a community on its own, it will return an empty list
                        print(i, "clique is on its own")
                        community_dict[i] = community_counter
                        community_counter += 1
                        # do soemtjhign here to store the clqieu
                else:
                        # get the indexes of the cliques that is a community with clique i
                        print("Getting cliques into community")
                        clique_community_index = clique_community.map(lambda x: [x[1], x[3]]).collect()
                        intersection_of_clique = set(sum(clique_community_index, [])) & set(community_dict.keys())
                        if len(intersection_of_clique) == 0: # new community starts
                                for j in set(sum(clique_community_index, [])):
                                        community_dict[j] = community_counter
                                community_counter += 1
                        else: # community exists
                                # pick corresponding key and use the community value
                                community_id = community_dict[list(intersection_of_clique)[0]]
                                for j in set(sum(clique_community_index, [])):# all the cliques get the same community id
                                        community_dict[j] = community_id
                # clique_community.collect()
                # print('community_dict', community_dict)
                # print("clique_community", clique_community.collect())
                # print(([sum(subsublist, []) for subsublist in clique_community.map(lambda x: [x[0], x[2]]).collect()], []))
                # print(set(sum([sum(subsublist, []) for subsublist in clique_community.map(lambda x: [x[0], x[2]]).collect()], [])))

        print("clique_community", clique_community.collect())
        print("community_dict", community_dict)
        json.dump(community_dict, open(sys.argv[3], 'w'))



