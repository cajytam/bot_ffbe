import json
import requests
import time
import traceback
import inspect
import random
import math
import yaml

from random import randint
from collections import OrderedDict
from classes.Tools import Tools
from classes.Login import Login
from stem import Signal
from stem.control import Controller
from classes.Updater import Updater

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class FFBE(object):
    def __init__(self, japan=False, lang="en"):
        self.is_japan=japan
        self.lang=lang.upper()
        self.current_mst=0
        self.current_rsc=0
        self.setRegion() #Init the region
        self.getVersionDetails() # init the version details
        self.t=Tools(self.region, self.lang) #Init of an object Tools
        self.r=self.setRequest() # Init the request
        self.s=self.setSettings() #Init the user array
        self.init_start=True
        self.new_account=False
        self.dict_device={}
        self.lastError="Unknown error" # error management
        self.lb=0
        self.arena_opponent=''
        self.arena_opponent_name=''
        self.arena_opponent_ratio=''
        self.arena_party=0
        self.friend=False
        self.refill_lapis=False
        self.refill_potion=False
        self.refill_raid_orbs=False
        self.refill_arena_orbs=False
        self.open_chest=False
        self.collect_loot=False
        self.collect_exploration_loot=False
        self.collect_unit=False
        self.solve_mission=False
        self.clear_arena=False
        self.clear_raid=False
        self.raid_mission_id=''
        self.raid_party=''
        self.collected_stuff=[]
        self.lastFriend=[]
        self.useFriend=False
        self.number_of_unit=0
        self._api_time=0
        self.mission_id_running=0
        self.is_facebook=False
        self.is_google=False
        self.is_starter=True
        self.SLEEPING_TIME_FARM=0
        self.SLEEPING_TIME_MISSION=9 #TODO voir pour augmenter la durée pour les explorations
        self.SLEEPING_TIME_ARENA=10
        self.v=self.loadVariablesFile()
        print('[+] Initialization completed')
        self.printVersionDetails()
        self.proxy='NO'
        self.dungeons_unlocked = []
        self.unit_already_TMRed = []
        self.changeUnitWithFullTMR=False
        self.multiplier_dmg=0
        self.raid_multiplier_dmg=0
        self.raidDmgMultiplier=False
        self.numberFarmAlreadyTurnOnce=0 # Permet d'eviter le bug de l'erreur de request si une modification d'unit dans une party intervient des la première iteration d'un farm
        self.autoFixWeaponDungeon=False

    def setAutoFixWeaponDungeon(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will auto fix dungeon weapon')
        self.autoFixWeaponDungeon=True

    def setRefillLapis(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will refill energy with lapis')
        self.refill_lapis=True

    def setRefillPotion(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will refill energy with potion')
        self.refill_potion=True

    def setLb(self,lb):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will add %s lb'%lb)
        self.lb=int(lb)

    def setRaidOrbs(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will refill orbs')
        self.refill_raid_orbs=True

    def setArenaOrbs(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will refill arena orbs')
        self.refill_arena_orbs=True

    def setOpenChests(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will open chests')
        self.open_chest=True

    def setCollectLoot(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will collect loot')
        self.collect_loot=True

    def setCollectExplorationLoot(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will collect exploration loot')
        self.collect_exploration_loot=True

    def setCollectUnits(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will collect units')
        self.collect_unit=True

    def setSolveMissions(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will solve missions')
        self.solve_mission=True

    def setUseFriend(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will use friends')
        self.useFriend=True

    def setChangeUnitWithFullTMR(self):
        self.dolog('[+] party with full TMR will be changed')
        self.changeUnitWithFullTMR=True

    def setClearArena(self):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will auto clear arena when orb available')
        self.clear_arena=True

    def setClearRaid(self,MissionId, party):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] bot will auto clear raid event when orb available')
        self.clear_raid=True
        self.raid_mission_id=MissionId
        self.raid_party=party
        self.clearRaid(self.raid_party,self.raid_mission_id)

    def setRaidMultiplierDmg(self,indiceMultiplier):
        self.dolog('%s() was called'%(self.whoami()))
        self.raid_multiplier_dmg = indiceMultiplier
        self.dolog('[+] damages will be multiplier by x' + str(self.raid_multiplier_dmg))
        self.raidDmgMultiplier = True

    def setArenaPartyNumber(self,number):
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('[+] %s party will be use for clear arena'%(number))
        self.arena_party=int(number)

    def setFacebookLogin(self, token):
        fb=Login()
        self.s['facebookToken']=token
        self.s['facebookId']=fb.setFacebook(token)
        self.is_facebook=True

    def setGoogleLogin(self, id, token):
        self.s['goo']=token
        self.s['gid']=id
        self.is_google=True

    def setSleepingTimeFarm(self,seconds=0):
        self.dolog('[+] Bot will sleep during %s second(s) between each interation'%(seconds))
        self.SLEEPING_TIME_FARM=seconds

    def setDeviceId(self, device, platform):
        self.dict_device['ios']={'id': 1,'name': "iOs"}
        self.dict_device['android']={'id': 2,'name': "Android"}
        self.dict_device['amazon']={'id': 101,'name': "Amazon"}

        self.s[self.v['DeviceId']]=device
        self.s[self.v['DevicePlatform']]=str(self.dict_device[platform]['id'])

        self.platform=self.dict_device[platform]['name']

        print('[+] Platform : ',self.platform)
        print('[+] Device ID : ', device)


    def renew_tor_ip(self):
        with Controller.from_port(port = 9051) as controller:
            controller.authenticate(password='3Bm33$QQmArEDXUPCchHJ2mo')
            controller.signal(Signal.NEWNYM)
            self.setProxie('5466','46545')
        # self.logProxyIP()


    def setRegion(self):
        if self.is_japan:
            self.region='jp'
        else:
            self.region='gl'


    def getVersionDetails(self):
        try:
            with open('data.yaml') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
            self.current_mst=data[self.region]['mst']
            self.version_build=data[self.region]['build_version']
            self.version_software=data[self.region]['software_version']
            self.version_rcs=data[self.region]['rsc']
            self.base_url=data[self.region]['base_url']

        except:
            print('Error with the config.json file')


    def loadVariablesFile(self):
        try:
            with open("data/variables.json") as json_file:
                return json.loads(json_file.read())

        except:
            print('Error with the variables file')


    def setRequest(self):
        r=requests.session()
        r.headers.update({'Content-Type':'application/x-www-form-urlencoded','Connection':'keep-alive','User-Agent':'FF%20EXVIUS/2.1.3 CFNetwork/808.1.4 Darwin/16.1.0','Accept-Language':'en-us'})
        r.verify=False
        return r

    def setProxie(self,ip,port):
        self.dolog('%s() was called'%(self.whoami()))
        if ip == 'NO':
            return
        if ip and 'tor' in ip:
            # r = self.r.get('http://httpbin.org/ip')
            self.r.proxies.update({'http': 'socks5h://localhost:9050','https': 'socks5h://localhost:9050',})
            # print('ip originelle :',r.text)
            # self.logProxyIP()


    def logProxyIP(self):
        p=self.r.get('http://httpbin.org/ip')
        print('ip tor :',p.text)

    def setSettings(self):
        s={}
        s['data']=''
        s['user']={}
        s['user']['units']={}
        s['user']['party_arena']={}
        s['user']['ach']=None
        s['user']['session_device']=self.t.genRandomDeviceID()
        s['openedChests']=[]
        s['friends']={}
        s['units']={}
        return s


    def printVersionDetails(self):
        print("[+] Region : ", (self.region).upper())
        print("[+] Software version : %s (%s)"%(self.version_software,self.version_build))
        print("[+] Data number : ", self.current_mst)



    def updateMST(self,data):
        self.dolog('%s() was called'%(self.whoami()))
        data=json.loads(data)
        data_version=data[self.v['T_VERSION']]
        for i in data_version:
            if 'F_RSC_VERSION' == i[self.v['KeyName']]:
                F_RSC_VERSION=i[self.v['Value']]
            if 'F_MST_VERSION' == i[self.v['KeyName']]:
                mst=i[self.v['Value']]
        print(int(self.current_mst) == int(mst),self.current_mst,mst)
        if int(self.current_mst) == int(mst):
            return
        else:
            print(int(self.current_mst) == int(mst),self.current_mst,mst)
            self.dolog('updating mst')
            self.t.updateJsonFile('data.yaml', self.region, "mst", mst, "integer")
            if self.is_japan:
                self.t.updateJsonFile('data.yaml', self.region, "rsc", F_RSC_VERSION,"integer")
            # try:
            Updater(self.region).setTT(data_version)
            # except:
                # self.dolog('Unable to launch updating mst')

    def test_unbreak_arme_amelioration(self):
        data={}
        data['jQsE54Iz']={}
        data['jQsE54Iz']['qo3PECw6'] = '99170101'
        data.update(self.createBody())
        #with open('deck.json', 'w') as file:
        #    file.write(json.dumps(data))
        self.dolog('%s() was called'%(self.whoami()))
        return self.callApi(data,'MissionWaveReStart')


    def PartyDeckEditRequest(self,CurrentParty,fix=False,unit_to_be_replace=None,unit_to_include=None):
        self.s['user']['current_party']=self.s['user']['team'][self.v['PartyId']]
        data={}
        data[self.v['UserPartyDeckInfo']]={}
        if unit_to_include:
          partyList=[]
          for party in self.s['user']['teams']:
            temp_json={}
            for key in party:
              value=party[key]
              if str(self.s['units'][unit_to_include]['id'][-2:]) in ['17', '27'] and key == self.v['PartyExtremForm']:
                  if value.count(',') >0:
                      value+= ',' + str(unit_to_include) + ':0'
                  else:
                      value=str(unit_to_include) + ':0'
              if party[self.v['PartyId']] == str(self.s['user']['current_party']):
                if key == self.v['PartyUnits']:
                    value=value.replace(unit_to_be_replace,unit_to_include)
                if str(unit_to_be_replace) in party[self.v['PartyExtremForm']]:
                  value=value.replace(str(unit_to_be_replace+':0'),'')
                  value=value.replace(str(unit_to_be_replace+':1'),'')
                  if len(str(value))>0:
                      if str(value)[0:1] == ',':
                          value=str(value)[1:]
                      if str(value)[-1] == ',':
                          value=str(value)[:-1]
                  value=value.replace(',,',',')
              if len(str(value))>0:
                  temp_json.update({key:str(value)})
            partyList.append(temp_json)
          self.dolog("L'unité %s va être intrégrée à l'équipe"%(self.getUnitName(self.s['units'][unit_to_include]['id'])))
            #     if party[self.v['PartyId']] == str(self.s['user']['current_party']):
            #       units=party[self.v['PartyUnits']].split(',')
                  # for unit in units:
                  #   uniqueUnitId=unit.split(':')[2]
          data[self.v['UserPartyDeckInfo']]=partyList

        else:
            data[self.v['UserPartyDeckInfo']]=self.s['user']['teams']
            if self.s['user']['current_party'] == CurrentParty:
                return
        if 'beasts' in self.s['user']:
            data[self.v['T_USER_BEAST_DECK_INFO']]={}
            data[self.v['T_USER_BEAST_DECK_INFO']]=self.s['user']['beasts']
        data[self.v['PartySelect']]=[]
        if fix:
            data[self.v['PartySelect']].append({
                self.v['CurrentParty']:'0',
                self.v['CompanionParty']:'0',
                self.v['ColosseumParty']:'0',
                self.v['ArenaParty']:'0',
                self.v['PartyId']:'0',
                "9ze0U6kA": "-1",
                "aG6Zpm0y": "-1",
                "b61ICxJk": "3",
                "nm25NP1Q": "3",
                "xBi3L6yR": "1",
                "Y5rP2KfR": "1",
                "e31jdZtk": "0"
                })
        else:
            data[self.v['PartySelect']].append({
                self.v['CurrentParty']:str(CurrentParty),
                self.v['CompanionParty']:str(self.s['user']['team'][self.v['CompanionParty']]),
                self.v['ColosseumParty']:str(self.s['user']['team'][self.v['ColosseumParty']]),
                self.v['ArenaParty']:str(self.s['user']['team'][self.v['ArenaParty']]),
                self.v['PartyId']:str(CurrentParty),
                "9ze0U6kA": "-1",
                "aG6Zpm0y": "-1",
                "b61ICxJk": "3",
                "nm25NP1Q": "3",
                "xBi3L6yR": "1",
                "Y5rP2KfR": "1",
                "e31jdZtk": "0"
                })

        #if unit_to_include:
        #    self.UnitEquipRequest(unit_to_be_replace,unit_to_include)
        data.update(self.createBody())
        #with open('deck.json', 'w') as file:
        #    file.write(json.dumps(data))
        self.dolog('%s() was called'%(self.whoami()))
        return self.callApi(data,'PartyDeckEdit')

    def UnitEquipRequest(self, unit_to_be_replace, unit_to_include):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['T_OPE_UNIT_EQUIP']]=[]
        data[self.v['T_OPE_UNIT_EQUIP']].append(
            {
                self.v['Equipment']:str(unit_to_be_replace)+":1-0@2-0@3-0@4-0@5-0@6-0"+','+str(unit_to_include)+':1-0@2-0@3-0@4-0@5-0@6-0',
                self.v['Materia']:str(unit_to_be_replace)+":1-0@2-0@3-0"+","+str(unit_to_include)+":1-0@2-0@3-0@4-0",
                'nQ1iAGf3':str(unit_to_be_replace)+":0-0"+','+str(unit_to_include)+":0-0",
                '2c8nqLrM':str(unit_to_be_replace)+":0"+','+str(unit_to_include)+':0',
                self.v['P_PARTY_TYPE']:"1",
                self.v['PartyId']:str(self.s['user']['current_party'])
            }
        )
        data.update(self.createBody())
        return self.callApi(data,'UnitEquip')


    def InitializeRequest(self):
        data={}
        data.update(self.createBody(True))
        if self.is_japan:
            if hasattr(self,'P_USER_ID'):
                data[self.v['T_USER_INFO']][0][self.v['UserIdGumi']]=self.P_USER_ID
                data[self.v['T_USER_INFO']][0][self.v['ModelChangeCnt']]=self.P_MODEL_CHANGE_CNT if hasattr(self,'P_MODEL_CHANGE_CNT') else '1'
        self.dolog('%s() was called'%(self.whoami()))
        r= self.callApi(data,'Initialize')
        if not r:
            self.lastError='can not load account'
            return None
        t=json.loads(r)
        if self.v['T_VERSION'] in t:
            for i in t[self.v['T_VERSION']]:
                if i[self.v['KeyName']]=='F_MST_VERSION':
                    self.current_mst=str(i[self.v['Value']])
                if i[self.v['KeyName']]=='F_RSC_VERSION':
                    self.current_rsc=str(i[self.v['Value']])
        return r


    def GetUserInfoRequest(self):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data.update(self.createBody())
        try:
            self.dolog('[+] our player id is %s:%s'%(self.s['user'][self.v['UserId']] if self.v['UserId'] in self.s['user'] else 'NONE',self.s['user'][self.v['UserName']]))
        except:
            pass
        tmp= self.callApi(data,'GetUserInfo')

        if tmp:
            _tmp=json.loads(tmp)
            # with open('avant.json', 'w') as file:
            #     file.write(json.dumps(_tmp))
            user_info_bis=self.callApi(data,'GetUserInfoBis')
            self.dolog('GetUserInfoBis was called')

            _tmp.update(json.loads(user_info_bis))
            #with open('apres.json', 'w') as file:
            #    file.write(json.dumps(_tmp))
            if self.v['TransferCode'] in tmp:
                if len(_tmp[self.v['T_USER_INFO']][0][self.v['TransferCode']])>=1:
                    self.P_ACCOUNT_ID=_tmp[self.v['T_USER_INFO']][0][self.v['TransferCode']]
            if self.v['ModelChangeCnt'] in tmp:
                self.P_MODEL_CHANGE_CNT=_tmp[self.v['T_USER_INFO']][0][self.v['ModelChangeCnt']]
            if self.v['UserPartyArenaInfo'] in tmp:
                self.s['user']['party_arena']=_tmp[self.v['UserPartyArenaInfo']]
            if self.v['T_OPE_RANKING_BATTLE'] in tmp:
                self.s['user']['ongoing_arena']=_tmp[self.v['T_OPE_RANKING_BATTLE']]
            if self.new_account:
                self.completeTutorial(True)
                self.new_account=False
            self.setAllUnits(tmp)
            if not self.is_japan:
                self.sgHomeMarqueeInfoRequest('en','hd')
            self.RoutineHomeUpdateRequest()
            self.RoutineWorldUpdateRequest()
            self.OfferwallInfoRequest()
            self.parseMyFriends()
        return tmp



    def setAllUnits(self,_data):
        self.dolog('%s() was called'%(self.whoami()))
        if _data:
            if self.v['T_USER_UNIT_INFO'] in _data:
                self.s['user']['units']=json.loads(_data)[self.v['T_USER_UNIT_INFO']]
                self.all_units=len(self.s['user']['units'])



    def sgHomeMarqueeInfoRequest(self,Language,ImageQuality):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['HomeMarqueeLocale']]=[]
        data[self.v['HomeMarqueeLocale']].append({self.v['Language']:Language})
        data[self.v['HomeMarqueeQuality']]=[]
        data[self.v['HomeMarqueeQuality']].append({self.v['ImageQuality']:ImageQuality})
        data.update(self.createBody())
        return self.callApi(data,'sgHomeMarqueeInfo')



    def routineEventUpdateRequest(self):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data.update(self.createBody())
        return self.callApi(data,'RoutineEventUpdate')


    def RoutineHomeUpdateRequest(self):
        data={}
        data.update(self.createBody())
        return self.callApi(data,'RoutineHomeUpdate')



    def RoutineWorldUpdateRequest(self):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data.update(self.createBody())
        return self.callApi(data,'RoutineWorldUpdate')



    def createBody(self,init=False):
        _data={}
        _data[self.v['T_VERSION']]=self.createVersionTag()
        _data[self.v['T_USER_INFO']]=self.createUserInfoTag()
        if self.is_facebook:
            _data[self.v['IdLinkedSocialNetwork']]=[{self.v['newValueFacebook']: "1"}]
        elif self.is_google:
            _data[self.v['IdLinkedSocialNetwork']]=[{self.v['ValueLinkedSocialNetwork']: "2"}]
        if not init:
            if not self.v['Data'] in self.s:
                self.s=self.setSettings()
            _data[self.v['T_SIGNAL_KEY']]=self.createSignalKeyTag()
        if self.is_facebook or self.is_google:
            _data[self.v['FacebookGoogle']]=[{self.v['UsingFacebookOrGoogle']:'1'}]
        return _data


    def callApi(self,dtt,id,MissionId=None,repeat=None):
        self.dolog('%s() was called'%(self.whoami()))
        request_id=self.t.getRequestID(id)
        request_key=self.t.getRequestKey(id)
        request_url=self.t.getRequestUrl(id)+'.php'
        # TODO a voir si lors de farm le TEAYk6R1 change ou pas
        if not repeat:
            _data={}
            _data[self.v['T_HEADER']]={}
            _data[self.v['T_HEADER']][self.v['RequestID']]=request_id
            _data[self.v['T_HEADER']][self.v['Milliseconds']]=self._api_time
            self._api_time+=randint(1,10000)
            _data[self.v['Encrypted']]={}
            try:
                _data[self.v['Encrypted']][self.v['Data']]=json.loads(json.dumps((self.t.encrypt(json.dumps(dtt),request_key))))
            except:
                self.lastError="Encrypt data error"
                self.dolog('Encrypt data error %s'%(dtt))
                return None
        else:
            _data=repeat
        tmp_url=self.base_url+request_url
        try:
            response=self.r.post(url=tmp_url,data=json.dumps(_data),stream=True)
        except requests.exceptions.ChunkedEncodingError:
            self.lastError='ChunkedEncodingError'
            self.dolog('ChunkedEncodingError proxy dead %s'%(self.s['user'][self.v['UserId']] if self.v['UserId'] in self.s['user'] else ''))
            time.sleep(1)
            return self.callApi(dtt,id)
        except requests.exceptions.ProxyError:
            self.updateProxy('proxy dead')
            self.renew_tor_ip()
            self.dolog('proxyerror proxy dead %s'%(self.proxy))
            self.lastError='ProxyError'
            return None
        except requests.exceptions.ConnectionError:
            self.updateProxy('proxy dead')
            self.renew_tor_ip()
            self.lastError='ConnectionError'
            self.dolog('connectionerror proxy dead %s'%(self.proxy))
            return None
        except requests.exceptions.Timeout:
            self.updateProxy('proxy dead')
            self.renew_tor_ip()
            self.dolog('Timeout %s'%(self.proxy))
            self.lastError='Timeout'
            time.sleep(2)
        except:
            self.lastError='some error'
            self.dolog('FUCKING EXCP %s'%(traceback.print_exc()))
            time.sleep(2)
        if response.status_code==500:
            self.dolog('we have 500')
            return None
        _chunks=''

        try:
            _chunks=response.text
        except:
            print('Error with the response received')
            return self.callApi(dtt,id)
        try:
            if not _chunks:
                self.dolog('no content...')
                return self.callApi(dtt,id)
        except:
            self.dolog('ficken ihn')
            time.sleep(2)
            return self.callApi(dtt,id)
        if 'SERVER_MSG_160' in _chunks:
            self.t.findError('SERVER_MSG_160',self.lang)
            return self.callApi(dtt,id)
        if 'SERVER_MSG_32' in _chunks:
            self.t.findError('SERVER_MSG_32',self.lang)
        if 'maintenance' in _chunks or '\u305f\u3060\u3044\u307e' in _chunks:
            self.dolog('We are undergoing mainten')
            maintain_info=json.loads(_chunks)[self.v['T_MESSAGE']][self.v['Message']]
            maintain_info_lang=json.loads(maintain_info)[self.lang.lower()]
            print(maintain_info_lang)
            exit(1)
        if 'SERVER_MSG_' in _chunks:
            self.dolog(self.t.findError(json.loads(_chunks)[self.v['T_MESSAGE']][self.v['Message']], self.lang))
        if self.v['Encrypted'] not in _chunks:
            self.dolog('No data received')
            # self.updateMST(plain_res)
            # self.relog()
            # return self.callApi(dtt,id)
        if self.v['T_MESSAGE'] in _chunks:
            # self.dolog('we have error? %s'%(response.content.replace('\n','').replace('\r','')))
            try:
                if 'SERVER_MSG_216' in _chunks or 'SERVER_MSG_269' in _chunks:
                    self.dolog('New data exists')
                    self.relog()
                    self.updateMST(_chunks)
                    return self.callApi(dtt,id)
                _erro=json.loads(_chunks)[self.v['T_MESSAGE']][self.v['Message']]
                _error_str=self.t.findError(_erro, self.lang)
                self.lastError=_error_str
            except:
                self.dolog('UNKNOWN RESPONSE RECEIVED')
                return self.callApi(dtt,id)
        if 'SERVER_MSG_114' in _chunks or 'SERVER_MSG_158' in _chunks or 'SERVER_MSG_36' in _chunks or 'SERVER_MSG_83' in _chunks or 'SERVER_MSG_190' in _chunks or 'SERVER_MSG_129' in _chunks or 'SERVER_MSG_85' in _chunks or 'SERVER_MSG_160' in _chunks:
            self.dolog('Error message in response')
            return None
        if '403 Forbidden' in _chunks:
            self.updateProxy('proxy dead')
            self.dolog('proxy dead 403 %s'%(self.proxy))
            self.lastError='proxy blocked'
            self.renew_tor_ip()
            # exit(1)
            # os.system("c: && cd c:/tor/tor && tor --service stop && tor --service start")
        if 'Bad Gateway' in _chunks:
            self.updateProxy('bad gateway')
            self.dolog('Bad Gateway %s'%(self.proxy))
            self.lastError='bad gateway'
            time.sleep(2)
            self.renew_tor_ip()
            return self.callApi(dtt,id)
        if 'SERVER_MSG_34' in _chunks:
            self.dolog("SERVER_MSG_34 - L'id de la mission ne semble pas correcte" + ' ' + str(id))
            time.sleep(0.5)
            exit("mauvais id de mission")
            return self.callApi(dtt,id) # l'id de la mission n'existe peut être pas
        if response.status_code != 200:
            self.updateProxy('proxy dead')
            self.dolog('not statut 200')
            self.lastError='no data from gumi'
            self.renew_tor_ip()
            time.sleep(2)
            return self.callApi(dtt,id)
        if '_MSG_' in _chunks or self.v['Data'] not in _chunks:
            return None
        if 'SERVER_MSG_225' in _chunks:
            self.dolog('SERVER_MSG_225')
            self.FriendListRequest(1)
            return self.MissionEndRequest(MissionId,_data)
        plain_res=None
        try:
            if self.v['Encrypted'] in _chunks:
                # print(type(_chunks))
                plain_res=json.dumps(json.loads(self.t.decrypt(json.loads(_chunks)[self.v['Encrypted']][self.v['Data']],request_key)))
        except:
            self.dolog('error when decrypting received data')
            time.sleep(0.5)
            return self.callApi(dtt,id,None,_data)
        if plain_res is None:
            self.dolog('no data received')
            return _chunks
        # self.updateProxy(str(r.elapsed.total_seconds()))
        if self.v['T_VERSION_INFO'] in plain_res:
            if self.version_build != json.loads(plain_res)[self.v['T_VERSION_INFO']][self.v['AppVersion']]:
                self.dolog('[+] update software version done : current version = ' + json.loads(plain_res)[self.v['T_VERSION_INFO']][self.v['AppVersion']])
                self.t.updateJsonFile('data.yaml', 'gl', 'build_version', json.loads(plain_res)[self.v['T_VERSION_INFO']][self.v['AppVersion']],"integer")
            self.version_build=json.loads(plain_res)[self.v['T_VERSION_INFO']][self.v['AppVersion']]
        if self.v['T_VERSION'] in plain_res and 'F_MST_VERSION' in plain_res:
            self.updateMST(plain_res)
        if self.v['Data'] in plain_res:
            self.s[self.v['Data']]=json.loads(plain_res)[self.v['T_SIGNAL_KEY']][0][self.v['Data']]
        if self.v['T_USER_INFO'] in plain_res:
            if self.v['UserId'] in plain_res:
                self.parseUserInfo(plain_res)
        if self.v['T_USER_UNIT_FAVORITE_MARGE'] in plain_res:
            self.parseFav(plain_res)
        if self.v['T_USER_TEAM_INFO'] in plain_res:
            self.parseUserData(plain_res)
            self.addAccountInfo(plain_res)
        if self.v['T_USER_UNIT_INFO'] in plain_res:
            self.parseMyUnits(plain_res)
        # if 'pzf5se6V' in plain_res: ancien friend TODO gestion des amis
        # if 'I53AVzSo' in plain_res:
        # 	self.parseMyFriends(plain_res)
        if self.v['UserPartyDeckInfo'] in plain_res:
            self.parseMyTeams(plain_res)
        if self.v['T_USER_ACTUAL_INFO'] in plain_res:
            self.parseMyTeamSetup(plain_res)
        if self.v['PartySelect'] in plain_res:
            print('OIUIOAEOUIZAOIEUAEOIAEOIEUZAEOIEOUAEIZAEOUZAOEZAEJBKJHBQSKJFDHFKJHSQDKUSQDKJHSQDKJQSDKJQSDKJHQSDKJSQDKJHSQDKJHSQDIZAEZDKZAUIJZEIHZIUEZAIUE IOAZUEZAEJIOZAE UIOZA EJIZA3 ERUI JAEZ IUEZ FIJEZFKJESD FKJ SD FK JSD F KJEZ FJO HEZAROI ZAIRJ ZAPOIR ZAPOIRJ ZAPIOJE APZO3IE PAIOZ EPZAI EPIOEZA  OPLZJELKZAE LKAZE LOLS D ZAOI ZAOUI')
        if self.v['T_RUNNING_MISSION_RESUME_INFO'] in plain_res and len(json.loads(plain_res)[self.v['T_RUNNING_MISSION_RESUME_INFO']][0][self.v['MissionId']])>=1:
            self.RmRetireRequest(json.loads(plain_res)[self.v['T_RUNNING_MISSION_RESUME_INFO']][0][self.v['MissionId']])
        self.parseUnlocked(plain_res)
        try:
            json.loads(plain_res)
        except:
            self.dolog('bad json from gumi')
            return self.callApi(dtt,id)
        return plain_res



    def createVersionTag(self):
        self.dolog('%s() was called'%(self.whoami()))
        _data=[]
        _data.append(self.makemesort('F_APP_VERSION_IOS' if self.s[self.v['DevicePlatform']]=='1' else 'F_APP_VERSION_AND', str(self.version_build)))
        _data.append(self.makemesort('F_RSC_VERSION',str(self.current_rsc)))
        _data.append(self.makemesort('F_MST_VERSION',str(self.current_mst)))
        return _data



    def createSignalKeyTag(self):
        _data=[]
        _data.append({self.v['Data']:self.s[self.v['Data']]})
        return _data


    def makemesort(self,q,w):
        return OrderedDict([(self.v['KeyName'],q),(str(self.v['Value']),w)])


    def createUserInfoTag(self):
        _data=[{}]
        if self.is_japan:
            _data[0][self.v['ModelChangeCnt']]='0'
            _data[0][self.v['OperatingSystem']]=self.t.genRandomDeviceString()
            _data[0][self.v['OperatingSystem']]=self.s[self.v['OperatingSystem']]
            _data[0][self.v['ContactId']]=self.t.getHashedDeviceID(self.s[self.v['DeviceId']]) #if not hasattr(self, 'device_id') else self.device_id
            _data[0][self.v['BuildVersion']]='ver.20180523'
            _data[0][self.v['Time']]=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            if not self.is_starter:
                _data[0][self.v['Password']]=self.s['user'][self.v['Password']]
                _data[0][self.v['UserName']]=self.s['user'][self.v['UserName']]
                _data[0][self.v['UserIdGumi']]=self.s['user'][self.v['UserIdGumi']]
                _data[0][self.v['UserId']]=self.s['user'][self.v['UserId']]
                _data[0][self.v['MacroToolRunningStatus']]=self.s['user'][self.v['MacroToolRunningStatus']]
                _data[0][self.v['ModelChangeCnt']]=self.s['user'][self.v['ModelChangeCnt']]
                _data[0][self.v['Ymd']]='0'
                _data[0]['40w6brpQ']='0'
                _data[0]['jHstiL12']='0'
                try:
                    _data[0][self.v['Ymd']]=self.s['user'][self.v['Ymd']]
                except:
                    pass
        else:
            _data[0][self.v['ModelChangeCnt']]='0'
            _data[0][self.v['OperatingSystem']]=self.t.genRandomDeviceString()
            _data[0][self.v['CountryCode']]=self.lang.upper()
            _data[0][self.v['BuildVersion']]=self.version_software
            _data[0][self.v['AdvertisingId']]=self.s['user']['session_device']
            _data[0][self.v['DevicePlatform']]=self.s[self.v['DevicePlatform']]
            _data[0][self.v['DeviceId']]=self.s[self.v['DeviceId']]
            _data[0][self.v['ContactId']]=self.t.getHashedDeviceID(self.s[self.v['DeviceId']])
            _data[0][self.v['Time']]=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            _data[0]['40w6brpQ']='0'
            _data[0]['jHstiL12']='0'
            if self.is_facebook:
                _data[0][self.v['FacebookUserId']]=self.s['facebookId']
                _data[0][self.v['FacebookToken']]=self.s['facebookToken']
            elif self.is_google:
                _data[0][self.v['GoogleUserId']]=self.s['gid']
                _data[0][self.v['GoogleToken']]=self.s['goo']
            if not self.is_starter:
                _data[0][self.v['Ymd']]='0'
                _data[0][self.v['Password']]=self.s['user'][self.v['Password']]
                _data[0][self.v['UserIdGumi']]=self.s['user'][self.v['UserIdGumi']]
                _data[0][self.v['UserId']]=self.s['user'][self.v['UserId']]
                try:
                    _data[0][self.v['Ymd']]=self.s['user'][self.v['Ymd']]
                except:
                    pass
                _data[0][self.v['UserName']]=self.s['user'][self.v['UserName']]
                _data[0][self.v['GumiId']]=self.s['user'][self.v['GumiId']]
                _data[0][self.v['MacroToolRunningStatus']]=self.s['user'][self.v['MacroToolRunningStatus']]
                _data[0][self.v['AppVersion']]=self.s['user'][self.v['AppVersion']]
                _data[0][self.v['GumiToken']]=self.s['user'][self.v['GumiToken']]
        if self.new_account:
            _data[0][self.v['UserName']]=self.s['user'][self.v['UserName']] if self.v['UserName'] in self.s['user'] else 'Rain'
        return _data


    def CreateUserRequest(self):
        data={}
        data.update(self.createBody())
        return self.callApi(data,'CreateUser')


    def parseUserInfo(self,data):
        user_info=json.loads(data)[self.v['T_USER_INFO']][0]
        # with open('chien.json', 'w') as f:
        # #     f.write(data)
        if self.v['UserIdGumi'] in user_info and len(user_info[self.v['UserIdGumi']])==0:
            if len(data)<=300:
                self.dolog('UNICORN %s'%(data))
            self.new_account=True
            self.dolog('[+] found fresh account, will do tutorial')
            exit(1)
            self.s['user'][self.v['UserName']]='Rain'
            self.CreateUserRequest()
        if self.v['UserIdGumi'] in user_info and len(user_info[self.v['UserIdGumi']])>=2:
            for i in user_info:
                self.s['user'][i]=user_info[i]
            self.is_starter=False

    def parseUserData(self,data):
        user_info=json.loads(data)[self.v['T_USER_TEAM_INFO']][0]
        if self.v['ArenaOrb'] in user_info:
            try:
                self.s['user']['arena_orbs']=int(json.loads(data)[self.v['T_USER_TEAM_INFO']][0][self.v['ArenaOrb']])
            except:
                self.renew_tor_ip()
            if self.clear_arena and self.s['user']['arena_orbs'] > 0:
                self.clearArena()
        if self.v['RaidOrb'] in user_info and self.t.is_integer(json.loads(data)[self.v['T_USER_TEAM_INFO']][0][self.v['RaidOrb']]):
            self.s['user']['raid_orbs']=int(json.loads(data)[self.v['T_USER_TEAM_INFO']][0][self.v['RaidOrb']])
        if self.v['UserIdGumi'] in user_info and len(user_info[self.v['UserIdGumi']])>=2:
            for i in user_info:
                if i==self.v['Energy']:
                    self.s['user']['current_energy']=int(user_info[i])
                self.s['user'][i]=user_info[i]


    def OfferwallInfoRequest(self):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data.update(self.createBody())
        self.callApi(data,'sgOfferwallInfo')


    def startMission(self,id,reenter=False,cnt=0):
        if self.changeUnitWithFullTMR and self.numberFarmAlreadyTurnOnce>1:
          self.checkIfUnitFullTMR()

        if ',' in str(id):
            id = id.split(',')
            res=[]
            for _m in id:
                r=self.startMission_(_m,reenter,cnt)
                if r:
                    if r[0]:
                        res.append(r[1])
            return [True,'\n'.join(res)]
        else:
            return self.startMission_(id,reenter,cnt)


    def isUnlocked(self, id):
        if 'unlocked' in self.s['user']:
            id=str(id)
            for i in self.s['user']['unlocked']:
                if i['vUCf4Rw3']==id and i['N6hVhvgf']=='1':
                    return True
        if 'dungeon_unlocked' in self.s['user']:
            id=str(id)
            for i in self.s['user']['dungeon_unlocked']:
                if i[self.v['P_SELECT_DUNGEON_ID']]==id and i[self.v['P_SELECT_YMD_REST_TIME']]!='0':
                    return True
        return False



    def sgMissionUnlockRequest(self,MissionId):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data['ySFXhkpu']=[]
        data['ySFXhkpu'].append({self.v['MissionId']:str(MissionId)})
        data.update(self.createBody())
        return self.callApi(data,'sgMissionUnlock')


    def dailyDungeonSelectRequest(self,MissionId):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['T_OPE_DUNGEON_SELECT']]=[]
        data[self.v['T_OPE_DUNGEON_SELECT']].append({self.v['DungeonId']:str(MissionId)})
        data.update(self.createBody())
        return self.callApi(data,'DailyDungeonSelect')



    def startMission_(self,id,reenter=False,cnt=0):
        need_unlock=[9200001,9200002,9200003,9210001,9210002,9210003]
        unlock_dungeon_gems=[2110501,2110502,2110503]
        self.dolog('%s() was called'%(self.whoami()))
        id=int(id)
        if id in unlock_dungeon_gems:
            id_dungeon=int(str(id)[0:5])
            if not self.isUnlocked(id_dungeon) and id not in self.dungeons_unlocked:
                update_unlocked=self.dailyDungeonSelectRequest(id_dungeon)
                self.parseUnlocked(update_unlocked)
                self.dungeons_unlocked.append(id)
        if id in need_unlock:
            if not self.isUnlocked(id) and id not in self.dungeons_unlocked:
                res=self.sgMissionUnlockRequest(id)
                self.dungeons_unlocked.append(id)
                if not res:
                    return None,None
        _mission_name=self.t.findMissionName(id, self.lang)
        self.dolog('[+] mission %s (%s) started'%(_mission_name,id))
        _ms_infos=self.t.findMissionInfo(int(id))
        self._ms_type=_ms_infos['type']
        _ecost=_ms_infos['energy']
        self.mission_rounds=_ms_infos['rounds']
        if self.refill_lapis and int(self.s['user'][self.v['UserLevel']])>8 and _ecost>self.s['user']['current_energy']:
            self.dolog('[+] refilling energy')
            self.ShopUseRequest(20,'')
        if self.refill_raid_orbs and int(self.s['user'][self.v['RaidOrb']])==0:
            self.dolog('[+] refilling orbs')
            self.ShopUseRequest(22,'')
        if self.refill_potion and int(self.s['user'][self.v['UserLevel']])>8 and _ecost>self.s['user']['current_energy']:
            if _ecost>int(self.s['user']['current_energy']):
                nb_potion=math.ceil((_ecost-self.s['user']['current_energy'])/10)
                self.dolog('[+] refilling energy with '+ str(nb_potion) +' potion(s)')
                self.ShopUseRequest('50','23:100:'+str(nb_potion),True)
            else:
                self.dolog('[+] refilling energy with potion not done - useless')
        if self._ms_type == 2:
            if reenter:
                _mission_data=self.MissionReStartRequest(id)
            else:
                _mission_data=self.MissionStartRequest(id)
        else:
            if reenter:
                _mission_data=self.MissionWaveReStartRequest(id)
            else:
                _mission_data=self.MissionWaveStartRequest(id)
        if _mission_data:
            if 'R_MSG_' in _mission_data or self.v['Data'] not in _mission_data and not 'SERVER_MSG_24' in _mission_data:
                # self.LogShit(_mission_data)
                return None,None
            self.DungeonResourceLoadMstListRequest(id)
            if _ecost == 0:
                sleeping=self.SLEEPING_TIME_FARM
            else:
                sleeping=self.SLEEPING_TIME_MISSION
            self.dolog("sleeping %s"%(sleeping))
            time.sleep(sleeping)
            _mission_end_data=self.MissionEndRequest(id,json.loads(_mission_data))
            if _mission_end_data:
                if 'R_MSG_' in _mission_end_data or self.v['Data'] not in _mission_end_data and not 'SERVER_MSG_24' in _mission_end_data:
                    # self.LogShit(_mission_end_data)
                    return None,None
                vd=self.checkReward(_mission_end_data,json.loads(_mission_end_data),id)
                vi=self.checkTMR(_mission_end_data)
                vd=vd+vi
                self.numberFarmAlreadyTurnOnce+=1
                self.dolog('[+] mission %s (%s) completed'%(_mission_name,id))
                return True,vd
        # if cnt <=3 and self.:
        #     self.dolog('fuck gumi %s'%(cnt))
        #     time.sleep(2)
        #     return self.startMission(id,reenter,cnt+1)
        # self.dolog('[+] line 691 wtf')
        self.dolog(self.getLastError())
        return None,None



    def ShopUseRequest(self,P_SHOP_ID,ItemCount=1,refillPotion=False):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['T_OPE_SHOP_USE']]=[]
        if refillPotion:
            data[self.v['T_OPE_SHOP_USE']].append({self.v['P_SHOP_ID']:P_SHOP_ID,self.v['P_ADD_INFO']:ItemCount})
        else:
            data[self.v['T_OPE_SHOP_USE']].append({self.v['P_SHOP_ID']:P_SHOP_ID,self.v['ItemCount']:ItemCount})
        data.update(self.createBody())
        return self.callApi(data,'ShopUse')


    def MissionStartRequest(self,MissionId):
        self.dolog('%s() was called'%(self.whoami()))

        data={}
        data[self.v['Mission']]=[]
        if self.useFriend:
            self.lastFriend=self.get_friend_id()
            data[self.v['Mission']].append({
                self.v['MissionId']:str(MissionId),
                self.v['FriendPoints']:str(10),
                self.v['ReinforcementFriendId']:str(self.lastFriend[0]),
                self.v['ReinforcementUnitId']:str(self.lastFriend[1]),
                'xojJ2w0S':str(0)
            })
            self.dolog('Friend unit name : ' + str(self.t.getUnitName(str(self.lastFriend[1]),self.lang)))
        else:
            data[self.v['Mission']].append({self.v['MissionId']:str(MissionId),self.v['FriendPoints']:'0',self.v['BonusUnit']:'0'})
        data.update(self.createBody())
        return self.callApi(data,'MissionStart')



    def MissionReStartRequest(self,MissionId):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['Mission']]=[]
        # TODO friend

        data[self.v['Mission']].append({self.v['MissionId']:str(MissionId),self.v['FriendPoints']:'0',self.v['BonusUnit']:'0'})
        data.update(self.createBody())
        return self.callApi(data,'MissionReStart')



    def MissionWaveStartRequest(self,MissionId):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['Mission']]=[]
        if self.useFriend:
            self.lastFriend=self.get_friend_id()
            data[self.v['Mission']].append({
                self.v['MissionId']:str(MissionId),
                self.v['FriendPoints']:str(10),
                self.v['ReinforcementFriendId']:str(self.lastFriend[0]),
                self.v['ReinforcementUnitId']:str(self.lastFriend[1]),
                'xojJ2w0S':str(0)
            })
            self.dolog('Friend unit name : ' + str(self.t.getUnitName(str(self.lastFriend[1]),self.lang)))
        else:
            data[self.v['Mission']].append({self.v['MissionId']:str(MissionId),self.v['FriendPoints']:'0',self.v['BonusUnit']:'0'})
        data.update(self.createBody())
        return self.callApi(data,'MissionWaveStart')

    def get_friend_id(self):
        # self.parseMyFriends()
        data=[]
        self.dolog('%s() was called'%(self.whoami()))
        # with open('avant.json', 'w') as file:
        #     file.write(json.dumps(friend_available))

        if not self.s['user']['FriendListFull']:
            self.parseMyFriends()
        if self.s['user']['FriendListFull']:
            friend=self.s['user']['FriendListFull'][1].split(':')
            friendId=friend[0]
            friendUnitId=friend[1]
            data.append(friendId)
            data.append(friendUnitId)
            return data

        friend_available=json.loads(self.GetReinforcementInfoRequest())
        if friend_available:
            for i in friend_available:
                if self.v['T_FRIEND_UNIT_INFO'] in i:
                    friend=json.loads(json.dumps(friend_available[i]))[0]
                    friendId=friend[self.v['UserId']]
                    friendUnitId=friend[self.v['UnitId']]
                    data.append(friendId)
                    data.append(friendUnitId)
                    return data



    def GetReinforcementInfoRequest(self, number_list_friend='0'):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['T_OPE_FRIEND_INFO']]=[]
        data[self.v['T_OPE_FRIEND_INFO']].append({
            self.v['FriendIdUniqueUnitIdList']:self.s['user']['FriendListId'],
            self.v['P_NORM_REIN_REQ']:'0',
            'i6PMuUn1':'1',
            'Y58ENcB4':str(number_list_friend)
            })
        data.update(self.createBody())
        return self.callApi(data,'GetReinforcementInfo')

    def parseMyFriends(self):
        data=''
        full_list=[]
        self.s['user']['FriendListId']=''
        self.s['user']['FriendListFull']=''
        self.dolog('%s() was called'%(self.whoami()))
        friend_list=json.loads(self.FriendListRequest(1))
        friends=json.loads(json.dumps(friend_list))[self.v['T_FRIEND_UNIT_INFO_UPD']] #ICI il doit tout y avoir
        # with open('amis.json', 'w') as file:
        #     file.write(json.dumps(friends))
        for friend in friends:
            if 'm3Wghr1j' in friend and 'G8mtXbf6' in friend:
                if len(data)>0:
                    data += ','
                data+=str(friend['m3Wghr1j']) + ':' + str(friend['G8mtXbf6'])
            if 'm3Wghr1j' in friend and '3HriTp6B' in friend:
                full_list.append(str(friend['m3Wghr1j']) + ':' + str(friend['3HriTp6B']))
        #print('data:',data)
        #print('full_list:',full_list)
        self.s['user']['FriendListFull']=full_list
        self.s['user']['FriendListId']=data


    def MissionWaveReStartRequest(self,MissionId):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['Mission']]=[]
        # TODO friend
        # if self.canFriend and len(self.settings['friends'].keys())>=1:
        #     rnd_friend=random.choice(self.settings['friends'].keys())
        #     self.dolog('[+] friend %s:%s'%(rnd_friend,self.settings['friends'][rnd_friend]['name']))
        #     v0XUs3Tv6='5' if len(self.settings['friends'][rnd_friend]['isfriend'])==0 else '10'
        #     data[self.v['Mission']].append({self.v['MissionId']:str(MissionId),self.v['FriendPoints']:str(v0XUs3Tv6),self.v['BonusUnit']:'0',self.v['NotFriendId']:rnd_friend,'qLke7K8f':self.settings['friends'][rnd_friend]['charid']})
        #     self.lastFriend=rnd_friend
        #     del self.settings['friends'][rnd_friend]
        #     if len(self.settings['friends'].keys())==0:
        #         self.FriendListRequest(1)
        # else:
        data[self.v['Mission']].append({self.v['MissionId']:str(MissionId),self.v['FriendPoints']:'0',self.v['BonusUnit']:'0'})
        data.update(self.createBody())
        return self.callApi(data,'MissionWaveReStart')



    def DungeonResourceLoadMstListRequest(self,id):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['T_OPE_DUNGEON_RESOURCE_LOAD']]=[]
        data[self.v['T_OPE_DUNGEON_RESOURCE_LOAD']].append({self.v['ObjectId']:str(id),self.v['EventType']:'0'})
        data.update(self.createBody())
        return self.callApi(data,'DungeonResourceLoadMstList')


    def MissionEndRequest(self,MissionId,_data):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['MissionEndContinue']]=[]
        data[self.v['MissionEndContinue']].append({self.v['Count']:'0'})
        data[self.v['Mission']]=[{}]
        data[self.v['Mission']][0][self.v['MissionId']]=str(MissionId)
        # if self.friend and len(self.s['friends'].keys())>=1:
        if self.useFriend:
            # data[self.v['Mission']][0][self.v['NotFriendId']]=str(self.lastFriend)
            data[self.v['Mission']][0][self.v['ReinforcementFriendId']]=self.lastFriend[0]
            data[self.v['Mission']][0][self.v['ReinforcementUnitId']]=self.lastFriend[1]
        # elif self.friend and len(self.s['friends'].keys())==0:
            # self.FriendListRequest(1)
            # return self.MissionEndRequest(MissionId,_data)
        data[self.v['MissionEndChallenge']]=[]
        _2=self.buildMissionEndChallenge(_data,MissionId)
        data[self.v['MissionEndChallenge']].append(_2 if _2 else {self.v['DeadCount']:'0'})
        data[self.v['MissionResults']]=self.buildMissionResults(_data,MissionId)
        data[self.v['T_USER_ARCHIVE_INFO']]=self.buildT_USER_ARCHIVE_INFO(_data,MissionId)
        if self.s['user']['ach'] and len(self.s['user']['ach'])>=1:
            data[self.v['T_USER_ARCHIVE_INFO']]={}
            data[self.v['T_USER_ARCHIVE_INFO']]=self.s['user']['ach']
        if self.open_chest and self._ms_type == 2:
            data[self.v['Mission']][0][self.v['GrantedSwitchId']]=','.join(self.s['openedChests'])
        data.update(self.createBody())
        return self.callApi(data,'MissionEnd')



    def buildMissionEndChallenge(self,data,MissionId):
        p=[]
        p2=[]
        _rr={}
        if self.solve_mission:
            _r=self.solveMission(MissionId)
            if _r:
                _rr.update(_r)
        if self.v['T_WAVE_BATTLE_INFO'] in data:
            for i in data[self.v['T_WAVE_BATTLE_INFO']]:
                if self.v['P_PHASE_NO'] in i and i[self.v['P_PHASE_NO']]:
                    _str='%s:%s:%s'%(i[self.v['P_PHASE_NO']],i[self.v['MissionWaveId']],i[self.v['MonstPartsNum']])
                    if _str not in p:
                        p.append(_str)
        if self.v['T_MONSTER_MST'] in data:
            for i in data[self.v['T_MONSTER_MST']]:
                if self.v['MissionWaveId'] in i and i[self.v['MissionWaveId']]:
                    _str='%s:0:0'%(i[self.v['MissionWaveId']])
                    p2.append(_str)
        p.sort()
        _rr[self.v['BattleClear']]=','.join(p)
        _rr[self.v['DeadCount']]='0'
        _rr[self.v['P_MONSTER_DATA']]=','.join(p2)
        return _rr


    def solveMission(self,id):
        try:
            res={}
            clgs=self.t.getChallenges(int(id))
            if clgs:
                for m in clgs:
                    q=clgs[m].split(',')
                    for p in q:
                        w=p.split(':')
                        w[0]=int(w[0])
                        if w[0]==68:#fin quest DONE
                            pass
                        elif w[0]==33:#no ko DONE
                            pass
                        elif w[0]==35:#party x less DONE
                            pass
                        elif w[0]==34:#party x more DONE
                            pass
                        elif w[0]==38:#no continue DONE
                            pass
                        elif w[0]==0:#use item DONE
                            res[self.v['Items_4p6CrcGt']]='101000100:1'
                        elif w[0]==1:#no items DONE
                            pass
                        elif w[0]==45:#evoke x more DONE
                            res[self.v['Espers']]='1:%s'%(int(w[1])+1)
                        elif w[0]==17:#lb unused DONE
                            pass
                        elif w[0]==16:#use lb DONE
                            res[self.v['LimitBreaks']]='100000202:1'
                        elif w[0]==6:#no magic DONE
                            pass
                        elif w[0]==5:#use magic DONE
                            if self.v['Magics'] in res:
                                res[self.v['Magics']]+=',30090:1'
                            else:
                                res[self.v['Magics']]='30090:1'
                        elif w[0]==28:#use esper DONE
                            res[self.v['Espers']]='1:1'
                        elif w[0]==41:#use magic x time DONE
                            if self.v['Magics'] in res:
                                res[self.v['Magics']]+=',30090:%s'%(int(w[1])+1)
                            else:
                                res[self.v['Magics']]='30090:%s'%(int(w[1])+1)#20010 MILA
                        elif w[0]==26:#deal x damage DONE
                            if self.v['ElementalAttacks'] in res:
                                res[self.v['ElementalAttacks']]+= ',%s:1'%(w[1])
                            else:
                                res[self.v['ElementalAttacks']]= '%s:1'%(w[1])
                        elif w[0]==49:#use more x lb DONE
                            res[self.v['LimitBreaks']]='100000202:%s'%(int(w[1])+1)
                        elif w[0]==7:#use x abiltiy DONE
                            if self.v['Magics'] in res:
                                res[self.v['Magics']]+=',%s:1'%(w[1])
                            else:
                                res[self.v['Magics']]='%s:1'%(w[1])
                        elif w[0]==21:#use x ability DONE
                            if self.v['Specials'] in res:
                                res[self.v['Specials']]+=',%s:1'%(w[1])
                            else:
                                res[self.v['Specials']]='%s:1'%(w[1])
                        elif w[0]==13:#use x magic DONE
                            if int(w[1])==2:
                                if self.v['Magics'] in res:
                                    res[self.v['Magics']]+= ',20190:1'
                                else:
                                    res[self.v['Magics']]= '20190:1'
                            elif int(w[1])==1:
                                if self.v['Magics'] in res:
                                    res[self.v['Magics']]+= ',10060:1'
                                else:
                                    res[self.v['Magics']]= '10060:1'
                            elif int(w[1])==3:
                                if self.v['Magics'] in res:
                                    res[self.v['Magics']]+= ',30010:1'
                                else:
                                    res[self.v['Magics']]= '30010:1'
                        elif w[0]==30:#evoke x DONE
                            if self.v['Espers'] in res:
                                res[self.v['Espers']]+=',%s:1'%(w[1])
                            else:
                                res[self.v['Espers']]='%s:1'%(w[1])
                        elif w[0]==12:#no x magic DONE
                            pass
                        elif w[0]==14:#magic unused DONE
                            pass
                        elif w[0]==40:#less x items DONE
                            pass
                        elif w[0]==36:#x in party
                            pass
                        elif w[0]==29:#no esper DONE
                            pass
                        elif w[0]==18:#kill boss with lb DONE
                            if self.v['KnockOuts'] in res:
                                res[self.v['KnockOuts']]+=',%s@%s:1@5:100000102'%(w[1],w[2])
                            else:
                                res[self.v['KnockOuts']]='%s@%s:1@5:100000102'%(w[1],w[2])
                        elif w[0]==15:#kill boss with magic DONE
                            res[self.v['KnockOuts']]='%s@%s:1@2:20020'%(w[1],w[2])
                        elif w[0]==59:#deal x x times DONE
                            #res[self.v['ElementalAttacks']]= '%s:%s'%(w[1],int(w[2])+1)
                            if self.v['ElementalAttacks'] in res:
                                res[self.v['ElementalAttacks']]+=',%s:%s'%(w[1],int(w[2])+1)
                            else:
                                res[self.v['ElementalAttacks']]='%s:%s'%(w[1],int(w[2])+1)
                        elif w[0]==32:#kill boss with esper DONE
                            res[self.v['KnockOuts']]='%s@%s:1@3:1'%(w[1],w[2])
                        elif w[0]==20:#no abiltity DONE
                            pass
                        elif w[0]==2:#use x item DONE
                            res[self.v['Items_4p6CrcGt']]='%s:1'%(w[1])
                        elif w[0]==23:#kill boss with ability
                            pass
                        elif w[0]==4:#kill boss with item
                            pass
                        elif w[0]==75:#clear within x turns DONE
                            pass
                        elif w[0]==77:#kill x within turns DONE
                            pass
                        elif w[0]==1000:#clear within x sec
                            res[self.v['P_MISSION_DATA']]='%s'%(int(w[1])-1)
                        elif w[0]==132:#elemntary combo x times in one turn
                            pass
                        elif w[0]==122:#combo x times in one turn
                            if self.v['ElementalAttacks'] in res:
                                res[self.v['ElementalAttacks']]+=',%s:%s'%(w[1],int(w[2])+1)
                            else:
                                res[self.v['ElementalAttacks']]='%s:%s'%(w[1],int(w[2])+1)
                        elif w[0]==69:#terrasser tous les bahamuts obscurs et bahamut #TODO
                            pass
                        elif w[0]==65:# Defeat Vlad's crystal with X #TODO
                            pass
                        else:
                            self.dolog('dont know %s for %s'%(w,id))#m,a,w
                            pass
                return res
            else:
                return None
        except:
            return None


    def buildMissionResults(self,data,id,colloeseum=False):
        res={}
        res[self.v['BonusGil']]=str(randint(200000,900000)) if not colloeseum else str(randint(0,200))
        res[self.v['StolenGil']]='0'
        res[self.v['EncounteredMonsters']]=self.buildEncounteredMonsters(data)
        res[self.v['P_GIL_THROW']]='0'
        res[self.v['MonstersKilledCount']]=self.buildMonstersKilledCount(data)
        res[self.v['MonsterSteal']]=self.buildItemsStolen(data) if self.collect_loot else ''
        if not colloeseum:
            res[self.v['UnitExperience']]=str(randint(200000,900000))
            res[self.v['P_EXP_SEASON_EVENT_ABILITY_ADD']]='0'
            res[self.v['P_GIL_SEASON_EVENT_ABILITY_ADD']]='0'
            res[self.v['ItemsDropped']]=self.buildT_ENCOUNT_INFO(data) if self.collect_loot else ''
            res[self.v['P_SEASON_EVENT_POINT']]='0'
            res[self.v['P_SEASON_EVENT_TOTAL_POINT']]='0'
            res[self.v['P_SEASON_EVENT_ABILITY_PARAM']]='0'
            res[self.v['P_SEASON_EVENT_LV_POINT']]='0'
            res[self.v['P_SEASON_EVENT_LV_PARAM']]='0'
            res[self.v['T_USER_CHALLENGE_INFO']]=[]
            res[self.v['T_USER_CHALLENGE_INFO']]=[ {self.v['MissionId']: "1110101",self.v['MissionIdChallenges']: "",self.v['P_CHALLENGE_TMP_CLEAR_INFO']: ""}]
            #TODO
            res[self.v['LBExperience']]=self.buildLBExperience(data) if self.lb >0 else ''
            res[self.v['P_RECIPE_BOOK_TREASURE']]=self.buildP_RECIPE_BOOK_TREASURE(data) if self.open_chest else ''
            res[self.v['EquipmentTreasure']]=self.buildEquipmentTreasure(data) if self.open_chest else ''
            res[self.v['ItemsTreasure']]=self.buildItemsTreasure(data) if self.open_chest else ''
            res[self.v['ItemsFound']]=self.buildItemsFound(data) if self.collect_exploration_loot else ''
            res[self.v['UnitsDropped']]=self.buildT_SCENARIO_BATTLE_INFO(data) if self.collect_unit else ''
            res[self.v['MonsterParts']]=self.buildMonsterParts(data)
            res[self.v['EncounterId']]=self.buildEncounterId(data)
        return [res]



    def buildT_USER_ARCHIVE_INFO(self,data,id,colloeseum=False):
        res=[]
        dmg=self.getMaxDMG(data)
        dmg = int(dmg * random.uniform(1, 2)) #* 10000000
        if colloeseum:
            res.append({self.v['ArchiveName']:'CLSM_TOTAL_DAMAGE',self.v['ArchiveValue']:str(dmg)})
            res.append({self.v['ArchiveName']:'CLSM_MAX_DAMAGE_TURN',self.v['ArchiveValue']:str(dmg)})
        else:
            res.append({self.v['ArchiveName']:'MAX_DAMAGE_TURN',self.v['ArchiveValue']:str(dmg)})
            res.append({self.v['ArchiveName']:'TOTAL_DAMAGE',self.v['ArchiveValue']:str(dmg)})
            res.append({self.v['ArchiveName']:'MAX_DAMAGE_HIT',self.v['ArchiveValue']:self.rndI(1000,100000)})
            res.append({self.v['ArchiveName']:'MAX_SPARK_CHAIN_TURN',self.v['ArchiveValue']:self.rndI(1,100)})
            res.append({self.v['ArchiveName']:'TOTAL_CRITICAL',self.v['ArchiveValue']:self.rndI(1,100)})
            res.append({self.v['ArchiveName']:'MAX_CRITICAL_TURN',self.v['ArchiveValue']:self.rndI(1,100)})
            res.append({self.v['ArchiveName']:'TOTAL_MAGIC_USE',self.v['ArchiveValue']:self.rndI(1,100)})
            res.append({self.v['ArchiveName']:'TOTAL_ABILITY_USE',self.v['ArchiveValue']:self.rndI(1,100)})
            res.append({self.v['ArchiveName']:'TOTAL_LB_CRISTAL',self.v['ArchiveValue']:self.rndI(1,100)})
            res.append({self.v['ArchiveName']:'MAX_ELEMENT_CHAIN_TURN',self.v['ArchiveValue']:self.rndI(50,100)})
            res.append({self.v['ArchiveName']:'MAX_CHAIN_TURN',self.v['ArchiveValue']:self.rndI(1,100)})
            res.append({self.v['ArchiveName']:'MAX_LB_CRISTAL',self.v['ArchiveValue']:self.rndI(1,100)})
            res.append({self.v['ArchiveName']:'TOTAL_BEAST_USE',self.v['ArchiveValue']:self.rndI(1,100)})
            if self.mission_rounds>=1:
                res.append({self.v['ArchiveName']:'TOTAL_MISSION_BATTLE_WIN',self.v['ArchiveValue']:str(self.mission_rounds)})
            else:
                res.append({self.v['ArchiveName']:'TOTAL_STEPS',self.v['ArchiveValue']:str(randint(1000,10000))})
        return res



    def buildEncounteredMonsters(self,data):
        res=[]
        if self.v['T_MONSTER_MST'] in data:
            for i in data[self.v['T_MONSTER_MST']]:
                res.append(i[self.v['MonsterId']])
        return ','.join(sorted(res))



    def buildMonstersKilledCount(self,data):
        res=[]
        rit={}
        if self.v['T_WAVE_BATTLE_INFO'] in data:
            for i in data[self.v['T_WAVE_BATTLE_INFO']]:
                j=i[self.v['MonsterPartId']]
                if j in rit:
                    rit[j]['count']+=1
                else:
                    rit[j]={}
                    rit[j]['count']=1
        if self.v['T_MONSTER_MST'] in data:
            for i in data[self.v['T_MONSTER_MST']]:
                j=i[self.v['MonsterPartId']]
                if j in rit:
                    rit[j]['count']+=1
                else:
                    rit[j]={}
                    rit[j]['count']=1
        if self.v['T_ENCOUNT_INFO'] in data: # a voir car 6v0LPiRe1 à la base au lieu de 6v0LPiRe
            for i in data[self.v['T_ENCOUNT_INFO']]:
                j=i[self.v['MonsterPartId']]
                if j in rit:
                    rit[j]['count']+=1
                else:
                    rit[j]={}
                    rit[j]['count']=1
        for e in rit:
            res.append('%s:%s'%(e,rit[e]['count']))
        return ','.join(sorted(res))



    def buildItemsStolen(self,data):
        if self.v['T_MONSTER_PARTS_MST'] not in data:
            return ''
        T_MONSTER_PARTS_MST=data[self.v['T_MONSTER_PARTS_MST']]
        T_BATTLE_GROUP_MST=data[self.v['T_BATTLE_GROUP_MST']]
        res=[]
        rit={}
        unt={}
        for i in T_BATTLE_GROUP_MST:
            j=i[self.v['MonsterPartId']]
            if j in unt:
                unt[j]['count']+=1
            else:
                unt[j]={}
                unt[j]['count']=1
        for i in T_MONSTER_PARTS_MST:
            mlt=unt[i[self.v['MonsterPartId']]]['count']
            if self.v['MonsterDrops'] in i and i[self.v['MonsterDrops']]:
                j=i[self.v['MonsterDrops']].split(',')
                for u in j:
                    z=u.split(':')
                    o='%s:%s'%(z[0],z[1])
                    if o in rit:
                        rit[o]['count']+=int(z[2])*mlt
                    else:
                        rit[o]={}
                        rit[o]['count']=int(z[2])*mlt
            if self.v['MonsterSteal'] in i and i[self.v['MonsterSteal']]:
                j=i[self.v['MonsterSteal']].split(',')
                for u in j:
                    z=u.split(':')
                    o='%s:%s'%(z[0],z[1])
                    if o in rit:
                        rit[o]['count']+=int(z[2])*mlt
                    else:
                        rit[o]={}
                        rit[o]['count']=int(z[2])*mlt
        for e in rit:
            res.append('%s:%s'%(e,rit[e]['count']))
        if len(res)==0:
            return ''
        return ','.join(sorted(res,key = lambda x: x.split(':')[1]))


    def buildT_ENCOUNT_INFO(self,data):
        #with open('buildT_ENCOUNT_INFO.json', 'w') as file:
        #    file.write(str(json.loads(json.dumps(data))))
        t={}
        p=[]
        if self.v['T_WAVE_BATTLE_INFO'] in data:
            T_WAVE_BATTLE_INFO=data[self.v['T_WAVE_BATTLE_INFO']]
            for i in T_WAVE_BATTLE_INFO:
                if self.v['MonsterDrops'] in i and i[self.v['MonsterDrops']]:
                    j=i[self.v['MonsterDrops']].split(':')
                    o='%s:%s'%(j[0],j[1])
                    if o in t:
                        t[o]['count']+=int(j[2])
                    else:
                        t[o]={}
                        t[o]['count']=int(j[2])
                if self.v['MonsterSpecialDrops'] in i and i[self.v['MonsterSpecialDrops']]:
                    j=i[self.v['MonsterSpecialDrops']].split(':')
                    o='%s:%s'%(j[0],j[1])
                    if o in t:
                        t[o]['count']+=int(j[2])
                    else:
                        t[o]={}
                        t[o]['count']=int(j[2])
        if self.v['T_ENCOUNT_INFO'] in data:
            T_ENCOUNT_INFO=data[self.v['T_ENCOUNT_INFO']]
            for i in T_ENCOUNT_INFO:
                if self.v['MonsterDrops'] in i and i[self.v['MonsterDrops']]:
                    j=i[self.v['MonsterDrops']].split(':')
                    o='%s:%s'%(j[0],j[1])
                    if o in t:
                        t[o]['count']+=int(j[2])
                    else:
                        t[o]={}
                        t[o]['count']=int(j[2])
                if self.v['MonsterSpecialDrops'] in i and i[self.v['MonsterSpecialDrops']]:
                    j=i[self.v['MonsterSpecialDrops']].split(':')
                    o='%s:%s'%(j[0],j[1])
                    if o in t:
                        t[o]['count']+=int(j[2])
                    else:
                        t[o]={}
                        t[o]['count']=int(j[2])
        if self.v['T_SCENARIO_BATTLE_INFO'] in data:
            T_SCENARIO_BATTLE_INFO=data[self.v['T_SCENARIO_BATTLE_INFO']]
            for i in T_SCENARIO_BATTLE_INFO:
                if self.v['MonsterDrops'] in i and i[self.v['MonsterDrops']]:
                    j=i[self.v['MonsterDrops']].split(':')
                    o='%s:%s'%(j[0],j[1])
                    if o in t:
                        t[o]['count']+=int(j[2])
                    else:
                        t[o]={}
                        t[o]['count']=int(j[2])
                if self.v['MonsterSpecialDrops'] in i and i[self.v['MonsterSpecialDrops']]:
                    j=i[self.v['MonsterSpecialDrops']].split(':')
                    o='%s:%s'%(j[0],j[1])
                    if o in t:
                        t[o]['count']+=int(j[2])
                    else:
                        t[o]={}
                        t[o]['count']=int(j[2])
        for e in t:
            if e:
                e_=e.split(':')
                p.append('%s:%s:%s'%(e_[0],e_[1],t[e]['count']))
        if len(p)==0:
            return ''
        return ','.join(p)


    def buildLBExperience(self,data):
        tmp=[]
        for u in self.s['units']:
            tmp.append('%s:%s'%(u,self.lb))
        return ','.join(tmp)



    def buildP_RECIPE_BOOK_TREASURE(self,data):
        p=[]
        c=[]
        if self.v['T_FIELD_TREASURE_MST'] in data:
            T_FIELD_TREASURE_MST=data[self.v['T_FIELD_TREASURE_MST']]
            for r in T_FIELD_TREASURE_MST:
                if self.v['FieldTreasureItem'] in r and self.v['GrantedSwitchId'] in r and r[self.v['GrantedSwitchId']] and r[self.v['FieldTreasureItem']]:# and (int(r[self.v['GrantedSwitchId']])<=50000000):
                    w=r[self.v['FieldTreasureItem']].split(':')
                    if int(w[0]) == 60:
                        o='%s:%s:%s:%s'%(w[0],w[1],w[2],r[self.v['GrantedSwitchId']])
                        c.append(r[self.v['GrantedSwitchId']])
                        p.append(o)
        if len(p)==0:
            return ''
        self.mergeChests(c)
        return ','.join(p)



    def buildEquipmentTreasure(self,data):
        p=[]
        c=[]
        if self.v['T_FIELD_TREASURE_MST'] in data:
            T_FIELD_TREASURE_MST=data[self.v['T_FIELD_TREASURE_MST']]
            for r in T_FIELD_TREASURE_MST:
                if self.v['FieldTreasureItem'] in r and self.v['GrantedSwitchId'] in r and r[self.v['GrantedSwitchId']] and r[self.v['FieldTreasureItem']]:# and (int(r[self.v['GrantedSwitchId']])<=50000000):
                    w=r[self.v['FieldTreasureItem']].split(':')
                    if int(w[0]) == 21:
                        o='%s:%s:%s:%s'%(w[0],w[1],w[2],r[self.v['GrantedSwitchId']])
                        c.append(r[self.v['GrantedSwitchId']])
                        p.append(o)
        if len(p)==0:
            return ''
        self.mergeChests(c)
        return ','.join(p)



    def buildItemsTreasure(self,data):
        p=[]
        c=[]
        if self.v['T_FIELD_TREASURE_MST'] in data:
            T_FIELD_TREASURE_MST=data[self.v['T_FIELD_TREASURE_MST']]
            for r in T_FIELD_TREASURE_MST:
                if self.v['FieldTreasureItem'] in r and self.v['GrantedSwitchId'] in r and r[self.v['GrantedSwitchId']] and r[self.v['FieldTreasureItem']]:# and (int(r[self.v['GrantedSwitchId']])<=50000000):
                    w=r[self.v['FieldTreasureItem']].split(':')
                    if int(w[0]) == 20:
                        # o='%s:%s:%s:%s'%(w[0],'1300000005',w[2],r[self.v['GrantedSwitchId']]) # test injection ced
                        o='%s:%s:%s:%s'%(w[0],w[1],w[2],r[self.v['GrantedSwitchId']])
                        c.append(r[self.v['GrantedSwitchId']])
                        p.append(o)
        if len(p)==0:
            return ''
        self.mergeChests(c)
        return ','.join(p)


    def mergeChests(self,new):
        self.s['openedChests'].extend(new)



    def buildItemsFound(self,data):
        r=[]
        t={}
        if self.v['T_HARVEST_DETAIL_INFO'] in data:
            T_HARVEST_DETAIL_INFO=data[self.v['T_HARVEST_DETAIL_INFO']]
            for i in T_HARVEST_DETAIL_INFO:
                if self.v['HarvestItem'] in i and i[self.v['HarvestItem']]:
                    o=i[self.v['HarvestItem']].split(':')
                    z='%s:%s'%(o[0],o[1])
                    if z in t:
                        t[z]['count']+=int(o[2])
                    else:
                        t[z]={}
                        t[z]['count']=int(o[2])
            for i in t:
                r.append('%s:%s'%(i,t[i]['count']))
        return ','.join(r)



    def buildT_SCENARIO_BATTLE_INFO(self,data):
        r=[]
        if self.v['T_WAVE_BATTLE_INFO'] in data:
            T_WAVE_BATTLE_INFO=data[self.v['T_WAVE_BATTLE_INFO']]
            for i in T_WAVE_BATTLE_INFO:
                if self.v['MonsterUnitDrops'] in i and i[self.v['MonsterUnitDrops']]:
                    r.append(str(i[self.v['MonsterUnitDrops']]))
        if self.v['T_SCENARIO_BATTLE_INFO'] in data:
            T_SCENARIO_BATTLE_INFO=data[self.v['T_SCENARIO_BATTLE_INFO']]
            for i in T_SCENARIO_BATTLE_INFO:
                if self.v['MonsterUnitDrops'] in i and i[self.v['MonsterUnitDrops']]:
                    r.append(str(i[self.v['MonsterUnitDrops']]))
        if self.v['T_MONSTER_PARTS_MST'] in data:
            T_MONSTER_PARTS_MST=data[self.v['T_MONSTER_PARTS_MST']]
            for i in T_MONSTER_PARTS_MST:
                if self.v['MonsterUnitDrops'] in i and i[self.v['MonsterUnitDrops']]:
                    r.append(str(i[self.v['MonsterUnitDrops']]))
        return ','.join(r)




    def buildMonsterParts(self,data):
        if self.v['T_MONSTER_MST'] not in data:
            return ''
        res=[]
        for i in data[self.v['T_MONSTER_MST']]:
            res.append('%s:1'%(i[self.v['MonsterPartId']]))
        return ','.join(sorted(res))




    def buildEncounterId(self,data):
        res=[]
        if self.v['T_ENCOUNT_INFO'] in data:
            for i in data[self.v['T_ENCOUNT_INFO']]:
                res.append('10:%s:%s'%(i[self.v['MissionWaveId']],i[self.v['P_ENCOUNT_NUM']]))
        if self.v['T_SCENARIO_BATTLE_GROUP_MST'] in data:
            for i in data[self.v['T_SCENARIO_BATTLE_GROUP_MST']]:
                res.append('0:%s:%s'%(i[self.v['MissionWaveId']],i[self.v['P_BEFORE_EFFECT_TYPE']]))
        if len(res)==0:
            return ''
        return ','.join(sorted(res))



    def checkReward(self,_data,_json,id):
        if _data:
            #with open('avant.json', 'w') as file:
            #    file.write(json.loads(json.dumps(_data)))
            reward_string=''
            if self.v['MissionResults'] in _data:
                _reward_table=_json[self.v['MissionResults']][0]
                possible=[
                    self.v['ItemsDropped'],self.v['ItemsUniqueDropped'],self.v['ItemsStolen'],self.v['ItemsUniqueStolen'],
                    self.v['ItemsTreasure'],self.v['ItemsFound'],self.v['P_ITEM_AFFINITY'],self.v['ItemsTrusted'],self.v['EquipmentDropped'],
                    self.v['EquipmentUniqueDropped'],self.v['EquipmentStolen'],self.v['EquipmentUniqueStolen'],self.v['EquipmentTreasure'],
                    self.v['EquipmentFound'],self.v['P_EQP_ITEM_AFFINITY'],self.v['EquipmentTrusted'],self.v['P_MATERIA_DROP'],self.v['P_MATERIA_UNIQUE_DROP'],
                    self.v['P_MATERIA_STEAL'],self.v['P_MATERIA_UNIQUE_STEAL'],self.v['P_MATERIA_TREASURE'],self.v['P_MATERIA_FIND'],self.v['P_MATERIA_AFFINITY']
                    ,self.v['MateriaTrusted'],self.v['P_IMPORTANT_ITEM_DROP'],self.v['P_IMPORTANT_ITEM_UNIQUE_DROP'],self.v['P_IMPORTANT_ITEM_STEAL'],
                    self.v['P_IMPORTANT_ITEM_UNIQUE_STEAL'],self.v['P_IMPORTANT_ITEM_TREASURE'],self.v['P_IMPORTANT_ITEM_FIND'],
                    self.v['P_IMPORTANT_ITEM_AFFINITY'],self.v['P_IMPORTANT_ITEM_REWARD'],self.v['P_RECIPE_BOOK_TREASURE'],self.v['UnitsDropped'],
                    self.v['P_ITEM_SEASON_EVENT_ABILITY']
                    ]
                for i in possible:
                    if i in _data and len(_reward_table[i])>=1:
                        reward_string=reward_string+','+ self.t.getRewardString(_reward_table[i])
                if len(reward_string)>=1:
                    if reward_string[0] == ',':
                        reward_string=reward_string[1:]
                # self.addLoot()
                reward_string='[+] mission %s completed\n[+] unit exp %s\n[+] rank exp %s, level %s\n[+] reward %s\n[+] energy left %s/%s\n[+] gil %s\n[+] Lapis %s\n[+] Orbs arena %s/%s\n[+] Orbs raid %s/%s'%(
                    self.t.findMissionName(id,self.lang),
                    _reward_table[self.v['UnitExperience']],
                    (str(self.s['user'][self.v['UserExperience']]) + '/' + str(self.t.getLevelExp(int(self.s['user'][self.v['UserLevel']])))) if int(self.s['user'][self.v['UserLevel']]) < 300 else 'Max Level',
                    self.s['user'][self.v['UserLevel']],
                    reward_string,
                    self.s['user'][self.v['Energy']],
                    _json[self.v['T_USER_TEAM_INFO']][0][self.v['EnergyMax']],
                    _json[self.v['T_USER_TEAM_INFO']][0][self.v['Gil']],
                    str(int(_json[self.v['UserLapisInfo']][0][self.v['LapisPaid']]) + int(_json[self.v['UserLapisInfo']][0][self.v['Lapis']])),
                    str(int(_json[self.v['T_USER_TEAM_INFO']][0][self.v['ArenaOrb']])),
                    str(int(_json[self.v['T_USER_TEAM_INFO']][0][self.v['ArenaOrbMax']])),
                    str(int(_json[self.v['T_USER_TEAM_INFO']][0][self.v['RaidOrb']])),
                    str(int(_json[self.v['T_USER_TEAM_INFO']][0][self.v['RaidOrbMax']]))
                    )
            return reward_string


    def checkTMR(self,data):
        changes=[]
        if self.v['T_USER_UNIT_INFO_UPD'] in data:
            T_USER_UNIT_INFO_UPD=json.loads(data)[self.v['T_USER_UNIT_INFO_UPD']]
            for unit in T_USER_UNIT_INFO_UPD:
                UniqueUnitId=unit[self.v['UniqueUnitId']]
                LastAccessBase=unit[self.v['UnitId']]#char id for name TODO a voir ID Unique ou last access base
                UnitTmr=unit[self.v['UnitTmr']]#tmr
                if UniqueUnitId in self.s['units']:
                    if UnitTmr != self.s['units'][UniqueUnitId]['tmr']:
                        changes.append('%s %s'%(self.getUnitName(LastAccessBase),self.convertTMRPercent(UnitTmr)))
                        # if 'win' not in sys.platform:
                        #     self.addTMR(UniqueUnitId,UnitTmr,self.t.findUnitName(LastAccessBase)[0])
                        self.s['units'][UniqueUnitId]['tmr']=UnitTmr
        if len(changes)>=1:
            return '\n[+] tmr changes %s'%(', '.join(changes))
        else:
            return ''

    def getUnitName(self,id):
        try:
            return self.t.getUnitName(id,self.lang)[0]
        except:
            return 'inconnu au bataillon'

    def convertTMRPercent(self,UnitTmr):
        return ('%s%%'%round(float(UnitTmr)/1000 * 100,1))

    def checkIfUnitFullTMR(self):
        self.dolog('%s() was called'%(self.whoami()))
        for party in self.s['user']['teams']:
          if str(party[self.v['PartyId']]) == str(self.s['user']['current_party']):
            units=party[self.v['PartyUnits']].split(',')
            for unit in units:
              uniqueUnitId=unit.split(':')[2]
              if self.s['units'][uniqueUnitId]['tmr'] == str(1000):
                new_unit=self.findUnitToMaxTMR(uniqueUnitId)
                self.PartyDeckEditRequest(
                self.s['user']['current_party']
                ,unit_to_be_replace=str(uniqueUnitId)
                ,unit_to_include=new_unit
                )

    def findUnitToMaxTMR(self,uniqueUnitId):
        self.dolog('%s() was called'%(self.whoami()))
        for unit in self.s['units']:
          uniqueUnitId=str(unit)
          if not str(self.s['units'][uniqueUnitId]['original_id']).startswith("9") and self.s['units'][uniqueUnitId]['tmr'] != str(1000) and str(uniqueUnitId) not in self.unit_already_TMRed:
              #if int(self.t.getUnitCost(self.s['units'][uniqueUnitId]['original_id'])) >0 or (int(self.t.getUnitCost(self.s['units'][uniqueUnitId]['original_id'])) ==0 and 'Neo Vision'.lower() in str(self.getUnitName(self.s['units'][uniqueUnitId]['original_id'])).lower()): #on verifie que l'id de l'unite en rarete minimal n'a pas un cout de 0. sinon unite original du jeu
              if isinstance(self.t.getUnitCost(self.s['units'][uniqueUnitId]['original_id']), int):
                  if int(self.t.getUnitCost(self.s['units'][uniqueUnitId]['original_id'])) >0 and int(self.t.getUnitMinRarety(self.s['units'][uniqueUnitId]['original_id'])) < 7:
                      self.unit_already_TMRed.append(str(uniqueUnitId))
                      return uniqueUnitId
         #si on ne trouve plus d'unité, on annule l'option de changement de unitFullTMR
        self.changeUnitWithFullTMR=False
        self.dolog(self.whoami()+" changeUnitWithFullTMR sur False car plus besoin de chercher")
        return None


    def rndI(self,min,max):
        return str(random.randint(min,max))


    def getMaxDMG(self,data):
        total=0
        if self.v['T_MONSTER_PARTS_MST'] in data:
            T_MONSTER_PARTS_MST=data[self.v['T_MONSTER_PARTS_MST']]
            for unt in T_MONSTER_PARTS_MST:
                if self.v['MonsterHp'] in unt:
                    MonsterHp=unt[self.v['MonsterHp']]
                    total+=int(MonsterHp)
        if self.multiplier_dmg == 0:
            return total
        else:
            return int(total * self.multiplier_dmg)


    def parseFav(self,data):
        if self.v['T_USER_UNIT_FAVORITE_MARGE'] in data and len(json.loads(data)[self.v['T_USER_UNIT_FAVORITE_MARGE']])>=1:
            try:
                self.s['user']['fav']={}
                self.s['user']['fav']=json.loads(data)[self.v['T_USER_UNIT_FAVORITE_MARGE']][0][self.v['UniqueUnitId']]
            except:
                pass


    def addAccountInfo(self,plain_res):
        pass

    def parseMyTeams(self,data):
        self.s['user']['teams']=[]
        # self.s['user']['teams'][self.v['UserPartyDeckInfo']]=[]
        for unit in json.loads(data)[self.v['UserPartyDeckInfo']]:
            temp={}
            temp.update({self.v['UserIdGumi']:str(self.s['user'][self.v['UserIdGumi']])})
            temp.update(unit)
            self.s['user']['teams'].append(temp)
        # self.s['user']['teams']=json.loads(data)[self.v['UserPartyDeckInfo']]

        if self.v['T_USER_BEAST_DECK_INFO'] in data:
            self.s['user']['beasts']=[]
            # self.s['user']['beasts'][self.v['T_USER_BEAST_DECK_INFO']]=[]
            for esper in json.loads(data)[self.v['T_USER_BEAST_DECK_INFO']]:
                temp={}
                temp.update({self.v['UserIdGumi']:str(self.s['user'][self.v['UserIdGumi']])})
                temp.update(esper)
                self.s['user']['beasts'].append(temp)

    def parseMyTeamSetup(self,data):
        self.s['user']['team']={}
        self.s['user']['team']=json.loads(data)[self.v['T_USER_ACTUAL_INFO']][0]
        self.s['user']['current_party']=self.s['user']['team'][self.v['PartyId']]


    def parseMyEquiment(self,data):
        self.s['user']['equipement']={}
        self.s['user']['equipement']=json.loads(data)[self.v['T_USER_UNIT_EQUIP_INFO']][0]

    def parseMyUnits(self,data):
        _units={}
        user_unit_info=json.loads(data)[self.v['T_USER_UNIT_INFO']]
        # with open('avant.json', 'w') as file:
        #   file.write(json.dumps(user_unit_info))
        for unit in user_unit_info:
            if self.v['UnitTmr'] in unit:
              units_tmr=unit[self.v['UnitTmr']]
              units_unique_id=unit[self.v['UniqueUnitId']]
              units_id=unit[self.v['UnitId']]
              units_original_id=unit[self.v['LastAccessBase']]
              lvl=unit[self.v['UserLevel']]
              if int(units_id)>=900000000:
                  pass
              if units_unique_id in _units:
                  pass
              else:
                  _units[units_unique_id]={}
                  _units[units_unique_id]['tmr']=units_tmr
                  _units[units_unique_id]['id']=units_id
                  _units[units_unique_id]['lvl']=lvl
                  _units[units_unique_id]['original_id']=units_original_id
        self.s['units']=_units


    def RmRetireRequest(self,MissionId):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['Mission']]=[]
        data[self.v['Mission']].append({self.v['FriendPoints']:'0',self.v['P_RANDOM_SEED']:'0',self.v['P_RESTART_TYPE']:'0',self.v['MissionId']:str(MissionId)})
        data.update(self.createBody())
        return self.callApi(data,'RmRetire')




    def parseUnlocked(self,data):
        try:
            if self.v['sgUserMissionLock'] in data and len(json.loads(data)[self.v['sgUserMissionLock']])>=1:
                self.dolog('%s() missions was called'%(self.whoami()))
                self.s['user']['unlocked']={}
                self.s['user']['unlocked']=json.loads(data)[self.v['sgUserMissionLock']]
            if self.v['T_USER_SP_DUNGEON_INFO'] in data and len(json.loads(data)[self.v['T_USER_SP_DUNGEON_INFO']])>=1:
                self.dolog('%s() dungeons was called'%(self.whoami()))
                self.s['user']['dungeon_unlocked']={}
                self.s['user']['dungeon_unlocked']=json.loads(data)[self.v['T_USER_SP_DUNGEON_INFO']]
        except:
            pass



    def completeTutorial(self,force=False):
        pass


    def clear_range_of_missions(self,first_mission_id,nb_of_missions=5,party=1, gap_between_2_missions=1):
        self.PartyDeckEditRequest(party)
        for m in range(0,int(nb_of_missions)):
            m=int(first_mission_id)+(int(gap_between_2_missions)*int(m))
            print(self.startMission(m)[1])

    def clear_repeated_mission(self, mission_id, how_many_times=5, party=0):
        self.PartyDeckEditRequest(party)
        for m in range(0,how_many_times):
            print(self.startMission(mission_id)[1])



    def callGetInfoUser3(self):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data.update(self.createBody())
        tmp=self.callApi(data,'GetUserInfo3')
        try:
            d=json.loads(tmp)[self.v['EquipGrowEventInfo']]
            id_weapon=str(d[0][self.v['EquipId']]).split(':')
            id_weapon=id_weapon[1]
        except:
            id_weapon=''
        if id_weapon:
            if not self.autoFixWeaponDungeon:
                exit('UN DONGEON D\'AMELIORATION D\'ARME EST EN COURS')
            else:
                self.fix_weapon_dungeon(id_weapon)
        #with open('info3.json', 'w') as file:
        #    file.write(json.loads(tmp))


    def relog(self):
        self.InitializeRequest()
        self.GetUserInfoRequest()
        self.callGetInfoUser3()


