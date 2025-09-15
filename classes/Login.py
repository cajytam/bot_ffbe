import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class Login():

    def __init__(self):
        self.token=''


    def setFacebook(self, token):
        self.token=token
        fb=Facebook(self.token)
        # id_fb = fb.getUserFacebookId()
        id_fb = "102536153865281"
        print('ID FACEBOOK : ',id_fb)
        return id_fb


class Facebook(Login):
    def __init__(self, token):
        self.token=token
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.r=requests.session()
        self.r.headers.update({'user-agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'})
        self.r.verify=False
        self.getUserFacebookId()

    def getUserFacebookId(self):
        rqt = 'https://graph.facebook.com/v14.0/me?fields=id%2Cname&access_token='+self.token
        result=self.r.get(rqt)
        json_result = result.json()
        if 'id' in json_result:
            id_fb = json_result['id']
            return str(id_fb)
        print('Unable to find the user ID from facebook')
        exit(1)
