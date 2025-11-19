from math import trunc


def is_hex(string_number):
    """
    Checks if provided string is a Hex number, returns True or False
    :param string_number:   String to check
    :return: True if string can be converted to a number, False otherwise
    """
    result = False
    try:
        result = int(string_number, 16)
    except ValueError:
        pass
    return result

def is_email(address, domain=None):
    """
    Check if provided string is a valid email address.
    If domain is provided, then the address will be checked to belong to it.)
    :param address: Email address (str), i.e. "johndoe@mymail.com".
    :param domain:  Email provider domain (str), i.e. "mymail.com" . If argument exist, the provided address
                    will be checked against it.
    :return:  True or False
    """
    addr = address.lower()
    result = False
    if all(ch in addr for ch in ['@', '.']):
        if domain:
           dom = domain.lower()
           addr_dom = addr.split('@')[1]
           if addr_dom == dom:
               result = True
        else:
            result = True
    return result


    def numbers_to_list(num_list, min_value=None, max_value=None, sort=None, remove_duplicates=True,
                    val_return_type=int):
    """
    Parses a string containing single values or ranges and generates a full, explicit list of them.
    Elements must be separated by commas, values must be in format [min_value]-[max_value]

    Example:
        num_list = "1,3,8, 12-15, 10"
        will produce: [1, 3, 8, 12, 13, 14, 15, 10]
    Optionally, the result list can be sorted and/or duplicate items removed

    :param num_list:            String of values, comma-separated, i.e. "1-5, 7, 9, 11-20"
    :param sort:                Allows to sort the result list. Allowed values: "ascending", "descending" or None (default)
    :param remove_duplicates:   True: Removes duplicated items from the result list
    :param val_return_type:     Type of value to return, i.e. int or str
    :return:    List of elements, in specified data type and format (sorted, duplicate-stripped)
    """
    result = []
    if not isinstance(num_list, list):
        num_list = [num_list]
    for num_item in num_list:
        spl = str(num_item).split(',')
        for i in spl:
            if i.strip().isnumeric():
                if min_value is not None and val_return_type(i) < min_value:
                    return ['error', f"Value {i} is below allowed minimum ({min_value})"]
                if max_value is not None and val_return_type(i) > max_value:
                    return ['error', f"Value {i} is over allowed maximum ({max_value})"]
                result.append(val_return_type(i))
            else:
                i = i.replace('..', '-')
                if '-' in i:
                    itemspl = i.split('-')
                    if len(itemspl) == 2:
                        min_ok = val_return_type(min_value) <= val_return_type(itemspl[0])
                        max_ok = val_return_type(max_value) >= val_return_type(itemspl[1])
                        if min_ok and max_ok:
                            rng = (list(range(int(itemspl[0]), int(itemspl[1]) + 1)))
                            for ritem in rng:
                                result.append(val_return_type(ritem)) # Slower, but generates values of requested type
                        else:
                            return ['error', f"Interval '{i}' exceeds bounds ({min_value}-{max_value})"]

                    else:
                        print(f"ERROR -invalid number of arguments.  Item: '{i}' ")
                        result = None
    if sort:
        if sort is True or str(sort).lower() in ['a', 'ascending', 'up']:
            result = sorted(result)
        elif sort.lower() in ['d', 'descending', 'down']:
            result = sorted(result, reverse=True)
    if remove_duplicates:
        result = list(dict.fromkeys(result))
    return result
