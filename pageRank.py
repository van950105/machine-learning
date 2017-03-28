from scipy.sparse import csc_matrix
import numpy as np
import scipy.sparse as ssp
import os
from numpy import linalg as LA
import time

start = time.time()
DAMPING = 0.8
transitionFile = 'transition.txt'
docTopicFile = 'doc_topics.txt'
queryTopicDistroFile = 'query-topic-distro.txt'
userTopicDistroFile = 'user-topic-distro.txt'
indri_folder = 'indri-lists'

row = []
col = []
data = []

with open(transitionFile, 'r') as file:
	count = 0 #set diag = 1
	for i in file:
		i = i.split()
		row.append(int(i[0]))
		row.append(count)
		col.append(int(i[1]))
		col.append(count)
		data.append(int(i[2]))
		data.append(1)
		count +=1

with open(docTopicFile,'r') as doctopic:
	topicDict = dict()
	for i in doctopic:
		i = i.split()
		docID = int(i[0])
		topic = int(i[1])
		if topic not in topicDict:
			topicDict[topic] = [docID]
		else:
			topicDict[topic].append(docID)

with open(queryTopicDistroFile, 'r') as qtDist:
	qtDict = dict()
	for i in qtDist:
		i = i.split()
		idQuery = (int(i[0]),int(i[1]))
		distribuion = [float(x[x.find(":")+1:]) for x in i[2:]]
		qtDict[idQuery] = distribuion

with open(userTopicDistroFile,'r') as utDist:
	utDict = dict()
	for i in utDist:
		i = i.split()
		idQuery = (int(i[0]),int(i[1]))
		distribuion = [float(x[x.find(":")+1:]) for x in i[2:]]
		utDict[idQuery] = distribuion



def notConverged(r):
	return np.count_nonzero(r)!=0

#get trans matrix
transMat = ssp.csc_matrix((data,(row,col)),shape=(max(row)+1,max(row)+1))
rowSum = 1./np.squeeze(np.asarray(transMat.sum(1)))
rowSum_sparse = ssp.lil_matrix((max(row)+1,max(row)+1))
rowSum_sparse.setdiag(rowSum)
normedTransMat = transMat*rowSum_sparse
normedTrnsMatT = normedTransMat.T

#get docID

def normalized(a, axis=-1, order=2):
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)


def GPR():
	r_old = 1./np.ones(max(row)+1)
	r_new = r_old
	r_test = r_new #naive implementation
	p_0 = r_old.T
	count = 0
	while notConverged(r_test):
	#for i in xrange(10):
		r_new = DAMPING * normedTrnsMatT * r_old + (1-DAMPING) * p_0
		r_test = r_new-r_old
		r_old = r_new
		#count +=1
	'''output_file = open('GPR-10.txt','w')
	for i in xrange(len(r_new)):
		output_file.write(('%d %f\n')%(i,r_new[i]))
	output_file.close()'''
	return r_new

def findpt(length):
	result = []
	for i in sorted(topicDict.keys()):
		temp = np.zeros(length)
		values = topicDict[i]
		val = np.full(len(values),float(1)/len(values))
		temp[values] = val
		result.append(temp)
	return result


def TSPR_offline(alpha,beta,gamma,noTopics=12):
	#Offline calculation
	p_0 = (1./np.ones(max(row)+1)).T
	offline_r_results = [] #len = noTopics
	p_topic = findpt(len(p_0))
	for i in xrange(noTopics):
		r_old = 1./np.ones(max(row)+1)
		r_new = r_old
		r_test = r_new #naive implementation
		while notConverged(r_test):
		#for i in xrange(10):
			r_new = alpha * normedTransMat * r_old + beta * p_topic[i] + gamma * p_0
			r_test = r_new - r_old
			r_old = r_new
		offline_r_results.append(r_new) #r is appended, not the actual rank
	return offline_r_results

def QTSPR(offline_r_results,user,query):
	prob = qtDict[(user,query)]
	r = offline_r_results[0] * prob[0]
	for i in xrange(len(prob)-1):
		r += r[i+1]*prob[i+1]
		'''
	output_file = open('QTSPR-U2Q1-10.txt','w')
	for i in xrange(len(r)):
		output_file.write(('%d %f\n')%(i,r[i]))
	output_file.close()'''
	return r

#QTSPR(TSPR_offline(0.7,0.2,0.1),2,1)

def PTSPR(offline_r_results,user,query):
	prob = utDict[(user,query)]
	r = offline_r_results[0] * prob[0]
	for i in xrange(len(prob)-1):
		r += r[i+1]*prob[i+1]'''
	output_file = open('PTSPR-U2Q1-10.txt','w')
	for i in xrange(len(r)):
		output_file.write(('%d %f\n')%(i,r[i]))
	output_file.close()'''
	return r

#PTSPR(TSPR_offline(0.7,0.2,0.1),2,1)

