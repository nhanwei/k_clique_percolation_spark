import networkx as nx
import pandas as pd
import sys
import time
from networkx.algorithms.clique import find_cliques

def main():
	# read the adjacent list
	df = pd.read_csv(sys.argv[1], skiprows = 0, header=0, names=["from","to"], engine='python')
	# df = pd.read_csv("C:\\Users\\nhanw\\OneDrive\\Desktop\\graph_proj\\sample.csv", names =['from', 'to'])
	# pandas to graph
	G = nx.from_pandas_edgelist(df, source='from', target='to')
	count = 1
	start = time.time()
	with open(sys.argv[2], 'w') as outfile: 
		for i in find_cliques(G):
			outfile.write(str(i)+'\n')
			if count % 100 == 0:
				print("Written out ", count, "cliques")
				print("Time elapsed ", time.time() - start)

if __name__ == '__main__':
	main()