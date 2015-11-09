import sys
import math
import copy

def log_sum(left,right):
	if right < left:
		return left + math.log1p(math.exp(right - left))
	elif left < right:
		return right + math.log1p(math.exp(left - right))
	else:
		return left + math.log1p(1)

def main():
	fileName=sys.argv[1]
	fileNameSec=sys.argv[2]
	emitFile=sys.argv[3]
	priorFile=sys.argv[4]
	with open(fileName,"rb") as txt:
		f=txt.readlines()
		sentence=[]
		for word in f:
			sentence.append(word[:-1])
	with open(fileNameSec,"rb") as txt:
		f=txt.readlines()
		transList=[]
		for word in f:
			transList.append(word[:-1])
	with open(emitFile,"rb") as txt:
		f=txt.readlines()
		emitList=[]
		for word in f:
			emitList.append(word[:-1])
	with open(priorFile,"rb") as txt:
		f=txt.readlines()
		priorList=[]
		for word in f:
			priorList.append(word[:-1])
	initDict=initState(priorList)
	transDict=initTran(transList)
	emitDict=initEmit(emitList)
	for sent in sentence:
		train(initDict,transDict,emitDict,sent)



def initState(priorList):
	d=dict()
	for i in priorList:
		d[i[0:2]] =(math.log(float(i[3:])))
	return d

def initTran(transList):
	i=0
	d=dict()
	for i in xrange(len(transList)):
		string=transList[i]
		newList=string.split()
		tempDict=initState(newList[1:])
		d[newList[0]]=tempDict
	return d

def initEmit(emitList):
	i=0
	d=dict()
	for i in xrange(len(emitList)):
		string =emitList[i]
		newList=string.split()
		tempDict=dict()
		for i in newList[1:]:
			index=i.index(":")
			a=((float(i[(index+1):])))
			tempDict[i[:index]]=math.log(a)
		d[newList[0]]=tempDict
	return d


def train(initDict,transDict,emitDict,sentence):
	sentence=sentence.split()
	sentence.reverse()
	currentDict=dict()
	prevDict=dict()
	for key in initDict:
		currentDict[key] = 0
		prevDict[key] = 0
	for index in xrange(len(sentence)-1):
		index=index+1
		for i in currentDict:
			beta=0
			for j in currentDict:
				prevBeta=prevDict[j]
				transProb=transDict[i][j]
				emitProb=emitDict[j][sentence[index-1]]#index-1 cuz the list is reversed
				sumBeta=prevBeta+transProb+emitProb
				if beta==0:
					beta=sumBeta
				else:
					beta=log_sum(beta,sumBeta)
			currentDict[i]=beta
		prevDict=copy.deepcopy(currentDict)
	totalP=0
	for key in currentDict:
		pi=initDict[key]
		emiti=emitDict[key][sentence[-1]]
		betai=currentDict[key]
		if totalP==0:
			totalP=pi+emiti+betai
		else:
			totalP=log_sum(totalP,pi+emiti+betai)
	print totalP



main()


