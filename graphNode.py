import sys

class Node:
	#outgoingEdges maps nodeid to weights
	def __init__(self, id, outgoingEdges, incomingEdges):
		self.id = id
		self.outgoingEdges = outgoingEdges
		self.incomingEdges = incomingEdges

	def setOutgoingEdges(self, outgoingEdges):
		self.outgoingEdges = outgoingEdges
		return

	def setIncomingEdges(self, incomingEdges):
		self.incomingEdges = incomingEdges
		return

class Graph:
	def __init__(self, nodes):
		self.nodes = nodes
		return


class BipartiteGraph(Graph):
	# numNodesSingleSide denotes the number of nodes on one side of the graph
	def __init__(self, numNodesSingleSide, trafficMatrix):
		self.nNodes = 2 * numNodesSingleSide
		self.nodes = []
		for i in range(2 * numNodesSingleSide):
			self.nodes.append(Node(i, None, None))
		for i in range(numNodesSingleSide):
			srcNode = self.nodes[i]
			outgoingEdges = []
			for j in range(numNodesSingleSide):
				dstNode = self.nodes[j + numNodesSingleSide]
				weight = sys.maxsize
				if trafficMatrix[srcNode.id][dstNode.id - numNodesSingleSide] == 0:
					weight = 0
				outgoingEdges.append((dstNode, weight))
			srcNode.setOutgoingEdges(outgoingEdges)
		return

	def findMaxWeightEdge(self):
		maxWeight = 0
		maxSrcNode = None
		maxDstNode = None
		for i in range(self.nNodes):
			srcNode = self.nodes[i]
			for dstNode, weight in srcNode.outgoingEdges:
				if weight == sys.maxsize:
					return [srcNode, dstNode, weight]
				elif weight > maxWeight:
					maxWeight = weight
					maxSrcNode = srcNode
					maxDstNode = dstNode
		return [maxSrcNode, maxDstNode, maxWeight] 
