from classes.Tools import Tools
import io
import json
import os
import re
import time
import inspect

class Updater():
	def __init__(self,region='gl', lang='en'):
		self.t=Tools()
		self.region=region
		self.lang=lang

	def getFolderRawFiles(self):
		return self.t.getRootDir() + "/data_dump/" + self.region + "/ffbe"

	def getFolderJsonFiles(self):
		return self.getFolderData() + self.region + "/"

	def getFolderData(self):
		return self.t.getRootDir() + "/data/"

	def log(self,msg):
		print('[%s]:%s'%(time.strftime('%H:%M:%S'),msg),flush=True)

	def setTT(self,data):
		self.updateData=data
		self.findMST()
		self.updateAll()
		self.t.loadFiles()


	def updateAll(self):
		self.parseMissionTypes()
		self.parseItemNames()
		self.parseEquipmentNames()
		self.parseMissionNames()
		self.parseRecipebookNames()
		self.parseUnit()

		# self.parseLevels()
		# self.parseErrors()
		# self.parseChallenges()
		# self.parseScheduleChallenge()


	def makeFolder(self,name):
		if not os.path.exists(name):
			os.makedirs(name)

	def isFolder(self,file):
		return os.path.exists(file)

	def save(self,data,file):
		with io.open(file, 'w', encoding='utf-8') as the_file:
				the_file.write('%s'%(str(data)))

	def parseMissionTypes(self):
		self.log('Parsing missions type...')
		target=self.getFolderRawFiles()+"/missions.json"
		#target='%s/missions.json'%(self.getFolderRawFiles())
		if self.isFolder(target):
			tempJson={}
			with open(target, encoding="utf8") as data_file:
				data = json.load(data_file)
				for m in data:
					d=data[m]
					mission_id=int(m)
					energy=int(d['cost']) if "cost" in d else 0
					mission_type=int(self.get_mission_type(d['type'])) if "type" in d else 1
					rounds=int(d['wave_count']) if "wave_count" in d else 0
					tempJson[mission_id]={}
					tempJson[mission_id]['type']=mission_type
					tempJson[mission_id]['energy']=energy
					tempJson[mission_id]['rounds']=rounds
				self.save('%s'%(json.dumps(tempJson, ensure_ascii=False)),self.getFolderJsonFiles() + 'mission_types_%s.json'%(self.region))

	def get_mission_type(self, name_type):
		if name_type.upper() == "EXPLORATION":
			return 2
		else:
			return 1

	def parseItemNames(self):
		self.log('Parsing items name...')
		fin={}
		save_file=False
		if self.region=='gl':
			target=self.getFolderRawFiles()+"/items.json"
			if self.isFolder(target):
				with open(target,encoding="utf8") as data_file:
					save_file=True
					data = json.load(data_file)
					for l in data:
						fin[l]={}
						fin[l]['EN']=data[l]['name']
		if save_file:
			self.save('%s'%(json.dumps(fin, ensure_ascii=False)),self.getFolderJsonFiles() + 'item_names_%s.json'%(self.region))

	def parseEquipmentNames(self):
		self.log('Parsing equipments name...')
		fin={}
		if self.region=='gl':
			target=self.getFolderRawFiles()+"/equipment.json"
			if self.isFolder(target):
				with open(target,encoding="utf8") as data_file:
					data = json.load(data_file)
					for l in data:
						fin[l]={}
						fin[l]['EN']=data[l]['name']
				self.save('%s'%(json.dumps(fin, ensure_ascii=False)),self.getFolderJsonFiles() + 'equipment_names_%s.json'%(self.region))

	def parseMissionNames(self):
		self.log('Parsing missions name...')
		fin={}
		if self.region=='gl':
			target=self.getFolderRawFiles()+"/missions.json"
			if self.isFolder(target):
				with open(target,encoding="utf8") as data_file:
					data = json.load(data_file)
					for l in data:
						fin[l]={}
						fin[l]['EN']=data[l]['name'] if "name" in data[l] else ''
					self.save('%s'%(json.dumps(fin, ensure_ascii=False)),self.getFolderJsonFiles() + 'mission_names_%s.json'%(self.region))

	def parseRecipebookNames(self):
		self.log('Parsing recipebooks name...')
		fin={}
		if self.region=='gl':
			target=self.getFolderRawFiles()+"/recipes.json"
			if self.isFolder(target):
				with open(target,encoding="utf8") as data_file:
					data = json.load(data_file)
					for l in data:
						fin[l]={}
						fin[l]['EN']=data[l]['name'] if "name" in data[l] else ''
					self.save('%s'%(json.dumps(fin, ensure_ascii=False)),self.getFolderJsonFiles() + 'recipebooks_%s.json'%(self.region))

	def parseLevels(self):
		self.log('Parsing levels...')
		_t={}
		target='%s/F_TEAM_LV_MST.json'%(self.getFolderRawFiles())
		if self.isFolder(target):
			with open(target,encoding="utf8") as data_file:
				data = json.load(data_file)
				for m in data:
					qo3PECw6=int(m['7wV3QZ80'])#energy use
					Z0EN6jSh=int(m['B6H34Mea'])#energy use
					if not qo3PECw6 in _t:
						_t[qo3PECw6]={}
					_t[qo3PECw6]=Z0EN6jSh
				# _t.update({"251": "Max level"})
				self.save('%s'%(json.dumps(_t, ensure_ascii=False)),self.getFolderData() + 'user_levels.json')

	def parseErrors(self):
		self.log('Parsing errors name...')
		fin={}
		target='%s/F_TEXT_TEXT_EN.json'%(self.getFolderRawFiles())
		if self.isFolder(target):
				with open(target,encoding="utf8") as data_file:
					data = data_file.readlines()
					for l in data:
						l=l.rstrip().split('^')
						if len(l[0]) >=1:
							try:
								cn= self.cleanDataName(l[0])
								fin[cn]={}
								fin[cn].update(self.setJsonLanguage(l))
							except:
								print("Issue for parsing",self.whoiam())
								break
					self.save('%s'%(json.dumps(fin, ensure_ascii=False)),self.getFolderJsonFiles() + 'errors_%s.json'%(self.region))

	def parseUnit(self):
		self.log('Parsing units name...')
		fin={}
		if self.region=='gl':
			target=self.getFolderRawFiles()+"/units.json"
			if self.isFolder(target):
				with open(target,encoding="utf8") as data_file:
					data = json.load(data_file)
					for l in data:
						d=data[l]
						unit_name=d['name'] if 'name' in d else ''
						cost=0 if (not 'TMR' in d or d['TMR']==None) else 1000
						min_rarety=d['rarity_min'] if 'rarity_min' in d else 0
						if 'entries' in d:
							for unit in d['entries']:
								fin[unit]={}
								fin[unit]['price']=cost
								fin[unit]['EN']=unit_name
								fin[unit]['min_rarety']=min_rarety
						else:
							fin[l]={}
							fin[l]['price']=cost
							fin[l]['EN']=unit_name
							fin[l]['min_rarety']=min_rarety
				self.save('%s'%(json.dumps(fin, ensure_ascii=False)),self.getFolderJsonFiles() + 'units_%s.json'%(self.region))

	def parseChallenges(self):
		self.log('Parsing challenges...')
		_t={}
		target='%s/F_CHALLENGE_MST.json'%(self.getFolderRawFiles())
		if self.isFolder(target):
			with open(target,encoding="utf8") as data_file:
				data = json.load(data_file)
				for m in data:
					qo3PECw6=int(m['qo3PECw6'])
					Pzn5h0Ga=str(m['Pzn5h0Ga'])
					Z0EN6jSh=int(m['Z0EN6jSh'])
					if qo3PECw6 in _t:
						_t[qo3PECw6][Z0EN6jSh]=Pzn5h0Ga
					else:
						_t[qo3PECw6]={}
						_t[qo3PECw6][Z0EN6jSh]=Pzn5h0Ga
				self.save('%s'%(json.dumps(_t, ensure_ascii=False)),self.getFolderJsonFiles() + 'challenges_%s.json'%(self.region))

	def parseScheduleChallenge(self):
		save_file=False
		self.log('Parsing Schedule challenges...')
		fin={}
		target='%s/F_TEXT_SPCHALLENGE.json'%(self.getFolderRawFiles())
		if self.isFolder(target):
			with open(target,encoding="utf8") as data_file:
				data = data_file.readlines()
				save_file=True
				for l in data:
					l=l.rstrip().split('^')
					if len(l[0]) >=1:
						try:
							cn= self.cleanDataName(l[0])
							fin[cn]={}
							fin[cn].update(self.setJsonLanguage(l))
						except:
							print("Issue for parsing",self.whoiam())
							break
		if save_file:
			self.save('%s'%(json.dumps(fin, ensure_ascii=False)),self.getFolderJsonFiles() + 'schedule_challenges_%s.json'%(self.region))

	def cleanDataName(self,n):
		return re.sub('.*NAME_','',n)

	def findMST(self):
		for i in self.updateData:
			if i['a4hXTIm0']=='F_MST_VERSION':
				self.log('found MST:%s'%(i['wM9AfX6I']))
				self.mst=i['wM9AfX6I']
				print('mst found is',self.mst)


	def setJsonLanguage(self,arrayData, idUnit=None):
		data={}
		if idUnit:
			if str(idUnit[-2:]) in ['17', '27']:
				nbStars= " NEO VISION"
			else:
				nbStars= " " + idUnit[-1:] + "*"
		else:
			nbStars=''
		if len(arrayData) > 3:
			data.update({
			'EN': str(arrayData[1]).replace('"','') + nbStars,
			'FR': str(arrayData[4]).replace('"','') + nbStars,
			'DE': str(arrayData[5]).replace('"','') + nbStars,
			'ES': str(arrayData[6]).replace('"','') + nbStars,
			'ZH': str(arrayData[2]).replace('"','') + nbStars,
			'KO': str(arrayData[3]).replace('"','') + nbStars
			})
		else:
			data.update({
			'EN': str(arrayData[1]).replace('"','') + nbStars,
			str(self.lang).upper() : str(arrayData[2]).replace('"','') + nbStars
			})
		return data

	def whoiam(self):
		return inspect.stack()[1][3]
