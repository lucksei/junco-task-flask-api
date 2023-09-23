# Junco Films - Tarea Tecnica

## Descripción

API simple que programe para la tarea tecnica de Junco Films

## Dependencias

Instalar `Python`, `Pip` y `venv` (si es necesario)

```sh
sudo apt update
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-venv
```

generar entorno virtual y activarlo

```sh
python3 -m venv .env
source /env/bin/activate
```

instalar `Flask`(opcional) y `Gunicorn` como servidor WSGI dentro del entorno virtual

```sh
pip3 install Flask
pip3 install Gunicorn
```

## Encender el servidor

1. Activar el entorno virtual

```sh
source /env/bin/activate
```

2. Exportar variable de entorno `API_KEY` que autoriza la conexión con el mismo

```sh
export SERVER_ENV=TEST
```

3. Encender el servidor WSGI con Gunicorn

```sh
gunicorn juncoapi:app
```

## Proxy a HTTPS usando NGINX

Decidi hacer un proxy server hacia la API en cambio de agregar las credenciales a la misma. Para eso utilize `NGINX` como proxy y certificado digital usando `certBot`.

Esto requiere algunas configuraciones adicionales para permitir `CORS` debido a que las peticiones de origen cruzado son negadas por los navegadores por defecto, la directiva usada es la siguiente

```nginx
location /api {
    add_header Access-Control-Allow-Origin 'https://4mynfg.csb.app';
    add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE';
    add_header Access-Control-Max-Age 3600;
    add_header Access-Control-Allow-Credentials 'true';
    add_header Access-Control-Allow-Headers 'authorization';
    proxy_pass http://localhost:8000/;
    }
```

Las cabeceras mas importantes:

- La cabecera `Access-Control-Allow-Origin` solo permite la conexion desde la pagina (`https://4mynfg.csb.app`), puede tambien ser configurado como `* always` para permitir cualquier origen.
- La cabecera `Access-Control-Allow-Credentials 'true'` expone los credenciales al Front end.
- La cabecera `Access-Control-Allow-Headers` permite al Front-end agregar la cabecera `request` de `authorization` que expone la `API-KEY` para poder acceder a la API. Ej:
  ```
  Authorization: Basic YWxhZGRpbjpvcGVuc2VzYW1l
  ```
  Donde la llave es nada mas que un usuario y contraseña, separados por dos puntos `aladdin:opensesame` codificado en base64, `YWxhZGRpbjpvcGVuc2VzYW1l`
