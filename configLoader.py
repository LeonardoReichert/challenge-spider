
"""
Este modulo carga la configuracion del programa
"""

import re;


fp = open("config.txt", "r");
dataConfig = fp.read();
fp.close();


domain = open("target_site.txt", "r").read().strip();

#eliminar comentarios antes de parsear:
dataConfig = re.sub("//.+?\r?\n", "", dataConfig, flags=re.DOTALL);
dataConfig = re.sub("/\*.+?\*/", "", dataConfig, flags=re.DOTALL);


def getConfig(header_name):
    value = re.findall(f"\[{header_name}\](.+)\[/{header_name}\]", dataConfig,
                                                flags=re.DOTALL)[0];
    return value.strip();


userAgent = getConfig("user-agent");
pathSaves = getConfig("path-saves");
filenameSaves = getConfig("filename-saves");
filesEncoding = getConfig("saves-encoding");

maxRetrys = int(getConfig("max-retrys-pages"));
retrySeconds = int(getConfig("wait-seconds-retry"));
maxThreads = int(getConfig("max-threads"));


_proxiesLines = getConfig("proxys").split();
proxies = {}
try:
    for line in _proxiesLines:
        parts = line.split("=", 1);
        if parts[0] and parts[1]:
            proxies[parts[0]] = parts[1];
    
    #programacion defensiva: derribar si se especificaron proxies pero no fueron en buen formato...
    assert not (_proxiesLines and not proxies); #<- succes ?
except:
    print("Las proxies en config.txt no llevan una buena forma escrita, debe ser proto:host ...");


if __name__ == "__main__":
    print("Tesging config loader...\n");

    print("domain:", domain);
    print("user-agent:", userAgent);
    print("path-saves:", pathSaves);

    print("proxies:", proxies)

    print("\nok ok");

