import sys
import math
import logsum
import copy



def main(fileName,fileNameSec,emitFile,priorFile):
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
	currentDict=dict()
	for key in initDict:
		currentDict[key]=initDict[key]+emitDict[key][sentence[0]]
	#Done step1, initializing
	for word in sentence[1:]:
		for i in currentDict:
			alphaCurrent=emitDict[i][word]
			prevSum=0
			for j in currentDict:
				alphaPrev=initDict[j]
				transProb=transDict[j][i]
				if prevSum==0:
					prevSum=alphaPrev+transProb
				else:
					prevSum=logsum.log_sum(prevSum,alphaPrev+transProb)
			currentDict[i]=prevSum+alphaCurrent
		initDict=copy.deepcopy(currentDict)
	totalP=0
	for i in currentDict:
		if totalP==0:
			totalP=currentDict[i]
		else:
			totalP=logsum.log_sum(totalP,currentDict[i])
	print totalP


main()
