# -*- coding: utf-8 -*-
#   Copyright (C) 2009 Stephan Peijnik (stephan@peijnik.at)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

__version__ = '0.9.0'

import inspect
import os
import warnings

from new import classobj

__all__ = ['ArgvalidateException',
    'DecoratorNonKeyLengthException', 'DecoratorKeyUnspecifiedException',
    'DecoratorStackingException', 'ArgumentTypeException',
    'func_args', 'method_args', 'return_value',
    'one_of', 'type_any', 'raises_exceptions', 'warns_kwarg_as_arg',
    'accepts', 'returns']

# Check for environment variables
argvalidate_warn = 0
if 'ARGVALIDATE_WARN' in os.environ:
    argvalidate_warn_str = os.environ['ARGVALIDATE_WARN']
    try:
        argvalidate_warn = int(argvalidate_warn_str)
    except ValueError:
        pass

argvalidate_warn_kwarg_as_arg = 0
if 'ARGVALIDATE_WARN_KWARG_AS_ARG' in os.environ:
    argvalidate_warn_kwarg_as_arg_str =\
         os.environ['ARGVALIDATE_WARN_KWARG_AS_ARG']
    try:
        argvalidate_warn_kwarg_as_arg =\
            int(argvalidate_warn_kwarg_as_arg_str)
    except ValueError:
        pass

class ArgvalidateException(Exception):
    """
    Base argvalidate exception.

    Used as base for all exceptions.

    """
    pass



class DecoratorNonKeyLengthException(ArgvalidateException):
    """
    Exception for invalid decorator non-keyword argument count.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * expected_count
        Number of arguments that were expected (int, read-only).

    * passed_count
        Number of arguments that were passed to the function (int, read-only).

    """
    def __init__(self, func_name, expected_count, passed_count):
        self.func_name = func_name
        self.expected_count = expected_count
        self.passed_count = passed_count
        msg = '%s: wrong number of non-keyword arguments specified in' %\
             (func_name) 
        msg += ' decorator (expected %d, got %d).' %\
             (expected_count, passed_count)
        ArgvalidateException.__init__(self, msg)

class DecoratorKeyUnspecifiedException(ArgvalidateException):
    """
    Exception for unspecified decorator keyword argument.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * arg_name
        Name of the keyword argument passed to the function, but not specified
        in the decorator (str, read-only).
        
    """
    def __init__(self, func_name, arg_name):
        self.func_name = func_name
        self.arg_name = arg_name
        msg = '%s: keyword argument %s not specified in decorator.' %\
            (func_name, arg_name)
        ArgvalidateException.__init__(self, msg)

class DecoratorStackingException(ArgvalidateException):
    """
    Exception for stacking a decorator with itself.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * decorator_name
        Name of the decorator that was stacked with itself (str, read-only).

    """
    def __init__(self, func_name, decorator_name):
        self.func_name = func_name
        self.decorator_name = decorator_name
        msg = '%s: decorator %s stacked with itself.' %\
            (func_name, decorator_name)
        ArgvalidateException.__init__(self, msg)

class ArgumentTypeException(ArgvalidateException):
    """
    Exception for invalid argument type.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (str, read-only).

    * arg_name
        Name of the keyword argument passed to the function, but not specified
        in the decorator (str, read-only).

    * expected_type
        Argument type that was expected (type, read-only).

    * passed_type
        Argument type that was passed to the function (type, read-only).

    """
    def __init__(self, func_name, arg_name, expected_type, passed_type):
        self.func_name = func_name
        self.arg_name = arg_name
        self.expected_type = expected_type
        self.passed_type = passed_type
        msg = '%s: invalid argument type for %r (expected %r, got %r).' %\
            (func_name, arg_name, expected_type, passed_type)
        ArgvalidateException.__init__(self, msg)

