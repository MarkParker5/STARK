import os, sys

root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root)

import uvicorn
from API.main import app


if __name__ == '__main__':
    uvicorn.run('main:app', host = '0.0.0.0', port = 8001, reload = True, reload_dirs=[root,])
