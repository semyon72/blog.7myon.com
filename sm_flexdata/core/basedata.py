# Project: blog_7myon_com
# Package: 
# Filename: basedata.py
# Generated: 2020 Dec 18 at 04:40 
# Description of <basedata>
#
# @author Semyon Mamonov <semyon.mamonov@gmail.com>


from functools import cached_property

class BaseData:
    """
        Main ideology is that self.data can be one of 3 states
            1 - None
            2 - list - it will consider as sequence
            3 - any other types that considering like sole value

        By default, setter of "data" property is attribute set_data(value).
        It considers the "value" as iterable data, excluding instances that have type
        pointed in ignore_iterable_types tuple. By default it contains only str type,
        and for each element of iterator run self._on_process_data(value) for some customization.
        If data is not iterable it also will be passed to self._process_data(value)

        Method "set_data" does not do any recursions.
    """

    ignore_iterable_types = (str, )
    """
        tuple of types that are iterable but does not considering as such
    """

    def __init__(self, data=None):
        self.__data = None
        self.data = data

    def is_sole_data(self):
        """
            Main ideology is that self.data can be one of 3 states
            1 - None - it considering like sole value
            2 - list - it will consider as sequence
            3 - any other types that considering like sole value also
        """
        return type(self.data) is not list

    def _on_process_value(self, value):
        return value

    def _process_value(self, value):
        if hasattr(value, '__iter__') and not isinstance(value, self.ignore_iterable_types):
            if isinstance(value, dict):
                value = (v for v in value.values())
            result = [self._on_process_value(v) for v in value]
        else:
            result = self._on_process_value(value)
        return result

    def set_data_as_is(self, value):
        """
        Method does not consider value as iterable. No matter whether data is sequence or no
        and does not run any action for customization.
        This should be consider like a last chance method.
        """
        self.__data = value

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        """
            Method consider the value as iterable data, excluding instances that have type
            pointed in ignore_iterable_types tuple. By default it contains only str type,
            and for each element run self._on_process_value(value) for some customization.
            Method does not do any recursions. This method is used in "data" property
            setter to process data by default.
        """
        self.__data = self._process_value(value)

    def data_as_list(self, data = None):
        if data is None:
            data = self.data
        if data is None:
            data = []
        elif not hasattr(data, '__iter__') or isinstance(data, self.ignore_iterable_types):
            data = [data]

        return data

    def add_data(self, value):
        """
            Add value to end of current data.
            Value can be list, simple value (str or any object) or None
            If data is neither list nor None (simple value) then list will be created
            No data type checking do.
        """
        if not self.is_sole_data():  # data is list
            if isinstance(value, (list,)):
                self.data.extend(self._process_value(value))
            else:
                # value is simple value
                self.data.append(self._process_value(value))
        elif self.data is None:
            # value either list or simple value
            self.data = value
        else:
            # self.data is simple value
            if isinstance(value, (list,)):
                self.data = [self.data, *value.copy()]
            else:
                # value is simple value
                self.data = [self.data, value]

        return self


class ParentedDataMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__parent = None

    def _on_process_value(self, value):
        # add self as parent if value supports ParentedDataMixin interface
        if isinstance(value, ParentedDataMixin):
            value.parent = self

        return super()._on_process_value(value)

    def __break_parent_relations(self, values: list):
        # try to uncouple all items of self.data (values)
        # who was coupled with self as children if value of values
        # supports ParentedDataMixin interface and coupled with self
        for v in values:
            if isinstance(v, ParentedDataMixin) and v.parent is self:
                v.parent = None

    def _process_value(self, value):
        olddata = self.data_as_list()
        result = super()._process_value(value)
        # This logic is possible because
        # _process_value and add_data each time return copies for self.data
        self.__break_parent_relations(olddata)
        return result

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        if not isinstance(value, (BaseData, type(None))):
            raise TypeError('value should be instance of BaseData type or None')
        self.__parent = value


class NamedDataMixin:

    def __init__(self, element_name=None):
        if not isinstance(self, BaseData):
            raise TypeError(
                'This mixin {0} can be applied to BaseData or its descendants only.'.format('NamedDataMixin')
            )
        self.element_name = element_name

    def on_get_element_name(self, name):
        return name

    @property
    def element_name(self):
        return self.on_get_element_name(self.__element_name)

    def on_set_element_name(self, name):
        return name

    @element_name.setter
    def element_name(self, value):
        if not isinstance(value, (str, type(None))):
            raise TypeError('"value" must be instance of "str" type or None.')
        self.__element_name = self.on_set_element_name(value)

    def get_elements_by(self, result: list,
                        value=None,
                        comparer=lambda el, v: el.element_name == str(v) if v is not None else el.element_name
                        ):
        """
        Comparer takes 2 parameters, element itself and value that should be compared with.
        By default, implemented lambda function that calqulate exact equality the value with element_name.
        If value is None (by default) then will be returned True for all elements

        :param result: List of found elements
        :param value: Value that will be passed inside the comparer as second argument
        :param comparer: function that should return boolean result.
        Comparer takes two arguments - first is current element
        and second is value that was passed as value argument
        """
        if not isinstance(result, (list, )):
            raise ValueError('Parameter "result" must be list type')

        # base case
        if comparer(self, value):
            result.append(self)

        # self.data returns either list or any other types but list type means we need to iterate over it,
        # though the other types also might be iterable.
        for element in self.data_as_list():
            # recursive case
            if hasattr(element, 'get_elements_by'):
                element.get_elements_by(result, value, comparer)


class NamedData(NamedDataMixin, BaseData):

    def __init__(self, data=None, element_name=None):
        BaseData.__init__(data)
        NamedDataMixin.__init__(element_name)
