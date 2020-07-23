'''
Created on Feb. 25, 2020

@author: ankita
'''
from django.core.validators import RegexValidator

alphanumeric = RegexValidator(
    r'^[0-9a-zA-Z-._]*$', 'Only alphanumeric characters, dashes, underscores and dots are allowed in names, spaces are not allowed.')
