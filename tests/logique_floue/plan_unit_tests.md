# Plan de tests unitaires – Logique floue
Objectif :  
Valider que la fonction `call_fuzzy_logic` retourne la bonne action finale en fonction
de la position du goal et de la proximité des murs.

---

## Test 1 – Goal à droite, aucun mur proche

**Description**  
Le goal est situé à droite du joueur. Aucun mur n’est proche dans aucune direction.

**Entrées**
- `gdx > 0`
- `gdy ≈ 0`
- Distances aux murs : `u = d = l = r = inf`

**Résultat attendu**
- `Action.RIGHT`

---

## Test 2 – Goal à gauche, aucun mur proche

**Description**  
Le goal est situé à gauche du joueur. Aucun mur n’est proche.

**Entrées**
- `gdx < 0`
- `gdy ≈ 0`
- Distances aux murs : `u = d = l = r = inf`

**Résultat attendu**
- `Action.LEFT`

---

## Test 3 – Goal en bas, aucun mur proche

**Description**  
Le goal est situé en bas du joueur. Aucun mur n’est proche.

**Entrées**
- `gdx ≈ 0`
- `gdy > 0`
- Distances aux murs : `u = d = l = r = inf`

**Résultat attendu**
- `Action.DOWN`

---

## Test 4 – Goal en haut, aucun mur proche

**Description**  
Le goal est situé en haut du joueur. Aucun mur n’est proche.

**Entrées**
- `gdx ≈ 0`
- `gdy < 0`
- Distances aux murs : `u = d = l = r = inf`

**Résultat attendu**
- `Action.UP`

---

## Test 5 – Goal à droite MAIS mur à droite très proche (évitement)

**Description**  
Le goal est à droite, mais un mur est très proche à droite.  
La logique floue doit prioriser l’évitement du mur.

**Entrées**
- `gdx > 0`
- Mur à droite très proche : `r` petit, `l` grand
- Autres murs loin : `u = d = inf`

**Résultat attendu**
- `Action.LEFT`  
- Justification : règle d’évitement `wallDx['right'] → moveX['left']`

---

## Test 6 – Goal en haut MAIS mur en haut très proche (évitement)

**Description**  
Le goal est en haut, mais un mur est très proche au-dessus du joueur.  
La logique floue doit forcer un mouvement vers le bas.

**Entrées**
- `gdy < 0`
- Mur en haut très proche : `u` petit, `d` grand
- Autres murs loin : `l = r = inf`

**Résultat attendu**
- `Action.DOWN`  
- Justification : règle d’évitement `wallDy['up'] → moveY['down']`

---

