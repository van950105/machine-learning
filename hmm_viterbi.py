import sys
import math
import copy



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
	sys.stdout.write("\n")



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
	vpDict=dict()
	pathDict=dict()
	for i in initDict:
		vpDict[i]=initDict[i]+emitDict[i][sentence[0]]
		pathDict[i]=[i]
	prevVPDict=copy.deepcopy(vpDict)
	prevPathDict=copy.deepcopy(pathDict)
	for word in sentence[1:]:
		for i in vpDict:
			(maxValue,maxArg)=findMax(prevVPDict,transDict,emitDict,i,word)
			vpDict[i]=maxValue
			maxPath=copy.deepcopy(prevPathDict[maxArg])
			maxPath.append(i)#might cause list problem here
			pathDict[i]=maxPath
		prevVPDict=copy.deepcopy(vpDict)
		prevPathDict=copy.deepcopy(pathDict)
	maxKey=max(vpDict.iterkeys(), key=lambda k: vpDict[k])
	maxList=pathDict[maxKey]
	for i in xrange(len(sentence)):
		sys.stdout.write(sentence[i]+"_"+maxList[i])
		if i!=len(sentence)-1:
			sys.stdout.write(" ")
		else:
			sys.stdout.write("\n")

def findMax(vpDict,transDict,emitDict,i,word):
	maxHelpDict=dict()
	for j in vpDict:
		maxHelpDict[j]=vpDict[j]+transDict[j][i]+emitDict[i][word]
	key=max(maxHelpDict.iterkeys(), key=lambda k: maxHelpDict[k])
	return maxHelpDict[key],key



main()
