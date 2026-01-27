STATES_COMPTEUR = [['blue', 'blue', 'blue', 'yellow'],
              ['yellow', 'blue', 'blue', 'black', 'white', 'black'],
              ['black', 'red', 'blue', 'white']]

CONTIENT = [True,True,False]

COUNT = ['3','2','1']

STATES = [['gold', 'red', 'red', 'blue', 'yellow', '', ''],
          ['gold', 'blue', 'blue', 'yellow', '', '', ''],
          ['gold', 'red', 'white', 'blue', 'yellow', 'white', 'black'],
          ['silver', 'red', 'red', 'blue', 'yellow', '', ''],
          ['silver', 'yellow', 'red', 'blue', 'yellow', 'black', ''],
          ['silver', 'red', 'red', 'blue', '', '', ''],
          ['bronze', 'red', 'red', 'blue', 'yellow', '', ''],
          ['bronze', 'red', 'red', 'blue', 'yellow', 'black', ''],
          ['bronze', 'red', 'red', 'blue', 'blue', 'black', 'white'],
          ['bronze', 'yellow', 'white', 'blue', 'yellow', 'black', 'white']]

KEYS = ['first',
        'second',
        'fourth',
        'second',
        'first',
        'first',
        'first',
        'first',
        'third',
        'sixth']

PROLOG_FILE = "C:/Users/pofor/S7/APP1/S7APP1/Prolog/cristaux.pl"


from swiplserver import PrologMQI
from Crystal import remove_crystal, clean_state, python_list_to_prolog_list

def test_crystal_states():
    for i, state in enumerate(STATES):

        result = remove_crystal([state])
        assert result == KEYS[i]

def test_contient():
    for i, state_compteur in enumerate(STATES_COMPTEUR):
        list_state = python_list_to_prolog_list(state_compteur)

        with PrologMQI() as mqi:
            with mqi.create_thread() as prolog:
                prolog.query(f"consult('{PROLOG_FILE}').")
                query_str = f"contient(yellow, {list_state})."
                result = prolog.query(query_str)

        assert bool(result) == bool(CONTIENT[i])

def test_compteur():
    for i, state_compteur in enumerate(STATES_COMPTEUR):
        list_state = python_list_to_prolog_list(state_compteur)

        with PrologMQI() as mqi:
            with mqi.create_thread() as prolog:
                prolog.query(f"consult('{PROLOG_FILE}').")
                query_str = f"compte_couleur(blue, {list_state}, N)."
                result = prolog.query(query_str)

        assert int(result[0]["N"]) == int(COUNT[i])

#Utilisé Chatgpt pour le main. Chatgpt version 5.2. Prompt: Fait une fonction
#main pour les fonctions suivantes dans le but de tester: *copier-coller des 3 fonctions ci-haut

def main():
    tests = [
        ("test_contient", test_contient),
        ("test_crystal_states", test_crystal_states),
        ("test_compteur", test_compteur),
    ]

    print("=== Running tests ===")
    passed = 0

    for name, fn in tests:
        try:
            fn()
            print(f"[OK]   {name}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {name}\n  -> {e}")
            raise  # stop direct
        except Exception as e:
            print(f"[ERROR] {name}\n  -> {type(e).__name__}: {e}")
            raise

    print(f"\n=== Done: {passed}/{len(tests)} passed ===")


if __name__ == "__main__":
    main()









