# from fastapi import status
# from fastapi.responses import JSONResponse
#
#
# class Response(JSONResponse):
#     def __init__(self, msg: str, dev: str, status_code: int)
#
# http_exceptions: dict[str, JSONResponse] = {
#     1000: JSONResponse({
#          'Undefined exception',
#     }, status_code = status.HTTP_400_BAD_REQUEST,
#     ),
#
#     1001: HTTPException(
#         status_code = status.HTTP_401_UNAUTHORIZED,
#         detail = 'Token invalid, expired, or belongs to unknown user',
#         headers = {'WWW-Authenticate': 'Bearer'},
#     ),
#
#     1003: HTTPException(
#         status_code = status.HTTP_403_FORBIDDEN,
#         detail = 'Access denied',
#     ),
#
#     1004: HTTPException(
#         status_code = status.HTTP_404_NOT_FOUND,
#         detail = 'Not found',
#     ),
#
#     1005: HTTPException(
#         status_code = 400,
#         detail = 'Resource already exist'
#     ),
#
#     1006: HTTPException(
#         status_code = 400,
#         detail = 'Hub not initialized'
#     ),
#
#     1022: HTTPException (
#         status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
#         detail = 'Data in invalid format'
#     )
# }