def GPR_analysis():
	GPR_result = GPR()
	NS_file = open('GPR_NS.txt','w')
	WS_file = open('GPR_WS.txt','w')
	CM_file = open('GPR_CM.txt','w')
	for file in os.listdir(indri_folder):
		userQuery = file[:file.find('.')]
		user = int(userQuery[:userQuery.find('-')])
		query = int(userQuery[userQuery.find('-')+1:])
		with open(indri_folder+'/'+file,'r') as indriList:
			docScoreList = []
			docScoreList_WS = []
			docScoreList_CM = []
			#normalized_result = normalized(GPR_result)[0]*10
			for line in indriList:
				line = line.split()
				docID = int(line[2])
				docScoreList.append((docID,GPR_result[docID]))
				docScoreList_WS.append((docID,GPR_result[docID]+float(line[4])))
				docScoreList_CM.append((docID,GPR_result[docID]+0.1*float(line[4])))
			sortedDocScoreList = sorted(docScoreList,key = lambda tup: tup[1])[::-1]
			sortedDocScoreList_WS = sorted(docScoreList_WS,key = lambda tup: tup[1])[::-1]
			sortedDocScoreList_CM = sorted(docScoreList_CM,key = lambda tup: tup[1])[::-1]
			count = 1
			for index in xrange(len(sortedDocScoreList)):
				NS_file.write(('%d-%d Q0 %d %d %f GPR-NS\n')%(user,query,sortedDocScoreList[index][0],count,sortedDocScoreList[index][1]))
				WS_file.write(('%d-%d Q0 %d %d %f GPR-NS\n')%(user,query,sortedDocScoreList_WS[index][0],count,sortedDocScoreList_WS[index][1]))
				CM_file.write(('%d-%d Q0 %d %d %f GPR-NS\n')%(user,query,sortedDocScoreList_CM[index][0],count,sortedDocScoreList_CM[index][1]))
				count+=1
	WS_file.close()
	CM_file.close()
	NS_file.close()

#GPR_analysis()


def QTPSR_analysis():
	TSPR_result = TSPR_offline(0.7,0.2,0.1) #alpha,beta,gamma
	NS_file = open('QTPSR_NS.txt','w')
	WS_file = open('QTPSR_WS.txt','w')
	CM_file = open('QTPSR_CM.txt','w')
	for file in os.listdir(indri_folder):
		userQuery = file[:file.find('.')]
		user = int(userQuery[:userQuery.find('-')])
		query = int(userQuery[userQuery.find('-')+1:])
		QTPST_r = QTSPR(TSPR_result,user,query)
		with open(indri_folder+'/'+file,'r') as indriList:
			docScoreList = []
			docScoreList_WS = []
			docScoreList_CM = []
			for line in indriList:
				line = line.split()
				docID = int(line[2])
				docScoreList.append((docID,QTPST_r[docID]))
				docScoreList_WS.append((docID,QTPST_r[docID]+float(line[4])))
				docScoreList_CM.append((docID,QTPST_r[docID]+0.1*float(line[4])))
			sortedDocScoreList = sorted(docScoreList,key = lambda tup: tup[1])[::-1]
			sortedDocScoreList_WS = sorted(docScoreList_WS,key = lambda tup: tup[1])[::-1]
			sortedDocScoreList_CM = sorted(docScoreList_CM,key = lambda tup: tup[1])[::-1]
			count = 1
			for index in xrange(len(sortedDocScoreList)):
				NS_file.write(('%d-%d Q0 %d %d %f QTPSR-NS\n')%(user,query,sortedDocScoreList[index][0],count,sortedDocScoreList[index][1]))
				WS_file.write(('%d-%d Q0 %d %d %f QTPSR-NS\n')%(user,query,sortedDocScoreList_WS[index][0],count,sortedDocScoreList_WS[index][1]))
				CM_file.write(('%d-%d Q0 %d %d %f QTPSR-NS\n')%(user,query,sortedDocScoreList_CM[index][0],count,sortedDocScoreList_CM[index][1]))
				count+=1
	WS_file.close()
	CM_file.close()
	NS_file.close()

#QTPSR_analysis()

def PTPSR_analysis():
	TSPR_result = TSPR_offline(0.7,0.2,0.1) #alpha,beta,gamma
	NS_file = open('PTPSR_NS.txt','w')
	WS_file = open('PTPSR_WS.txt','w')
	CM_file = open('PTPSR_CM.txt','w')
	for file in os.listdir(indri_folder):
		userQuery = file[:file.find('.')]
		user = int(userQuery[:userQuery.find('-')])
		query = int(userQuery[userQuery.find('-')+1:])
		PTPST_r = PTSPR(TSPR_result,user,query)
		with open(indri_folder+'/'+file,'r') as indriList:
			docScoreList = []
			docScoreList_WS = []
			docScoreList_CM = []
			for line in indriList:
				line = line.split()
				docID = int(line[2])
				docScoreList.append((docID,PTPST_r[docID]))
				docScoreList_WS.append((docID,PTPST_r[docID]+float(line[4])))
				docScoreList_CM.append((docID,PTPST_r[docID]+0.1*float(line[4])))
			sortedDocScoreList = sorted(docScoreList,key = lambda tup: tup[1])[::-1]
			sortedDocScoreList_WS = sorted(docScoreList_WS,key = lambda tup: tup[1])[::-1]
			sortedDocScoreList_CM = sorted(docScoreList_CM,key = lambda tup: tup[1])[::-1]
			count = 1
			for index in xrange(len(sortedDocScoreList)):
				NS_file.write(('%d-%d Q0 %d %d %f PTPSR-NS\n')%(user,query,sortedDocScoreList[index][0],count,sortedDocScoreList[index][1]))
				WS_file.write(('%d-%d Q0 %d %d %f PTPSR-NS\n')%(user,query,sortedDocScoreList_WS[index][0],count,sortedDocScoreList_WS[index][1]))
				CM_file.write(('%d-%d Q0 %d %d %f PTPSR-NS\n')%(user,query,sortedDocScoreList_CM[index][0],count,sortedDocScoreList_CM[index][1]))
				count+=1
	WS_file.close()
	CM_file.close()
	NS_file.close()


#PTPSR_analysis()

