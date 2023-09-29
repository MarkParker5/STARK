class LocalizableString:
    string: str
    language_code: str
    arguments: dict[str, str]
    
    def __init__(self, string: str, language_code: str = '', /, **arguments: str):
        self.string = string
        self.language_code = language_code
        self.arguments = arguments
    
    def __str__(self): return self.string
    def __repr__(self): return self.string
