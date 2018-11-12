#!/usr/bin/env python
# encoding: utf-8

import logging
import pytest
import pdb


@pytest.fixture(scope='module', autouse=True)
def case_module_hook(request, common):
    """
    automatically call `before_module(common)` and `after_module(common)`
    once call for each module
    """
    if request.module is None:
        return

    ns = '%s.py' % (request.module.__name__)

    log_print(1, 'STARTING MODULE %s' % ns)
    fn_call(request.module, 'before_module', 'SETUPING', ns, common)

    def module_teardown():
        fn_call(request.module, 'after_module', 'CLEANUPING', ns, common)
        log_print(1, 'COMPLETED MODULE %s' % ns)

    request.addfinalizer(module_teardown)


@pytest.fixture(scope='class', autouse=True)
def case_class_hook(request, common):
    """
    automatically call `before_class(cls,common)` and `after_class(cls,common)`
    once call for each class
    """
    if request.cls is None:
        return

    ns = '%s.py::%s' % (request.module.__name__, request.cls.__name__)

    log_print(1, 'STARTING CLASS %s' % ns)
    fn_call(request.cls, 'before_class', 'SETUPING', ns, common)

    def cls_teardown():
        fn_call(request.cls, 'after_class', 'CLEANUPING', ns, common)
        log_print(1, 'COMPLETED CLASS %s' % ns)

    request.addfinalizer(cls_teardown)


@pytest.fixture(scope='function', autouse=True)
def case_function_hook(request, common):
    """
    automatically call `cleanup_<case_name>(self,common)` after call `test_<case_name>(...)`
    automatically call `before_each_func(self,common)` and `after_each_func(self,common)`
    once call for each function
    """
    ns = request.module.__name__ + '.py'
    if request.cls is not None:
        ns = ns + '::' + request.cls.__name__

    fn_name_case = request.function.__name__
    fn_name_cleanup = 'cleanup_' + request.function.__name__[5:]
    log_print(1, 'STARTING FUNCTION %s::%s' % (ns, fn_name_case))

    fn_parent_obj = request.cls
    if request.cls is None:
        fn_parent_obj = request.module

    fn_call(fn_parent_obj, 'before_each_func', 'SETUPING', ns, common, request.instance)

    def func_teardown():
        #fn_call(fn_parent_obj, fn_name_cleanup, 'CLEANUPING', ns, common, request.instance)
        fn_call(fn_parent_obj, 'after_each_func', 'CLEANUPING', ns, common, request.instance)
        log_print(1, 'COMPLETED FUNCTION %s::%s' % (ns, fn_name_case))

    request.addfinalizer(func_teardown)


def fn_call(fn_parent_obj, fn_name, action, ns, common, instance=None):
    fn = getattr(fn_parent_obj, fn_name, None)
    if fn is None:
        return

    log_print(2, '%s %s::%s' % (action, ns, fn_name))
    if instance is None:
        fn(common)
    else:
        fn(instance, common)


def log_print(level, message):
    dim = '=' if level == 1 else '-'
    dim = dim * 60

    logging.info(dim)
    logging.info('    ' + message)
    logging.info(dim)


