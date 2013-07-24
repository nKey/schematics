# -*- coding: utf-8 -*-

import gettext
import os

translation = {
    'pt_BR': {
        '%s is an illegal field.': '%s é um campo inválido.',
        'This field is required.': 'Este campo é obrigatório.',
        'Value must be one of {}.': 'Valor deve ser um dos {}.',
        'Illegal data value': 'Valor para dados inválido',
        'String value is too long': 'Texto é muito grande',
        'String value is too short': 'Texto é muito pequeno',
        'String value did not match validation regex': 'Valor do texto não corresponde com a expressão regular',
        'Not a well formed email address.': 'Endereço de e-mail inválido.',
        'Not {}': 'Não {}',
        '{} value should be greater than {}': '{} deve ser maior que {}',
        '{} value should be less than {}': '{} deve ser menor que {}',
        'Hash value is wrong length.': 'Hash tem o tamanho errado.',
        'Hash value is not hexadecimal.': 'Hash não é hexadecimal.',
        'Must be either true or false.': 'Deve ser \'true\' or \'false\'',
        'Could not parse {}. Should be ISO8601 (YYYY-MM-DD).': 'Campo {} não está no formato ISO8601 (YYYY-MM-DD).',
        'Could not parse {}. Should be ISO8601.': 'Campo {} não está no formato ISO8601.',
        'Please supply a clean model instance.': 'Por favor forneca uma instancia limpa de modelo.',
        'Please use a mapping for this field or {} instance instead of {}.': 'Por favor use um mapa para este campo ou {} instância ao invés de {}.',
        '%s Model has no role \"%s\"': 'O modelo %s não possui o papel \"%s\"',
        'Please provide at least %d item.': 'Por favor forneca no mínimo %d item.',
        'Please provide at least %d items.': 'Por favor forneça no mínimo %d itens.',
        'Please provide no more than %d item.': 'Por favor não forneça mais de %d item.',
        'Please provide no more than %d items.': 'Por favor não forneça mais de %d itens.',
        'Only dictionaries may be used in a DictType': 'Somente dicionários (dict) podem ser utilizados em um DictType',
    }
}

def translate(key):
    if translation.has_key('pt_BR') and translation['pt_BR'].has_key(key):
        return translation['pt_BR'][key]
    return key


# locale_path = os.path.dirname(os.path.realpath(__file__)) + '/locale'
# print 'locale_path' + locale_path
# print 'realpath' + os.path.realpath(__file__)
# print 'dirname' + os.path.dirname(os.path.realpath(__file__))
# gettext.bind_textdomain_codeset('schematics', codeset='UTF-8')  
# t = gettext.translation('schematics', locale_path, languages=['pt_BR'], fallback=False, codeset='UTF-8')
_ = translate
# ngettext = t.ungettext