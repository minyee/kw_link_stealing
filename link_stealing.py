import sys
from gangingStrategies import *
from graphNode import *
from random import *
import math

def readTrafficMatrix(filename):
	file = open(filename, 'r')
	mat = []
	linenum = 0
	size = 0
	for line in file:
		if linenum == 0:
			size = int(line)
			linenum += 1
			continue
		line = line.split()
		newFloatLine = []
		lineTotal = 0
		for word in line:
			newFloatLine.append(int(word))
			lineTotal += int(word)
		#lineTotal = sum(line)
		newFloatLine = [(float) (elem * (size - 1)/lineTotal) for elem in newFloatLine]
		mat.append(newFloatLine)
	return mat

def formBipartiteGraph(numGroups):
	nTotalNodes = 2 * numGroups
	nodesCollections = []

	# First start forming all the nodes
	for id in range(nTotalNodes):
		node = Node(id, None, None)
		nodesCollections.append(node)
	# Now start forming the edges with infinite weights
	for srcId in range(numGroups):
		srcNode = nodesCollections[srcId]
		srcOutgoingEdges = {}
		for dstId in range(numGroups, nTotalNodes - 1, 1):
			dstNode = nodesCollections[dstId]
			srcOutgoingEdges.insert({dstId:sys.maxsize})
		srcNode.srcOutgoingEdges(srcOutgoingEdges)
	return Graph(nodesCollections)

# given a total size of the matrix, where it is totalSize x totalSize, and switch radix
# form block matrix, which gangs based on the block matrix
def formBlockMatrix(totalSize, switchRadix, rowOffset, colOffset):
	overallMatrix = []
	for i in range(totalSize):
		overallMatrix.append([0]*totalSize)
	for rad in range(switchRadix):
		rowIndex = (rad + rowOffset) % totalSize
		for rad2 in range(switchRadix):
			colIndex = (rad2 + colOffset) % totalSize	
			overallMatrix[rowIndex][colIndex] = 1
	return overallMatrix


def formStrideMatrix(totalSize, switchRadix, rowOffset, colOffset):
	overallMatrix = []
	for i in range(totalSize):
		overallMatrix.append([0]*totalSize)
	for rad in range(switchRadix):
		rowIndex = (rad * 2 + rowOffset) % totalSize
		for rad2 in range(switchRadix):
			colIndex = (rad2 * 2 + colOffset) % totalSize	
			overallMatrix[rowIndex][colIndex] = 1
	return overallMatrix

# Form Block-Src-Stride-Dst
def formBSSDMatrix(totalSize, switchRadix, rowOffset, colOffset):
	overallMatrix = []
	for i in range(totalSize):
		overallMatrix.append([0]*totalSize)
	for rad in range(switchRadix):
		rowIndex = (rad*2 + rowOffset) % totalSize
		for rad2 in range(switchRadix):
			colIndex = (rad2 + colOffset) % totalSize	
			overallMatrix[rowIndex][colIndex] = 1
	return overallMatrix


def formPermutationMatrices(numGroups,radix,numMasks,gangingStrategy):
	collection = []
	
	if gangingStrategy == GangingStrategy.BLOCK:
		rowOffset = 0
		colOffset = 0
		for i in range(numMasks): 
			collection.append(formBlockMatrix(numGroups, radix, rowOffset, colOffset))
			if colOffset + radix >= numGroups:
				rowOffset = (rowOffset + radix) % numGroups
			colOffset = (colOffset + radix) % numGroups
	elif gangingStrategy == GangingStrategy.STRIDE:
		isEven = True
		lastOddRowIndex = 1
		lastOddColIndex = 1
		lastEvenRowIndex = 0
		lastEvenColIndex = 0
		rowOffset = lastEvenRowIndex
		colOffset = lastEvenColIndex
		for i in range(numMasks):
			collection.append(formStrideMatrix(numGroups, radix, rowOffset, colOffset))
			if (isEven):
				# this iteration uses the even offsets
				if (lastEvenColIndex + 2 * radix) >= numGroups:
					lastEvenRowIndex = (lastEvenRowIndex + 2 * radix) % numGroups
				lastEvenColIndex = (lastEvenColIndex + 2 * radix) % numGroups
				rowOffset = lastOddRowIndex
				colOffset = lastOddColIndex
			else:
				# this iteration uses the odd offsets
				if (lastOddColIndex + 2 * radix) >= numGroups:
					lastOddRowIndex = (lastOddRowIndex + 2 * radix) % numGroups
				lastOddColIndex = (lastOddColIndex + 2 * radix) % numGroups
				rowOffset = lastEvenRowIndex
				colOffset = lastEvenColIndex
			isEven = not isEven
	else:
		isEven = True
		lastOddRowIndex = 1
		lastEvenRowIndex = 0
		rowOffset = lastEvenRowIndex
		colOffset = lastEvenColIndex
		for i in range(numMasks):
			collection.append(formBSSDMatrix(numGroups, radix, rowOffset, colOffset))
			if (isEven):
				# this iteration uses the even offsets
				if (colOffset + radix) >= numGroups:
					lastEvenRowIndex = (lastEvenRowIndex + 2 * radix) % numGroups
				rowOffset = lastOddRowIndex
			else:
				# this iteration uses the odd offsets
				if (colOffset + radix) >= numGroups:
					lastOddRowIndex = (lastOddRowIndex + 2 * radix) % numGroups
				rowOffset = lastEvenRowIndex
			colOffset = (colOffset + radix) % numGroups
			isEven = not isEven
	return collection

