from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse, JSONResponse
from exceptions.Internal import InternalException


http_codes = {
    1000: 400,
    1001: 401,
    1003: 403,
    1004: 404,
    1005: 400,
    1006: 400,
    1022: 422,
}

def internal(request: Request, exc: InternalException) -> Response:
    return JSONResponse({
        'msg': exc.msg,
        'detail': exc.debug
    }, status_code = http_codes.get(exc.code) or 400)

def setup(app: FastAPI):
    app.exception_handler(InternalException)(internal)
