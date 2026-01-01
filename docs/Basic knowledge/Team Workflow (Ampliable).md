
### Sistema de PRs
Lo correcto seria subir un PR y que alguien lo revise también

Se baja la rama con el comando 
```
git fetch git@github.com:USUARIO/REPO.git rama-remota:rama-local
```
Si verifican que esta correcto, entonces que el que ha hecho el Pull Request haga el merge y avise a los demas, para que hagan pull.

Y estos hagan pull a la rama principal local, y que tambien hagan pull a la rama que esten tocando. Mas que nada al principio

### Resolucion de conflictos

rebase y eso,