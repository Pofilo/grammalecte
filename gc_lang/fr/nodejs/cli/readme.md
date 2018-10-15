# Client/Serveur de Grammalecte pour NodeJS

## Informations

Il y a trois modes de fonctionnement: client / client intératif / serveur.

* Client intéractif: «gramma-cli -i».
* Client: «gramma-cli --command \"mot/texte\"».
* Serveur: lancé avec la commande «gramma-cli --server --port NumPort».

## Installation

```
npm install grammalecte-cli -g
```

## Commandes

* help           : Affichie les informations que vous lisez ;)
* perf           : Permet d'afficher le temps d'exécution des commandes.
* json           : Réponse en format format json.
* exit           : Client intéractif: Permet de le quitter.
* format         : Permet de mettre en forme le texte.
* check          : Vérifie la grammaire et l'orthographe d'un texte.
* lexique        : Affiche le lexique du texte.
* spell          : Vérifie l'existence d'un mot.
* suggest        : Suggestion des orthographes possible d'un mot.
* morph          : Affiche les informations pour un mot.
* lemma          : Donne le lemme d'un mot.
* text           : Client / Server: Définir un texte pour plusieurs actions.
* gceoption      : Défini une option a utilisé par le correcteur de grammaire.

## Client intéractif

Pour le lancé vous devez saisir «gramma-cli -i», il est un mode question/réponse.

Exemple pour les vérifications portant sur un mot:

```
CMD> gramma-cli -i
Bienvenu sur Grammalecte pour NodeJS!!!
GrammaJS> suggest salit
Suggestion possible de: salit
 ├ salit
 ├ salît
 ├ salie
 ├ salis
 ├ salir
 ├ salin
 ├ sali
 ├ salait
 ├ salut
 └ salât
GrammaJS> exit
```

Exemple pour les vérifications portant sur un texte:

```
CMD> gramma-cli -i
Bienvenu sur Grammalecte pour NodeJS!!!
GrammaJS> format
> salut,les copains!!!
> vous allez bien ?
> /format
Mise en forme:
salut, les copains!!!
vous allez bien ?
GrammaJS> exit
```

**Note : Vous pouvez vérifier tout un fichier avec pour chaque ligne ayant une commande :**
**cat script.verf | gramma-cli -i**

## Client

Exemple simple:

```
CMD> gramma-cli --spell saluti
Le mot saluti innexistant

CMD>
```

Exemple faisant plusiseurs action:

```
CMD> gramma-cli --lemma --morph --suggest --text salut
Morph possible de: salut
 └ >salut/:N:m:s/*
Lemma possible de: salut
 └ salut
Suggestion possible de: salut
 ├ salut
 ├ salit
 ├ salue
 ├ salua
 ├ saluai
 ├ saluts
 ├ salué
 ├ saluât
 ├ salât
 └ salît

CMD>
```

## Serveur

Le serveur supporte les requêtes POST et GET...

Par défaut le port d'écoute est le 2212.

## Les fichiers

grammalecte/*   : Tout le contennu de Grammalecte pour javascript

api.js          : Un warper pour simplifié l'utilisation de Grammalecte

gramma-cli.bat  : Fait juste un appel «node gramma-cli.js .argument(s)»

gramma-cli.js   : Le code principale pour la console

minimist.js     : Une librairie pour simplifier le parssage des arguments

readme.md       : Le fichier que vous lisez (ou pas) actuellement ;)

script.verf     : Exemple de script pour faire des vérifications automatiques

* (sous widows) type script.verf | gramma-cli -i
* (sous linux) cat script.verf | gramma-cli -i

## Utilisation d'une librairie (incluse)

* [Minimist](https://github.com/substack/minimist) => Simplify parser argument