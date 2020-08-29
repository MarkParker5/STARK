import os

modules = {
    'Voice Assistant':  'voice_assistant',
    'Telegram bot':     'telegram_bot',
}

for name, module in modules.items():
    try:
        print(f'launching the {name}')
        os.system(f'start python {module}.py')
    except:
        print(f'[error]\t{name} launch failed')
