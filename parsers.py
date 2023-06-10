
"""
Este modulo parsea/aclara un diccionario o json de producto
"""

from re import findall;


class DictProduct(dict):
    def getId(self):
        return self["productId"];

    def getName(self):
        return self["productName"];

    def getPrice(self):
        #precio regular
        return self["items"][0]["sellers"][0]["commertialOffer"]["Price"];
    
    def getListPrice(self):
        #precio publicado
        return self["items"][0]["sellers"][0]["commertialOffer"]["ListPrice"];

    def getCategory(self):
        return self["categories"][0];

    def getSKU(self):
        link = self["items"][0]["sellers"][0]["addToCartLink"];
        sku = findall("sku=([0-9]+)", link);
        if sku:
            return sku[0];
        return "";

    def getUrl(self):
        return self["link"];

    def getStock(self):
        return self["items"][0]["sellers"][0]["commertialOffer"]["AvailableQuantity"];

    def getDescription(self):
        return self["description"];

    def parse(self):
        return {"productId": self.getId(),
                "productName": self.getName(),
                "price": self.getPrice(),
                "ListPrice": self.getListPrice(),
                "category": self.getCategory(),
                "sku": self.getSKU(),
                "url": self.getUrl(),
                "stock": self.getStock(),
                "description": self.getDescription(),
                };