# -------------- ARENE ------------------- #

    def clearReEnterArena(self):
        if self.s['user']['party_arena'] == '':
            self.relog()
        self.dolog('%s() an ongoing arena has been found'%(self.whoami()))
        rb_entry = self.RbEntryRequest()
        self.RbMatching(rb_entry)
        rb_start = self.RbStart(rb_entry)
        self.RbEnd(self.s['user']['party_arena'][self.arena_party],self.s['user']['units'], rb_start, rb_entry)



    def RbReStart(self): #TODO
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['T_USER_RB_MATCHING_INFO']]=[]
        data[self.v['T_OPE_RANKING_BATTLE']]=[]
        data[self.v['T_USER_RB_MATCHING_INFO']].append({self.v['RbEnemyId']:self.arena_opponent})
        data[self.v['T_OPE_RANKING_BATTLE']].append(json.loads(RbEntry)[self.v['T_OPE_RANKING_BATTLE']][0])
        data.update(self.createBody())
        return self.callApi(data,'RbStart')



    def clearArena(self):
        try:
            if self.s['user']['party_arena'] == '':
                self.relog()
            orbs = self.s['user']['arena_orbs']
            while (orbs > 0):
                self.dolog('Enter in arena - %s fight(s) left'%(orbs))
                rb_entry = self.RbEntryRequest()
                while True:
                    if self.RbMatching(rb_entry):
                        break
                rb_start = self.RbStart(rb_entry)
                self.RbEnd(self.s['user']['party_arena'][self.arena_party],self.s['user']['units'], rb_start, rb_entry)
                orbs=orbs-1
        except:
            return [0,'erreur arena']


    def RbEntryRequest(self):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data.update(self.createBody())
        return self.callApi(data,'RbEntry')



    def RbMatching(self, RbEntry):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['T_USER_RB_MATCHING_INFO']]=[]
        data[self.v['T_OPE_RANKING_BATTLE']]=[]
        opponent = json.loads(RbEntry)[self.v['T_RB_MATCHING_LIST_INFO']][0][self.v['ArenaOpponents']]
        self.arena_opponent = str(opponent.split(':')[0])
        try:
            self.arena_opponent_name = str(opponent.split(':')[1]) #TODO A voir
        except:
            self.arena_opponent_name=''
        self.arena_opponent_ratio = str(int(opponent.split(':')[7])/ 100)
        data[self.v['T_USER_RB_MATCHING_INFO']].append({self.v['RbEnemyId']:self.arena_opponent})
        data[self.v['T_OPE_RANKING_BATTLE']].append(json.loads(RbEntry)[self.v['T_OPE_RANKING_BATTLE']][0])
        data.update(self.createBody())
        return self.callApi(data,'RbMatching')



    def RbStart(self, RbEntry):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['T_USER_RB_MATCHING_INFO']]=[]
        data[self.v['T_OPE_RANKING_BATTLE']]=[]
        data[self.v['T_USER_RB_MATCHING_INFO']].append({self.v['RbEnemyId']:self.arena_opponent})
        data[self.v['T_OPE_RANKING_BATTLE']].append(json.loads(RbEntry)[self.v['T_OPE_RANKING_BATTLE']][0])
        data.update(self.createBody())
        return self.callApi(data,'RbStart')



    def RbEnd(self, userPartyDeckInfo, PartyList, RbStart, RbEntry):
        self.dolog('%s() was called'%(self.whoami()))
        partyUnitsBrut = userPartyDeckInfo[self.v['PartyUnits']].split(',')
        totalDmg = 0
        ArenaPlayerDmg = []
        ArenaEnemyDmg = []
        # our team
        for partyUnits in partyUnitsBrut:
            unitUniqueId = partyUnits.split(':')[2]
            unitId = ''
            unitPVArray = []
            dmg = random.randint(9000, 14000)
        for unit in PartyList:
            if unit[self.v['UniqueUnitId']] == unitUniqueId:
                unitId=unit[self.v['UnitId']]
                unitPVArray=unit[self.v['UnitHp']].split('-')
                unitPY=(int(unitPVArray[0]) + int(unitPVArray[1]) * 3)
                break
        ArenaPlayerDmg.append(str(unitId) + ":" + str(unitUniqueId) + ":" + str(unitPY) + ":0")
        totalDmg = totalDmg + round(dmg * 1.3,0)
        myTeamResult = ','.join(ArenaPlayerDmg)

        # enemy  team
        enemyUnits = str(json.loads(RbStart)[self.v['T_USER_RB_VS_INFO']][0][self.v['RbEnemyUnitList']]).split(';')
        for enemyUnit in enemyUnits:
            infoEnemyUnit = enemyUnit.split(':')
            ArenaEnemyDmg.append(str(infoEnemyUnit[1]) + ":" + str(infoEnemyUnit[0]) + ":0:1")
            enemyTeamResult = ','.join(ArenaEnemyDmg)

        #generation of the request send
        data={}
        data[self.v['T_OPE_RANKING_BATTLE']]=[]
        data[self.v['T_OPE_RANKING_BATTLE']].append(json.loads(RbEntry)[self.v['T_OPE_RANKING_BATTLE']][0])

        data[self.v['T_RB_RESULT']]=[]
        data[self.v['T_RB_RESULT']].append({
            self.v['ArenaPlayerDmg'] : myTeamResult,
            self.v['ArenaEnemyDmg']: enemyTeamResult,
            self.v['ArenaPlayerTotalDmg']:str(totalDmg),
            self.v['ArenaEnemyTotalDmg']:"0",
            self.v['ArenaResult']: "1",
            self.v['ArenaTurns']: "0", #TODO voir si nb tours > 0 ?
            self.v['ArenaVsFriend']: "0"
            })

        max_lb_cristal=str(random.randint(50,100))
        data[self.v['T_USER_ARCHIVE_INFO']]=[]
        data[self.v['T_USER_ARCHIVE_INFO']].append({self.v['ArchiveName']: "ARENA_TOTAL_ABILITY_USE",self.v['ArchiveValue']: "6"})
        data[self.v['T_USER_ARCHIVE_INFO']].append({self.v['ArchiveName']: "ARENA_MAX_DAMAGE_HIT",self.v['ArchiveValue']: str(random.randint(3000,5000))})
        data[self.v['T_USER_ARCHIVE_INFO']].append({self.v['ArchiveName']: "ARENA_TOTAL_LB_CRISTAL",self.v['ArchiveValue']: max_lb_cristal})
        data[self.v['T_USER_ARCHIVE_INFO']].append({self.v['ArchiveName']: "ARENA_TOTAL_DAMAGE",self.v['ArchiveValue']: str(totalDmg)})
        data[self.v['T_USER_ARCHIVE_INFO']].append({self.v['ArchiveName']: "ARENA_MAX_ELEMENT_CHAIN_TURN",self.v['ArchiveValue']: "0"})
        data[self.v['T_USER_ARCHIVE_INFO']].append({self.v['ArchiveName']: "ARENA_MAX_SPARK_CHAIN_TURN",self.v['ArchiveValue']: str(random.randint(20,50))})
        data[self.v['T_USER_ARCHIVE_INFO']].append({self.v['ArchiveName']: "ARENA_MAX_CHAIN_TURN",self.v['ArchiveValue']: str(random.randint(20,80))})
        data[self.v['T_USER_ARCHIVE_INFO']].append({self.v['ArchiveName']: "ARENA_MAX_LB_CRISTAL",self.v['ArchiveValue']:max_lb_cristal})
        data[self.v['T_USER_ARCHIVE_INFO']].append({self.v['ArchiveName']: "ARENA_MAX_DAMAGE_TURN",self.v['ArchiveValue']:str(totalDmg)})
        data.update(self.createBody())
        time.sleep(self.SLEEPING_TIME_ARENA)
        self.dolog('[+] Arena clear against ID : %s - %s - ratio : %s'%(self.arena_opponent, self.arena_opponent_name, self.arena_opponent_ratio))
        #TODO avoir la validation de victoire apres la requete
        return self.callApi(data,'RbEnd')


