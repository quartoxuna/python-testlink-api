#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from testlink.objects.tl_object import TestlinkObjectFromAPIBuilder
from testlink.objects.tl_object import TestlinkObjectBuilder
from testlink.objects.tl_object import TestlinkObject


class UserFromAPIBuilder(TestlinkObjectFromAPIBuilder):
    """Testlink User Builder for raw Testlink API data

    :ivar str login: Login name of the User
    :ivar str first_name: The first name of the User
    :ivar str last_name: The last name of the User
    :ivar str email: The email address of the User
    :ivar bool active: The status of the User
    """

    def __init__(self, *args, **kwargs):
        self.login = kwargs.pop('login', None)
        self.first_name = kwargs.pop('firstName', None)
        self.last_name = kwargs.pop('lastName', None)
        self.email = kwargs.pop('email', None)
        self.active = kwargs.pop('active', None)
        _id = kwargs.pop('dbID', None)
        super(UserFromAPIBuilder, self).__init__(id=_id, *args, **kwargs)

        # Fiy types
        if self.active is not None:
            self.active = bool(int(self.active))


class UserBuilder(TestlinkObjectBuilder,
                  UserFromAPIBuilder):
    """General User Builder"""

    def __init__(self, *args, **kwargs):
        super(UserBuilder, self).__init__(*args, **kwargs)

    def with_login(self, login):
        """Set the login name of the User

        :param str login: The login name of the User
        :rtype: UserBuilder
        """
        self.login = login
        return self

    def with_first_name(self, first_name):
        """Set the first name of the User

        :param str first_name: The first name of the User
        :rtype: UserBuilder
        """
        self.first_name = first_name
        return self

    def with_last_name(self, last_name):
        """Set the last name of the User

        :param str last_name: The last name of the User
        :rtype: UserBuilder
        """
        self.last_name = last_name
        return self

    def with_email(self, email):
        """Set the email address of the User

        :param str email: The email address of the User
        :rtype: UserBuilder
        """
        self.email = email
        return self

    def is_active(self, active=True):
        """Set the status of the User to active

        :param bool active: Active status of the User
        :rtype: UserBuilder
        """
        self.active = active
        return self

    def is_not_active(self):
        """Set the status of the User to inactive

        :rtype: UserBuilder
        """
        self.active = False
        return self

    def build(self):
        """Generates a new User"""
        # Sanity checks
        assert self.login is not None, "Invalid login defined"
        assert self.active is not None, "Invalid active status defined"

        return User(self)


class User(TestlinkObject):
    """Testlink User

    :ivar str login: Login name of the User
    :ivar str name: Name of the User
    :ivar str first_name: First name of the User
    :ivar str last_name: Last name of the User
    :ivar str email: Email address of the User
    :ivar bool active: Active status of the User
    """

    def __init__(self, builder, *args, **kwargs):
        super(User, self).__init__(builder, *args, **kwargs)
        self.__login = builder.login
        self.__first_name = builder.first_name
        self.__last_name = builder.last_name
        self.__email = builder.email
        self.__active = builder.active

    @staticmethod
    def builder(**api_data):
        """Generates a new UserBuilder

        :param api_data: Raw API Data
        :rtype: UserBuilder
        """
        return UserBuilder(**api_data)

    @property
    def login(self):
        return self.__login

    @property
    def first_name(self):
        return self.__first_name

    @property
    def last_name(self):
        return self.__last_name

    @property
    def name(self):
        return " ".join([self.first_name, self.last_name])

    @property
    def email(self):
        return self.__email

    @property
    def active(self):
        return self.__active
