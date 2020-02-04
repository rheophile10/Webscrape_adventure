
from selenium import webdriver
import json
import time

url = 'https://emf2.bundesnetzagentur.de/karte/Default.aspx?lat=52.4107723&lon=14.2930953&zoom=14'

browser = webdriver.Chrome()
browser.get(url)
browser.execute_script("""
(function(XHR) {
  "use strict";

  var element = document.createElement('div');
  element.id = "interceptedResponse";
  element.appendChild(document.createTextNode(""));
  document.body.appendChild(element);

  var open = XHR.prototype.open;
  var send = XHR.prototype.send;

  XHR.prototype.open = function(method, url, async, user, pass) {
    this._url = url; // want to track the url requested
    open.call(this, method, url, async, user, pass);
  };

  XHR.prototype.send = function(data) {
    var self = this;
    var oldOnReadyStateChange;
    var url = this._url;

    function onReadyStateChange() {
      if(self.status === 200 && self.readyState == 4 /* complete */) {
        document.getElementById("interceptedResponse").innerHTML +=
            '{"data":' + self.responseText + '}*****';
      }
      if(oldOnReadyStateChange) {
        oldOnReadyStateChange();
      }
    }

    if(this.addEventListener) {
      this.addEventListener("readystatechange", onReadyStateChange,
        false);
    } else {
      oldOnReadyStateChange = this.onreadystatechange;
      this.onreadystatechange = onReadyStateChange;
    }
    send.call(this, data);
  }
})(XMLHttpRequest);
""")

time.sleep(5)

browser.execute_script("""
  var element2 = document.createElement('div');
  element2.id = "decryptedResponse";
  element2.appendChild(document.createTextNode(""));
  document.body.appendChild(element2);""")

def get_data():
    data = browser.find_element_by_id("interceptedResponse").text
    data = data.split("*****")
    encrypted = []
    for d in data:
        try:
            x = json.loads(d)
            x = x['data']['d']['Result']
            encrypted.append(x)
        except:
            pass
    return encrypted


def decrypt(encrypted):
    for e in encrypted:
        browser.execute_script("""
        var a = DecryptData('"""+e+"""')
        document.getElementById("decryptedResponse").innerHTML += a + '*****';""")
    data_dcpt = browser.find_element_by_id("decryptedResponse").text
    data_dcpt = data_dcpt.split("*****")
    final_data = []
    for d in data_dcpt:
        if len(d)>2:
            final_data.append(json.loads(d))
    return final_data









