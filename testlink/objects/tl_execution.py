#!/usr/bin/env python
# pylint: disable=line-too-long
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# -*- coding: utf-8 -*-

"""Execution Object"""

# IMPORTS
import datetime

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import _STRPTIME_FUNC as strptime
from testlink.objects.tl_object import normalize_list

from testlink.objects.tl_attachment import Attachment

from testlink.exceptions import NotSupported

from testlink.enums import EXECUTION_TYPE as ExecutionType

class Execution(TestlinkObject):
    """Testlink TestCase Execution representation
    @ivar id: The internal ID of the Execution
    @type id: int
    @ivar testplan_id: The internal ID of the parent TestPlan
    @type testplan_id: int
    @ivar build_id: The internal ID of the parent Build
    @type build_id: int
    @ivar tcversion_id: The internal ID of the parent TestCase Version
    @type tcversion_id: int
    @ivar tcversion_number: The version of the parent TestCase
    @type tcversion_number: int
    @ivar status: The status of the Execution
    @type status: str
    @ivar notes: Notes of the Execution
    @type notes: str
    @ivar execution_type: Execution Type
    @type execution_type: ExecutionType
    @ivar execution_ts: Timestamp of execution
    @type execution_ts: datetime
    @ivar tester_id: The internal ID of the tester
    @type tester_id: int
    """

    __slots__ = ("id", "testplan_id", "platform_id", "build_id", "tcversion_id", "tcversion_number", "status",\
            "notes", "execution_type", "execution_ts", "tester_id", "__tester", "duration")

    def __init__(
            self,\
            testplan_id=-1,\
            platform_id=-1,\
            build_id=-1,\
            tcversion_id=-1,\
            tcversion_number=0,\
            status='',\
            notes="",\
            execution_type=ExecutionType.MANUAL,\
            execution_ts=str(datetime.datetime.min),\
            tester_id=-1,\
            execution_duration=0.0,\
            api=None,\
            **kwargs\
        ):
        TestlinkObject.__init__(self, kwargs.get('id'), kwargs.get('id', "None"), api)
        self.testplan_id = int(testplan_id)
        self.platform_id = int(platform_id)
        self.build_id = int(build_id)
        self.tcversion_id = int(tcversion_id)
        self.tcversion_number = int(tcversion_number)
        self.status = status
        self.notes = notes
        self.execution_type = int(execution_type)
        try:
            self.execution_ts = strptime(str(execution_ts), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.execution_ts = datetime.datetime.min
        self.tester_id = int(tester_id)
        self.__tester = None
        try:
            self.duration = float(execution_duration)
        except ValueError:
            self.duration = float(0.0)

    def __str__(self):
        """String representaion"""
        return "Execution (%d) [%s] %s" % (self.id, self.status, self.notes)

    @property
    def tester(self):
        """Tester of this execution"""
        if self.__tester is None:
            try:
                user = self._api.getUserByID(self.tester_id)
                if isinstance(user, list) and len(user) == 1:
                    user = user[0]
                self.__tester = "%s %s" % (unicode(user['firstName']), unicode(user['lastName']))
            except NotSupported:
                pass
        return self.__tester

    def delete(self):
        """Delete this execution"""
        self._api.deleteExecution(self.id)

    def iterAttachment(self, **params):
        """Iterated over Execution attachments specified by parameters
        @returns: Matching Attachments
        @rtype: generator
        """
        # Get all attachments for this object
        response = self._api.getAttachments(self.id, "executions")
        attachments = [Attachment(api=self._api, **a) for a in response.values()]

        # Filter
        if len(params)>0:
            for attach in attachments:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        if not unicode(getattr(attach, key)) == unicode(value):
                            attach = None
                            break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Attachment: %s" % key)
                if attach is not None:
                    yield attach
        else:
            # Return all found attachments
            for attach in attachments:
                yield attach

    def getAttachment(self, **params):
        """Returns all Attachments specified by parameters
        @returns: Matching Attachments
        @rtype: mixed
        """
        return normalize_list([p for p in self.iterAttachment(**params)])
