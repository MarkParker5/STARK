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
    # docs_url = None,
)

# app.mount('/static', StaticFiles(directory = 'view/static'), name = 'static')

api = APIRouter(prefix = '/api')
api.include_router(endpoints.hub.router)
api.include_router(endpoints.rooms.router)
api.include_router(endpoints.devices.router)
app.include_router(api)

endpoints.admin.setup(app)

# @app.get('/docs', include_in_schema = False)
# async def custom_swagger_ui_html():
#     return endpoints.docs.get_swagger_ui_html()
