# -*- coding: utf-8 -*-
from operator import attrgetter
from pyangbind.lib.yangtypes import RestrictedPrecisionDecimalType
from pyangbind.lib.yangtypes import RestrictedClassType
from pyangbind.lib.yangtypes import TypedListType
from pyangbind.lib.yangtypes import YANGBool
from pyangbind.lib.yangtypes import YANGListType
from pyangbind.lib.yangtypes import YANGDynClass
from pyangbind.lib.yangtypes import ReferenceType
from pyangbind.lib.base import PybindBase
from collections import OrderedDict
from decimal import Decimal
from bitarray import bitarray
import six

# PY3 support of some PY2 keywords (needs improved)
if six.PY3:
  import builtins as __builtin__
  long = int
elif six.PY2:
  import __builtin__

class yc_probes_brewerslab__tests_temperature_probes(PybindBase):
  """
  This class was auto-generated by the PythonClass plugin for PYANG
  from YANG module brewerslab - based on the path /tests/temperature/probes. Each member element of
  the container is represented as a class variable - with a specific
  YANG type.
  """
  __slots__ = ('_path_helper', '_extmethods', '__probeid','__run','__value',)

  _yang_name = 'probes'

  _pybind_generated_by = 'container'

  def __init__(self, *args, **kwargs):

    self._path_helper = False

    self._extmethods = False
    self.__probeid = YANGDynClass(base=[RestrictedClassType(base_type=six.text_type, restriction_dict={'pattern': '28-[0-9a-f]{1,32}'}),], is_leaf=True, yang_name="probeid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='brewerslab-types:temperature-probe', is_config=True)
    self.__run = YANGDynClass(base=YANGBool, is_leaf=True, yang_name="run", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='boolean', is_config=True)
    self.__value = YANGDynClass(base=RestrictedPrecisionDecimalType(precision=3), is_leaf=True, yang_name="value", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='brewerslab-types:temperature', is_config=True)

    load = kwargs.pop("load", None)
    if args:
      if len(args) > 1:
        raise TypeError("cannot create a YANG container with >1 argument")
      all_attr = True
      for e in self._pyangbind_elements:
        if not hasattr(args[0], e):
          all_attr = False
          break
      if not all_attr:
        raise ValueError("Supplied object did not have the correct attributes")
      for e in self._pyangbind_elements:
        nobj = getattr(args[0], e)
        if nobj._changed() is False:
          continue
        setmethod = getattr(self, "_set_%s" % e)
        if load is None:
          setmethod(getattr(args[0], e))
        else:
          setmethod(getattr(args[0], e), load=load)

  def _path(self):
    if hasattr(self, "_parent"):
      return self._parent._path()+[self._yang_name]
    else:
      return ['tests', 'temperature', 'probes']

  def _get_probeid(self):
    """
    Getter method for probeid, mapped from YANG variable /tests/temperature/probes/probeid (brewerslab-types:temperature-probe)
    """
    return self.__probeid
      
  def _set_probeid(self, v, load=False):
    """
    Setter method for probeid, mapped from YANG variable /tests/temperature/probes/probeid (brewerslab-types:temperature-probe)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_probeid is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_probeid() directly.
    """
    parent = getattr(self, "_parent", None)
    if parent is not None and load is False:
      raise AttributeError("Cannot set keys directly when" +
                             " within an instantiated list")

    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=[RestrictedClassType(base_type=six.text_type, restriction_dict={'pattern': '28-[0-9a-f]{1,32}'}),], is_leaf=True, yang_name="probeid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='brewerslab-types:temperature-probe', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """probeid must be of a type compatible with brewerslab-types:temperature-probe""",
          'defined-type': "brewerslab-types:temperature-probe",
          'generated-type': """YANGDynClass(base=[RestrictedClassType(base_type=six.text_type, restriction_dict={'pattern': '28-[0-9a-f]{1,32}'}),], is_leaf=True, yang_name="probeid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='brewerslab-types:temperature-probe', is_config=True)""",
        })

    self.__probeid = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_probeid(self):
    self.__probeid = YANGDynClass(base=[RestrictedClassType(base_type=six.text_type, restriction_dict={'pattern': '28-[0-9a-f]{1,32}'}),], is_leaf=True, yang_name="probeid", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, is_keyval=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='brewerslab-types:temperature-probe', is_config=True)


  def _get_run(self):
    """
    Getter method for run, mapped from YANG variable /tests/temperature/probes/run (boolean)

    YANG Description: Describes if we want the test to be running or not.
    """
    return self.__run
      
  def _set_run(self, v, load=False):
    """
    Setter method for run, mapped from YANG variable /tests/temperature/probes/run (boolean)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_run is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_run() directly.

    YANG Description: Describes if we want the test to be running or not.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=YANGBool, is_leaf=True, yang_name="run", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='boolean', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """run must be of a type compatible with boolean""",
          'defined-type': "boolean",
          'generated-type': """YANGDynClass(base=YANGBool, is_leaf=True, yang_name="run", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='boolean', is_config=True)""",
        })

    self.__run = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_run(self):
    self.__run = YANGDynClass(base=YANGBool, is_leaf=True, yang_name="run", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='boolean', is_config=True)


  def _get_value(self):
    """
    Getter method for value, mapped from YANG variable /tests/temperature/probes/value (brewerslab-types:temperature)

    YANG Description: The temperature we want to report.
    """
    return self.__value
      
  def _set_value(self, v, load=False):
    """
    Setter method for value, mapped from YANG variable /tests/temperature/probes/value (brewerslab-types:temperature)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_value is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_value() directly.

    YANG Description: The temperature we want to report.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=RestrictedPrecisionDecimalType(precision=3), is_leaf=True, yang_name="value", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='brewerslab-types:temperature', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """value must be of a type compatible with brewerslab-types:temperature""",
          'defined-type': "brewerslab-types:temperature",
          'generated-type': """YANGDynClass(base=RestrictedPrecisionDecimalType(precision=3), is_leaf=True, yang_name="value", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='brewerslab-types:temperature', is_config=True)""",
        })

    self.__value = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_value(self):
    self.__value = YANGDynClass(base=RestrictedPrecisionDecimalType(precision=3), is_leaf=True, yang_name="value", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='brewerslab-types:temperature', is_config=True)

  probeid = __builtin__.property(_get_probeid, _set_probeid)
  run = __builtin__.property(_get_run, _set_run)
  value = __builtin__.property(_get_value, _set_value)


  _pyangbind_elements = OrderedDict([('probeid', probeid), ('run', run), ('value', value), ])


