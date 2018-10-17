# Client/Serveur de Grammalecte pour NodeJS

## Informations

Il y a trois modes de fonctionnement : client / client interactif / serveur.

* Client interactif: `gramma-cli -i`.
* Client: `gramma-cli --command \"mot/texte\"`.
* Serveur: lancé avec la commande `gramma-cli --server --port NumPort`.

## Installation

> npm install grammalecte-cli -g

## Commandes

| Commande  | Argument | Description                                                   |
| --------- | -------- | ------------------------------------------------------------- |
| help      |          | Affiche les informations que vous lisez ;)                    |
| perf      | on/off   | Permet d’afficher le temps d’exécution des commandes.         |
| json      | on/off   | Réponse en format json.                                       |
| exit      |          | Client interactif : permet de le quitter.                     |
| text      | texte    | Client / Server: Définir un texte pour plusieurs actions.     |
| format    | texte    | Permet de mettre en forme le texte.                           |
| check     | texte    | Vérifie la grammaire et l’orthographe d'un texte.             |
| lexique   | texte    | Affiche le lexique du texte.                                  |
| spell     | mot      | Vérifie l’existence d'un mot.                                 |
| suggest   | mot      | Suggestion des orthographes possible d’un mot.                |
| morph     | mot      | Affiche les informations pour un mot.                         |
| lemma     | mot      | Donne le lemme d’un mot.                                      |
| gceoption | +/-name  | Définit les options à utiliser par le correcteur grammatical. |
| tfoption  | +/-name  | Définit les options à utiliser par le formateur de texte.     |

## Client interactif

Le mode interactif est un mode question/réponse. Pour le lancer vous devez saisir `gramma-cli -i`.

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
Bienvenue sur Grammalecte pour NodeJS!!!
GrammaJS> format
> salut,les copains!!!
> vous allez bien ?
> /format
Mise en forme:
salut, les copains!!!
vous allez bien ?
GrammaJS> exit
```

## Client

Exemple simple:

```
CMD> gramma-cli --spell saluti
Le mot saluti innexistant

CMD>
```

Exemple faisant plusieurs actions:

```
CMD> gramma-cli --lemma --morph --suggest --text salut
Morph possible de: salut
 └ >salut/:N:m:s/*
Lemme possible de: salut
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

Par défaut le port d’écoute est le 2212, pour le changer utilisez l’argument `--port` lors du lancement.

## Les fichiers

* bin/gramma-cli.bat  : Fait juste un appel `node gramma-cli.js argument(s)`
* bin/gramma-cli.js   : Le code principal pour la console
* data/script.gramma  : Exemple de script pour faire des vérifications automatiques
  * (sous widows) `type script.gramma | gramma-cli -i`
  * (sous linux)  `cat script.gramma  | gramma-cli -i`
* lib/minimist.js     : Une librairie pour simplifier la gestion des arguments
* package.json        : Fichier d’information pour npm
* readme.md           : Le fichier que vous lisez (ou pas) actuellement ;)

## Utilisation d'une librairie (incluse)

* [Minimist](https://github.com/substack/minimist) => Simplify parser argument
