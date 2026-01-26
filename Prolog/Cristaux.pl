contient(E, [E|_]).
contient(E, [_|Xs]) :- contient(E, Xs).

compte_couleur(_, [], 0).
compte_couleur(E, [E|Xs], N) :-
    compte_couleur(E, Xs, N1),
    N is N1 + 1.
compte_couleur(E, [X|Xs], N) :-
    X \= E,
    compte_couleur(E, Xs, N).

cristaux3([C1,C2,C3], [C1,C2,C3]).
cristaux4([C1,C2,C3,C4], [C1,C2,C3,C4]).
cristaux5([C1,C2,C3,C4,C5], [C1,C2,C3,C4,C5]).
cristaux6([C1,C2,C3,C4,C5,C6], [C1,C2,C3,C4,C5,C6]).

enlever_position([S,C1,C2,C3], P) :-
    enlever_position3([S,C1,C2,C3], P).

enlever_position([S,C1,C2,C3,C4], P) :-
    enlever_position4([S,C1,C2,C3,C4], P).

enlever_position([S,C1,C2,C3,C4,C5], P) :-
    enlever_position5([S,C1,C2,C3,C4,C5], P).

enlever_position([S,C1,C2,C3,C4,C5,C6], P) :-
    enlever_position6([S,C1,C2,C3,C4,C5,C6], P).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 3 cristaux
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

enlever_position3([_Serrure|Queue], Position) :-
    cristaux3(Queue, [C1,C2,C3]),
    (
        \+ contient(red, [C1,C2,C3]) ->
            Position = second
    ;   C3 = white ->
            Position = third
    ;   compte_couleur(blue, [C1,C2,C3], NbBleu),
        NbBleu > 1 ->
            ( C3 = blue -> Position = third
            ; C2 = blue -> Position = second
            ;               Position = first
            )
    ;   Position = first
    ).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 4 cristaux
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

enlever_position4([Serrure|Queue], Position) :-
    cristaux4(Queue, [C1,C2,C3,C4]),
    (
        Serrure = silver,
        compte_couleur(red, [C1,C2,C3,C4], NbRouge),
        NbRouge > 1 ->
            ( C4 = red -> Position = fourth
            ; C3 = red -> Position = third
            ; C2 = red -> Position = second
            )

    ;   C4 = yellow,
        \+ contient(red, [C1,C2,C3,C4]) ->
            Position = first

    ;   compte_couleur(blue, [C1,C2,C3,C4], NbBleu),
        NbBleu =:= 1 ->
            Position = first

    ;   compte_couleur(yellow, [C1,C2,C3,C4], NbJaune),
        NbJaune > 1 ->
            Position = fourth

    ;   Position = second
    ).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 5 cristaux
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

enlever_position5([Serrure|Queue], Position) :-
    cristaux5(Queue, [C1,C2,C3,C4,C5]),
    (
        C5 = black,
        Serrure = gold ->
            Position = fourth

    ;   compte_couleur(red, [C1,C2,C3,C4,C5], NbRouge),
        NbRouge =:= 1,
        compte_couleur(yellow, [C1,C2,C3,C4,C5], NbJaune),
        NbJaune > 1 ->
            Position = first

    ;   compte_couleur(black, [C1,C2,C3,C4,C5], NbNoir),
        NbNoir =:= 0 ->
            Position = second

    ;   Position = first
    ).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 6 cristaux
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

enlever_position6([Serrure|Queue], Position) :-
    cristaux6(Queue, [C1,C2,C3,C4,C5,C6]),
    (
        compte_couleur(yellow, [C1,C2,C3,C4,C5,C6], NbJaune),
        NbJaune =:= 0,
        Serrure = bronze ->
            Position = third

    ;   compte_couleur(yellow, [C1,C2,C3,C4,C5,C6], NbJaune2),
        NbJaune2 =:= 1,
        compte_couleur(white, [C1,C2,C3,C4,C5,C6], NbBlanc),
        NbBlanc > 1 ->
            Position = fourth

    ;   compte_couleur(red, [C1,C2,C3,C4,C5,C6], NbRouge),
        NbRouge =:= 0 ->
            Position = sixth

    ;   Position = first
    ).
