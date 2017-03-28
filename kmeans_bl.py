from scipy import spatial
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
import random
import numpy as np
import sys 

dev_dv_file = open("HW2_data\HW2_dev.docVectors","r")
test_dv_file = open("HW2_data\HW2_test.docVectors","r")

def cosSim(x,y):
	return cosine_similarity(x,y)[0][0]

def calcMaxSim(mat,centers,obj):
	maxSim =0 #cossim<1
	for index in centers:
		maxSim = max(maxSim,cosSim(obj,mat[index]))
	return maxSim**2


def simProb(centers,mat):
	sim = []
	for i in xrange(sparse.csr_matrix.get_shape(mat)[0]):
		maxSim = calcMaxSim(mat,centers,mat[i])
		sim.append(maxSim)
	simSum = sum(sim)
	prob = np.divide(sim,simSum)
	return prob


def chooseKCenters(k,mat):
	centers = range(sparse.csr_matrix.get_shape(mat)[0])
	np.random.shuffle(centers)
	centers = centers[:k]
	return [mat[center] for center in centers]

def clustering(centers,mat):
	clusterResults = [[] for i in xrange(len(centers))]
	for i in xrange(sparse.csr_matrix.get_shape(mat)[0]):
		maxSimIndex = -1
		maxSim = 0
		for j in xrange(len(centers)):
			if cosSim(mat[i],centers[j])>=maxSim:
				maxSimIndex = j
				maxSim = cosSim(mat[i],centers[j])
		clusterResults[maxSimIndex].append(i)
	rerun = 0
	for i in xrange(len(clusterResults)):
		if len(clusterResults[i])==0:
			rerun = 1
			centers[i]=mat[random.randint(0,sparse.csr_matrix.get_shape(mat)[0]-1)]
	if rerun: clusterResults = clustering(centers,mat)
	return clusterResults

def findVec(points,mat):
	vec = []
	for i in points:
		vec.append(mat[i])
	return vec


def findNewCenters(oldCluster,mat):
	count = 0
	newClusters = []
	for points in oldCluster:
		pointsVec = findVec(points,mat)
		temp = sparse.csr_matrix((1,14063))
		for j in pointsVec:
			temp += j
			count+=1
		newClusters.append(temp/count)
	return newClusters

def stopping(a,b,k):
	a = sorted(a)
	b = sorted(b)
	return a==b

def kmeans(k,mat,iterno):
	kCenters = chooseKCenters(k,mat)#KCenters is in [[vec],..] form
	oldCluster = clustering(kCenters,mat)#oldCluster is in [[docIndex,...],...] form
	print 'done old cluster'
	newCenters = findNewCenters(oldCluster,mat)
	newClusters = clustering(newCenters,mat)
	print 'done new cluster'
	count = 0
	#while not stopping(oldCluster,newClusters,k):
	while count<20:
		print 'iter %s' % count
		newCenters = findNewCenters(oldCluster,mat)
		newClusters = clustering(newCenters,mat)
		count+=1
	tempDict = dict()
	for clusterID in xrange(len(newClusters)):
		for docID in newClusters[clusterID]:
			tempDict[docID] = clusterID
	sortedDict = sorted(tempDict.items())
	outputFile = open('outputCluster_iter%s_%s.txt'%(k,iterno),'w')
	for key,values in sortedDict:
		outputFile.write('%s %s\n'% (key,values))
	outputFile.close()

def chooseKCenterspp(k,mat):
	noDocs = sparse.csr_matrix.get_shape(mat)[0]
	centers = []
	c1 = random.randint(0,noDocs-1)
	count = 1
	centers.append(c1)
	while count<k:
		probVec = simProb(centers,mat)
		newCenter = np.random.choice(noDocs,1,p=probVec)
		centers.append(newCenter)
		count+=1
	return [mat[center] for center in centers]


