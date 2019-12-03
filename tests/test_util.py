#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Kai Borowiak

TestSuite for testlink.util
"""

# IMPORTS
import unittest

from testlink.util import lazy

class LazyLoadingTest(unittest.TestCase):
    """Tests for LazyLoading Decorator"""

    def __init__(self, *args, **kwargs):
        super(LazyLoadingTest, self).__init__(*args, **kwargs)
        self._testMethodDoc = 'LazyLoading: ' + self._testMethodDoc

    def test_lazy_loading(self):
        """Caching"""

        # Initialize Test Object
        testobject = object()

        # Generate Testclass as closure
        class TestClass:
            def __init__(self):
                self.called = 0
            @lazy
            def attribute(self):
                self.called += 1  
                return testobject

        # Initialize TestClass instance
        testclass = TestClass()

        # Check that nothing has been loaded yet
        self.assertFalse(hasattr(testclass, '_lazy_attribute'))
        self.assertEqual(testclass.called, 0)

        # Access attribute first time
        # Check that loader has been called
        self.assertEqual(testclass.attribute, testobject)
        self.assertEqual(testclass.called, 1)

        # Check that lazy attribute has been created and internal
        # attribute is set to value from lazy loading function
        self.assertTrue(hasattr(testclass, '_lazy_attribute'))
        self.assertEqual(testclass._lazy_attribute, testobject)

        # Finally, check that property access still returns correct object
        # And that loader is not called anymore
        for _ in xrange(5):
            self.assertEqual(testclass.attribute, testobject)
            self.assertEqual(testclass.called, 1)

    def test_pre_initialisation(self):
        """Preset cached value"""

        # Initialize Test Object
        testobject = object()

        # Generate Testcass as closure
        class TestClass:
            def __init__(self):
                self._lazy_attribute = testobject
            @lazy
            def attribute(self):
                # Raise Exception, since this
                # code should not run
                raise NotImplementedError()

        # Initialize TestClass instance
        testclass = TestClass()

        # Access attribute first time
        # Check that loader has NOT been called
        self.assertEqual(testclass.attribute, testobject)

    def test_pre_none_initialisation(self):
        """Preset cached value with None"""

        # Initialize Test Object
        testobject = object()

        # Generate Testcass as closure
        class TestClass:
            def __init__(self):
                self._lazy_attribute = None
            @lazy
            def attribute(self):
                return testobject

        # Initialize TestClass instance
        testclass = TestClass()

        # Access attribute first time
        # Check that loader has NOT been called
        self.assertEqual(testclass.attribute, testobject)
