from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles

from . import models
from . import endpoints
from . import dependencies


models.Base.metadata.create_all(bind = dependencies.database.engine)

description = '''
[**Admin**](/admin)

[**GitHub**](https://github.com/MarkParker5/ArchieCloud)

[**FastAPI**](https://fastapi.tiangolo.com)
'''

app = FastAPI(
    title = 'Archie Hub',
    description = description,
    version = '0.0.1',
    swagger_ui_parameters = {
        'syntaxHighlight.theme': 'obsidian',
        'docExpansion': 'none',
    }
)

api = APIRouter(prefix = '/api')
api.include_router(endpoints.house.router)
api.include_router(endpoints.hub.router)
api.include_router(endpoints.room.router)
api.include_router(endpoints.device.router)
app.include_router(api)
app.include_router(endpoints.ws.router)

endpoints.admin.setup(app)
