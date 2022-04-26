from fastapi import HTTPException, status


credentials = HTTPException(
    status_code = status.HTTP_401_UNAUTHORIZED,
    detail = 'Incorrect username or password',
    headers = {'WWW-Authenticate': 'Bearer'},
)

invalid_token = HTTPException(
    status_code = status.HTTP_401_UNAUTHORIZED,
    detail = 'Token invalid or expired',
    headers = {'WWW-Authenticate': 'Bearer'},
)

access_denied = HTTPException(
    status_code = status.HTTP_403_FORBIDDEN,
    detail = 'Access denied',
)

not_found = HTTPException(
    status_code = status.HTTP_404_NOT_FOUND,
    detail = 'Not found',
)

already_exist = HTTPException(
    status_code = 400,
    detail = 'Resource already exist'
)
