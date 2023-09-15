# from .object import Object, Pattern, classproperty

# class Number(Object):
#     value: float
#     isPercentage: bool = False

#     def __init__(self, value: float):
#         self.value = value

#     @classmethod
#     def parse(cls, fromString: str):
#         string = string.replace(' ', '').replace(',', '.').replace('%', '')
#         value = float(string)

#         if '%' in stringValue:
#             value /= 100
#             isPercentage = True

#         acNumber = Number(value = value)
#         acNumber.isPercentage = isPercentage
#         acNumber.stringValue = stringValue

#         return acNumber

#     @classproperty
#     def pattern() -> Pattern:
#         return Pattern('[:digits:,\.%\s]')
