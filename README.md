# Totodile

<div style="text-align:center"><img src="https://img.pokemondb.net/artwork/vector/large/cyndaquil.png" width="250"/></div>

cyndaquil es un Microserervicio para el proceso de pld.

Permite inicializar con la estructura básica un proyecto con Flask + SQLAlchemy + Alembic + MySQL.

### *NO usa docker-compose*

## Uso
Crear la imagen
1. docker build -t cyndaquil:ejmeplo .
```shell
docker build -t image:version .
```
2. Correr la imagen

Windows:
```
docker run --rm -it --env-file=.env_example -v ${PWD}:/usr/src/app -p 5009:5000 --name totodile  cyndaquil:ejmeplo
```
*NIX:
```
docker run --rm -it --env-file=.env_example -v $(pwd):/usr/src/app -p 5009:5000 --name totodile  cyndaquil:ejmeplo
```
Comentarios:el .env_example remplazalo por .env para que no modifiques nada de los ejemplos y solo agrega en el gitignore el .env que utilices
## Licencia

Cura Deuda 2020
