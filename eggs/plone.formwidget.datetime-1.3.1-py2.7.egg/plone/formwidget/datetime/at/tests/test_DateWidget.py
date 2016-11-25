from datetime import datetime
from DateTime import DateTime
import mock
import unittest2 as unittest


class TestDateWidget(unittest.TestCase):

    def createInstance(self):
        from plone.formwidget.datetime.at.widget import DateWidget
        widget = DateWidget()
        widget.request = {}
        return widget

    def test_subclass(self):
        from plone.formwidget.datetime.at.widget import DateWidget
        from plone.formwidget.datetime.base import AbstractDateWidget
        from Products.Archetypes.Widget import TypesWidget
        self.assertTrue(DateWidget, (AbstractDateWidget, TypesWidget))

    def test__properties(self):
        instance = self.createInstance()
        self.assertEqual(
            instance._properties,
            {
                'blurrable': False,
                'condition': '',
                'description': '',
                'first_day': None,
                'helper_css': (),
                'helper_js': (),
                'label': '',
                'macro': 'date_input',
                'modes': ('view', 'edit'),
                'populate': True,
                'postback': True,
                'show_calendar': True,
                'show_content_type': False,
                'visible': {'edit': 'visible', 'view': 'visible'},
                'years_range': (-10, 10),
            }
        )

    def test__call_(self):
        instance = self.createInstance()
        mode = mock.Mock()
        ins = mock.MagicMock()
        request = mock.Mock()
        ins.REQUEST = request
        instance(mode, ins)

    def test_name(self):
        instance = self.createInstance()
        instance.getName = mock.Mock(return_value='name')
        self.assertTrue(instance.name, 'name')

    def test_process_form_value_is_empty(self):
        instance = self.createInstance()
        ins = mock.Mock()
        field = mock.Mock()
        form = {}
        self.assertFalse(instance.process_form(ins, field, form))

    def test_process_form_with_invalid_date_emptyReturnsMarker_False(self):
        instance = self.createInstance()
        ins = mock.Mock()
        field = mock.Mock()
        field.getName.return_value = 'field'
        form = {
            'field-calendar': 'value',
            'field-year': None,
        }
        self.assertEqual(
            instance.process_form(ins, field, form),
            ('', {})
        )
        self.assertFalse(form['field'])

    def test_process_form_with_invalid_date_emptyReturnsMarker_True(self):
        instance = self.createInstance()
        ins = mock.Mock()
        field = mock.Mock()
        field.getName.return_value = 'field'
        form = {
            'field-calendar': 'value',
            'field-year': None,
        }
        self.assertFalse(
            instance.process_form(ins, field, form, emptyReturnsMarker=True)
        )

    def test_process_form_with_valid_date_without_time(self):
        instance = self.createInstance()
        ins = mock.Mock()
        field = mock.Mock()
        field.getName.return_value = 'field'
        form = {
            'field-calendar': 'value',
            'field-year': '2011',
            'field-month': '11',
            'field-day': '22',
        }
        self.assertEqual(
            instance.process_form(ins, field, form)[0].asdatetime(),
            datetime(2011, 11, 22, 0, 0)
        )
        self.assertEqual(
            form['field'].asdatetime(),
            datetime(2011, 11, 22, 0, 0)
        )

    def test_process_form_with_oldyear(self):
        instance = self.createInstance()
        ins = mock.Mock()
        field = mock.Mock()
        field.getName.return_value = 'field'
        form = {
            'field-calendar': 'value',
            'field-year': '99',
            'field-month': '11',
            'field-day': '22',
        }
        R = DateTime(datetime(99,11,22))
        self.assertEqual(
            instance.process_form(ins, field, form),
            (R, {})
        )
        self.assertEqual(form['field'], R)

