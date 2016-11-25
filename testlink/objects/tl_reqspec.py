#!/usr/bin/env python
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=star-args
# -*- coding: utf-8 -*-

"""ReqSpec Object"""

# IMPORTS
import datetime

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list
from testlink.objects.tl_object import _STRPTIME_FUNC as strptime

from testlink.objects.tl_req import Requirement
from testlink.objects.tl_attachment import IAttachmentGetter

from testlink.enums import REQSPEC_TYPE as RequirementSpecificationType

class RequirementSpecification(TestlinkObject, IAttachmentGetter):
    """Testlink Requirement Specification representation"""

    __slots__ = ("doc_id", "typ", "scope", "testproject_id", "author_id", "creation_ts",\
            "modifier_id", "modification_ts", "total_req", "node_order", "_parent_testproject")

    def __init__(\
            self,\
            doc_id='',\
            title='',\
            typ=RequirementSpecificationType.SECTION,\
            scope='',\
            testproject_id=-1,\
            author_id=-1,\
            creation_ts=str(datetime.datetime.min),\
            modifier_id=-1,\
            modification_ts=str(datetime.datetime.min),\
            total_req=0,\
            node_order=0,\
            api=None,\
            parent_testproject=None,\
            **kwargs\
            ):
        """Initializes a new Requirement Specification with the specified parameters.
        @todo: doc
        """
        TestlinkObject.__init__(self, kwargs.get('id'), title, api)
        IAttachmentGetter.__init__(self)
        self.doc_id = str(doc_id)
        self.typ = int(typ)
        self.scope = scope
        self.testproject_id = int(testproject_id)
        self.author_id = int(author_id)
        try:
            self.modifier_id = int(modifier_id)
        except ValueError:
            self.modifier_id = -1
        self.total_req = int(total_req)
        self.node_order = int(node_order)
        try:
            self.creation_ts = strptime(str(creation_ts), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.creation_ts = datetime.datetime.min
        try:
            self.modification_ts = strptime(str(modification_ts), TestlinkObject.DATETIME_FORMAT)
        except ValueError:
            self.modification_ts = datetime.datetime.min
        self._parent_testproject = parent_testproject

    def __str__(self):
        return "Requirement Specification %s: %s" % (self.doc_id, self.name)

    def getTestProject(self):
        """Returns associated TestProject"""
        return self._parent_testproject

    def iterRequirement(self, name=None, **params):
        """Iterates over Requirements specified by parameters
        @param name: The title of the wanted Requirement
        @type name: str
        @returns: Matching Requirements
        @rtype: generator
        """
        # No Simple API Call possible, get all and convert to Requirement instances
        response = self._api.getRequirementsForRequirementSpecification(self.id, self.getTestProject().id)
        requirements = [Requirement(api=self._api, parent_testproject=self.getTestProject(), **req) for req in response]

        # Filter
        if len(params) > 0 or name:
            params['name'] = name
            for req in requirements:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        try:
                            if not unicode(getattr(req, key)) == unicode(value):
                                req = None
                                break
                        except AttributeError:
                            # Try as custom field
                            cf_val = self._api.getRequirementCustomFieldDesignValue(req.id, req.getTestProject().id, key)
                            if not unicode(cf_val) == unicode(value):
                                req = None
                                break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Requirement: %s" % key)
                if req is not None:
                    yield req
        # Return all Requirements
        else:
            for req in requirements:
                yield req

    def getRequirement(self, name=None, **params):
        """Returns all Requirements with the specified parameters
        @param name: The title of the wanted Requirement
        @type name: str
        @returns: Matching Requirements
        @rtype: mixed
        """
        return normalize_list([r for r in self.iterRequirement(name, **params)])

