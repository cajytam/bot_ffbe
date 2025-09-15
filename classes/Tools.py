from Crypto.Cipher import AES
from classes.PKCS7Encoder import PKCS7Encoder

from io import StringIO

import binascii
import base64
import random
import json
import os
import yaml

class Tools(object):

    def __init__(self, region="gl", lang="en"):
        self.region = region
        self.BASE_DIR = os.path.join( os.path.dirname( __file__ ), '..' )
        self.encoder = PKCS7Encoder()
        self.keys=self.loadRequestsFile() # Init the requests information keys
        self.loadFiles()
        self.lang=lang.upper()


#################### DEVICE MANAGEMENT ####################

    def genRandomDeviceString(self):
        #valid=['iPad1,1_%s.%s','iPad2,1_%s.%s','iPad2,2_%s.%s','iPad2,3_%s.%s','iPad2,4_%s.%s','iPad2,5_%s.%s','iPad2,6_%s.%s','iPad2,7_%s.%s','iPad3,1_%s.%s','iPad3,2_%s.%s','iPad3,3_%s.%s','iPad3,4_%s.%s','iPad3,5_%s.%s','iPad3,6_%s.%s','iPad4,1_%s.%s','iPad4,2_%s.%s','iPad4,3_%s.%s','iPad4,4_%s.%s','iPad4,5_%s.%s','iPad4,6_%s.%s','iPad4,7_%s.%s','iPad4,8_%s.%s','iPad4,9_%s.%s','iPad5,1_%s.%s','iPad5,2_%s.%s','iPad5,3_%s.%s','iPad5,4_%s.%s','iPad6,4_%s.%s','iPad6,7_%s.%s','iPad6,8_%s.%s','iPhone1,1_%s.%s','iPhone1,2_%s.%s','iPhone2,1_%s.%s','iPhone3,1_%s.%s','iPhone3,2_%s.%s','iPhone3,3_%s.%s','iPhone4,1_%s.%s','iPhone5,1_%s.%s','iPhone5,2_%s.%s','iPhone5,3_%s.%s','iPhone5,4_%s.%s','iPhone6,1_%s.%s','iPhone6,2_%s.%s','iPhone7,1_%s.%s','iPhone7,2_%s.%s','iPhone8,1_%s.%s','iPhone8,2_%s.%s']
        #return random.choice(valid)%(random.randint(1,10),random.randint(0,9))
        return 'SM-G935F_android5.1.1'


    def genRandomDeviceID(self):
        return '%s-%s-%s-%s-%s'%(self.genRandomHex(8),self.genRandomHex(4),self.genRandomHex(4),self.genRandomHex(4),self.genRandomHex(12))


    def genRandomHex(self,n):
        return ''.join([random.choice('0123456789ABCDEF') for x in range(n)])


    def getHashedDeviceID(self,id):
        return self.encrypt(id,'Zy3MDURw')

#################### END DEVICE MANAGEMENT ####################


#################### REQUEST MANAGEMENT ####################
    def getRequestUrl(self,id):
        try:
            return self.keys[id]['url']
        except:
            print('ERROR : no url for ',id,'request')



    def getRequestID(self,id):
        try:
            return self.keys[id]['id']
        except:
            print('ERROR : no id for ',id,'request')



    def getRequestKey(self,id):
        try:
            return self.keys[id]['key']
        except:
            print('ERROR : no key for ',id,'request')



    def loadRequestsFile(self):
        try:
            with open(self.BASE_DIR + "/data/requests.json") as json_file:
                return json.loads(json_file.read())

        except:
            print('Error with the requests file')

#################### END REQUEST MANAGEMENT ####################

#################### MISSION MANAGEMENT ####################

    def findMissionName(self,id,lang):
        id=str(id)
        if id in self.mission_names:
            return self.mission_names[id][lang]
        print('Mission name not find',id)
        return '--'


    def findMissionInfo(self,id):
        try:
            try:
                return {
                    "type": self.mission_types[str(id)]['type'],
                    "energy": self.mission_types[str(id)]['energy'],
                    "rounds": self.mission_types[str(id)]['rounds']
                }
            except: return {
                    "type": self.mission_types[int(id)]['type'],
                    "energy": self.mission_types[int(id)]['energy'],
                    "rounds": self.mission_types[int(id)]['rounds']
                }
        except:
            print('error in findMissionInfo' ,id)
            return  {"type": 1,"energy": 1,"rounds": 1}


    def getChallenges(self,id):
        try:
            return self.challenges[str(id)]
        except:
            return None


    def findMissionByName(self, name, lang='en'):
        for mission in self.mission_names:
            if self.mission_names[mission][lang.upper()] == name:
                return mission
        return None


