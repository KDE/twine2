#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
############################################################################
# sealed.py                                                                #
#                                                                          #
# Copyright (C) 2007 by Simon Edwards <simon@simonzone.com>                #
#                                                                          #
# This program is free software; you can redistribute it and/or modify     #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
############################################################################
import sys

def sealed(func):
    """Decorator to seal an object after initialisation
    
    This decorator can be used to enforce the initialisation pattern where
    any attributes are initialised in __init__() and no other attributes
    can be added once initialisation has been done.
    
    This decorator should be applied to __init__ methods.
    
    >>> x = MyNormalClass()
    >>> x.new_attribute_y = True   # <- Succeeds as normal
    
    >>> x = MySealedClass()
    >>> x.new_attribute_y = True   # <- Raises an AttributeError
    """
    def sealing_init(self, *args, **kw):
        func(self, *args, **kw)
        
        # Do not do anything if we are called from the __init__ method of a subclass.
        caller = sys._getframe(1)
        if caller.f_code.co_name=='__init__':
            if 'self' in caller.f_locals:
                if caller.f_locals['self'] is self:
                    return

        # Only create the wedge class once.
        if sealing_init.wedge_class is None:
            class wedge_class(self.__class__):
                def __setattr__(self,name,value):
                    getattr(self,name)
                    #if name not in self.__dict__:  
                    #    raise AttributeError("No new attributes may be added to this object.")
                    super(wedge_class,self).__setattr__(name,value)
            sealing_init.wedge_class = wedge_class
            sealing_init.wedge_class.__name__ = self.__class__.__name__+" @sealed"
        # Replace the class of self with a new one that has a modified __setattr__.
        self.__class__ = sealing_init.wedge_class
        
    sealing_init.wedge_class = None
    return sealing_init
