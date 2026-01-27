# Test de validation

Objectif : Tester les intégrations des différents modules ensemble, et valider que l'agent se comporte comme prévu dans différents labyrinthes.
Problèmes connus : la logique floue ne fonctionne pas pour l'évitement d'obstacles, le joueur peut parfois rester bloqué à cause de cela.

## mazeSmall_0 :
  - trouver le chemin A* : ✓
  - La logique floue suit l'objectif : ✓
  - La logique floue évite les murs : ✓
  - Labyrinthe complété : ✓

## mazeSmall_1 :
  - trouver le chemin A* : ✓
  - La logique floue suit l'objectif : ✓
  - La logique floue évite les murs : ✓
  - La logique floue évite les obstacles : X
  - Labyrinthe complété : X (dépend des positions des obstacles)

## mazeSmall_2 :
  - trouver le chemin A* : ✓
  - La logique floue suit l'objectif : ✓
  - La logique floue évite les murs : ✓
  - La logique floue évite les obstacles : X
  - Tue tous les monstres : ✓
  - Ouvre toutes les portes : ✓
  - Labyrinthe complété : X (dépend des positions des obstacles)

## mazeLarge_2 :
  - trouver le chemin A* : ✓
  - La logique floue suit l'objectif : ✓
  - La logique floue évite les murs : ✓
  - La logique floue évite les obstacles : X
  - Tue tous les monstres : ✓
  - Ouvre toutes les portes : ✓
  - Labyrinthe complété : X