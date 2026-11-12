import json

# Backend responses are untrusted: bound what we are willing to materialise.
MAX_LIST_ITEMS = 5000


def cast_to_list_of_type(result_as_string, t_type: type, max_items: int = MAX_LIST_ITEMS) -> list:
    result_list = []
    json_array = json.loads(result_as_string)
    if not isinstance(json_array, list) or len(json_array) > max_items:
        raise ValueError(f"expected a list of at most {max_items} items")

    for json_obj in json_array:
        if not isinstance(json_obj, dict):
            raise ValueError("expected a list of objects")
        obj = t_type(**json_obj)
        result_list.append(obj)
        #print('generic parse call', obj)
    return result_list

def cast_to_type(string_object: str, t_type: type):
    json_obj = json.loads(string_object)
    if not isinstance(json_obj, dict):
        raise ValueError("expected a JSON object")
    obj = t_type(**json_obj)
    return obj