# Programme de traitement de nombres en C
## Description :

Créez un programme en langage C qui prend des arguments en ligne de commande.
Le programme doit être exécutable de la manière suivante :
`./app 12,23,45,1`

## Fonctionnalités :
- Afficher la suite de nombres passée en paramètre, chaque nombre sur une ligne distincte :
  ```
  12
  23
  45
  1
  ```
- Les nombres saisis sont des entiers positifs.
- Si plus de 20 nombres sont fournis, le programme doit retourner un code d'erreur `2`.

## Options :
- `-n` : Affiche le numéro de ligne avant chaque nombre.
  ```
  1) 12
  2) 23
  ...
  ```
- `-o` : Affiche les nombres triés par ordre décroissant.
- `-v` : Affiche un message avec la version du programme et quitte. Cette option a la plus haute priorité.

### Utilisation des options :
- Les options peuvent être utilisées ensemble dans n'importe quel ordre.
- Exemple d'appels corrects avec options combinées :
  - `./app -n -o 12,23,4`
  - `./app 12,23 -n -o`
  - `./app -o 12,23 -n`
  - `./app -o 12,23 -n --version`
  - 
## Comportements supplémentaires :
- Si aucun nombre n'est fourni, le programme quitte avec un code d'erreur `4`.
- Si deux virgules se suivent dans la liste de nombres, le programme quitte avec un code d'erreur `3`.
- Si autre chose qu'un nombre ou une virgule est fourni, le programme quitte avec un code d'erreur `1`.

## Bonnes pratiques de développement :
- Développer des fonctions booléennes pour vérifier la présence des options :
  - `bool option_linenumber_present()`
  - `bool option_version_present()`
  - `bool option_order_present()`

- Créer des fonctions pour séparer les différentes parties du programme.
- Utiliser des noms de fonctions et de variables explicites.
- Réduire la portée des variables.
- Appliquer le principe SSOT (Single Source of Truth).

## Aide :
- Trouver un moyen pour supprimer un nombre du tableau une fois que vous l'avez affiché.
- Le code suivant peut vous aider

```c
void func(char str[], int tab[]){
    int pos = 0;
    for(int i=0; str[i] != '\0'; i++){
        if(str[i] == ','){
            pos++;
        }
        else if(str[i] >= '0' && str[i] <= '9'){
            tab[pos] = tab[pos]*10 + (str[i] - '0');
        }
    }
}
```