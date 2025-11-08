
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