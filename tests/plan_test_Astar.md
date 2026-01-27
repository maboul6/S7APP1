# Plan de test – Algorithme A*

**Objectif :**  
Valider que l’algorithme `a_star_search` :
- Trouve un chemin valide entre l’entrée `S` et la sortie `E`,
- Ne traverse pas les murs,
- Temps de calcul adéquat.

---

## Contexte

- Algorithme testé : `a_star_search` 
- Labyrinthe utilisé : `mazeMedium_0`

---

## Test 1 – Existence d’un chemin valide

**Description**  
L’algorithme A* doit être capable de trouver un chemin reliant l’entrée `S` à la sortie `E`.

**Entrées**
- Labyrinthe : `mazeMedium_0`

**Procédure**
- Charger le labyrinthe depuis le fichier CSV.
- Lancer `a_star_search(maze)`.
- Vérifier que le chemin retourné n’est pas nul.

**Résultats attendus**
- `path != None`


---

## Test 2 – Validation des positions initiale et finale

**Description**  
Le premier point du chemin doit correspondre à la position de départ `S`, et le dernier point à la position d’arrivée `E`.

**Entrées**
- Labyrinthe : `mazeMedium_0`
- Chemin retourné par `a_star_search`

**Procédure**
- Identifier la position de `S` via `find_symbol(maze, "S")`.
- Identifier la position de `E` via `find_symbol(maze, "E")`.
- Convertir les coordonnées `(row, col)` en `(x, y)`.
- Comparer avec les extrémités du chemin.

**Résultats attendus**
- `path[0] == position(S)`
- `path[-1] == position(E)`

---

## Test 3 – Absence de collision avec les murs

**Description**  
Le chemin généré ne doit jamais traverser une cellule représentant un mur.

**Entrées**
- Chemin retourné par `a_star_search`
- Grille binaire issue de `convert_maze`

**Procédure**
- Convertir le labyrinthe en grille binaire (`0` = libre, `1` = mur).
- Pour chaque point `(x, y)` du chemin, vérifier la valeur de la cellule.

**Résultats attendus**
- Pour tout `(x, y)` du chemin : `grid01[y][x] == 0`

---

## Test 4 – Performance temporelle (temps de calcul)

**Description**  
Le temps d’exécution de l’algorithme A* doit rester suffisamment faible pour permettre une exécution fluide.

**Entrées**
- Labyrinthe : `mazeMedium_0`

**Procédure**
- Mesurer le temps d’exécution avec `time.perf_counter()`.
- Calculer le temps écoulé en millisecondes.

**Résultats attendus**
- Temps d’exécution raisonnable < 50 ms
---
