
"""
Este modulo carga la configuracion del programa
"""

import re;


fp = open("config.txt", "r");
dataConfig = fp.read();
fp.close();


domain = open("target_site.txt", "r").read().strip();


def getConfig(header_name):
    value = re.findall(f"\[{header_name}\](.+)\[/{header_name}\]", dataConfig,
                                                flags=re.DOTALL)[0].replace("\n", "");
    return value;


userAgent = getConfig("user-agent");
pathSaves = getConfig("path-saves");
filenameSaves = getConfig("filename-saves");
maxRetrys = getConfig("max-retrys-pages");
retrySeconds = getConfig("wait-seconds-retry");;
maxThreads = getConfig("max-threads");


if __name__ == "__main__":
    print("Tesging config loader...\n");

    print("domain:", domain);
    print("user-agent:", userAgent);
    print("path-saves:", pathSaves);

    print("\nok ok");

