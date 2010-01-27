import re
import time
import urllib
import urllib2

class LoginError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class _Bank():
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.accounts = []
        self._opener = urllib2.build_opener(urllib2.HTTPCookieProcessor)
        
    def __str__(self):
        return self

    def _urlopen(self, url, data=None, headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2) Gecko/2008091620 Firefox/3.0.2', 'Connection':'Keep-Alive', 'Content-Type':'application/x-www-form-urlencoded'}): 
        if hasattr(data, "__iter__"):
            data = urllib.urlencode(data)
        return self._opener.open(urllib2.Request(url, data, headers))
    
    def _str2num(self, s):
        """Convert string to either int or float."""
        s = s.replace(".","").replace(",",".").replace(" ","").replace("&nbsp;","")
        try:
            return int(s)
        except ValueError:
            return float(s)

    
class Nordea(_Bank):
    def __init__(self, username, password):
        _Bank.__init__(self, username, password)
        self.update()

    def update(self):
        """Update the accounts information."""
        params = dict(kundnr=self.username, pinkod=self.password, OBJECT='TT00', prev_link='https://gfs.nb.se/privat/bank/login_kod2.html', CHECKCODE='checkcode')
        self._urlopen("https://gfs.nb.se/bin2/gfskod?OBJECT=KK20") #Get cookies
        data = self._urlopen("https://gfs.nb.se/bin2/gfskod", params).read()
        if not "reDirect" in data:
            raise LoginError("Wrong username or password.")
    
        data = self._urlopen("https://gfs.nb.se/bin2/gfskod?OBJECT=KF00T&show_button=No").read()
        data = data.replace(chr(10),"").replace(chr(13),"").replace("&nbsp;","")
    
        balance = re.findall(r'(?is)nowrap>(.+?)SEK<',data)
        account = re.findall(r"(?is)Kontoutdraget';.*?>(.*?)</a></td>",data)
        if not (balance and account):
            raise ParseError('Unable to parse data.')
        self.accounts = []
        for x in range(len(account)):
            self.accounts.append((account[x].capitalize(), self._str2num(balance[x]), "SEK"))
        return self
            
            
class Swedbank(_Bank):
    def __init__(self, username, password):
        _Bank.__init__(self, username, password)
        self.update()
    
    def update(self):
        """Update the accounts information."""
        data = self._urlopen("https://mobilbank.swedbank.se/banking/swedbank-light/login.html").read()
        #Find the Cross-site request forgery token
        m = re.search(r'csrf_token"\s*value="(?P<csrftoken>[^"]+)"', data, re.I)
        if not m:
            raise ParseError('Unable to find CSRF token.')
        csrftoken = m.group("csrftoken")
        params = dict(xyz=self.username, zyx=self.password, _csrf_token=csrftoken)
        data = self._urlopen("https://mobilbank.swedbank.se/banking/swedbank/login.html", params).read()
        
        if "misslyckats" in data:
            raise LoginError("Wrong username or password.")
        data = self._urlopen("https://mobilbank.swedbank.se/banking/swedbank-light/accounts.html").read().replace('\xa0','')
        
        accounts = re.finditer(r'<span.*?/span>(?P<account>[^<]+) <.*?secondary">(?P<balance>[0-9 .,-]+)</span', data, re.I)
        if not accounts:
            raise ParseError('Unable to parse data.')
        
        self.accounts = []
        for account in accounts:
            self.accounts.append((account.group("account").capitalize(), self._str2num(account.group("balance")), "SEK"))
        return self