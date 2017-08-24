#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Requirement Object"""

# IMPORTS
import datetime

from testlink.objects.tl_object import TestlinkObject
from testlink.objects.tl_object import normalize_list
from testlink.objects.tl_object import strptime

from testlink.objects.tl_risk import Risk
from testlink.objects.tl_attachment import IAttachmentGetter

from testlink.enums import REQUIREMENT_TYPE as REQUIREMENT_TYPE
from testlink.enums import REQUIREMENT_STATUS as REQUIREMENT_STATUS


class Requirement(TestlinkObject, IAttachmentGetter):
    """Testlink Requirement representation"""

    __slots__ = ("srs_id", "req_doc_id", "req_spec_title", "type", "version", "version_id", "revision",
                 "revision_id", "scope", "status", "node_order", "is_open", "active", "expected_coverage",
                 "testproject_id", "author", "author_id", "creation_ts", "modifier", "modifier_id", "modification_ts",
                 "_parent_testproject", "_parent_requirement_specification")

    def __init__(self, srs_id=None, req_doc_id='', title='', req_spec_title=None, version=-1, version_id=-1,
                 revision=-1, revision_id=-1, scope='', status=REQUIREMENT_STATUS.DRAFT, node_order=0, is_open="1",
                 active="1", expected_coverage=1, testproject_id=-1, author=None, author_id=-1,
                 creation_ts=str(datetime.datetime.min), modifier=None, modifier_id=-1,
                 modification_ts=str(datetime.datetime.min), api=None, parent_testproject=None,
                 parent_requirement_specification=None, **kwargs):
        """Initializes a new Requirement with the specified parameters
        @todo: doc
        """
        TestlinkObject.__init__(self, kwargs.get('id', -1), title, api)
        IAttachmentGetter.__init__(self)
        self.srs_id = str(srs_id)
        self.req_doc_id = unicode(req_doc_id)
        self.req_spec_title = req_spec_title
        self.type = int(kwargs.get('type', REQUIREMENT_TYPE.INFO))
        self.version = int(version)
        self.version_id = int(version_id)
        self.revision = int(revision)
        self.revision_id = int(revision_id)
        self.scope = scope
        self.status = str(status)
        self.node_order = int(node_order)
        self.is_open = bool(int(is_open))
        self.active = bool(int(active))
        self.expected_coverage = int(expected_coverage)
        self.testproject_id = int(testproject_id)
        self.author = unicode(author)
        self.author_id = int(author_id)
        self.modifier = unicode(modifier)
        try:
            self.modifier_id = int(modifier_id)
        except ValueError:
            self.modifier_id = -1
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
        return "Requirement %s: %s" % (self.req_doc_id, self.name)

    def __unicode__(self):
        return unicode(u"Requirement %s: %s" % (self.req_doc_id, self.name))

    def iterTestProject(self):
        """Returns the associated TestProject"
        @returns: TestProject
        @rtype: generator
        """
        yield self._parent_testproject

    def getTestProject(self):
        """Returns the associated TestProject"
        @returns: TestProject
        @rtype: TestProject
        """
        return self._parent_testproject

    def iterRequirementSpecification(self):
        """Returns the parent Requirement Specification
        @returns: RequirementSpecification
        @rtype: generator
        """
        yield self._parent_requirement_specification

    def getRequirementSpecification(self):
        """Returns the parent Requirement Specification
        @returns: RequirementSpecification
        @rtype: generator
        """
        return self._parent_requirement_specification

    def iterRisk(self, name=None, **params):
        """Returns all Risks with the specified parameters.
        @param name: The name of the wanted Risk
        @type name: str
        @returns: Matching Risks
        @rtype: generator
        """
        # No simple API call, so get all Risks for the current Requirement
        response = self._api.getRisksForRequirement(self.id)
        risks = [Risk(api=self._api, parent_testproject=self.getTestProject(), **risk) for risk in response]

        # Filter
        if len(params) > 0 or name:
            params['name'] = name
            for rk in risks:
                for key, value in params.items():
                    # Skip None
                    if value is None:
                        continue
                    try:
                        if not unicode(getattr(rk, key)) == unicode(value):
                            rk = None
                            break
                    except AttributeError:
                        raise AttributeError("Invalid Search Parameter for Risk: %s" % key)
                # Return found risk
                if rk is not None:
                    yield rk
        # Return all found risks
        else:
            for rk in risks:
                yield rk

    def getRisk(self, name=None, **params):
        """Returns all Risks with the specified parameters
        @param name: The name of the Risk
        @type name: str
        @returns: Matching Risks
        @rtype: mixed
        """
        return normalize_list([r for r in self.iterRisk(name, **params)])

    def iterCoverage(self, testplan=None, platform=None):
        """Returns Requirement Coverage within the specified context
        @param testplan: <OPTIONAL> Regard coverage within this testplan
        @type testplan: TestPlan
        @param platform: <OPTIONAL> Regard coverage within this platform
        @type platform: Platform
        @returns: TestCases covering this Requirement within the given context
        @rtype: generator
        """
        testplan_id = None
        platform_id = None
        if testplan is not None:
            testplan_id = testplan.id
        if platform is not None:
            platform_id = platform.id

        response = self._api.getRequirementCoverage(self.id, testplan_id, platform_id)
        if isinstance(response, list):
            for r in response:
                yield self.getTestProject().getTestCase(id=r['id'])

    def getCoverage(self, testplan=None, platform=None):
        """Returns Requirement Coverage within the specified context
        @param testplan: <OPTIONAL> Regard coverage within this testplan
        @type testplan: TestPlan
        @param platform: <OPTIONAL> Regard coverage within this platform
        @type platform: Platform
        @returns: TestCases covering this Requirement within the given context
        @rtype: mixed
        """
        return normalize_list([c for c in self.iterCoverage(testplan, platform)])
