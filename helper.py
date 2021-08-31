import os, config

def getClass(name):
    str = f'''
from Command import Command                     #   import parent class

class {name} (Command):
    def start(self, string):                    #   main method
        pass
    '''
    return str.strip()

def getCommand(name, parent, bg):
    str = f'''
from .{parent} import *
from Command import Response
################################################################################
{f"@{parent}.background(answer = '', voice = '')" if bg else ''}
def method(params{', finish_event' if bg else ''}):
    voice = text = ''
    {'finish_event.set()' if bg else ''}
    return Response(text = text, voice = voice)

keywords = {{}}
patterns = []
{name} = {parent}('{name}', keywords, patterns)
{name}.setStart(method)
    '''
    return str.strip()

def makeModule(name):
    path = f'{config.path}/{name}'
    if os.path.isdir(path): return
    os.mkdir(path)
    with open(path+'/'+name+'.py', 'w+') as f:
        f.write(getClass(name))
    with open(config.path+'/modules.py', 'a+') as f:
        f.write(f'import {name}\n')

def makeCommand(name, parent, background):
    path = f'{config.path}/{parent}/{name}.py'
    if os.path.exists(path):
        print(path + ' already exist\n')
        return
    with open(path, 'w+') as f:
        f.write(getCommand(name, parent, background))

    init = f'{config.path}/{parent}/__init__.py'
    if not os.path.exists(init):
        with open(init, 'w+'): pass
    with open(init, 'a+') as f:
        f.write(f'from .{name} import *\n')



while True:
    num = int(input("\nCreate:\n\t0 - Module\n\t1 - Command\n\t2 - Background Command\n -> "))
    name = str(input("Name: "))

    if num:
        parent, name = name.split('.')
        makeModule(parent)
        makeCommand(name, parent, num-1)
    else:
        makeModule(name)
