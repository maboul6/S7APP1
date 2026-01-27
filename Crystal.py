from swiplserver import PrologMQI
import ast
PROLOG_FILE = "C:/Users/pofor/S7/APP1/S7APP1/Prolog/cristaux.pl"

def clean_state(state):
    state = state[0]
    cleaned = []
    for item in state:
        if item in ("", None, "NULL"):
            continue
        cleaned.append(str(item))
    return cleaned

def python_list_to_prolog_list(py_list):
    items = []
    for x in py_list:
        x = str(x).replace("'", "''")
        items.append(f"'{x}'")
    return "[" + ",".join(items) + "]"

def remove_crystal(state):
    cool_state = clean_state(state)
    prolog_list = python_list_to_prolog_list(cool_state)

    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog:
            prolog.query(f"consult('Prolog/Cristaux.pl').")
            #prolog.query(f"consult('{PROLOG_FILE}').")
            query_str = f"enlever_position({prolog_list}, P)."

            print("STATE repr:", repr(state))
            print("QUERY repr:", repr(query_str))

            result = prolog.query(query_str)

            if not result:
                raise ValueError(f"Aucune solution Prolog pour: {query_str}")

            return result[0]["P"]
