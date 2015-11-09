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


def train(oldDict,transDict,emitDict,sentence):
	currentDict=dict()
	sentence=sentence.split()
	for key in oldDict:
		currentDict[key] = (oldDict[key]) + (emitDict[key][sentence[0]])
		#currentDict has been updated/a_1(i)
	oldDict=copy.deepcopy(currentDict)
	for word in (sentence[1:]):
		for targetState in currentDict:
			bj=emitDict[targetState][word]
			sm=0
			isFirst=True
			for sourceState in oldDict:
				prevValue=oldDict[sourceState]
				transProb=transDict[sourceState][targetState]
				oneDir=(prevValue)+(transProb)+bj
				if isFirst:
					sm=oneDir
					isFirst=False
				else:
					sm=log_sum(oneDir,sm)
			currentDict[targetState]=sm
		oldDict=copy.deepcopy(currentDict)
	totalP=0
	for i in currentDict.values():
		if totalP==0:
			totalP=i
		else:
			totalP=log_sum(totalP,i)
	print totalP


main()


