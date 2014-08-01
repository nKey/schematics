# -*- coding: utf-8 -*-

import functools

translation = {
    'pt-BR': {
        '%s is an illegal field.': '%s é um campo inválido.',
        'This field is required.': 'Este campo é obrigatório.',
        'Value must be one of {}.': 'Valor deve ser um dos {}.',
        'Invalid IPv4 address': 'Endereço IPv4 inválido',
        "Couldn't interpret value as string.": 'Não foi possível interpretar o valor como string',
        'Illegal data value': 'Valor para dados inválido',
        'String value is too long': 'Texto é muito grande',
        'String value is too short': 'Texto é muito pequeno',
        'String value did not match validation regex': 'Valor do texto não corresponde com a expressão regular',
        "Not a well formed URL.": 'URL inválida.',
        "URL does not exist.": 'URL não existe.',
        'Not a well formed email address.': 'Endereço de e-mail inválido.',
        'Not {}': 'Não {}',
        "Value is not {}": 'Valor não é {}',
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
        'Both values in point must be float or int': 'Ambos valores no ponto devem ser float ou inteiro',
        'GeoPointType can only accept tuples, lists, or dicts': 'GeoPointType somente aceita tuples, lists, ou dicts',
        'Only dictionaries may be used in a DictType': 'Apenas dictionaries podem ser usados em um DictType',
        

    }
}

def translate(key, language):
    if translation.has_key(language) and translation[language].has_key(key):
        return translation[language][key]
    return key

def translate_partial(key):
    return functools.partial(translate, key)