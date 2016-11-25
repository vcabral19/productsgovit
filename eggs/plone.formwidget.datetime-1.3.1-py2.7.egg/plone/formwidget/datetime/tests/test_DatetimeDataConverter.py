from plone.formwidget.datetime.z3cform.converter import DateDataConverter
from plone.formwidget.datetime.z3cform.converter import DatetimeDataConverter
from plone.formwidget.datetime.z3cform.interfaces import\
    DatetimeValidationError

import mock
import unittest2 as unittest


class TestDatetimeDataConverter(unittest.TestCase):

    def createInstance(self):
        field = mock.Mock()
        widget = mock.Mock()
        return DatetimeDataConverter(field, widget)

    def test_subclass(self):
        self.assertTrue(DatetimeDataConverter, DateDataConverter)

    def test_instance(self):
        instance = self.createInstance()
        self.assertTrue(isinstance(instance, DatetimeDataConverter))

    def test_toWidgetValue__value_is_missing(self):
        instance = self.createInstance()
        value = instance.field.missing_value
        self.assertEqual(
            instance.toWidgetValue(value),
            ('', '', '', '00', '00', '')
        )

    def test_toWidgetValue__value_is_not_missing(self):
        instance = self.createInstance()
        value = mock.Mock()
        value.year = 'year'
        value.month = 'month'
        value.day = 'day'
        value.hour = 'hour'
        value.minute = 'minute'
        self.assertEqual(
            instance.toWidgetValue(value)[:-1],
            ('year', 'month', 'day', 'hour', 'minute')
        )

    def test_toFieldValue_no_value(self):
        instance = self.createInstance()
        value = [None]
        instance.field.missing_value = 'missing_value'
        self.assertEqual(
            instance.toFieldValue(value),
            'missing_value'
        )

    def test_toFieldValue_map_ValueError(self):
        instance = self.createInstance()
        value = 'abcde'
        self.assertRaises(
            DatetimeValidationError,
            lambda: instance.toFieldValue(value)
        )

    def test_toFieldValue_date_ValueError(self):
        instance = self.createInstance()
        value = ('a', 2, 3, 4)
        self.assertRaises(
            DatetimeValidationError,
            lambda: instance.toFieldValue(value)
        )

    def test_toFieldValue__value_is_nissing(self):
        instance = self.createInstance()
        instance.field.missing_value = 'missing_value'
        value = (1, 2, 3, '')
        self.assertEqual(
            instance.toFieldValue(value),
            'missing_value'
        )
