# Plan de tests unitaires – Cristaux (Prolog + Python)

Objectif :  
Valider que la logique Prolog (`cristaux.pl`) retournent les résultats attendus de:
- la sélection du cristal à retirer
- la présence d’une couleur dans une liste 
- le comptage d’une couleur dans une liste


---

## A. Tests – `remove_crystal(state)` (sélection de la clé)

### Test 1 

**Description**  
La porte est en or. La séquence de cristaux est : `red, red, blue, yellow`.

**Entrées**
- `state = ['gold', 'red', 'red', 'blue', 'yellow', '', '']`

**Résultat attendu**
- `first`

---

### Test 2 

**Description**  
La porte est en or. La séquence de cristaux est : `blue, blue, yellow`.

**Entrées**
- `state = ['gold', 'blue', 'blue', 'yellow', '', '', '']`

**Résultat attendu**
- `second`

---

### Test 3 

**Description**  
La porte est en or. La séquence de cristaux est : `red, white, blue, yellow, white, black`.

**Entrées**
- `state = ['gold', 'red', 'white', 'blue', 'yellow', 'white', 'black']`

**Résultat attendu**
- `fourth`

---

### Test 4 

**Description**  
La porte est en argent. La séquence de cristaux est : `red, red, blue, yellow`.

**Entrées**
- `state = ['silver', 'red', 'red', 'blue', 'yellow', '', '']`

**Résultat attendu**
- `second`

---

### Test 5 

**Description**  
La porte est en argent. La séquence de cristaux est : `yellow, red, blue, yellow, black`.

**Entrées**
- `state = ['silver', 'yellow', 'red', 'blue', 'yellow', 'black', '']`

**Résultat attendu**
- `first`

---

### Test 6 

**Description**  
La porte est en argent. La séquence de cristaux est : `red, red, blue`.

**Entrées**
- `state = ['silver', 'red', 'red', 'blue', '', '', '']`

**Résultat attendu**
- `first`

---

### Test 7 

**Description**  
La porte est en bronze. La séquence de cristaux est : `red, red, blue, yellow`.

**Entrées**
- `state = ['bronze', 'red', 'red', 'blue', 'yellow', '', '']`

**Résultat attendu**
- `first`

---

### Test 8 

**Description**  
La porte est en bronze. La séquence de cristaux est : `red, red, blue, yellow, black`.

**Entrées**
- `state = ['bronze', 'red', 'red', 'blue', 'yellow', 'black', '']`

**Résultat attendu**
- `first`

---

### Test 9 

**Description**  
La porte est en bronze. La séquence de cristaux est : `red, red, blue, blue, black, white`.

**Entrées**
- `state = ['bronze', 'red', 'red', 'blue', 'blue', 'black', 'white']`

**Résultat attendu**
- `third`

---

### Test 10 

**Description**  
La porte est en bronze. La séquence de cristaux est : `yellow, white, blue, yellow, black, white`.

**Entrées**
- `state = ['bronze', 'yellow', 'white', 'blue', 'yellow', 'black', 'white']`

**Résultat attendu**
- `sixth`

---

## B. Tests – `contient()`

> Requête Prolog utilisée : `contient(yellow, List).`

### Test 11 – `yellow` présent (cas 1)

**Description**  
La liste contient au moins un cristal `yellow`.

**Entrées**
- `List = ['blue', 'blue', 'blue', 'yellow']`

**Résultat attendu**
- `True`

---

### Test 12 – `yellow` présent (cas 2)

**Description**  
La liste contient `yellow` (même si plusieurs autres couleurs sont présentes).

**Entrées**
- `List = ['yellow', 'blue', 'blue', 'black', 'white', 'black']`

**Résultat attendu**
- `True`

---

### Test 13 – `yellow` absent

**Description**  
La liste ne contient aucun `yellow`.

**Entrées**
- `List = ['black', 'red', 'blue', 'white']`

**Résultat attendu**
- `False`

---

## C. Tests – `compte_couleur` (comptage d’une couleur)

> Requête Prolog utilisée : `compte_couleur(blue, List, N).`

### Test 14 – 3 bleus

**Description**  
La liste contient exactement trois `blue`.

**Entrées**
- `List = ['blue', 'blue', 'blue', 'yellow']`

**Résultat attendu**
- `N = 3`

---

### Test 15 – 2 bleus

**Description**  
La liste contient exactement deux `blue`.

**Entrées**
- `List = ['yellow', 'blue', 'blue', 'black', 'white', 'black']`

**Résultat attendu**
- `N = 2`

---

### Test 16 – 1 bleu

**Description**  
La liste contient exactement un `blue`.

**Entrées**
- `List = ['black', 'red', 'blue', 'white']`

**Résultat attendu**
- `N = 1`

---

