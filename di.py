"""
Class and related tools relating to a light dependency injection framework to allow modules to auto-create

The class will automatically determine the necessary dependencies of the injected class and build them and their
subdependencies. This will not support non-object based imports, classes that do not have type hints, or items that
rely on circular dependencies (though the system should recognize circular dependencies at runtime).

Additional support has been added to allow dependencies to be manually set in order to improve future-proofing the
application and allow for better testability of the code base.
"""

import typing


class CircularDependencyError(Exception):
    def __init__(self, message):
        super(CircularDependencyError, self).__init__(message)


class DependencyContainer:
    """
    Dependency Injection container for auto-building objects.
    This class assumes the object to be built should be a single instance within the container's scope
    and that all necessary dependencies that build the object, should also be single instances within the scope.

    The container relies heavily on type hints for a class (in fact, it will not work if a class does not have valid
    type hints for its input parameters) but dependencies can be manually set using the set command (see implementation
    for details)
    """
    def __init__(self):
        # dictionary of <class 'type'> to class object (for example, self.build_stack[T] = T())
        # used to hold single instances of the required class
        self.__container = {}

        # Container of classes currently being built, used to prevent circular dependencies resulting in broken stack
        # dictionary chosen for O(1) lookup. Value does not matter in this case
        self.build_stack = {}

    def get(self, cls):
        """
        Retrieves a copy of the class object from the container

        This will build the object if it does not exist, as well as all neccessary dependencies.
        This can not handle direct circular references between objects. I.e. if T depends on R, and R on T then the
        call will raise LookupError (T.__init__(self, r:R), R.__init(self, t:T) will not raise error)

        :param cls: The class type as a type object (not a string)

        :raises CircularDependencyError: if a circular dependency is encountered
        :raises TypeError: if the object to be obtained requires parameters that are not objects

        :return: The class instance
        """
        if cls in self.__container:
            return self.__container[cls]

        try:
            self.set(cls, self.__build(cls))
        except TypeError:
            raise TypeError("Could not build object of type %s. Check to ensure that you aren't trying to build an "
                            "object that takes something other than objects as input parameters and that the correct "
                            "type annotations are set." % cls)
        return self.get(cls)

    def set(self, cls_name, set_instance):
        """
        Manually sets the instance of a class type in the container

        This is primarily useful for testing or if the intended operation requires something that abides by the
        contract of the object interface, but should not be the object itself

        For example, if T implements x() and R implements x(), calling set(T, R()) allows an R instance to be retrieved
        when a T instance normally would. This sets the single instance of T in the container to the R instance, and
        will utilize that whenever a T instance is required for any future objects added to the container

        :param cls_name: The class type as a type object (not a string)

        :param set_instance: The instance to set for cls_name

        :return: None
        """
        self.__container[cls_name] = set_instance

    def __build(self, cls):
        """
        Builds the requested object

        This will build any dependency objects as well and add them to the container. It will also
        verify that there are no existing circular dependencies

        :param cls: The class type as a type object (not a string)

        :raises CircularDependencyError: if a circular dependency is encountered
        :raises TypeError: if the object to be obtained requires parameters that are not objects

        :return: An instance of the requested class
        """
        params = typing.get_type_hints(cls.__init__).copy()
        if not params:
            return cls.__call__()

        # Prevent circular dependencies
        if cls in self.build_stack:
            raise CircularDependencyError
        else:
            self.build_stack[cls] = True

        for key, value in params.items():
            params[key] = self.get(value)

        # Item fully built, so remove from build stack
        del self.build_stack[cls]
        return cls.__call__(**params)