import re

def zeroLengthCheck(variable):
    if len(variable) == 0:
        return 1
    return 0

def lengthValidation(variable, targetSize):
    if len(variable) > targetSize:
        return 1
    return 0

def passwordRegEx(variable):
    if not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', variable):
        return 1
    return 0
