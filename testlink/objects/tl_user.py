#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""User Object"""

class User(object):
    """Testlink User representation"""

    __slots__ = ["id", "name", "login", "email", "active", "_api"]

    def __init__(self, dbID, login, api=None, *args, **kwargs):
        self._api = api
        self.id = int(dbID)
        self.name = " ".join([kwargs.get('firstName', ''), kwargs.get('lastName')])
        self.login = unicode(login)
        self.email = kwargs.get('emailAddress')
        self.active = bool(int(kwargs.get('isActive','0')))

    def __str__(self):
        return "User: %s" % self.login
