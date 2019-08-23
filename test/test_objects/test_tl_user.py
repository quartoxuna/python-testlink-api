# pylint: disable=missing-docstring

# IMPORTS
import unittest
import mock

from testlink.objects.tl_user import UserFromAPIBuilder
from testlink.objects.tl_user import User


class UserFromAPIBuilderTests(unittest.TestCase):

    def test_api_data(self):
        """Test builder initialization with raw API data"""
        data = {'dbID': '123', 'login': 'testuser', 'firstName': 'Tom',
                'lastName': 'Riddle', 'email': 'tom.riddle@hogwarts.uk', 'active': '1'}
        builder = UserFromAPIBuilder(**data)
        self.assertEqual(builder.testlink_id, 123)
        self.assertEqual(builder.login, 'testuser')
        self.assertEqual(builder.first_name, 'Tom')
        self.assertEqual(builder.last_name, 'Riddle')
        self.assertEqual(builder.email, 'tom.riddle@hogwarts.uk')
        self.assertTrue(builder.active)


class UserBuilderTests(unittest.TestCase):

    def test_with_id(self):
        """Test setter for Testlink ID"""
        builder = User.builder()
        self.assertEqual(builder, builder.with_id(123))
        self.assertEqual(builder.testlink_id, 123)

    def test_from_testlink(self):
        """Test setter for parent Testlink instance"""
        testlink = mock.MagicMock()
        builder = User.builder()
        self.assertEqual(builder, builder.from_testlink(testlink))
        self.assertEqual(builder.testlink, testlink)

    def test_with_login(self):
        """Test setter for login name"""
        builder = User.builder()
        self.assertEqual(builder, builder.with_login('testuser'))
        self.assertEqual(builder.login, 'testuser')

    def test_with_first_name(self):
        """Test setter for first name"""
        builder = User.builder()
        self.assertEqual(builder, builder.with_first_name("Tom"))
        self.assertEqual(builder.first_name, "Tom")

    def test_with_last_name(self):
        """Test setter for last name"""
        builder = User.builder()
        self.assertEqual(builder, builder.with_last_name("Riddle"))
        self.assertEqual(builder.last_name, "Riddle")

    def test_with_email(self):
        """Test setter for email address"""
        builder = User.builder()
        self.assertEqual(builder, builder.with_email('tom.riddle@hogwarts.uk'))
        self.assertEqual(builder.email, 'tom.riddle@hogwarts.uk')

    def test_is_active(self):
        """Test setter for active status"""
        builder = User.builder()
        self.assertEqual(builder, builder.is_active())
        self.assertTrue(builder.active)
        builder.is_active(False)
        self.assertFalse(builder.active)

    def test_is_not_active(self):
        """Test setter for inactive status"""
        builder = User.builder()
        self.assertEqual(builder, builder.is_not_active())
        self.assertFalse(builder.active)


class UserTests(unittest.TestCase):

    def test_builder(self):
        """Test initialization with default builder"""
        testlink = mock.MagicMock()
        user = User.builder()\
               .with_id(123)\
               .from_testlink(testlink)\
               .with_login('testuser')\
               .with_first_name("Tom")\
               .with_last_name("Riddle")\
               .with_email('tom.riddle@hogwarts.uk')\
               .is_active()\
               .build()
        self.assertEqual(user.id, 123)
        self.assertEqual(user.testlink, testlink)
        self.assertEqual(user.login, 'testuser')
        self.assertEqual(user.first_name, 'Tom')
        self.assertEqual(user.last_name, 'Riddle')
        self.assertEqual(user.email, 'tom.riddle@hogwarts.uk')
        self.assertTrue(user.active)

    def test_api_builder(self):
        """Test initialization of default builder with raw API data"""
        testlink = mock.MagicMock()
        data = {'dbID': '123', 'login': 'testuser', 'firstName': 'Tom',
                'lastName': 'Riddle', 'email': 'tom.riddle@hogwarts.uk', 'active': '0'}
        user = User.builder(**data)\
               .from_testlink(testlink)\
               .build()
        self.assertEqual(user.id, 123)
        self.assertEqual(user.testlink, testlink)
        self.assertEqual(user.login, 'testuser')
        self.assertEqual(user.first_name, 'Tom')
        self.assertEqual(user.last_name, 'Riddle')
        self.assertEqual(user.email, 'tom.riddle@hogwarts.uk')
        self.assertFalse(user.active)