class yc_temperature_brewerslab__tests_temperature(PybindBase):
  """
  This class was auto-generated by the PythonClass plugin for PYANG
  from YANG module brewerslab - based on the path /tests/temperature. Each member element of
  the container is represented as a class variable - with a specific
  YANG type.
  """
  __slots__ = ('_path_helper', '_extmethods', '__probes',)

  _yang_name = 'temperature'

  _pybind_generated_by = 'container'

  def __init__(self, *args, **kwargs):

    self._path_helper = False

    self._extmethods = False
    self.__probes = YANGDynClass(base=YANGListType("probeid",yc_probes_brewerslab__tests_temperature_probes, yang_name="probes", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='probeid', extensions=None), is_container='list', yang_name="probes", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='list', is_config=True)

    load = kwargs.pop("load", None)
    if args:
      if len(args) > 1:
        raise TypeError("cannot create a YANG container with >1 argument")
      all_attr = True
      for e in self._pyangbind_elements:
        if not hasattr(args[0], e):
          all_attr = False
          break
      if not all_attr:
        raise ValueError("Supplied object did not have the correct attributes")
      for e in self._pyangbind_elements:
        nobj = getattr(args[0], e)
        if nobj._changed() is False:
          continue
        setmethod = getattr(self, "_set_%s" % e)
        if load is None:
          setmethod(getattr(args[0], e))
        else:
          setmethod(getattr(args[0], e), load=load)

  def _path(self):
    if hasattr(self, "_parent"):
      return self._parent._path()+[self._yang_name]
    else:
      return ['tests', 'temperature']

  def _get_probes(self):
    """
    Getter method for probes, mapped from YANG variable /tests/temperature/probes (list)
    """
    return self.__probes
      
  def _set_probes(self, v, load=False):
    """
    Setter method for probes, mapped from YANG variable /tests/temperature/probes (list)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_probes is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_probes() directly.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=YANGListType("probeid",yc_probes_brewerslab__tests_temperature_probes, yang_name="probes", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='probeid', extensions=None), is_container='list', yang_name="probes", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='list', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """probes must be of a type compatible with list""",
          'defined-type': "list",
          'generated-type': """YANGDynClass(base=YANGListType("probeid",yc_probes_brewerslab__tests_temperature_probes, yang_name="probes", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='probeid', extensions=None), is_container='list', yang_name="probes", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='list', is_config=True)""",
        })

    self.__probes = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_probes(self):
    self.__probes = YANGDynClass(base=YANGListType("probeid",yc_probes_brewerslab__tests_temperature_probes, yang_name="probes", parent=self, is_container='list', user_ordered=False, path_helper=self._path_helper, yang_keys='probeid', extensions=None), is_container='list', yang_name="probes", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='list', is_config=True)

  probes = __builtin__.property(_get_probes, _set_probes)


  _pyangbind_elements = OrderedDict([('probes', probes), ])


class yc_tests_brewerslab__tests(PybindBase):
  """
  This class was auto-generated by the PythonClass plugin for PYANG
  from YANG module brewerslab - based on the path /tests. Each member element of
  the container is represented as a class variable - with a specific
  YANG type.
  """
  __slots__ = ('_path_helper', '_extmethods', '__temperature',)

  _yang_name = 'tests'

  _pybind_generated_by = 'container'

  def __init__(self, *args, **kwargs):

    self._path_helper = False

    self._extmethods = False
    self.__temperature = YANGDynClass(base=yc_temperature_brewerslab__tests_temperature, is_container='container', yang_name="temperature", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='container', is_config=True)

    load = kwargs.pop("load", None)
    if args:
      if len(args) > 1:
        raise TypeError("cannot create a YANG container with >1 argument")
      all_attr = True
      for e in self._pyangbind_elements:
        if not hasattr(args[0], e):
          all_attr = False
          break
      if not all_attr:
        raise ValueError("Supplied object did not have the correct attributes")
      for e in self._pyangbind_elements:
        nobj = getattr(args[0], e)
        if nobj._changed() is False:
          continue
        setmethod = getattr(self, "_set_%s" % e)
        if load is None:
          setmethod(getattr(args[0], e))
        else:
          setmethod(getattr(args[0], e), load=load)

  def _path(self):
    if hasattr(self, "_parent"):
      return self._parent._path()+[self._yang_name]
    else:
      return ['tests']

  def _get_temperature(self):
    """
    Getter method for temperature, mapped from YANG variable /tests/temperature (container)
    """
    return self.__temperature
      
  def _set_temperature(self, v, load=False):
    """
    Setter method for temperature, mapped from YANG variable /tests/temperature (container)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_temperature is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_temperature() directly.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=yc_temperature_brewerslab__tests_temperature, is_container='container', yang_name="temperature", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='container', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """temperature must be of a type compatible with container""",
          'defined-type': "container",
          'generated-type': """YANGDynClass(base=yc_temperature_brewerslab__tests_temperature, is_container='container', yang_name="temperature", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='container', is_config=True)""",
        })

    self.__temperature = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_temperature(self):
    self.__temperature = YANGDynClass(base=yc_temperature_brewerslab__tests_temperature, is_container='container', yang_name="temperature", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='container', is_config=True)

  temperature = __builtin__.property(_get_temperature, _set_temperature)


  _pyangbind_elements = OrderedDict([('temperature', temperature), ])


