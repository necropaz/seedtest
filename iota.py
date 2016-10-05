import httplib
import json
import random

error="No Fails!"
txCounter=0
txAddress=0

#API calls
#gecheckt
def getNodeInfo():
	command = {'command': 'getNodeInfo'}
	return sendRequest(command)

def getMilestoneIndex():
	command = {'command': 'getNodeInfo'}
	res=sendRequest(command)
	try:
		return res['milestoneIndex']
	except Exception as e:
		error="Can't confirm the transaction."+str(e)
		return None

def getMilestone(index):
	command = {"command": "getMilestone", "index": index}
	res=sendRequest(command)
	try:
		return res['milestone']
	except Exception as e:
		error="Can't confirm the transaction."+str(e)
		return None

def getNeighbors():
	command = {"command": "getNeighbors"}
	return sendRequest(command)

def getTips():
	command = {'command': 'getTips'}
	return sendRequest(command)

def getTransfers(seed, securityLevel =1):
	command = {'command': 'getTransfers','seed':seed,'securityLevel': securityLevel}
	return sendRequest(command)

def findTransactions(bundles=None, addresses=None, digests=None, approvees=None):
	if bundles!=None:
		command = {'coiotammand': 'findTransactions','bundles':bundles}
	elif addresses!=None:
		command = {'command': 'findTransactions','addresses':addresses}
	elif digests!=None:
		command = {'command': 'findTransactions','digests':digests}
	elif approvees!=None:
		command = {'command': 'findTransactions','approvees':approvees}
	else:
		error="No input. Add a parameter in find Transaction."
		print(error)
		return None
	return sendRequest(command)

def getInclusionStates(transactions, tips):
	command = {'command': 'getInclusionStates','transactions':transactions,'tips': tips}
	return sendRequest(command)

def getBundle(transaction):
	command = {'command': 'getBundle','transaction': transaction}
	return sendRequest(command)

def getTrytes(hashes):
	command = {'command': 'getTrytes','hashes': hashes}
	return sendRequest(command)

def analyzeTransactions(trytes):
	command = {'command': 'analyzeTransactions','trytes': trytes}
	return sendRequest(command)

def getNewAddress(seed, securityLevel=1):
	command = {'command': 'getNewAddress','seed': seed ,'securityLevel': securityLevel}
	return sendRequest(command)

def prepareTransfers( transfers, seed, securityLevel=1):
	command = {'command': 'prepareTransfers','seed': seed, 'securityLevel': securityLevel ,'transfers': transfers}
	return sendRequest(command)

def getTransactionsToApprove(milestone):
	command = {'command': 'getTransactionsToApprove','milestone': milestone}
	return sendRequest(command)

def attachToTangle(trunkTransaction, branchTransaction, trytes, minWeightMagnitude=13):
	command = {'command': 'attachToTangle','trunkTransaction': trunkTransaction,'branchTransaction':branchTransaction, 'minWeightMagnitude': minWeightMagnitude,'trytes': [trytes] }
	return sendRequest(command)

def interruptAttachingToTangle():
	command = {'command': 'interruptAttachingToTangle'}
	return sendRequest(command)
	
def broadcastTransactions(trytes):
	command = {'command': 'broadcastTransactions','trytes': trytes}
	return sendRequest(command)

def storeTransactions(trytes):
	command = {'command': 'storeTransactions','trytes': trytes}
	return sendRequest(command)
	
def replayTransfer(transaction):
	command = {'command': 'replayTransfer','transaction': transaction}
	return sendRequest(command)

def pullTransactions(hashes):
	command = {'command': 'pullTransactions','hashes': hashes}
	return sendRequest(command)

#helping functions

def sendRequest(command):
	headers = {"Content-type": "application/json", "Accept": "text/plain"}
	try:
		conn = httplib.HTTPConnection('localhost:14265')
		conn.request("POST", "/", json.dumps(command), headers)
		bd = conn.getresponse().read()
		ld = json.loads(bd)
		if ld.get("error"):
    			print("failed to talk to node: {}".format(bd))
			error="Can't reach the IOTA Node."+str(bd)
		return ld
	except Exception as e:
		error="Can't reach the IOTA Node."+str(e)
		print(error)
		return None

def genTransfer(address, value="0", message=""):
	transfer = {'address': address,'value': value, 'message': message}
	return transfer		
	
def genAddress(seed, securityLevel=1):
	address=getNewAddress(seed, securityLevel=securityLevel)
	while True:
		if sendTransfer(address= address, seed=seed, securityLevel=securityLevel)==True:
			break
	return address			
			
def sendTransaction(address, seed, message="", value="0", securityLevel=1):
	try:
		message=messageEncode(message)
		tx=genTransfer(address, value=value, message=message)
		trytes=prepareTransfers([tx], seed, securityLevel=securityLevel)["trytes"][0]
		milestone=getMilestone(getNodeInfo()['milestoneIndex'])
		txToApprove=getTransactionsToApprove(milestone)
		trytes=attachToTangle(txToApprove['trunkTransaction'], txToApprove['branchTransaction'], trytes, minWeightMagnitude=13)
		broadcastTransactions([trytes['trytes'][0]])
		storeTransactions([trytes['trytes'][0]])
		return True
	except Exception as e:
		error="No Message with this transaction."+str(e)
		print(error)
		return None

