import unittest
from mock import Mock, patch

from xivo_agid.handlers.userfeatures import UserFeatures
from xivo_agid import objects


class TestUserFeatures(unittest.TestCase):

    def setUp(self):
        self._variables = {'XIVO_USERID': 42,
                           'XIVO_DSTID': 33,
                           'XIVO_LINEID': 5,
                           'XIVO_CALLORIGIN' : 'my_origin',
                           'XIVO_CALLFILTER_BYPASS': 'my_filter',
                           'XIVO_SRCNUM': '1000',
                           'XIVO_DSTNUM': '1003',}

        def get_variable(key):
            return self._variables[key]

        self._agi = Mock()
        self._agi.get_variable = get_variable
        self._cursor = Mock()
        self._args = Mock()

    def tearDown(self):
        pass

    def test_set_pickup_info(self):
        context = 'foo'
        number = '101'
        line_list = [{'id': '2',
                      'number': number,
                      'context': context},]
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)
        self.assertEqual(None, userfeatures._pickup_context)

        userfeatures._lines = Mock(objects.Lines)
        userfeatures._lines.lines = line_list
        userfeatures._dstnum = number
        userfeatures._set_pickup_info()

        self.assertEqual(context, userfeatures._pickup_context)
        self.assertEqual(number, userfeatures._pickup_exten)

    def test_userfeatures(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)

        self.assertEqual(userfeatures._agi, self._agi)
        self.assertEqual(userfeatures._cursor, self._cursor)
        self.assertEqual(userfeatures._args, self._args)

    def test_set_members(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)
        userfeatures._set_feature_list = Mock()
        userfeatures._set_caller = Mock()
        userfeatures._set_lines = Mock()
        userfeatures._set_user = Mock()

        userfeatures._set_members()

        objects.ExtenFeatures = Mock()
        old_user, objects.User = objects.User, Mock()

        self.assertEqual(userfeatures._userid, self._variables['XIVO_USERID'])
        self.assertEqual(userfeatures._dstid, self._variables['XIVO_DSTID'])
        self.assertEqual(userfeatures._lineid, self._variables['XIVO_LINEID'])
        self.assertEqual(userfeatures._zone, self._variables['XIVO_CALLORIGIN'])
        self.assertEqual(userfeatures._bypass_filter, self._variables['XIVO_CALLFILTER_BYPASS'])
        self.assertEqual(userfeatures._srcnum, self._variables['XIVO_SRCNUM'])
        self.assertEqual(userfeatures._dstnum, self._variables['XIVO_DSTNUM'])
        self.assertTrue(userfeatures._set_feature_list.called)
        self.assertTrue(userfeatures._set_caller.called)
        self.assertTrue(userfeatures._set_lines.called)
        self.assertTrue(userfeatures._set_user.called)

        objects.User, old_user = old_user, None

    def test_set_feature_list(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)
        
        with patch.object(objects.ExtenFeatures, '__init__') as extenfeatures_init:
            extenfeatures_init.return_value = None
            userfeatures._set_feature_list()
            extenfeatures_init.assert_called_with(self._agi, self._cursor)
        self.assertNotEqual(userfeatures._feature_list, None)
        self.assertTrue(isinstance(userfeatures._feature_list, objects.ExtenFeatures))

    def test_set_caller(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)

        userfeatures._set_caller()

        self.assertTrue(userfeatures._caller is None)

        userfeatures._userid = self._variables['XIVO_USERID']

        with patch.object(objects.User, '__init__') as user_init:
            user_init.return_value = None

            userfeatures._set_caller()

            user_init.assert_called_with(self._agi, self._cursor, self._variables['XIVO_USERID'])
        self.assertTrue(userfeatures._caller is not None)
        self.assertTrue(isinstance(userfeatures._caller, objects.User))

    def test_set_lines(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)

        userfeatures._set_lines()

        self.assertEqual(userfeatures._lines, None)

        userfeatures._dstid = self._variables['XIVO_DSTID']
        with patch.object(objects.Lines, '__init__') as lines_init:
            lines_init.return_value = None

            userfeatures._set_lines()

            lines_init.assert_called_with(self._agi, self._cursor, int(self._variables['XIVO_DSTID']))
        self.assertNotEqual(userfeatures._lines, None)
        self.assertTrue(isinstance(userfeatures._lines, objects.Lines))

    def test_set_user(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)
        userfeatures._set_xivo_user_name = Mock()

        userfeatures._set_user()

        self.assertTrue(userfeatures._user is None)
        self.assertEqual(userfeatures._set_xivo_user_name.call_count, 0)

        userfeatures._dstid = self._variables['XIVO_DSTID']

        with patch.object(objects.User, '__init__') as user_init:
            user_init.return_value = None

            userfeatures._set_user()

            self.assertEqual(userfeatures._set_xivo_user_name.call_count, 1)
            self.assertTrue(userfeatures._user is not None)
            self.assertTrue(isinstance(userfeatures._user, objects.User))

    def test_execute(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)
        userfeatures._set_members = Mock()
        userfeatures._set_xivo_ifaces = Mock()
        userfeatures._set_user_filter = Mock()
        userfeatures._boss_secretary_filter = Mock()

        userfeatures.execute()

        self.assertEqual(userfeatures._set_members.call_count, 1)
        self.assertEqual(userfeatures._set_xivo_ifaces.call_count, 1)

    def test_xivo_set_iface_nb(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)
        self._agi.set_variable = Mock()

        userfeatures._set_xivo_iface_nb(0)

        self._agi.set_variable.assert_called_once_with('XIVO_INTERFACE_NB', 0)

    def test_is_main_line(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)

        self.assertFalse(userfeatures._is_main_line())

        lineid = '97'
        userfeatures._lineid = lineid
        userfeatures._lines = Mock()
        userfeatures._lines.lines = [{'id': lineid}, ]

        self.assertTrue(userfeatures._is_main_line())

    def test_set_xivo_user_name(self):
        userfeatures = UserFeatures(self._agi, self._cursor, self._args)

        self._agi.set_variable = Mock()

        userfeatures._set_xivo_user_name()

        self.assertEqual(self._agi.call_count, 0)

        self._agi.set_variable.reset_mock()

        userfeatures._user = Mock()
        userfeatures._user.firstname = 'firstname'
        userfeatures._user.lastname = 'lastname'

        userfeatures._set_xivo_user_name()

        self.assertEqual(self._agi.set_variable.call_count, 2)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()