class ReturnValueTypeException(ArgvalidateException):
    """
    Exception for invalid return value type.

    This exception provides the following attributes:

    * func_name
        Name of function that caused the exception to be raised
        (string, read-only).

    * expected_type
        Argument type that was expected (type, read-only).

    * passed_type
        Type of value returned by the function (type, read-only).

    """
    def __init__(self, func_name, expected_type, passed_type):
        self.func_name = func_name
        self.expected_type = expected_type
        self.passed_type = passed_type
        msg = '%s: invalid type for return value (expected %r, got %r).' %\
            (func_name, expected_type, passed_type)
        ArgvalidateException.__init__(self, msg)

class KWArgAsArgWarning(ArgvalidateException):
    def __init__(self, func_name, arg_name):
        msg = '%s: argument %s is a keyword argument and was passed as a '\
            'non-keyword argument.' % (func_name, arg_name)
        ArgvalidateException.__init__(self, msg)

def __raise(exception, stacklevel=3):
    if argvalidate_warn:
        warnings.warn(exception, stacklevel=stacklevel)
    else:
        raise exception

def __check_return_value(func_name, expected_type, return_value):
    return_value_type = type(return_value)
    error = False

    if expected_type is None:
        error = False

    elif isinstance(return_value, classobj):
        if not isinstance(return_value, expected_type) and\
            not issubclass(return_value.__class__, expected_type):
                error=True
    else:
        if not isinstance(return_value, expected_type):
            error=True

    if error:
        __raise(ReturnValueTypeException(func_name, expected_type,\
             return_value_type), stacklevel=3)

def __check_type(func_name, arg_name, expected_type, passed_value,\
    stacklevel=4):
    passed_type = type(passed_value)
    error=False

    # None means the type is not checked
    if expected_type is None:
        error=False

    # Check a class
    elif isinstance(passed_value, classobj):
        if not isinstance(passed_value, expected_type) and\
            not issubclass(passed_value.__class__, expected_type):
            error=True
    
    # Check a type
    else:
        if not isinstance(passed_value, expected_type):
            error=True

    if error:
        __raise(ArgumentTypeException(func_name, arg_name, expected_type,\
            passed_type), stacklevel=stacklevel)

