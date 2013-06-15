
from .exceptions import BaseError, ValidationError


def validate(model, raw_data, partial=False, strict=False, context=None):
    """
    Validate some untrusted data using a model. Trusted data can be passed in
    the `context` parameter.

    :param model:
        The model to use as source for validation. If given an instance,
        will also run instance-level validators on the data.
    :param raw_data:
        A ``dict`` or ``dict``-like structure for incoming data.
    :param partial:
        Allow partial data to validate; useful for PATCH requests.
        Essentially drops the ``required=True`` arguments from field
        definitions. Default: False
    :param strict:
        Complain about unrecognized keys. Default: False
    :param context:
        A ``dict``-like structure that may contain already validated data.

    :returns: tuple(data, errors)
        data dict contains the valid raw_data plus the context data.
        errors dict contains all ValidationErrors found.
    """
    data = dict(context) if context is not None else {}
    errors = {}

    # set and validate instance serializable fields
    if hasattr(model, '_data'):
        serializable_errors = _serializable_setters(model, raw_data)
        errors.update(serializable_errors)

    # validate raw_data by the model fields
    for field_name, field in model._fields.iteritems():
        serialized_field_name = field.serialized_name or field_name
        if serialized_field_name in raw_data:
            value = raw_data[serialized_field_name]
        elif field_name in raw_data:
            value = raw_data[field_name]
        elif field_name in data:
            continue  # skip already validated data
        else:
            value = field.default

        if value is None:
            if field.required and not partial:
                errors[serialized_field_name] = [field.messages['required'], ]
        else:
            try:
                value = field.convert(value)
                field.validate(value)
                data[field_name] = value
            except BaseError as e:
                errors[serialized_field_name] = e.messages

    if strict:
        rogues_found = set(data) - set(model._fields)
        if len(rogues_found) > 0:
            for field_name in rogues_found:
                errors[field_name] = [u'%s is an illegal field.' % field_name]

    # validate an instance with its own validators
    if hasattr(model, '_data'):
        instance_errors = _validate_instance(model, data)
        errors.update(instance_errors)

    if len(errors) > 0:
        raise ValidationError(errors)

    return data


def _validate_instance(instance, data):
    """
    Validate data using instance level methods.

    :param data:
        A dict with data to validate. Invalid items are removed from it.

    :returns:
        Errors of the fields that did not pass validation.
    """
    errors = {}
    for field_name, value in data.items():
        if field_name in instance._validator_functions:
            try:
                context = dict(instance._data, **data)
                instance._validator_functions[field_name](instance, context, value)
            except BaseError as e:
                field = instance._fields[field_name]
                serialized_field_name = field.serialized_name or field_name
                errors[serialized_field_name] = e.messages
                data.pop(field_name, None)  # get rid of the invalid field
    return errors


def _serializable_setters(instance, raw_data):
    """
    Set and validate serializable fields.

    :param raw_data:
        A dict with the input data.

    :returns:
        Errors of the setter fields that failed validation.
    """
    errors = {}
    for field_name, serializable in instance._serializables.iteritems():
        serialized_field_name = serializable.serialized_name or field_name
        if serializable.fset and serialized_field_name in raw_data:
            value = raw_data[serialized_field_name]
            try:
                setattr(instance, field_name, value)
            except BaseError as e:
                errors[serialized_field_name] = e.messages
    return errors
