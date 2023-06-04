
"""
Este modulo contiene la plantilla de browser para cada conexion
"""


import requests;
import time;
import threading;
import re;
import json;

from configLoader import userAgent, maxRetrys, retrySeconds;


class Browser(requests.Session):

    def __init__(self):
        requests.Session.__init__(self);
        self.headers.update({"User-Agent": userAgent});

    def getPage(self, url):
        """ Debe devolver el contenido en <str> de la pagina, insiste, o un -1 si no tiene exito """
        
        for nRetry in range(maxRetrys):
            browser = Browser();
            try:
                browser.cookies.clear();
                page = browser.get(url);
                page.raise_for_status();
                break; #<- succes
            except Exception as msg:
                #print("error page %s... wait 10 seconds..." % url);
                #print(str(msg));
                time.sleep(retrySeconds);
        
        if nRetry+1 == maxRetrys:
            return -1;

        return page.content.decode("utf-8", errors="replace");




