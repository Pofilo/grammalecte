# Note pour le dévellepement pour NodeJS

## Commande pour définir l’utilisation d’un paquetage local

```
cd core
npm link
cd ..
cd cli
npm link grammalecte
npm install --global
cd ..
```

## Commande désinstaller le paquetage local et son utilisation

```
npm rm grammalecte --global
cd cli
npm unlink grammalecte
npm rm grammalecte-cli --global
cd ..
```