def __check_args(type_args, type_kwargs, start=-1):
    type_nonkey_argcount = len(type_args)
    type_key_argcount = len(type_kwargs)

    def validate(f):
        accepts_func = getattr(f, 'argvalidate_accepts_stacked_func', None)
        
        if accepts_func:
            if start == -1:
                raise DecoratorStackingException(accepts_func.func_name,\
                    'accepts')
            if start == 0:
                raise DecoratorStackingException(accepts_func.func_name,\
                     'function_accepts')
            elif start == 1:
                raise DecoratorStackingException(accepts_func.func_name,\
                     'method_accepts')
            else:
                raise DecoratorStackingException(accepts_func.func_name,\
                     'unknown; start=%d' % (start))

        func = getattr(f, 'argvalidate_returns_stacked_func', f)
        f_name = func.__name__
        (func_args, func_varargs, func_varkw, func_defaults) =\
             inspect.getargspec(func)

        func_argcount = len(func_args)
        is_method = True

        # The original idea was to use inspect.ismethod here,
        # but it seems as the decorator is called before the
        # method is bound to a class, so this will always
        # return False.
        # The new method follows the original idea of checking
        # tha name of the first argument passed.
        # self and cls indicate methods, everything else indicates
        # a function.
        if start < 0 and func_argcount > 0 and func_args[0] in ['self', 'cls']:
            func_argcount -= 1
            func_args = func_args[1:]
        elif start == 1:
            func_argcount -=1
            func_args = func_args[1:]
        else:
            is_method = False

        if func_varargs:
            func_args.remove(func_varargs)
            
        if func_varkw:
            func_args.remove(func_varkw)

        func_key_args = {}
        func_key_argcount = 0

        if func_defaults:
            func_key_argcount = len(func_defaults)
            tmp_key_args = zip(func_args[-func_key_argcount:], func_defaults)

            for tmp_key_name, tmp_key_default in tmp_key_args:
                func_key_args.update({tmp_key_name: tmp_key_default})

            # Get rid of unused variables
            del tmp_key_args
            del tmp_key_name
            del tmp_key_default

        func_nonkey_args = []
        if func_key_argcount < func_argcount:
            func_nonkey_args = func_args[:func_argcount-func_key_argcount]
        func_nonkey_argcount = len(func_nonkey_args)

        # Static check #0:
        #
        # Checking the lengths of type_args vs. func_args and type_kwargs vs.
        # func_key_args should be done here.
        #
        # This means that the check is only performed when the decorator
        # is actually invoked, not every time the target function is called.
        if func_nonkey_argcount != type_nonkey_argcount:
            __raise(DecoratorNonKeyLengthException(f_name,\
                func_nonkey_argcount, type_nonkey_argcount))
                
        if func_key_argcount != type_key_argcount:
            __raise(DecoratorKeyLengthException(f_name,\
                func_key_argcount, type_key_argcount))

        # Static check #1:
        #
        # kwarg default value types.
        if func_defaults:
            tmp_kw_zip = zip(func_args[-func_key_argcount:], func_defaults)
            for tmp_kw_name, tmp_kw_default in tmp_kw_zip:
                if not tmp_kw_name in type_kwargs:
                    __raise(DecoratorKeyUnspecifiedException(f_name,\
                         tmp_kw_name))
                
                tmp_kw_type = type_kwargs[tmp_kw_name]
                __check_type(f_name, tmp_kw_name, tmp_kw_type, tmp_kw_default)
            
            del tmp_kw_type
            del tmp_kw_name
            del tmp_kw_default
            del tmp_kw_zip

        def __wrapper_func(*call_args, **call_kwargs):
            call_nonkey_argcount = len(call_args)
            call_key_argcount = len(call_kwargs)
            call_nonkey_args = []

            if is_method:
                call_nonkey_args = call_args[1:]
            else:
                call_nonkey_args = call_args[:]

            # Dynamic check #1:
            #
            #
            # Non-keyword argument types.
            if type_nonkey_argcount > 0:
                tmp_zip = zip(call_nonkey_args, type_args,\
                     func_nonkey_args)
                for tmp_call_value, tmp_type, tmp_arg_name in tmp_zip:
                    __check_type(f_name, tmp_arg_name, tmp_type, tmp_call_value)


            # Dynamic check #2:
            #
            # Keyword arguments passed as non-keyword arguments.
            if type_nonkey_argcount < call_nonkey_argcount:
                tmp_kwargs_as_args = zip(call_nonkey_args[type_nonkey_argcount:],\
                    func_args[-func_key_argcount:])

                for tmp_call_value, tmp_kwarg_name in tmp_kwargs_as_args:
                    tmp_type = type_kwargs[tmp_kwarg_name]

                    if argvalidate_warn_kwarg_as_arg:
                        warnings.warn(KWArgAsArgWarning(f_name, tmp_kwarg_name))

                    __check_type(f_name, tmp_kwarg_name, tmp_type,\
                         tmp_call_value)

            # Dynamic check #3:
            #
            # Keyword argument types.
            if call_key_argcount > 0:
                for tmp_kwarg_name in call_kwargs:
                    if tmp_kwarg_name not in type_kwargs:
                        continue

                    tmp_call_value = call_kwargs[tmp_kwarg_name]
                    tmp_type = type_kwargs[tmp_kwarg_name]
                    __check_type(f_name, tmp_kwarg_name, tmp_type,\
                         tmp_call_value)
            
            return func(*call_args, **call_kwargs)

        
        __wrapper_func.func_name = func.__name__
        __wrapper_func.__doc__ = func.__doc__
        __wrapper_func.__dict__.update(func.__dict__)

        __wrapper_func.argvalidate_accepts_stacked_func = func
        return __wrapper_func
    
    return validate

