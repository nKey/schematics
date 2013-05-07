
import unittest

from schematics.models import Model
from schematics.types import IntType, StringType
from schematics.exceptions import ValidationError


class TestDataIntegrity(unittest.TestCase):

    def test_dont_serialize_invalid_data(self):
        """
        Serialization must always contain just the subset of valid
        data from the model.

        """
        class Player(Model):
            code = StringType(max_length=4)

        p1 = Player({'code': 'invalid1'})
        self.assertRaises(ValidationError, p1.validate)
        self.assertEqual(p1.serialize(), {'code': None})

    def test_dont_overwrite_with_invalid_data(self):
        """
        Model-level validators are black-boxes and we should not assume
        that we can set the instance data at any time.

        """
        class Player(Model):
            id = IntType()

            def validate_id(self, context, value):
                if self.id:
                    raise ValidationError('Cannot change id')

        p1 = Player({'id': 4})
        p1.id = 3
        self.assertRaises(ValidationError, p1.validate)
        self.assertEqual(p1.id, 4)

    def test_dont_revalidate_valid_data(self):
        """
        A field should have a way to define data as already validated.

        It would be difficult to deal with data that is not symmetrically
        convertible otherwise.

        In this example, data is validated and then mutated to an "encoded"
        valid format for security purposes during conversion.

        """
        class PasswordType(StringType):
            def __init__(self, *a, **kw):
                self.sep = '|||'
                self.alg = 'dummy'
                super(PasswordType, self).__init__(*a, **kw)

            def _dummy_hash(self, value):
                # super secure way to encode a password
                dummy_hash = str(abs(hash(value)))
                return self.sep.join((self.alg, dummy_hash))

            def _check_hash(self, value):
                # validate the password is encoded securely
                try:
                    alg, digest = value.split(self.sep)
                except ValueError:
                    return False
                return (alg == self.alg) and digest.isdigit()

            def convert(self, value):
                # password can come encoded or requiring encoding
                value = super(PasswordType, self).convert(value)
                if self.sep in value:
                    return value  # already encoded, so it is valid
                self.validate(value)
                return self._dummy_hash(value)

        class Player(Model):
            password = PasswordType(min_length=6, max_length=6)

        p1 = Player({'password': 'secret'})
        self.assertNotEqual(p1.password, 'secret')
        p1.validate()
        self.assertNotIn('secret', p1.serialize()['password'])
