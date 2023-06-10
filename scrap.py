
"""

creado el scrap crawler challenge

"""

from browser import Browser;

import time;
import threading;
import re;
import json;

from configLoader import domain, userAgent, maxRetrys, retrySeconds, maxThreads;

from parsers import DictProduct;



class Scraper:
    programThreads = [];

    def __init__(self):
        pass;
    
    def waitThreads(self, wait_all=False):
        """ Espera mientras la cantidad de threads este al limite """
        if wait_all:
            print(f"Esperando {len(self.programThreads)} threads...")
        while (len(self.programThreads) >= maxThreads) or (wait_all and self.programThreads):
            for thread in self.programThreads:
                if not thread.is_alive():
                    self.programThreads.remove(thread);
            #        print("removido un thread")
            time.sleep(0.01); #10ms no estresa cpu
        if wait_all:
            print("Threads finalizados.")


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
        result = Browser().getPage(domain + slug);
        if result != -1:
            categories = json.loads(result);
        else:
            print("Hubieron problemas al leer la api de categorias.");
            return False;
        
        self.apisCategories = [];

        for dictCategory in categories:

            #quitamos el nombre de host y conservamos el slug: https://dominio.com/slug_category/
            slug = dictCategory["url"].split("//", 1)[1].split("/", 1)[1];
            
            urlApi = domain+"/api/catalog_system/pub/products/search/%s/"%slug;
            self.apisCategories.append(urlApi);

            #las sub-categorias de esta categoria las agregamos a este for proceso:
            categories.extend(dictCategory["children"]);

        print("hay %d slugs categorias" % len(self.apisCategories))
        
        return True;  #succes
    

    def getProductsFromSucursal(self, scId):
        """ devuelve la lista de productos de la sucursal consultada """

        #a este punto las api-categorias ya fueron extraidas

        browser = Browser();

        products = [];

        _countCategory = 0;
        def procGetProductsFromCategory(urlApiCategory):
            nonlocal _countCategory;

            maxProducts = 50;
            for _from in range(0, 2550, maxProducts):
                to = _from + maxProducts-1;

                url = urlApiCategory + f"?_from={_from}&_to={to}&sc={scId}";
                result = browser.getPage( url );
                if result == -1:
                    return; #fail
                            
                jsonResult = json.loads(result);

                result = [DictProduct(prod).parse() for prod in jsonResult];
                if not result:
                    break;
                
                products.extend(result); #una simple prueba aun
            
            #mostrar progreso de esta busqueda:
            _countCategory += 1;
            progress = _countCategory / len(self.apisCategories) * 100;
            if progress>0 and (progress % 5.0) == 0.0:
                print(f"sc: {scId} progress: %.02f %%" % (progress) );
        
        for urlApiCategory in self.apisCategories:
            self.startNewThread(procGetProductsFromCategory, urlApiCategory);
        
        self.waitThreads(True); #esperando a que finalice la busqueda de esta sucursal

        return products;

            
    def getProductsFromAllSucursals(self):
        """ Revisa todas las sucursales y devuelve todos sus productos """

        if not self._recvApiCategories():
            print("Hubo un error...");
            return -1;
        
        sucursals = self.getAvailableSucursalIds();

        results = {};
        for scId in list(sorted(sucursals.keys())):

            nameSucursal = sucursals[scId];
            print(f"Siguiente sucursal ID {scId}: {nameSucursal}");
            results[scId] = self.getProductsFromSucursal( scId );
            
        print(f"Finalizando todos los {len(self.programThreads)} threads... ");
        self.waitThreads(True);
        print("listo.");
        
        return results;


    def getAvailableSucursalIds(self):
        """ Obtiene el ID de sucursales disponibles """

        url =  "/institucional/sucursales";
        print("Obteniendo sucursales desde: %s ..." % url);

        url = domain + url;

        browser = Browser();

        try:
            html = browser.get(url).text;
        except Exception as msg:
            print("Error: "+str(msg));
            return {};

        stores_data = re.findall("<div id=\"stores-data\">(.+)</div>", html, flags=re.DOTALL);
        if not stores_data:
            print("Error, no hay '<div>' stores-data en %s..." %url);
            return {};
    
        stores_data = json.loads(stores_data[0]);
        stores_data = stores_data["stores"];

        #tomamos el primer id 101 y lo restamos para solo obtenerlos como indices:
        base_index = stores_data[0]["id"]-1; #101 - 1 = 100

        sucursals = {};

        def test_sc(scId, scName):
            #thread que prueba una sucursal
            testUrl = f"{domain}/api/catalog_system/pub/products/search/?sc={scId}";
            try:
                resp = browser.get(testUrl);
                resp.raise_for_status();
                sucursals[scId] = scName; #funciona
            except Exception as msg:
                #sucursal no permitida
                pass;

        for store in stores_data:
            scId =  store["id"] - base_index;
            self.startNewThread(test_sc, scId, store["name"]);
        
        self.waitThreads(wait_all=True);

        print("%d id sucursales disponibles..." % len(sucursals));

        return sucursals;


b = Scraper();
results = b.getProductsFromAllSucursals();
print(f"teniendo {len(results)}");
sc = b.getAvailableSucursalIds();

for scId, products in results.items():
    print(f"sc-id {scId}: tiene {len(products)} products");

input("fin")