class brewerslab(PybindBase):
  """
  This class was auto-generated by the PythonClass plugin for PYANG
  from YANG module brewerslab - based on the path /brewerslab. Each member element of
  the container is represented as a class variable - with a specific
  YANG type.
  """
  __slots__ = ('_path_helper', '_extmethods', '__tests',)

  _yang_name = 'brewerslab'

  _pybind_generated_by = 'container'

  def __init__(self, *args, **kwargs):

    self._path_helper = False

    self._extmethods = False
    self.__tests = YANGDynClass(base=yc_tests_brewerslab__tests, is_container='container', yang_name="tests", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='container', is_config=True)

    load = kwargs.pop("load", None)
    if args:
      if len(args) > 1:
        raise TypeError("cannot create a YANG container with >1 argument")
      all_attr = True
      for e in self._pyangbind_elements:
        if not hasattr(args[0], e):
          all_attr = False
          break
      if not all_attr:
        raise ValueError("Supplied object did not have the correct attributes")
      for e in self._pyangbind_elements:
        nobj = getattr(args[0], e)
        if nobj._changed() is False:
          continue
        setmethod = getattr(self, "_set_%s" % e)
        if load is None:
          setmethod(getattr(args[0], e))
        else:
          setmethod(getattr(args[0], e), load=load)

  def _path(self):
    if hasattr(self, "_parent"):
      return self._parent._path()+[self._yang_name]
    else:
      return []

  def _get_tests(self):
    """
    Getter method for tests, mapped from YANG variable /tests (container)
    """
    return self.__tests
      
  def _set_tests(self, v, load=False):
    """
    Setter method for tests, mapped from YANG variable /tests (container)
    If this variable is read-only (config: false) in the
    source YANG file, then _set_tests is considered as a private
    method. Backends looking to populate this variable should
    do so via calling thisObj._set_tests() directly.
    """
    if hasattr(v, "_utype"):
      v = v._utype(v)
    try:
      t = YANGDynClass(v,base=yc_tests_brewerslab__tests, is_container='container', yang_name="tests", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='container', is_config=True)
    except (TypeError, ValueError):
      raise ValueError({
          'error-string': """tests must be of a type compatible with container""",
          'defined-type': "container",
          'generated-type': """YANGDynClass(base=yc_tests_brewerslab__tests, is_container='container', yang_name="tests", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='container', is_config=True)""",
        })

    self.__tests = t
    if hasattr(self, '_set'):
      self._set()

  def _unset_tests(self):
    self.__tests = YANGDynClass(base=yc_tests_brewerslab__tests, is_container='container', yang_name="tests", parent=self, path_helper=self._path_helper, extmethods=self._extmethods, register_paths=True, extensions=None, namespace='http://brewerslabng.mellon-collie.net/yang/main', defining_module='brewerslab', yang_type='container', is_config=True)

  tests = __builtin__.property(_get_tests, _set_tests)


  _pyangbind_elements = OrderedDict([('tests', tests), ])


