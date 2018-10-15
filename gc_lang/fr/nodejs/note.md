# Note pour le dévellepement pour NodeJS

## Commande pour définir l'utilisation d'un packetage local

```
cd core
npm link
cd ..
cd cli
npm link grammalecte
npm install
cd ..
```

## Commande désintaller le packetage local et son utilisation

```
npm rm grammalecte --global
cd cli
npm unlink grammalecte
npm rm grammalecte-cli --global
cd ..
```