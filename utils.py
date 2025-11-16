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


def numbers_to_list(num_list, val_type=int, sort=None, remove_duplicates=True):
    result = []
    if not isinstance(num_list, list):
        num_list = [num_list]
    for num_item in num_list:
        spl = str(num_item).split(',')
        for i in spl:
            if i.strip().isnumeric():
                result.append(val_type(i))
            else:
                i = i.replace('..', '-')
                if '-' in i:
                    itemspl = i.split('-')
                    if len(itemspl) == 2:
                        rng = (list(range(int(itemspl[0]), int(itemspl[1]) + 1)))
                        for ritem in rng:
                            result.append(val_type(ritem))
                    else:
                        print(f"ERROR -invalid number of arguments.  Item: '{i}' ")
                        result = None

            # print(result)

    if sort:
        if sort is True or str(sort).lower() in ['a', 'ascending', 'up']:
            result = sorted(result)
        elif sort.lower() in ['d', 'descending', 'down']:
            result = sorted(result, reverse=True)

    if remove_duplicates:
        result = list(dict.fromkeys(result))


    return result

if __name__ == "__main__":
    r = numbers_to_list(["3,6, 7,11-23, 32..43", 22, "29-33"], sort=True, remove_duplicates=True)
    print(r)