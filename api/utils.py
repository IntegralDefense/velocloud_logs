from datetime import datetime
import json

# TODO - NOT FULLY TESTED YET!!!


def serialize_json(obj, _format=None):
    """
    Turns datetime objects in JSON into strings which can be then be
    serialized by json.dumps.

    This will also check strings to see if any json objects are
    encapsulated and will convert them to dictionaries, lists, etc.
    in order to investigate them.
        For example:  {'lastLogin': datetime.datetime(*args)} will
        become {'lastLogin': 'Monday, Feb ......' }
        For example:   { 'hello': "{'inside_key': 'inside_value',
        'inside_key_2': 'inside_value_2'}"} will become { 'hello': 
        {'inside_key': 'inside_value', 'inside_key_2': 'inside_value_2'}}

    Parameters
    ----------
    obj: any object type
        The object to be inspected
    format: str
        Format for the datetime object to be represented as when
        it is converted to a string. If None, then datetime.ctime()
        will be used instead.

    Returns
    ----------
    Depends on the original object.

    Raises
    ----------
    ValueError
        Raised if object is not JSON serializable and is not a datetime
        object.
    """

    # Base cases
    serializable_types = (int, float, bool)
    if (isinstance(obj, serializable_types)) or (obj is None):
        return obj
    elif isinstance(obj, datetime):
        if format:
            return obj.strftime(_format)
        else:
            return obj.ctime()

    # Recursive cases
    elif isinstance(obj, str):
        try:
            # To catch any json elements that might be encased by a string
            return serialize_json(json.loads(obj), _format=_format)
        except Exception:
            # Just return the string
            return obj

    elif isinstance(obj, list):
        if obj:
            return [serialize_json(each, _format=_format) for each in obj]
        else:
            return []

    elif isinstance(obj, dict):
        new_obj = {key: value for (key, value) in obj.items()}
        for key in new_obj.keys():
            new_obj[key] = serialize_json(new_obj[key], _format=_format)
        return new_obj

    elif isinstance(obj, set):
        return {serialize_json(each, _format=_format) for each in obj}

    else:
        raise ValueError("Not a valid JSON element.")
