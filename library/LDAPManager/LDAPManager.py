import ldap
import library.config.peachSharedConfig


def check_login(username, password):
    """
    Returns whether the given credentials (username and password) are valid credential for the dkfz AD (LDAP) Server. 
    At the moment it will only be checked in the "ad" group. (username@ad, password)
    TODO: Also look in all other groups

    Example usage:
    >>> check_login("thename", "mysupersecretpassword")
    1

    @param username: The username to check
    @param password: The password to check 
    @return: 0, 1 or 2 (0 = valid combination, 1 = wrong combination, 2 = any other error, e.g. server down)
    """
    if len(username) <= 0 or len(password) <= 0:
        return 1
        

    connect = ldap.open(library.config.peachSharedConfig.get_ldap_server())
    try:
        connect.simple_bind_s(library.config.peachSharedConfig.get_ldap_dn(username), password)
        return 0
    except ldap.LDAPError:
        connect.unbind_s()
        return 1
    except:
        return 2