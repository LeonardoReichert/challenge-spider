
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
        #print("esperando threads")
        while (len(self.programThreads) >= maxThreads) or (wait_all and self.programThreads):
            for thread in self.programThreads:
                if not thread.is_alive():
                    self.programThreads.remove(thread);
            #        print("removido un thread")
            time.sleep(0.01); #10ms no estresa cpu
            #print(self.programThreads)
        #print("listo")

    def startNewThread(self, func, *args):
        self.waitThreads();
        thread = threading.Thread(target=func, args=args);
        thread.start();
        self.programThreads.append(thread);
    
    def getInfoCategories(self):
        slug = "/api/catalog_system/pub/category/tree/50";
        result = self.getPage(domain + slug);
        if result != -1:
            result = json.loads(result);
        else:
            print("Hubieron problemas al leer la api de categorias.");

    
    def getProductsFromSucursal(self, sc):

        browser = Browser();

        products = [];
        for _from in range(0, 2550, 50):
            to = _from + 49;
#            print(_from, to)

            def procGetProducts():
                result = browser.getPage(
                  domain+f"/api/catalog_system/pub/products/search/?_from={_from}&_to={to}&sc={sc}");
                if result == -1:
                    print("Error no pagina sucursal", sc);
                    #time.sleep(120);
                    return [];
            
                products.extend(re.findall("\"productId\":\"([0-9]+)\"", result))
                #print("resultado: %d " % result.count("productId"));
            
            self.startNewThread(procGetProducts);

        return products;
            
    def getProductsFromAllSucursals(self):
        """ Revisa todas las sucursales y devuelve todos sus productos """

        results = []
        for surcursal in range(1, 17):

            results.append( b.getProductsFromSucursal(surcursal) );
    
            #products.extend(results);
            #products = list(set(products));
            print(f"probando sucursal {surcursal} con {len(self.programThreads)} threads");
            #self.startNewThread(procProducts);

            #time.sleep(5)
        
        print("Finalizando todos los threads... ", end="")
        self.waitThreads(True);
        print("listo.")

        t1 = time.time();
        products = []
        for res in results:
            products.extend(res);
        
        passed = time.time()-t1;
        products = list(set(products));
        print("Segundos pasados en agrupar todos los resultados: ", passed)
        
        return products;

b = Scraper();

results = b.getProductsFromAllSucursals();

print(f"teniendo {len(results)}");

input("fin")




