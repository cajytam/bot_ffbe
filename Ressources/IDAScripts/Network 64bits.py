from idautils import *
from idaapi import *
import json

json_request={}
nomfichier = "d:\\android\\requesrts64bits.json"
def get_string(addr):
	out = ""
	while True:
		if Byte(addr) != 0:
			out += chr(Byte(addr))
		else:
			break
		addr += 1
	return out
  
def get_string_from_head(head):
	refs = DataRefsFrom(head)
	for ref in refs:
		refs2 = DataRefsFrom(ref)
		for ref2 in refs2:
			stringval = get_string(ref2)
			return stringval

with open(nomfichier, 'w') as file:
	file.write('')

def get_request_name(name, key):
	functionName = name[3:]
	functionName = functionName[:functionName.index(key)]
	functionName = ''.join([i for i in functionName if not i.isdigit()])
	functionName = functionName[:len(functionName)-7]
	return functionName

def dumpkvp(functionName, addr):
	type_request='pass next function'
	if 'getUrl' in functionName:
		type_request = "getUrl"
		key_request = "url"
	elif 'getRequestID' in functionName:
		type_request = "getRequestID"
		key_request = "id"
	elif 'getEncodeKey' in functionName:
		type_request = "getEncodeKey"
		key_request = "key"
	if type_request in functionName and'Request' in functionName:
		functionName = get_request_name(functionName,type_request)
		with open(nomfichier, 'a') as file:
			file.write(functionName + '\n')
			
		for (startea, endea) in Chunks(addr):
			for head in Heads(startea, endea):
				operand = GetDisasm(head)
				with open(nomfichier, 'a') as file:
					file.write(operand + '\n')
				if 'ADRP' in operand:
					value=operand[operand.index('PAGE')+len('PAGE')+1:]
					value=value.replace('"','')
					value=value.replace('/actionSymbol/','')
					value=value.replace('.php','')
					if not functionName in json_request:
						json_request[functionName]={}
						# json_request[functionName].update({"name":functionName})
					json_request[functionName].update({key_request:str(value).strip()})
					with open(nomfichier, 'a') as file:
						file.write(value + '\n')

for funcea in Functions(0x00000000, 0x03194180):
	functionName = GetFunctionName(funcea)

	dumpkvp(functionName, funcea)
	#dumpbody(functionName, funcea, 'createBody')

with open(nomfichier, 'w') as file:
	file.write(json.dumps(json_request))

print('finish')