def accepts(*type_args, **type_kwargs):
    """
    Decorator used for checking arguments passed to a function or method.

    :param start: method/function-detection override. The number of arguments
                  defined with start are ignored in all checks.

    :param type_args: type definitions of non-keyword arguments.
    :param type_kwargs: type definitions of keyword arguments.

    :raises DecoratorNonKeyLengthException: Raised if the number of non-keyword
        arguments specified in the decorator does not match the number of
        non-keyword arguments the function accepts.

    :raises DecoratorKeyLengthException: Raised if the number of keyword
        arguments specified in the decorator does not match the number of
        non-keyword arguments the function accepts.

    :raises DecoratorKeyUnspecifiedException: Raised if a keyword argument's
        type has not been specified in the decorator.

    :raises ArgumentTypeException: Raised if an argument type passed to the
        function does not match the type specified in the decorator.

    Example::

        class MyClass:
            @accepts(int, str)
            def my_method(self, x_is_int, y_is_str):
                [...]

        @accepts(int, str)
        def my_function(x_is_int, y_is_str):
            [....]

    """
    return __check_args(type_args, type_kwargs, start=-1)

def returns(expected_type):
    """
    Decorator used for checking the return value of a function or method.

    :param expected_type: expected type or return value

    :raises ReturnValueTypeException: Raised if the return value's type does not
        match the definition in the decorator's `expected_type` parameter.

    Example::
    
        @return_value(int)
        def my_func():
            return 5
            
    """
    def validate(f):

        returns_func = getattr(f, 'argvalidate_returns_stacked_func', None)
        if returns_func:
            raise DecoratorStackingException(returns_func.func_name,'returns')

        func = getattr(f, 'argvalidate_accepts_stacked_func', f)

        def __wrapper_func(*args, **kwargs):
            result = func(*args, **kwargs)
            __check_return_value(func.func_name, expected_type, result)
            return result

        __wrapper_func.func_name = func.__name__
        __wrapper_func.__doc__ = func.__doc__
        __wrapper_func.__dict__.update(func.__dict__)
            
        __wrapper_func.argvalidate_returns_stacked_func = func
        return __wrapper_func
    
    return validate

# Wrappers for old decorators
def return_value(expected_type):
    """
    Wrapper for backwards-compatibility.

    :deprecated: This decorator has been replaced with :func:`returns`.

    """
    warnings.warn(DeprecationWarning('The return_value decorator has been '\
        'deprecated. Please use the returns decorator instead.'))
    return returns(expected_type)


def method_args(*type_args, **type_kwargs):
    """
    Wrapper for backwards-compatibility.

    :deprecated: This decorator has been replaced with :func:`accepts`.

    """
    warnings.warn(DeprecationWarning('The method_args decorator has been '\
        'deprecated. Please use the accepts decorator instead.'))
    return __check_args(type_args, type_kwargs, start=1)

def func_args(*type_args, **type_kwargs):
    """
    Wrapper for backwards-compatibility.

    :deprecated: This decorator has been replaced with :func:`accepts`.
    """
    warnings.warn(DeprecationWarning('The func_args decorator has been '\
        'deprecated. Please use the accepts decorator instead.'))
    return __check_args(type_args, type_kwargs, start=0)


class __OneOfTuple(tuple):
    def __repr__(self):
        return 'one of %r' % (tuple.__repr__(self))

# Used for readability, using a tuple alone would be sufficient.
def one_of(*args):
    """
    Simple helper function to create a tuple from every argument passed to it.

    :param args: type definitions

    A tuple can be used instead of calling this function, however, the tuple
    returned by this function contains a customized __repr__ method, which
    makes Exceptions easier to read.

    Example::

        @func_check_args(one_of(int, str, float))
        def my_func(x):
            pass
            
    """
    return __OneOfTuple(args)

def raises_exceptions():
    """
    Returns True if argvalidate raises exceptions, False if argvalidate
    creates warnings instead.

    This behaviour can be controlled via the environment variable
    :envvar:`ARGVALIDATE_WARN`.
    """
    return not argvalidate_warn

def warns_kwarg_as_arg():
    """
    Returns True if argvalidate generates warnings for keyword arguments
    passed as arguments.

    This behaviour can be controlled via the environment variable
    :envvar:`ARGVALIDATE_WARN_KWARG_AS_ARG`.
    """
    return argvalidate_kwarg_as_arg

# Used for readbility, using None alone would be sufficient
type_any = None
