#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility methods
"""

# IMPORTS

__all__ = ["lazy"]

def lazy(loader):
    """Decorator for lazy loading properties"""

    # Attribute name for real attr_name
    attr_name = '_lazy_' + loader.__name__

    @property
    def _lazy(self):
        if getattr(self, attr_name, None) is None:
            setattr(self, attr_name, loader(self))
        return getattr(self, attr_name)
    return _lazy
