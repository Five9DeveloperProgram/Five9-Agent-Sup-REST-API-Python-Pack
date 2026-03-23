class Five9DuplicateLoginError(Exception):
    """Raised when a session-start request is rejected because the user is
    already logged in on another session.

    Callers should log out the existing session and retry.
    """