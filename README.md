Para poner en funcionamiento la aplicación se requieren una serie de dependencias, por comodidad se recomienda seguir los siguientes comandos para establecer un entorno virtual desde el que ejecutar la aplicación y sus dependencias sin que persistan en todo el sistema.

# En /GeoScope

.\.venv\Scripts\activate

pip install -r requirements.txt

# En /GeoScope/src

python -m main.views.app

Con estos comandos GeoScope debería correr en http://localhost:5000 si no se ha configurado para que lo haga de otra manera.
