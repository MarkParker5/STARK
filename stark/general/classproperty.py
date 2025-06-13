
class classproperty(property): # TODO: typing
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
