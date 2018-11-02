# -*- encoding: utf-8 -*-

from flask import Flask 
import base64
import urllib2
import urllib
import cookielib


app = Flask(__name__)

def _get_basic_auth(username, password):
  code = base64.encodestring(username + ":" + password)[:-1]
  return "Basic " + code

# only tested at vsphere6.5
def _get_html_from_vsphere(ipaddr, username, password):
    user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36(KHTML,' \
        'like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    base_url = r"https://%s" % ipaddr 
    headers = {
        "Referer": base_url + r"/vsphere-client/?csp",
        "User-Agent": user_agent}
    cookie = cookielib.CookieJar()
    handler=urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)

    url1 = base_url +  r"/vsphere-client/logon"
    request = urllib2.Request(url=url1, headers=headers)
    response = opener.open(request)
    try:
        print "the cookies like"
        for i in cookie:
          print "name", i.name
          print "value", i.value
        print "headers:", response.headers.dict
        print "code:", response.code
        print "url: ", response.geturl()
    finally:
        response.close()
    cookie_data = {i.name: i.value for i in cookie}

    # step2
    url2 = response.geturl() + r"&passwordSupplied=1"
    search_str ="passwordEntry=1"
    replace_str ='passwordSupplied=1'
    referer_url = response.geturl()
    referer_url = referer_url.replace(search_str, replace_str)

    auth = _get_basic_auth(username, password)

    cookie2 = cookielib.CookieJar()
    handler2 = urllib2.HTTPCookieProcessor(cookie2)
    opener2 = urllib2.build_opener(handler2)

    request2 = urllib2.Request(url=url2)
    request2.add_header("Referer", referer_url)
    request2.add_header("User-Agent", user_agent)
    request2.add_header("Cookie", cookie_data)
    request2.add_header('Content-type', 'application/x-www-form-urlencoded')

    login_data = 'CastleAuthorization=' + urllib.quote(auth)
    request2.add_data(login_data)
    response2 = opener2.open(request2)
    result = None
    try:
        print "the latest cookies like"
        for i in cookie2:
            print "name", i.name
            print "value", i.value
        print "headers:", response2.headers.dict
        print "code:", response2.code
        print "url: ", response2.geturl()
        print "info: ", response2.info()
        result = response2.read()
    finally:
        response2.close()
    return result


# the vars must encoded by base64
@app.route('/generate_html/<ipaddr>/<username>/<password>/')
def generate_login_html(ipaddr, username, password):
    ip = base64.decodestring(ipaddr)
    user = base64.decodestring(username)
    passwd = base64.decodestring(password)
    return _get_html_from_vsphere(ip, user, passwd)
