
"""
Este modulo contiene la plantilla de browser para cada conexion
"""


import requests;
import time;

from configLoader import userAgent, maxRetrys, retrySeconds, proxies, filesEncoding;


class Browser(requests.Session):
    
    def __init__(self, robotParser):
        requests.Session.__init__(self);
        self.headers.update({"User-Agent": userAgent});
        self.proxies = proxies;
        self.robotParser = robotParser;


    def getPage(self, url):
        """ Debe devolver el contenido en <str> de la pagina, insiste,
          o devuelve -1 si no tiene exito o no puede acceder """
        
        if not self.robotParser:
            print("Sin chequear el archivo de robots no se intentaran lecturas.")
            return -1;
        elif not self.robotParser.can_fetch(self.headers["User-Agent"], url):
            print(f"No se puede acceder al recurso {url} porque {self.robotParser.url} no lo admite.")
            return -1;
    
        #print(f"Leyendo: {url}")

        for _nRetry in range(maxRetrys):
            
            try:
                page = self.get(url);
                page.raise_for_status(); # <- raise errors
                return page.content.decode(filesEncoding, errors="replace"); #<- succes
                #return page.text; #success
            except Exception as msg:
                #print("error page %s... wait 10 seconds..." % url);
                #print(str(msg));
                time.sleep(retrySeconds);

        return -1;




