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
- Les nombres sont des entiers positifs, la valeur `0` est acceptée. On admet que chaque nombre tient dans un `int`.
- Les nombres sont donnés dans **un seul** argument, séparés par des virgules, sans espace.
- Il peut y avoir au maximum 20 nombres.

## Options :
- `-n` : Affiche le numéro de ligne avant chaque nombre.
  ```
  1) 12
  2) 23
  ...
  ```
- `-o` : Affiche les nombres triés par ordre décroissant.
- `-v` ou `--version` : Affiche un message avec la version du programme et quitte avec le code de retour `0`. Cette option a la plus haute priorité : si elle est présente, les autres arguments sont ignorés, même s'ils contiennent une erreur.

### Utilisation des options :
- Les options peuvent être utilisées ensemble dans n'importe quel ordre.
- Exemple d'appels corrects avec options combinées :
  - `./app -n -o 12,23,4`
  - `./app 12,23 -n -o`
  - `./app -o 12,23 -n`
  - `./app -o 12,23 -n --version`
  - `./app -v`
- Avec les options `-n` et `-o` ensemble, le numéro est celui de la ligne affichée et non la position du nombre dans la liste de départ :
  ```
  ./app -n -o 12,23,4
  1) 23
  2) 12
  3) 4
  ```

## Erreurs :
Dans tous les cas d'erreur, le programme quitte avec le code de retour `1` :
- aucun nombre n'est fourni ;
- plus de 20 nombres sont fournis ;
- il manque un nombre avant ou après une virgule ;
- la liste contient autre chose que des chiffres et des virgules ;
- une option est inconnue ;
- plusieurs listes de nombres sont fournies.

Exemples d'appels qui retournent `1` :

| Appel | Pourquoi |
|---|---|
| `./app` | aucun nombre |
| `./app -n` | aucun nombre |
| `./app 1,,2` | il manque un nombre entre les deux virgules |
| `./app ,1,2` | il manque un nombre avant la première virgule |
| `./app 1,2,` | il manque un nombre après la dernière virgule |
| `./app 1,a,3` | `a` n'est pas un chiffre |
| `./app -x 1,2` | l'option `-x` n'existe pas |
| `./app -5,3` | un argument qui commence par `-` est une option, et elle n'existe pas |
| `./app 1,2 3,4` | deux listes de nombres |

Si tout se passe bien, le programme retourne `0`.

Le programme doit être robuste : quels que soient les arguments reçus, il affiche le résultat demandé ou il quitte avec le code `1`.

## Bonnes pratiques de développement :
- Développer des fonctions booléennes pour vérifier la présence des options :
  - `bool option_linenumber_present(int argc, char* argv[])`
  - `bool option_version_present(int argc, char* argv[])`
  - `bool option_order_present(int argc, char* argv[])`
- Ces trois fonctions font presque la même chose : pour ne pas dupliquer le code, elles peuvent appeler une fonction commune qui cherche une option donnée dans les arguments.

- Créer des fonctions pour séparer les différentes parties du programme.
- Utiliser des noms de fonctions et de variables explicites.
- Réduire la portée des variables.
- Appliquer le principe SSOT (Single Source of Truth).

## Aide :
- Pour l'option `-o` : trouver un moyen pour supprimer un nombre du tableau une fois que vous l'avez affiché.
- Le code suivant est un indice sur le principe pour extraire les nombres de la chaîne de caractères. Il ne gère aucune erreur et ne peut pas être utilisé tel quel : vous devez l'adapter.

```c
void extract_numbers(char str[], int tab[]){
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

## Tests :
Des tests automatiques sont fournis pour contrôler votre programme. Chaque test lance `./app` avec des arguments, puis contrôle ce qu'il affiche et son code de retour.

Pour compiler le programme et lancer les tests :

```console
make test
```

Chaque ligne correspond à un test : `OK` s'il est réussi, `ÉCHEC` sinon, avec la commande qui a été lancée.

```console
Tests du programme ./app (14 tests)
──────────────────────────────────────────────────────────────────────────────
  OK     affiche un nombre par ligne              ./app 12,23,45,1
  OK     option -n : numéro devant chaque nombre  ./app -n 12,23,45,1
  ÉCHEC  option -o : ordre décroissant            ./app -o 12,23,4
  ...
```

Pour les premiers tests en échec, le détail montre ce qui était attendu et ce que votre programme a fait :

```console
ÉCHEC : option -o : ordre décroissant
Commande : ./app -o 12,23,4

Affichage attendu :
    23
    12
    4
Affichage de votre programme :
    12
    23
    4
La première différence est à la ligne 1.
```

Pour rejouer un test à la main, copiez sa commande dans le terminal. La commande `echo $?` affiche ensuite le code de retour :

```console
./app 1,,2
echo $?
1
```

Si `make test` indique que pytest n'est pas installé :

```console
pip3 install pytest --break-system-packages
```

Les tests ne contrôlent pas tout le cahier des charges : un programme qui réussit tous les tests peut encore contenir des erreurs.

Ne modifiez pas les fichiers du dossier `tests/`.
