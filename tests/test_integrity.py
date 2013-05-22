
import unittest
import hashlib

from schematics.models import Model
from schematics.types import IntType, StringType, MD5Type
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
                if self._data.get('id'):
                    raise ValidationError('Cannot change id')

        p1 = Player({'id': 4})
        p1.validate()
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
        def gen_digest(value):
            return hashlib.md5(value).hexdigest()

        class Player(Model):
            password = StringType(min_length=6, max_length=6)
            secret = MD5Type()

            transformers = {
                password: (secret, gen_digest),
            }

        p1 = Player({'password': 'secret'})
        p1.validate()
        self.assertNotEqual(p1.password, 'secret')
        self.assertTrue(p1.secret)
        self.assertNotIn('secret', p1.serialize().values())

        with self.assertRaises(ValidationError):
            p2 = Player({'password': 'tiny'})
            p2.validate()
