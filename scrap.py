
"""
creado el scrap crawler etico aqui
"""

from browser import Browser;

import time;
import threading;
import re;
import json;

from configLoader import domain, userAgent, maxRetrys, retrySeconds, maxThreads;




class Scraper:
    programThreads = [];

    def __init__(self):
        pass;
    
    def waitThreads(self, wait_all=False):
        """ Espera mientras la cantidad de threads este al limite """
        if wait_all:
            print("esperando threads")
        while (len(self.programThreads) >= maxThreads) or (wait_all and self.programThreads):
            for thread in self.programThreads:
                if not thread.is_alive():
                    self.programThreads.remove(thread);
            #        print("removido un thread")
            time.sleep(0.01); #10ms no estresa cpu
        if wait_all:
            print("listo threads")


    def startNewThread(self, func, *args):
        self.waitThreads();
        thread = threading.Thread(target=func, args=args);
        thread.start();
        self.programThreads.append(thread);
    

    def _recvApiCategories(self):
        """
        recupera las url-api de categorias o subcategorias para consultar posteriormente productos
        devuelve True si tiene exito, False si tuvo error"""

        print("Recuperando las slugs-categorias... ", end="");

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
    

    def getProductsFromSucursal(self, sc):
        """ devuelve la lista de sucursales consultada, pero en proceso aun """

        #a este punto las api-categorias ya fueron extraidas

        browser = Browser();

        products = [];

        count = 0;
        
        for urlApi in self.apisCategories:
            def procGetProducts():
                
                for _from in range(0, 2550, 50):
                    to = _from + 49;

                    url = urlApi + f"?_from={_from}&_to={to}&sc={sc}";
                    result = browser.getPage( url );
                    if result == -1:
                        return;

                    result = re.findall("\"productId\":\"([0-9]+)\"", result);
                    if not result:
                        break;
                    
                    products.extend(result) #una simple prueba aun
                        #print("resultado: %d " % result.count("productId"));
                    
            self.startNewThread(procGetProducts);
            count += 1;
            #print(f"Encontrados {len(result)} resultados en {url}..");
            progress = count / len(self.apisCategories) * 100;
            if not progress % 10:
                print("sc: %d progress: %.02f %%" % (sc, progress) );
        

        return products;
            
    def getProductsFromAllSucursals(self):
        """ Revisa todas las sucursales y devuelve todos sus productos """

        if not self._recvApiCategories():
            print("Hubo un error...");
            return -1;
        
        results = [];
        for surcursal in range(1, 17): #<- los sc se calcularan

            pendingResult = self.getProductsFromSucursal( surcursal );
            results.append( pendingResult );
    
            #products.extend(results);
            #products = list(set(products));
            print(f"probando sucursal {surcursal} con {len(self.programThreads)} threads");
            #self.startNewThread(procProducts);
            self.waitThreads(True);

            print("productos:", len(pendingResult));
            #break;

            #time.sleep(5)
        
        print("Finalizando todos los threads... ", end="");
        self.waitThreads(True);
        print("listo.");

        t1 = time.time();
        products = []
        for res in results:
            products.extend(res);
        
        passed = time.time()-t1;
        products = list(set(products));
        print("Segundos pasados en agrupar todos los resultados: ", passed)
        
        return products;

    def getAvailableSucursalIds(self):
        """ Obtiene el ID de sucursales disponibles """

        url = domain + "/institucional/sucursales";

        print("Obteniendo sucursales desde: %s ..." % url, end="");
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

        for store in stores_data:
            sc =  store["id"] - base_index;
            
            test_url = domain + "/api/catalog_system/pub/products/search/?sc=%d" % sc;
            try:
                resp = browser.get(test_url);
                resp.raise_for_status();
                sucursals[str(sc)] = store["name"]; #funciona
            except Exception as msg:
                #sucursal no permitida
                pass;

        return sucursals;

            

        


b = Scraper();
#results = b.getProductsFromAllSucursals();
#print(f"teniendo {len(results)}");

#sc = b.getAvailableSucursalIds();
#print("sc:", sc)

input("fin")




