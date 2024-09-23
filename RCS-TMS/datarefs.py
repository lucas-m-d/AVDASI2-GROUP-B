import json

## this here does use chatGPT - a quick way of adding datarefs

class DataRef:
    def __init__(self, **kwargs):
        with open('datarefs.json', 'r') as f:
            datarefs = json.load(f)
        print(datarefs)
        self.schema = datarefs['attributes']
        
        for key, value in kwargs.items():
            if key in self.schema:
                expected_type = self.schema[key]
                if not self.validate_type(value, expected_type):
                    raise TypeError(f'Expected {expected_type}, got {value} instead')
                setattr(self, key, value)
            else:
                #setattr(self, key, None)
                raise ValueError(f"Unexpected attribute: '{key}'")
        
        passedKeys = [i for i, _ in kwargs.items()]
        for key in self.schema:
            if key not in passedKeys:
                setattr(self, key, None)
                


    def validate_type(self, value, expected_type):
        type_map = {
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
        }
        return isinstance(value, type_map.get(expected_type))

    def __repr__(self):
        return f"DynamicDataRef({self.__dict__})"