# -------------- FIN ARENE ------------------- #

# -------------- PULL ------------------- #


    def pullInit(self):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data.update(self.createBody())
        response=self.callApi(data,'GachaEntry')

        gacha_list={}
        gacha_schedule=response[self.v['GachaSchedule']]
        for banner in gacha_schedule:
            gacha_list[banner[self.v['GachaId']]]={}
            gacha_list[banner[self.v['GachaId']]].update({
                "options":banner[self.v['Options']],
                "description":banner[self.v['Description']],
                "start": banner[self.v['DateStart']],
                "end": banner[self.v['DateEnd']],
            })

        gacha_details=response[self.v['GachaDetails']]
        for banner in gacha_details:
            if banner[self.v['GachaId']] in gacha_list:
                gacha_list[banner[self.v['GachaId']]].update({
                    "options":banner[self.v['Options']],
                    "description":banner[self.v['Description']],
                    "start": banner[self.v['DateStart']],
                    "end": banner[self.v['DateEnd']],
                })
        #TODO a terminer


    def pullRequest(self,GachaId,GachaSubId,nbPull,cost):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['GachaExe']]=[]
        data[self.v['GachaExe']].append({
            self.v['GachaId']:GachaId,
            self.v['GachaSubId']:GachaSubId,
            self.v['GachaRepeat']:nbPull,
            self.v['GachaCost_zJ1A6HXm']:cost
        })
        data.update(self.createBody())
        response = self.callApi(data,'GachaExe')
        if response:
            _response=json.loads(response)
            if self.v['GachaUnitList'] in response:
                self.dolog('Pull done')
                raw_pulled=_response[self.v['GachaExe']][0][self.v['GachaUnitList']]
                array_pulled=raw_pulled.split(',')
                self.getPulledRewards(array_pulled)
        #TODO proposer de vendre les jetons en trop


    def getPulledRewards(self,raw_rewards):
        json_rewards={}
        string_rewards=''
        for item in raw_rewards:
            item_id=item.split(':')[1]
            if item_id not in json_rewards:
                json_rewards[item_id]=1
            else:
                json_rewards[item_id]=json_rewards[item_id]+1
        for id_item, number in json_rewards.items():
            string_rewards=string_rewards+ '\n' + '- ' + self.t.findItemName(id_item,self.lang) + ' : ' + str(number)
        self.dolog(string_rewards)