def kmeanspp(k,mat,iterno):
	kCenters = chooseKCenterspp(k,mat)#KCenters is in [[vec],..] form
	oldCluster = clustering(kCenters,mat)#oldCluster is in [[docIndex,...],...] form
	print 'done old cluster'
	newCenters = findNewCenters(oldCluster,mat)
	newClusters = clustering(newCenters,mat)
	print 'done new cluster'
	for i in xrange(20):
		print 'iter %s'%i
		newCenters = findNewCenters(oldCluster,mat)
		newClusters = clustering(newCenters,mat)
	tempDict = dict()
	for clusterID in xrange(len(newClusters)):
		for docID in newClusters[clusterID]:
			tempDict[docID] = clusterID
	sortedDict = sorted(tempDict.items())
	outputFile = open('outputCluster_pp_iter%s_%s.txt'%(k,iterno),'w')
	for key,values in sortedDict:
		outputFile.write('%s %s\n'% (key,values))
	outputFile.close()

def eucDist(x,y):
	return euclidean_distances(x,y)[0][0]


def calcMinDist(mat,centers,obj):
	minDist = sys.maxint 
	for index in centers:
		minDist = min(minDist,eucDist(obj,mat[index]))
	return minDist**2



def simProb_cus(centers,mat):
	sim = []
	for i in xrange(sparse.csr_matrix.get_shape(mat)[0]):
		maxSim = calcMinDist(mat,centers,mat[i])
		sim.append(maxSim)
	simSum = sum(sim)
	prob = np.divide(sim,simSum)
	return prob

def clustering_cus(centers,mat):
	clusterResults = [[] for i in xrange(len(centers))]
	for i in xrange(sparse.csr_matrix.get_shape(mat)[0]):
		minDistIndex = -1
		minDist = sys.maxint
		for j in xrange(len(centers)):
			if eucDist(mat[i],centers[j])<=minDist:
				minDistIndex = j
				minDist = eucDist(mat[i],centers[j])
		clusterResults[minDistIndex].append(i)
	rerun = 0
	for i in xrange(len(clusterResults)):
		if len(clusterResults[i])==0:
			rerun = 1
			centers[i]=mat[random.randint(0,sparse.csr_matrix.get_shape(mat)[0]-1)]
	if rerun: clusterResults = clustering(centers,mat)
	return clusterResults



def chooseKCenterspp_cus(k,mat):
	noDocs = sparse.csr_matrix.get_shape(mat)[0]
	centers = []
	c1 = random.randint(0,noDocs-1)
	count = 1
	centers.append(c1)
	while count<k:
		probVec = simProb_cus(centers,mat)
		newCenter = np.random.choice(noDocs,1,p=probVec)
		centers.append(newCenter)
		count+=1
	return [mat[center] for center in centers]



def kmeanspp_cus(k,mat,iterno):
	kCenters = chooseKCenterspp_cus(k,mat)#KCenters is in [[vec],..] form
	oldCluster = clustering_cus(kCenters,mat)#oldCluster is in [[docIndex,...],...] form
	print 'done old cluster'
	newCenters = findNewCenters(oldCluster,mat)
	newClusters = clustering_cus(newCenters,mat)
	print 'done new cluster'
	for i in xrange(20):
		print 'iter %s'%i
		newCenters = findNewCenters(oldCluster,mat)
		newClusters = clustering_cus(newCenters,mat)
	tempDict = dict()
	for clusterID in xrange(len(newClusters)):
		for docID in newClusters[clusterID]:
			tempDict[docID] = clusterID
	sortedDict = sorted(tempDict.items())
	outputFile = open('outputCluster_ppcus_iter%s_%s.txt'%(k,iterno),'w')
	for key,values in sortedDict:
		outputFile.write('%s %s\n'% (key,values))
	outputFile.close()






def createList(length,d):
	returnList = [0 for i in xrange(length)]
	for i in d:
		returnList[i] = d[i]
	return returnList




mat = []
for i in test_dv_file:
	tempDict = dict()
	i = i.split()
	for tf in i:
		index = tf.find(":")
		word = int(tf[:index])
		freq = int(tf[index+1:])
		tempDict[word] = freq
	mat.append(createList(14063,tempDict))#13924 for testfile

mat = sparse.csr_matrix(mat)
#print mat[1]/5
#print euclidean_distances(mat[0],mat[1])[0][0]
#print sparse.csr_matrix.get_shape(mat)[0]
#kmeans(100,mat,99999)
for ksize in (5,10,25,50,100):
	for iterno in range(10):
		kmeans(ksize,mat,iterno)
		kmeanspp(ksize,mat,iterno)
		#kmeanspp_cus(ksize,mat,iterno+200)
		print 'ksize %s done iter %s'%(ksize,iterno)