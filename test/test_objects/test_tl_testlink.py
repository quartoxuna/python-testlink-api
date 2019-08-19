# pylint: disable=missing-docstring

# IMPORTS
import unittest
import mock

from testlink.api.xmlrpc import TestlinkXMLRPCAPI
from testlink.api.xmlrpc import TestlinkAPI
from testlink.objects.tl_testlink import Testlink

from testlink.objects.tl_testproject import TestProject

class TestlinkTests(unittest.TestCase):

    def test_initialization(self):
        """Test default initialisation"""
        proxy = mock.MagicMock()
        api = TestlinkXMLRPCAPI(proxy)

        testlink = Testlink(api)
        self.assertEqual(testlink.api, api)

    def test_iterate_testprojects(self):
        """Iterate over testprojects"""
        # Initialize Testlink Object
        testlink_api = mock.create_autospec(spec=TestlinkAPI)
        testlink = Testlink(testlink_api)

        # Prepare Server Mock
        testlink_api.getProjects = mock.MagicMock()
        testlink_api.getProjects.return_value = [
            {'id': '123', 'name': "TestProject1", 'prefix': 'ABC',
             'notes': "Description TestProject 1", 'active': '0', 'is_public': '1',
             'color': '#00FF00', 'tc_counter': '42',
             'opt': {
                 'requirementsEnabled': '1',
                 'testPriorityEnabled': '0',
                 'automationEnabled': '1',
                 'inventoryEnabled': '0'
             }
            },
            {'id': '456', 'name': "TestProject2", 'prefix': 'DEF',
             'notes': "Description TestProject 2", 'active': '1', 'is_public': '0',
             'color': '#FF0000', 'tc_counter': '23',
             'opt': {
                 'requirementsEnabled': '0',
                 'testPriorityEnabled': '1',
                 'automationEnabled': '0',
                 'inventoryEnabled': '1'
             }
            }
        ]

        # Generate expected results
        expected_projects = [
            TestProject.builder()\
            .with_id(123)\
            .from_testlink(testlink)\
            .with_name("TestProject1")\
            .with_description("Description TestProject 1")\
            .with_prefix("ABC")\
            .is_not_active()\
            .is_public()\
            .with_color('#00FF00')\
            .with_testcase_count(42)\
            .with_requirement_feature()\
            .with_automation_feature()\
            .without_priority_feature()\
            .without_inventory_feature()\
            .build(),
            TestProject.builder()\
            .with_id(456)\
            .from_testlink(testlink)\
            .with_name("TestProject2")\
            .with_description("Description TestProject 2")\
            .with_prefix("DEF")\
            .is_active()\
            .is_not_public()\
            .with_color('#FF0000')\
            .with_testcase_count(23)\
            .without_requirement_feature()\
            .without_automation_feature()\
            .with_priority_feature()\
            .with_inventory_feature()\
            .build()
        ]

        # Check results
        for i, testproject in enumerate(testlink.testprojects):
            expected = expected_projects[i]
            self.assertEqual(expected, testproject)
            self.assertEqual(expected.id, testproject.id)
            self.assertEqual(expected.testlink, testproject.testlink)
            self.assertEqual(expected.name, testproject.name)
            self.assertEqual(expected.description, testproject.description)
            self.assertEqual(expected.prefix, testproject.prefix)
            self.assertEqual(expected.active, testproject.active)
            self.assertEqual(expected.public, testproject.public)
            self.assertEqual(expected.color, testproject.color)
            self.assertEqual(expected.requirement_feature, testproject.requirement_feature)
            self.assertEqual(expected.priority_feature, testproject.priority_feature)
            self.assertEqual(expected.automation_feature, testproject.automation_feature)
            self.assertEqual(expected.inventory_feature, testproject.inventory_feature)
        self.assertTrue(len(list(testlink.testprojects)) == 2)