# -------------- END PULL ------------------- #

# -------------- RAID ------------------- #
    def clearRaid(self, party, IdMission):
        try:
          changeTMRInitialBool=False
          orbs = self.s['user']['raid_orbs']
          self.dolog('%s() was called and you got %s orb(s)'%(self.whoami(), orbs))
          if orbs < 1:
              return
          while (orbs > 0):
            self.dolog('Enter in raid mode - %s fight(s) left'%(orbs))
            self.PartyDeckEditRequest(party)

            farm_disable_solve=False
            farm_disable_collect_loot=False
            farm_disable_collect_unit=False

            if self.raidDmgMultiplier:
                self.multiplier_dmg=self.raid_multiplier_dmg

            if self.changeUnitWithFullTMR:
              changeTMRInitialBool=True
              self.changeUnitWithFullTMR=False

            if not self.solve_mission:
                self.setSolveMissions()
                farm_disable_solve=True
            if not self.collect_loot:
                self.setCollectLoot()
                farm_disable_collect_loot=True
            if not self.collect_unit:
                self.setCollectUnits()
                farm_disable_collect_unit=True
            self.setLb(100000)

            print(self.startMission(int(IdMission))[1])

            self.PartyDeckEditRequest(2)
            # if self.s['user']['current_party']:
            #     self.PartyDeckEditRequest(self.s['user']['current_party'])

            if farm_disable_solve:
                self.solve_mission=False
            if farm_disable_collect_loot:
                self.collect_loot=False
            if farm_disable_collect_unit:
                self.collect_unit=False
            if self.raidDmgMultiplier:
                self.multiplier_dmg=0
            self.setLb(100000)
            orbs=orbs-1
            if changeTMRInitialBool:
              self.changeUnitWithFullTMR=True

        except:
            return [0,'erreur raid']

