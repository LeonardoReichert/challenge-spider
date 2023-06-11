# challenge-spider

### Descripción:
Cumplir con un reto de programación, un proyecto etico con buenos fines.

### Requisitos tecnicos:
 * Se uso **Python 3.11** para su desarrollo, aunque podria funcionar en otras versiones de Python 3.x
 * Instalar la libreria **requests** con el comando **"pip install requests"**
 * Crear el archivo **target_site.txt** que contenga una sola linea del **host apuntado**.

### Forma de uso:
 * Instalar Python y las **dependencias requirements.txt** usando el comando:
  **"pip install -r requirements.txt"**
 * Crear el archivo **target_site.txt** que contenga el nombre de host
 * Modificar a gusto el archivo **config.txt**, en él se encuentran detalles y comentarios sobre cada cosa, no deben usarse valores equivocados o incorrectos porque donde van Boleanos, Numeros, o Texto hacerlo respetando el formato propuesto en los ejemplos del archivo.
 Nota: El archivo **config.txt** conserva una logica de comentarios adecuada para cierto uso, pero no se debe abusar de parametros fuera de lo comun.
 * Ejecutar el modulo **scrap.py**

### Mas sobre config.txt
 Es un archivo que tiene cierta **configuración** y comentarios, los comentarios pueden empezar con // o # o tener varias lineas con /* linea, linea 2, etc */  tal como en algunos lenguajes de programación.
 Los valores de configuración se implementaron con etiquetas con el formato **\[variable]valor\[/variable]** y no es una implementación completa de uso de etiquetas asi que es limitado y se debe guiar por los comentarios.