def processMask(matrix, radix):	
	size = len(matrix)
	rowsContainingOnes = []
	colsContainingOnes = []
	foundCols = False
	for i in range(size):
		if not foundCols:
			for j in range(size):
				if matrix[i][j] > 0:
					colsContainingOnes.append(j)
					foundCols = True
			if foundCols:
				rowsContainingOnes.append(i)
		else:
			if matrix[i][colsContainingOnes[0]] > 0:
				rowsContainingOnes.append(i) 
				
	print len(rowsContainingOnes)
	print len(colsContainingOnes)
	assert(len(rowsContainingOnes) == len(colsContainingOnes))
	for row in rowsContainingOnes:

		if len(colsContainingOnes) <= 1:
			col = colsContainingOnes[0]
		else:
			col = colsContainingOnes[randint(0, len(colsContainingOnes) - 1)]
			print "length is %d" % len(colsContainingOnes)
		for row2 in rowsContainingOnes:
			if row2 == row:
				continue 
			else:
				matrix[row2][col] = 0
		colsContainingOnes.remove(col)
	

	return matrix

# performs the summation of two matrices
def matrixSum(mat1, mat2):
	size = len(mat1)
	sol = []
	for i in range(size):
		sol.append([0]*size)
		for j in range(size):
			sol[i][j] = mat1[i][j] + mat2[i][j] 
	return sol

def printMatrix(matrix):
	size = len(matrix)
	for i in range(size):
		print matrix[i]
	return

## TIP FOR SELF: for the ke's link_stealing, do it exactly like his version, where you only have like r permutation
## matrices and then use the block src stride shit
def linkSteal(filename, radix, gangingStrategy):
	numArgs = len(sys.argv)
	solution = []

	if (numArgs < 2):
		print "There needs to be a file to read from, eg. python link_stealing.py --filename"
		exit()
	trafficMat = readTrafficMatrix(filename)
	ngroups = len(trafficMat)
	
	# Initiate the solution matrix first
	for i in range(ngroups):
		solution.append([0] * ngroups)

	N = math.ceil((ngroups * (ngroups - 1))/radix) # total number of required switches based of g * (g - 1) = Nr relationship
	N = int(N)
	print N
	maskCollection = formPermutationMatrices(ngroups, radix, N, gangingStrategy)
	for mask in maskCollection:
		processMask(mask, radix)
	#bipartiteGraph = formBipartiteGraph(ngroups, trafficMat)
	bipartiteGraph = BipartiteGraph(ngroups, trafficMat)
	masksDone = 0
	while masksDone < N:
		maxWeightPair = bipartiteGraph.findMaxWeightEdge()
		srcNode = maxWeightPair[0]
		dstNode = maxWeightPair[1]
		maxWeight = maxWeightPair[2]
		srcId = srcNode.id
		dstId = dstNode.id - ngroups # reset the offset that is by default given to the target group
		found = False
		for mask in maskCollection:
			
			if mask[srcId][dstId] > 0:
				solution = matrixSum(solution, mask)
				srcNode.outgoingEdges[dstId] = (dstNode, trafficMat[srcId][dstId]/(solution[srcId][dstId] + 1))
				found = True
		if not found:
			srcNode.outgoingEdges[dstId] = (dstNode, 1)

		masksDone += 1
	return solution

filename = sys.argv[1]
solution = linkSteal(filename, 16, GangingStrategy.BLOCK)
printMatrix(solution)
