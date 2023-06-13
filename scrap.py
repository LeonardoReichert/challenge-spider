
"""

creado el scrap crawler challenge

"""

from browser import Browser;

import time;
import threading;
import re;
import json;
import csv;
import os;
import os.path;
from urllib.robotparser import RobotFileParser;

#owns modules:
from configLoader import *;
#(hostname, maxThreads, pathSaves, filenameSaves, filesEncoding,
                          #proxies, maxRetrys, retrySeconds);
from parsers import DictProduct;



def reportProgress(progress, unprogress, countThreads):
    """ Muestra de manera amigable el progreso en una sola linea """
    print(f"\r{'#'*int(20/100*progress)}{'-'*int(20/100*unprogress)} progress: {progress:.02f}%.  \
 {countThreads} threads. {' '*10}", end="");
    

class Scraper:
    programThreads = [];

    def __init__(self, hostname):
        self.hostname = hostname;

        try:
            print("Leyendo el archivo robots...", end="");
            self.robotParser = RobotFileParser(url=f"{hostname}/robots.txt");
            self.robotParser.read();
            print(" Listo.");
        except:
            print(f"No se pudo leer el archivo {hostname}/rotobts.txt")
            self.robotParser = None; #Error
                
    
    def waitThreads(self, wait_all=False):
        """ Espera mientras la cantidad de threads este al limite """
        #if wait_all:
        #    print(f"Esperando {len(self.programThreads)} threads...")
        while (len(self.programThreads) >= maxThreads) or (wait_all and self.programThreads):
            for thread in self.programThreads:
                if not thread.is_alive():
                    self.programThreads.remove(thread);
            #        print("removido un thread")
            time.sleep(0.01); #10ms no estresa cpu
        #if wait_all:
        #    print("Threads finalizados.")


    def startNewThread(self, func, *args):
        """ Inicia un thread y lo pone en la lista de threads, pero espera si la lista esta en tope """
        self.waitThreads();
        thread = threading.Thread(target=func, args=args);
        thread.start();
        self.programThreads.append(thread);
    

    def _recvApiCategories(self):
        """
        recupera las url-api de categorias o subcategorias para consultar posteriormente productos
        devuelve True si tiene exito, False si tuvo error"""

        print("Recuperando las slugs-categorias... ");

        #50 es la profundidad entre categorias y subcategorias
        slug = "/api/catalog_system/pub/category/tree/50";
        result = Browser(self.robotParser).getPage(self.hostname + slug);
        if result != -1:
            categories = json.loads(result);
        else:
            print("Hubieron problemas al leer la api de categorias.");
            return False;
        
        self.apisCategories = [];

        for dictCategory in categories:

            #quitamos el nombre de host y conservamos el slug: https://dominio.com/slug_category/
            slug = dictCategory["url"].split("//", 1)[1].split("/", 1)[1];
            
            urlApi = self.hostname+"/api/catalog_system/pub/products/search/%s/"%slug;
            self.apisCategories.append(urlApi);

            #las sub-categorias de esta categoria las agregamos a este for proceso:
            categories.extend(dictCategory["children"]);

        print("hay %d slugs categorias" % len(self.apisCategories))
        
        return True;  #succes
    

    def getProductsFromSucursal(self, scId):
        """ devuelve la lista de productos de la sucursal consultada """

        #a este punto las api-categorias ya fueron extraidas

        browser = Browser(self.robotParser);

        products = [];
        errors = 0;

        _countCategory = 0;
        def procGetProductsFromCategory(urlApiCategory):
            nonlocal _countCategory;
            nonlocal errors;

            maxProducts = 50;
            for _from in range(0, 2550, maxProducts):
                to = _from + maxProducts-1;

                url = urlApiCategory + f"?_from={_from}&_to={to}&sc={scId}";
                result = browser.getPage( url );
                if result == -1:
                    errors += 1;
                    return; #fail
                
                jsonResult = json.loads(result);

                if not result:
                    break;

                #tomamos solo lo necesario:
                result = [DictProduct(prod).parse() for prod in jsonResult];
                
                products.extend(result); #una simple prueba aun
            
            #mostrar progreso de esta busqueda:
            if showProgress:
                _countCategory += 1;
                progress = _countCategory / len(self.apisCategories) * 100;
                unprogress = 100-progress;
                reportProgress(progress, unprogress, len(self.programThreads));
                
        for urlApiCategory in self.apisCategories:
            self.startNewThread(procGetProductsFromCategory, urlApiCategory);
        
        self.waitThreads(True); #esperando a que finalice la busqueda de esta sucursal
        print("\nFinalizados los threads.")
        if errors > 0:
            print(f"Hubieron {errors} errores o peticiones sin respuesta.");

        return products;

            
    def getProductsFromAllSucursals(self):
        """ Revisa todas las sucursales y devuelve todos sus productos """

        if not self._recvApiCategories():
            print("Hubo un error...");
            return -1;
        
        sucursals = self.getAvailableSucursalIds();
        if not sucursals:
            print("Ocurrio un error o no se han obtenido sucursales.");
            return -1;

        resultProducts = {};
        for scId in list(sorted(sucursals.keys())):

            nameSucursal = sucursals[scId];
            print(f"\nSiguiente sucursal ID {scId}: {nameSucursal}");
            marcaTiempo = time.time();
            resultProducts[scId] = self.getProductsFromSucursal( scId );
            transcurrido = time.time()-marcaTiempo;
            print(f"Transcurrios {transcurrido:.01f} segundos por sucursal ID {scId}...");
        
        print(f"Finalizando todos los {len(self.programThreads)} threads... ");
        self.waitThreads(True);
        print("listo.");
        
        return sucursals, resultProducts;


    def getAvailableSucursalIds(self):
        """ Obtiene el ID de sucursales disponibles """

        url =  "/files/fit-home.js";
        print("Obteniendo sucursales desde: %s ..." % url);

        url = self.hostname + url;

        browser = Browser(self.robotParser);

        html = browser.getPage(url);
        if html == -1:
            return {};

        stores_data = re.findall('"ecommerce":true,"id":[0-9]+?,"name":"(.+?)","sc":([0-9]+?),', html, flags=re.DOTALL);
        if not stores_data:
            print("Error, no hay patron 'id, name, y sc' en %s..." %url);
            return {};
    
        sucursals = {};

        def test_sc(scId, scName):
            #thread que prueba una sucursal
            testUrl = f"{self.hostname}/api/catalog_system/pub/products/search/?sc={scId}";
            resp = browser.getPage(testUrl);
            if resp != -1:
                sucursals[scId] = scName; #funciona
            
        for name, scId in stores_data:
            self.startNewThread(test_sc, scId, name);
        
        self.waitThreads(wait_all=True);

        print("%d id sucursales disponibles:" % len(sucursals));
        for scId in sorted([int(sc) for sc in sucursals]):
            name = sucursals[str(scId)];
            print(f" id {scId}: {name}");

        return sucursals;