# -------------- FIN RAID ------------------- #

# -------------- GIFT MANAGEMENT ------------------- #

    def giftAcceptAll(self):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data[self.v['MailReceipt']]=[]
        data[self.v['MailReceipt']].append({self.v['P_OPE_TYPE']:'2'})
        data.update(self.createBody())
        return self.callApi(data,'MailReceipt')

# -------------- END GIFT MANAGEMENT ------------------- #


    def dolog(self,s):
        try:
            print('%s%s %s'%('[%s]'%self.s['user'][self.v['UserId']] if self.v['UserId'] in self.s['user'] else '',s,time.strftime('%H:%M:%S')))
        except:
            pass

    def getLastError(self):
        return self.lastError

    def whoami(self):
        try:
            return inspect.stack()[1][3]
        except:
            return ''


    def updateProxy(self,time):
        pass


    def FriendListRequest(self, list):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data.update(self.createBody())
        return self.callApi(data,'FriendList')


    def generate_json_current_event(self):
        self.dolog('%s() was called'%(self.whoami()))
        list_missions_id={}
        list_missions_id['events']={}
        list_event=self.routineEventUpdateRequest()
        temp=json.loads(list_event)[self.v['T_SP_DUNGEON_COND_MST']]
        for event in temp:
            if event[self.v['MapId']] == "2":
                list_missions_id['events'].update({
                    event[self.v['MissionId']]:event[self.v['Description']]
                })
        with open('list_events.json', 'w',encoding='utf8') as file:
            file.write(json.dumps(list_missions_id))
            self.dolog('Fichier avec liste des events en cours mis à jour')

    def get_list_id_raid_available(self):
        list_mission_id=[]
        list_event=self.routineEventUpdateRequest()
        temp=json.loads(list_event)[self.v['T_SP_DUNGEON_COND_MST']]
        for event in temp:
            if event['C8Qf5bs6'] == "1":
                list_mission_id.append(event[self.v['MissionId']])
        self.dolog('List of raid id mission : ' + str(' '.join(list_mission_id)))
        return list_mission_id


    def do_clear_raid_farm(self,party=1):
      self.dolog('%s() was called'%(self.whoami()))
      if self.raid_mission_id == '':
        list_mission_id=self.get_list_id_raid_available()
        if list_mission_id:
          self.raid_mission_id=int(max(list_mission_id))
      if self.raid_mission_id != '':
        self.setClearRaid(self.raid_mission_id,party)


    def do_clear_raid_all_once(self, party=1):
        self.dolog('%s() was called'%(self.whoami()))
        list_mission_id=self.get_list_id_raid_available()
        if list_mission_id:
          for mission_id in list_mission_id:
            self.clear_repeated_mission(mission_id,1,party)



    def get_id_quest_challenge_vortex(self):
        list_mission_id=[]
        list_event=self.routineEventUpdateRequest()
        #with open('deck.json', 'w') as file:
        #    file.write(json.loads(json.dumps(list_event)))
        temp=json.loads(list_event)[self.v['T_SP_DUNGEON_COND_MST']]
        for event in temp:
            if event[self.v['P_REWARD_GET_ID']] == "9013":
                list_mission_id.append(event[self.v['MissionId']])
        id=int(min(list_mission_id))
        self.dolog('Vortex challenge mission id find : ' + str(id))
        return id


    def SpChallengeEntry(self):
        self.dolog('%s() was called'%(self.whoami()))
        data={}
        data.update(self.createBody())
        return self.callApi(data,'SpChallengeEntry')

    def fix_weapon_dungeon(self, id_arme):
        # ID de l'arme est dispo dans le GetUserInfo3
        # => EquipGrowEventInfo => EquipId
        self.dolog('%s() was called'%(self.whoami()))
        self.dolog('Le donjon d\'amélioration d\'arme (' + str(id_arme) + ') va être automatiquement corrigé')
        data={}
        data.update(self.createBody())
        data['YEFfeo27']=[]
        data['YEFfeo27'].append({
                'J1YX9kmM': str('21:')+str(id_arme),
                '6tSP4s8J': "1",
                'a1bk2rmo': "2"
            })
        return self.callApi(data, 'EquipGrowAbilityFix')


    def clear_revisit_quest_world(self):
        id_challenge=0
        list_missions_id=[]
        list_missions_name=[]
        list_challenge=self.SpChallengeEntry()
        temp=json.loads(list_challenge)[self.v['T_SP_CHALLENGE_SCHEDULE_MST']]
        for event in temp:
            if "revisit" in str(event[self.v['Description']]).lower():
                id_challenge = int(event[self.v['GatheringStageId']])
        if id_challenge > 0:
            self.dolog('The ID of the revisit world quest is : ' + str(id_challenge))
            schedule_challange_json=self.t.get_schedule_challenge_content()
            for item in schedule_challange_json:
                if str(item).startswith(str(id_challenge)) and len(item) == 7:
                    list_missions_name.append(str(schedule_challange_json[item]['EN']).replace('Clear', '').strip())
            self.dolog('Checking after the missions ID')
            for mission_name in list_missions_name:
                mission_id=self.t.findMissionByName(mission_name)
                if mission_id:
                    list_missions_id.append(mission_id)
            self.dolog(str(len(list_missions_id)) + ' missions ID found')
            self.refill_potion=True
            farm_disable_solve=False
            farm_disable_collect_loot=False
            farm_disable_collect_unit=False

            if not self.solve_mission:
                self.setSolveMissions()
                farm_disable_solve=True
            if not self.collect_loot:
                self.setCollectLoot()
                farm_disable_collect_loot=True
            if not self.collect_unit:
                self.setCollectUnits()
                farm_disable_collect_unit=True
            self.setLb(100000)

            for mission_id in list_missions_id:
                print(self.startMission(int(mission_id))[1])

            self.refill_potion=False
            if farm_disable_solve:
                self.solve_mission=False
            if farm_disable_collect_loot:
                self.collect_loot=False
            if farm_disable_collect_unit:
                self.collect_unit=False
            self.setLb(0)
        else:
            self.dolog('No revisit world quest find')
