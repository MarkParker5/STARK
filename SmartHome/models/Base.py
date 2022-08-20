from sqlalchemy.ext.declarative import declarative_base, declared_attr


class BaseClass(object):

    @declared_attr
    def __tablename__(cls):
        return f'{cls.__name__.lower()}s'

    def __str__(self):
        return f'{type(self).__name__}({self.id.hex[:8]})'

Base = declarative_base(cls = BaseClass)