#################### FIN MISSION MANAGEMENT ####################


#################### REWARD AND END MISSION MANAGEMENT ####################

    def getRewardString(self,io):
        r=[]
        if '@' in io:
            rewards=io.split(',')
            for e in rewards:
                try:
                    w=e.split('@')
                    if len(w)==3:
                        reward=w[1].split(':')
                        if len(reward)==4:
                            # self.dropped_stuff.append((reward[1],reward[2]))
                            r.append('%s x%s'%(self.findItemName(reward[1], self.lang),reward[2]))
                except:
                    pass
        else:
            rewards = io.split(',')
            for reward in rewards:
                try:
                    if reward:
                        reward= reward.split(':')
                        # self.dropped_stuff.append((reward[1],reward[2]))
                        r.append('%s x%s'%(self.findItemName(reward[1], self.lang),reward[2]))
                except:
                    pass
        return ', '.join(r)


    def getUnitName(self,id,lang):
        if id in self.units:
            try:
                return self.units[id][lang],str(id)
            except:
                print(id,'missing id')
                return '--',id


    def getUnitCost(self,id):
        if id in self.units:
            return self.units[id]['price']
        print(id,'missing cost for unit %s'%(id))
        return '--',id

    def getUnitMinRarety(self,id):
        if id in self.units:
            return self.units[id]['min_rarety']
        print(id,'missing min_rarety for unit %s'%(id))
        return '--',id



    def getLevelExp(self,lvl):
        try:
            return self.levels[str(int(lvl)+1)]
        except:
            return 4690529

    def findItemName(self,id,lang):
        # id=str(id)
        if id in self.items:
            return self.items[id][lang]
        elif id in self.recipebooks:
            return self.recipebooks[id][lang]
        elif id in self.units:
            return self.units[id][lang]
        elif id in self.equipment:
            return self.equipment[id][lang]
        else:
            print('%s missing name'%(id))
            return '--'

#################### FIN REWARD AND END MISSION MANAGEMENT ####################


#################### CRYPTAGE MANAGEMENT ####################

    def encrypt(self, data, key):
        return self.encoder.encrypt(data, key)

    def decrypt(self, data, key):
        return self.encoder.decrypt(data, key)

#################### FIN CRYPTAGE MANAGEMENT ####################

#################### FILE MANAGEMENT ####################


    def loadFiles(self):
        self.levels=self.readFile("/data/user_levels.json")
        self.mission_types=self.readFile("/data/" + self.region + "/mission_types_" + self.region + ".json")
        self.mission_names=self.readFile("/data/" + self.region + "/mission_names_" + self.region + ".json")
        self.challenges=self.readFile("/data/" + self.region + "/challenges_" + self.region + ".json")
        self.units=self.readFile("/data/" + self.region + "/units_" + self.region + ".json")
        self.recipebooks=self.readFile("/data/" + self.region + "/recipebooks_" + self.region + ".json")
        self.items=self.readFile("/data/" + self.region + "/item_names_" + self.region + ".json")
        self.errors=self.readFile("/data/" + self.region + "/errors_" + self.region + ".json")
        self.equipment=self.readFile("/data/" + self.region + "/equipment_names_" + self.region + ".json")
        self.schedule_challenge=self.readFile("/data/" + self.region + "/schedule_challenges_" + self.region + ".json")


    def get_schedule_challenge_content(self):
        return self.schedule_challenge


    def updateJsonFile(self,file,region,keyToChange,NewValue,format_value="text"):

        try:
            with open(self.BASE_DIR + "/" +'data.yaml') as f:
                temp_json = yaml.load(f, Loader=yaml.FullLoader)
            #with open(self.BASE_DIR + "/" + file) as json_file:
            #    temp_json=json.loads(json_file.read())

            if format_value=="integer":
                NewValue=int(NewValue)

            if not keyToChange in temp_json[region]:
                temp_json[region].update({keyToChange:NewValue})
            else:
                temp_json[region][keyToChange] = NewValue
            with open(file, 'w') as file:
                yaml.dump(temp_json, file, allow_unicode=True)

        except:
            print('Error when saving file',file)


    def readFile(self,file_name):
        try:
            with open(self.BASE_DIR + file_name, encoding="utf8") as json_file:
                return json.loads(json_file.read())
        except:
            print('Error when loading the ' + file_name + ' file')

    def getRootDir(self):
        return self.BASE_DIR

#################### FIN FILE MANAGEMENT ####################

    def findError(self,rr,lang):
        try:
            return '[+] ' + self.errors[rr][lang]
        except:
            return 'unknown error %s'%(rr)

    def is_integer(self,n):
        try:
            float(n)
        except ValueError:
            return False
        else:
            return float(n).is_integer()
