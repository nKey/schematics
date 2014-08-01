import uuid
import re
import datetime
import decimal
import itertools
import functools

from ..exceptions import StopValidation, ValidationError, ConversionError
from ..localization import translate_partial as _


def force_unicode(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    elif not obj is None:
        obj = unicode(obj)

    return obj


_last_position_hint = -1
_next_position_hint = itertools.count().next


class TypeMeta(type):
    """
    Meta class for BaseType. Merges `MESSAGES` dict and accumulates
    validator methods.
    """

    def __new__(cls, name, bases, attrs):
        messages = {}
        validators = []

        for base in reversed(bases):
            if hasattr(base, 'MESSAGES'):
                messages.update(base.MESSAGES)

            if hasattr(base, "_validators"):
                validators.extend(base._validators)

        if 'MESSAGES' in attrs:
            messages.update(attrs['MESSAGES'])

        attrs['MESSAGES'] = messages

        for attr_name, attr in attrs.iteritems():
            if attr_name.startswith("validate_"):
                validators.append(attr)

        attrs["_validators"] = validators

        return type.__new__(cls, name, bases, attrs)


class BaseType(object):
    """
    A base class for Types in a Schematics model. Instances of this
    class may be added to subclasses of ``Model`` to define a model schema.

    Validators that need to access variables on the instance
    can be defined be implementing methods whose names start with ``validate_``
    and accept one parameter (in addition to ``self``)

    :param required:
        Invalidate field when value is None or is not supplied. Default:
        False.
    :param default:
        When no data is provided default to this value. May be a callable.
        Default: None.
    :param serialized_name:
        The name of this field defaults to the class attribute used in the
        model. However if the field has another name in foreign data set this
        argument. Serialized data will use this value for the key name too.
    :param choices:
        An iterable of valid choices. This is the last step of the validator
        chain.
    :param validators:
        A list of callables. Each callable receives the value after it has been
        converted into a rich python type. Default: []
    :param serialize_when_none:
        Dictates if the field should appear in the serialized data even if the
        value is None. Default: True
    :param messages:
        Override the error messages with a dict. You can also do this by
        subclassing the Type and defining a `MESSAGES` dict attribute on the
        class. A metaclass will merge all the `MESSAGES` and override the
        resulting dict with instance level `messages` and assign to
        `self.messages`.

    """

    __metaclass__ = TypeMeta

    MESSAGES = {
        'required': _(u"This field is required."),
        'choices': _(u"Value must be one of {}."),
    }

    def __init__(self, required=False, default=None, serialized_name=None,
                 choices=None, validators=None,
                 serialize_when_none=None, messages=None):
        self.required = required
        self._default = default
        self.serialized_name = serialized_name
        self.choices = choices

        self.validators = [functools.partial(v, self) for v in self._validators]
        if validators:
            self.validators += validators

        self.serialize_when_none = serialize_when_none
        self.messages = dict(self.MESSAGES, **(messages or {}))
        self._position_hint = _next_position_hint()  # For ordering of fields

    def __call__(self, value):
        return self.convert(value)

    def copy(self):
        copy = object.__new__(self.__class__)
        copy.__dict__.update(self.__dict__)
        copy.validators = self.validators[:]
        return copy

    @property
    def default(self):
        default = self._default
        if callable(self._default):
            default = self._default()
        return default

    def to_primitive(self, value):
        """Convert internal data to a value safe to serialize.
        """
        return value

    def convert(self, value, language=None):
        """
        Convert untrusted data to a richer Python construct.
        """
        return value

    def validate(self, value, old_value=None, language=None):
        """
        Validate the field and return a clean value or raise a
        ``ValidationError`` with a list of errors raised by the validation
        chain. Stop the validation process from continuing through the
        validators by raising ``StopValidation`` instead of ``ValidationError``.

        """

        errors = []

        for validator in self.validators:
            try:
                validator(value, old_value=old_value, language=language)
            except ValidationError, e:
                errors.extend(e.messages)

                if isinstance(e, StopValidation):
                    break

        if errors:
            raise ValidationError(errors)

    def validate_required(self, value, old_value=None, language=None):
        if self.required and value is None:
            raise ValidationError(self.messages['required'](language))

    def validate_choices(self, value, old_value=None, language=None):
        if self.choices is not None:
            if value not in self.choices:
                raise ValidationError(self.messages['choices'](language)
                    .format(unicode(self.choices)))


class UUIDType(BaseType):
    """A field that stores a valid UUID value.
    """

    def convert(self, value, language=None):
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value

    def to_primitive(self, value):
        return str(value)


class IPv4Type(BaseType):
    """ A field that stores a valid IPv4 address """

    def __init__(self, auto_fill=False, **kwargs):
        super(IPv4Type, self).__init__(**kwargs)

    def _jsonschema_type(self):
        return 'string'

    @classmethod
    def valid_ip(cls, addr):
        try:
            addr = addr.strip().split(".")
        except AttributeError:
            return False
        try:
            return len(addr) == 4 and all(int(octet) < 256 for octet in addr)
        except ValueError:
            return False

    def validate(self, value, old_value=None, language=None):
        """
          Make sure the value is a IPv4 address:
          http://stackoverflow.com/questions/9948833/validate-ip-address-from-list
        """
        if not IPv4Type.valid_ip(value):
            error_msg = _(u'Invalid IPv4 address')(language)
            raise ValidationError(error_msg)
        return True

    def _jsonschema_format(self):
        return 'ip-address'

    @classmethod
    def _from_jsonschema_formats(self):
        return ['ip-address']

    @classmethod
    def _from_jsonschema_types(self):
        return ['string']


class StringType(BaseType):
    """A unicode string field. Default minimum length is one. If you want to
    accept empty strings, init with ``min_length`` 0.
    """

    allow_casts = (int, str)

    MESSAGES = {
        'convert': _(u"Couldn't interpret value as string."),
        'max_length': _(u"String value is too long."),
        'min_length': _(u"String value is too short."),
        'regex': _(u"String value did not match validation regex."),
    }

    def __init__(self, regex=None, max_length=None, min_length=None, **kwargs):
        self.regex = re.compile(regex) if regex else None
        self.max_length = max_length
        self.min_length = min_length

        super(StringType, self).__init__(**kwargs)

    def convert(self, value, language=None):
        if value is None:
            return None

        if not isinstance(value, unicode):
            if isinstance(value, self.allow_casts):
                if not isinstance(value, str):
                    value = str(value)
                value = unicode(value, 'utf-8')
            else:
                raise ConversionError(self.messages['convert'](language))

        return value

    def validate_length(self, value, old_value=None, language=None):
        len_of_value = len(value) if value else 0

        if self.max_length is not None and len_of_value > self.max_length:
            raise ValidationError(self.messages['max_length'](language))

        if self.min_length is not None and len_of_value < self.min_length:
            raise ValidationError(self.messages['min_length'](language))

    def validate_regex(self, value, old_value=None, language=None):
        if self.regex is not None and self.regex.match(value) is None:
            raise ValidationError(self.messages['regex'](language))


class URLType(StringType):
    """A field that validates input as an URL.

    If verify_exists=True is passed the validate function will make sure
    the URL makes a valid connection.
    """

    MESSAGES = {
        'invalid_url': _(u"Not a well formed URL."),
        'not_found': _(u"URL does not exist."),
    }

    URL_REGEX = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    def __init__(self, verify_exists=False, **kwargs):
        self.verify_exists = verify_exists
        super(URLType, self).__init__(**kwargs)

    def validate_url(self, value, old_value=None, language=None):
        if not URLType.URL_REGEX.match(value):
            raise StopValidation(self.messages['invalid_url'](language))
        if self.verify_exists:
            import urllib2
            try:
                request = urllib2.Request(value)
                urllib2.urlopen(request)
            except Exception:
                raise StopValidation(self.messages['not_found'](language))


class EmailType(StringType):
    """A field that validates input as an E-Mail-Address.
    """

    MESSAGES = {
        'email': _(u"Not a well formed email address.")
    }

    EMAIL_REGEX = re.compile(
        # dot-atom
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
        # quoted-string
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016'
        r'-\177])*"'
        # domain
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$',
        re.IGNORECASE
    )

    def validate_email(self, value, old_value=None, language=None):
        if not EmailType.EMAIL_REGEX.match(value):
            raise StopValidation(self.messages['email'](language))


class NumberType(BaseType):
    """A number field.
    """

    MESSAGES = {
        'number_coerce': _(u"Value is not {}"),
        'number_min': _(u"{} value should be greater than {}"),
        'number_max': _(u"{} value should be less than {}"),
    }

    def __init__(self, number_class, number_type,
                 min_value=None, max_value=None, **kwargs):
        self.number_class = number_class
        self.number_type = number_type
        self.min_value = min_value
        self.max_value = max_value

        super(NumberType, self).__init__(**kwargs)

    def convert(self, value, language=None):
        try:
            value = self.number_class(value)
        except (TypeError, ValueError):
            raise ConversionError(self.messages['number_coerce'](language)
                .format(self.number_type.lower()))

        return value

    def check_value(self, value):
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(self.messages['number_min'](language)
                .format(self.number_type, self.min_value))

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(self.messages['number_max'](language)
                .format(self.number_type, self.max_value))

        return value


class IntType(NumberType):
    """A field that validates input as an Integer
    """

    def __init__(self, *args, **kwargs):
        super(IntType, self).__init__(number_class=int,
                                      number_type='Int',
                                      *args, **kwargs)


class LongType(NumberType):
    """A field that validates input as a Long
    """
    def __init__(self, *args, **kwargs):
        super(LongType, self).__init__(number_class=long,
                                       number_type='Long',
                                       *args, **kwargs)


class FloatType(NumberType):
    """A field that validates input as a Float
    """
    def __init__(self, *args, **kwargs):
        super(FloatType, self).__init__(number_class=float,
                                        number_type='Float',
                                        *args, **kwargs)


class DecimalType(BaseType):
    """A fixed-point decimal number field.
    """

    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value

        super(DecimalType, self).__init__(**kwargs)

    def to_primitive(self, value):
        return unicode(value)

    def convert(self, value, language=None):
        if not isinstance(value, decimal.Decimal):
            if not isinstance(value, basestring):
                value = unicode(value)
            try:
                value = decimal.Decimal(value)

            except (TypeError, decimal.InvalidOperation):
                raise ConversionError(self.messages['number_coerce'](language)
                    .format(self.number_type))

        return value

    def validate_range(self, value, old_value=None, language=None):
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(self.messages['number_min'](language)
                .format(self.number_type, self.min_value))

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(self.messages['number_max'](language)
                .format(self.number_type, self.max_value))

        return value


class HashType(BaseType):

    MESSAGES = {
        'hash_length': _(u"Hash value is wrong length."),
        'hash_hex': _(u"Hash value is not hexadecimal."),
    }

    def convert(self, value, language=None):
        if len(value) != self.LENGTH:
            raise ValidationError(self.messages['hash_length'](language))
        try:
            value = int(value, 16)
        except ValueError:
            raise ConversionError(self.messages['hash_hex'](language))
        return value


class MD5Type(HashType):
    """A field that validates input as resembling an MD5 hash.
    """

    LENGTH = 32


class SHA1Type(HashType):
    """A field that validates input as resembling an SHA1 hash.
    """

    LENGTH = 40


class BooleanType(BaseType):
    """A boolean field type. In addition to ``True`` and ``False``, coerces these
    values:

    + For ``True``: "True", "true", "1"
    + For ``False``: "False", "false", "0"

    """

    TRUE_VALUES = ('True', 'true', '1')
    FALSE_VALUES = ('False', 'false', '0')

    def convert(self, value, language=None):
        if isinstance(value, basestring):
            if value in self.TRUE_VALUES:
                value = True
            elif value in self.FALSE_VALUES:
                value = False

        if not isinstance(value, bool):
            raise ConversionError(_(u'Must be either true or false.')(language))

        return value


class DateType(BaseType):
    """Defaults to converting to and from ISO8601 date values.
    """

    SERIALIZED_FORMAT = '%Y-%m-%d'
    MESSAGES = {
        'parse': _(u'Could not parse {}. Should be ISO8601 (YYYY-MM-DD).'),
    }

    def __init__(self, **kwargs):
        self.serialized_format = self.SERIALIZED_FORMAT
        super(DateType, self).__init__(**kwargs)

    def convert(self, value, language=None):
        if isinstance(value, datetime.date):
            return value

        try:
            return datetime.datetime.strptime(value, self.serialized_format).date()
        except (ValueError, TypeError):
            raise ConversionError(self.messages['parse'](language).format(value))

    def to_primitive(self, value):
        return value.strftime(self.serialized_format)


class DateTimeType(BaseType):
    """Defaults to converting to and from ISO8601 datetime values.

    :param formats:
        A value or list of values suitable for ``datetime.datetime.strptime``
        parsing. Default: `('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S')`
    :param serialized_format:
        The output format suitable for Python ``strftime``. Default: ``'%Y-%m-%dT%H:%M:%S.%f'``

    """

    DEFAULT_FORMATS = ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S')
    SERIALIZED_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    MESSAGES = {
        'parse': _(u'Could not parse {}. Should be ISO8601.'),
    }

    def __init__(self, formats=None, serialized_format=None, **kwargs):
        """

        """
        if isinstance(format, basestring):
            formats = [formats]
        if formats is None:
            formats = self.DEFAULT_FORMATS
        if serialized_format is None:
            serialized_format = self.SERIALIZED_FORMAT
        self.formats = formats
        self.serialized_format = serialized_format
        super(DateTimeType, self).__init__(**kwargs)

    def convert(self, value, language=None):
        if isinstance(value, datetime.datetime):
            return value

        for format in self.formats:
            try:
                return datetime.datetime.strptime(value, format)
            except (ValueError, TypeError):
                continue
        raise ConversionError(self.messages['parse'](language).format(value))

    def to_primitive(self, value):
        if callable(self.serialized_format):
            return self.serialized_format(value)
        return value.strftime(self.serialized_format)


class GeoPointType(BaseType):
    """A list storing a latitude and longitude.
    """

    MESSAGES = {
        'invalid_point_value': _('Both values in point must be float or int'),
        'invalid_value': _('GeoPointType can only accept tuples, lists, or dicts'),
    }

    def convert(self, value, language=None):
        """Make sure that a geo-value is of type (x, y)
        """
        if not len(value) == 2:
            raise ValueError('Value must be a two-dimensional point')
        if isinstance(value, dict):
            for v in value.values():
                if not isinstance(v, (float, int)):
                    raise ValueError(_('Both values in point must be float or int')(language))
        elif isinstance(value, (list, tuple)):
            if (not isinstance(value[0], (float, int)) or
                    not isinstance(value[1], (float, int))):
                raise ValueError(self.messages['invalid_point_value'](language))
        else:
            raise ValueError(self.messages['invalid_value'](language))

        return value