def spam(address="IJOJVQQKHACN9UNOHKRBHUKPFQFCZLUXYPOLNQLBLXDBJMJF9TBUQHCSSQDQIESXGTPBXMEHJUSQBCBYN", message="", value="0", securityLevel=1):
	try:
		spamCounter=0
		while True:
			availValues = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"
			seed=""
			for i in range (0,81):
				seed+=availValues[random.randint(0,26)]
			message=messageEncode(message)
			tx=genTransfer(address, value=value, message=message)
			trytes=prepareTransfers([tx], seed, securityLevel=securityLevel)["trytes"][0]
			milestone=getMilestone(getNodeInfo()['milestoneIndex'])
			txToApprove=getTransactionsToApprove(milestone)
			trytes=attachToTangle(txToApprove['trunkTransaction'], txToApprove['branchTransaction'], trytes, minWeightMagnitude=13)
			broadcastTransactions([trytes['trytes'][0]])
			storeTransactions([trytes['trytes'][0]])
			spamCounter=spamCounter+1
			print("TxCounter: "+str(spamCounter)+"\tDurationToApprove: "+str(txToApprove['duration'])+"\tDurationToAttach: "+str(trytes['duration'])+"\tSeed: "+seed+"\taddress: "+address)
		return True
	except Exception as e:
		error="No Message with this transaction."+str(e)
		print(error)
		return None

def readeMessage(transaction, i=0 ):
	bundle=getBundle(transaction)
	try:
		data=messageDecode(str(bundle['transactions'][i]['signatureMessageChunk']))
		string=data.split('}')
		data=string[0]+'}'
		return data
	except Exception as e:
		error="No Message with this transaction."+str(e)
		print(error)
		return error			
			
def byteToTryte(byte):
	availValues = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	try:
		byte=ord(byte)
		firstValue = byte % 27
		secondValue = (byte - firstValue) / 27
		trytesValue = availValues[firstValue] + availValues[int(secondValue)]
		return trytesValue
	except Exception as e:
		error="Failure in byteToTryte."+str(e)
		print(error)
		return None

def tryteToByte(tryte):
	availValues = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	try:
		firstValue = availValues.rfind(tryte[0])
		secondValue = availValues.rfind(tryte[1])
		byte=(secondValue*27)+firstValue
		data=str(chr(byte))
		return data
	except Exception as e:
		error="Failure in tryteToByte."+str(e)
		print(error)
		return None

def messageEncode(message):
	encoded=""
	try:
		for i in message:
			encoded= encoded + byteToTryte(i)
		return encoded
	except Exception as e:
		error="Failure in messageEncode."+str(e)
		print(error)
		return None

def messageDecode( trytes):
	decoded=""
	try:
		for i in range(0,len(trytes)-1,2):
			decoded= decoded + tryteToByte(trytes[i]+trytes[i+1])
		return decoded
	except Exception as e:
		error="Failure in messageDecode."+str(e)
		print(error)
		return None
			
def checkConfirmed(seed=None):
	transaction=getTransfers(seed=seed,)
	try:
		i=len(transaction['transfers'])-1
		persistence=transaction['transfers'][i]['persistence']
		return persistence
	except Exception as e:
		error="Can't confirm the transaction."+str(e)
		return None
		
def searchTransaction( seed=None, address=None, securityLevel=1):
	if seed!=None:
		transaction=getTransfers(seed=seed, securityLevel=securityLevel)
		try:
			length=len(transaction['transactions'])-1
			data=transaction['transactions'][length]['hash'].encode('ascii')
			return data
		except Exception as e:
			error="No transaction with this seed."+str(e)
			return None
	elif address!=None:
		transaction=findTransactions([address])
		try:
			length=len(transaction['hashes'])-1
			data=transaction['hashes'][length].encode('ascii')
			return data
		except Exception as e:
			error="No transaction with this address."+str(e)
			return None
	else:
		error="Check your Seed."
		return None		
			
def searchNewTransaction( seed=None, address=None, securityLevel=1):
	if seed!=None:
		transaction=getTransfers(seed=seed, securityLevel=securityLevel)
		try:
			length=len(transaction['transfers'])-1
			if length!=txCounter:
				data=transaction['transfers'][length]['hash'].encode('ascii')
				txCounter=txCounter+1
			else:
				error="No new transaction."
				data=False
			return data
		except Exception as e:
			error="No transaction with this seed."+str(e)
			return  None
	elif address!=None:
		transaction=findTransactions([address])
		try:
			length=len(transaction['hashes'])-1
			if length!=txAddress:
				data=transaction['hashes'][length].encode('ascii')
				txAddress=txAddress+1
			else:
				error="No new transaction."
				data=False
			return  data
		except Exception as e:
			error="No transaction with this address."+str(e)
			return None
	else:
		error="Check your Seed."
		return data

def printNeighbors():
	neighbors=getNeighbors()
	length=len(neighbors['neighbors'])
	for i in range (0,length):
		print("IP:\t"+str(neighbors['neighbors'][i]['address'])+"\tnumberOfAllTransactions:\t"+str(neighbors['neighbors'][i]['numberOfAllTransactions'])+"\tnumberOfNewTransactions:\t"+str(neighbors['neighbors'][i]['numberOfNewTransactions']))

def printTransaction(seed):
	tx=getTransfers(seed)
	length=len(tx['transfers'])
	for i in range (0,length):
		print("hash: "+str(tx['transfers'][i]['hash'])+"\tpersistence: "+str(tx['transfers'][i]['persistence'])+"\tTimestamp: "+str(tx['transfers'][i]['timestamp']))

