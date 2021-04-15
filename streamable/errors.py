class AuthError(Exception):
    """ Generic auth error """

    pass


class UserNotFoundError(AuthError):
    """ User is not registered on streamable.com """

    pass


class IncorrectPasswordError(AuthError):
    """ Wrong password provided """

    pass
