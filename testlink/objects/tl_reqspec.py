#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ReqSpec Object"""

# IMPORTS
import datetime

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list
from testlink.objects.tl_object import strptime

from testlink.objects.tl_req import Requirement
from testlink.objects.tl_attachment import IAttachmentGetter

from testlink.enums import REQSPEC_TYPE


class RequirementSpecification(TestlinkObject, IAttachmentGetter):
    """Testlink Requirement Specification representation"""

    __slots__ = ("doc_id", "typ", "scope", "testproject_id", "author_id", "creation_ts",
                 "modifier_id", "modification_ts", "total_req", "node_order", "_parent_testproject",
                 "_parent_requirement_specification")

    def __init__(self, doc_id='', title='', typ=REQSPEC_TYPE.SECTION, scope='', testproject_id=-1, author_id=-1,
                 creation_ts=str(datetime.datetime.min), modifier_id=-1, modification_ts=str(datetime.datetime.min),
                 total_req=0, node_order=0, parent_testproject=None, parent_requirement_specification=None,
                 *args, **kwargs):
        """Initializes a new Requirement Specification with the specified parameters.
        @todo: doc
        """
        kwargs['name'] = title
        super(RequirementSpecification, self).__init__(*args, **kwargs)
        self.doc_id = unicode(doc_id)
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
        self._parent_requirement_specification = parent_requirement_specification

    def __str__(self):
        return "Requirement Specification %s: %s" % (self.doc_id, self.name)

    def getTestProject(self):
        """Returns associated TestProject"""
        return self._parent_testproject

    def iterRequirementSpecification(self, name=None, recursive=False, **params):
        """Returns all Requirement Specifications specified by parameters
        @param name: The name of the Requirement Specification
        @type name: str
        @param recursive: Search recursive to get all nested Requirement Specifications
        @type recursive: bool
        @returns: Matching Requirement Specifications
        @rtype: generator
        """
        # Simple API call not possible
        response = self._api.getRequirementSpecificationsForRequirementSpecification(self.id)
        specs = [RequirementSpecification(api=self._api, parent_testproject=self.getTestProject(),
                                          parent_requirement_specification=self, **reqspec) for reqspec in response]

        # Filter
        if len(params) > 0 or name:
            params['name'] = name
            for rspec in specs:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        try:
                            if not unicode(getattr(rspec, key)) == unicode(value):
                                rspec = None
                                break
                        except AttributeError:
                            # Try to treat as custom field
                            cf_val = self._api.getReqSpecCustomFieldDesignValue(rspec.id,
                                                                                rspec.getTestProject().id,
                                                                                key)
                            if not unicode(cf_val) == unicode(value):
                                rspec = None
                                break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Requirement Specification: %s" % key)
                if rspec is not None:
                    yield rspec
            # If recursive is specified,
            # also search in nested specs
            if recursive:
                # For each reqspec of this level
                for rspec in specs:
                    # Yield nested specs that match
                    for r in rspec.iterRequirementSpecification(recursive=recursive, **params):
                        yield r
        # Return all Requirement Specifications
        else:
            for rspec in specs:
                # First return the reqspecs from this level,
                # then return nested ones if recursive is specified
                yield rspec
                if recursive:
                    for r in rspec.iterRequirementSpecification(name=name, recursive=recursive, **params):
                        yield r

    def getRequirementSpecification(self, name=None, recursive=False, **params):
        """Returns all Requirement Specifications specified by parameters
        @param name: The name of the Requirement Specification
        @type name: str
        @param recursive: Search recursive to get all nested Requirement Specifications
        @type recursive: bool
        @returns: Matching Requirement Specifications
        @rtype: mixed
        """
        return normalize_list([r for r in self.iterRequirementSpecification(name, recursive, **params)])

    def iterRequirement(self, name=None, **params):
        """Iterates over Requirements specified by parameters
        @param name: The title of the wanted Requirement
        @type name: str
        @returns: Matching Requirements
        @rtype: generator
        """
        # No Simple API Call possible, get all and convert to Requirement instances
        response = self._api.getRequirementsForRequirementSpecification(self.id, self.getTestProject().id)
        requirements = [Requirement(api=self._api, parent_testproject=self.getTestProject(),
                                    parent_requirement_specification=self, **req) for req in response]

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
                            cf_val = self._api.getRequirementCustomFieldDesignValue(req.id,
                                                                                    req.getTestProject().id,
                                                                                    key)
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
