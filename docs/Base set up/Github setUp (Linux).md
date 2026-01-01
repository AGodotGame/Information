Primero tenemos que añadir la clave ssh

Seguimos literalmente el tutorial de [aqui](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=linux)

> [!Intro a todo] 
> Aunque nos pida poner passphrase y archivo solo dale intro y siguiente

Despues hacemos **cat** al archivo .pub y añadimos todo dentro de el menu de SSH key dentro de nuestra configuración de el perfil. Es este tutorial de [aquí](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) 

Luego iremos a una terminal 

Pondremos 
```
ssh -T git@github.com
```

Nos aparecerá algo como 
```
Hi PauMasia! You've successfully authenticated, but GitHub does not provide shell access.
```

Eso significa que funciona.

Si hemos creado algún repositorio y no nos deja subirlo, tenemos que revisar el upstream, hilo de subida.
```
pau@pau-HP-Laptop-15s-eq2xxx:/media/pau/General/mkdocs/adventure-one$ git remote -v
origin	https://github.com/AGodotGame/AdventureOne.git (fetch)
origin	https://github.com/AGodotGame/AdventureOne.git (push)

```

Si tenemos **https://** al inicio no podremos subirlo rápidamente, nos pedirá que nos registremos y aun así no funcionará

El git@github es para que se haga desde SSH, es lo que buscamos.

Para cambiarlo ejecutaremos el siguiente comando 
```
pau@pau-HP-Laptop-15s-eq2xxx:/media/pau/General/mkdocs/adventure-one$ git remote set-url origin git@github.com:AGodotGame/AdventureOne.git
```

De forma que el resultado sera el siguiente 
```
git remote -v
origin	git@github.com:AGodotGame/AdventureOne.git (fetch)
origin	git@github.com:AGodotGame/AdventureOne.git (push)
```