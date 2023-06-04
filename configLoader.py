
"""
Este modulo carga la configuracion del programa
"""

import re;


fp = open("config.txt", "r");
dataConfig = fp.read();
fp.close();


domain = open("target_site.txt", "r").read().strip()

#domain = re.findall("\[domain\](.+)\[/domain\]", dataConfig, flags=re.DOTALL)[0].replace("\n", "");

userAgent = re.findall("\[user-agent\](.+)\[/user-agent\]", dataConfig,
                                                        flags=re.DOTALL)[0].replace("\n", "");

pathSaves = re.findall("\[path-saves\](.+)\[/path-saves\]", dataConfig,
                                                        flags=re.DOTALL)[0].replace("\n", "");


maxRetrys = int(re.findall("\[max-retrys-pages\](.+)\[/max-retrys-pages\]", dataConfig,
                                                        flags=re.DOTALL)[0].replace("\n", ""));

retrySeconds = int(re.findall("\[wait-seconds-retry\](.+)\[/wait-seconds-retry\]", dataConfig,
                                                        flags=re.DOTALL)[0].replace("\n", ""));


maxThreads = int(re.findall("\[max-threads\](.+)\[/max-threads\]", dataConfig,
                                                        flags=re.DOTALL)[0].replace("\n", ""));



if __name__ == "__main__":
    print("Tesging config loader...\n");

    print("domain:", domain);
    print("user-agent:", userAgent);
    print("path-saves:", pathSaves);

    print("\nok ok");