def main():
    """
        pone a trabajar
    """
    
    print("Comenzando...\n")
    print("--------------------------------------------------------")
    if proxies:
        print("Se han configurado proxies, y la configuración es", proxies)
        print("Las proxies se configuran en config.txt")
    print(f'Los archivos csv se guardaran en "{pathSaves}"')
    print(f'Los archivos csv se en formato como "{filenameSaves}"')
    print(f'Los archivos csv se guardaran en la codificación: "{filesEncoding}"')
    print("--------------------------------------------------------")
    print(f"Se usaran un maximo de {maxThreads} threads.");
    print(f"Se usaran un maximo de {maxRetrys} intentos por solicitud.");
    print(f"Se esperara {retrySeconds} segundos despues de cada reintento.");
    print("--------------------------------------------------------")

    if not os.path.exists(pathSaves):
        try:
            os.makedirs(pathSaves);
            print(f'Creada la carpeta "{pathSaves}"')
        except Exception as msg:
            print(f"No se ha podido crear la carpeta {pathSaves}\n abortando proceso... Razon: {msg}");
            return -1;

    scrap = Scraper(hostname);

    sucursalNames, productBySucursals = scrap.getProductsFromAllSucursals();

    print("\nTerminado.")
    print("--------------------------------------------------------")
    print("Guardando resultados...")


    countSave = 0;

    for scId, listProduct in productBySucursals.items():
        
        countSave += 1;

        filename = filenameSaves.replace("%nsave%", str(countSave));
        filename = filename.replace("%sc%", scId);
        filename = filename.replace("%scname%", sucursalNames[scId]);
        filename = f"{pathSaves}/{filename}".replace("//", "/");

        fieldnames = list(listProduct[0].keys());

        print(filename, end="... ");

        try:
            with open(filename, "w", encoding=filesEncoding) as fp:
                writer = csv.DictWriter(fp, fieldnames);
                writer.writeheader();
                writer.writerows(listProduct);
            print("[Saved]")
        except Exception as msg:
            print(f"[Error] Razon: {msg}")
            break;


if __name__ == "__main__":
    main();
    input("fin - enter para salir...")

