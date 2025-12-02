# Sopa de Letras (Word Search) - Proyecto

Pequeña app en Flask + Flask-SocketIO para generar y jugar una sopa de letras.

Requisitos mínimos
- Python 3.10+ (preferible 3.11)
- `pip`

Pasos para iniciar (Windows PowerShell):

1. Crear y activar un entorno virtual (si aún no lo tienes):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Ejecutar la aplicación:

```powershell
python servidor.py
```

4. Abrir el navegador en `http://localhost:5000`.

Notas y recomendaciones
- Actualmente la versión del proyecto estaba situada dentro de la carpeta `venv/`. He copiado los ficheros esenciales al raíz del repositorio para facilitar ejecución y mantenimiento.
- Para ver la solución de una sesión desde otra página puedes abrir `http://localhost:5000/resolver/<sid>` (reemplaza `<sid>` por el socket id mostrado en la consola o que obtengas desde el cliente). La página trae un botón para solicitar la solución correspondiente.
- Si prefieres no subir el `venv` al repositorio, deja el `venv/` en `.gitignore` y elimina la carpeta del control de versiones.

Cambios relevantes
- El servidor ahora usa `Flask-SocketIO` en modo `threading` (hilos de Python) para cumplir el requisito de emplear hilos por palabra.
- El generador crea un hilo por palabra al intentar colocarla en el tablero.
- El cliente muestra el `SID` en la interfaz (área de log) al conectarse; puedes abrir `http://localhost:5000/resolver/<sid>` para ver la solución de la sesión correspondiente.

Seguridad y notas
- Actualmente las partidas se guardan en memoria (`games` en `servidor.py`). Si necesitas persistencia o multi-host, considera usar una base de datos o archivos.
- La opción `RESOLVER` devuelve las posiciones tal cual están en memoria; ten en cuenta que cualquiera que conozca el `sid` puede ver la solución. Si quieres restringir el acceso, puedo añadir tokens o una autenticación simple.
