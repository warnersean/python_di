# python_di
Dependency Injection container for python3 using type annotations. This works similar to the DI containers used in Angular.

# Usage
Create a new DI container

``` python
dependency_container = DependencyContainer()
```

To construct a new object and access it from the container, use the get accessor with the needed class as the parameter. All dependencies for the class will automatically be created and stored as single instances within the container.

``` python
class_object = dependency_container.get(ClassObject)
```

If a different class is needed in place of the annotated for all instances throughout the application, it can be registered with the set method, using the class of the overwritten class as the first parameter, and an instance of the overwriting class as the second parameter.

``` python
mock_instance = MockClassObject()
dependency_container.set(ClassObject, mock_instance)
```

These two methods can be used to construct mocked instances of classes, while utilizing other instances from the DI container, if needed.

``` python
parameter_instance = dependency_container.get(SomeParameterClass)
mock_instance = MockClassObject(parameter_instance)
dependency_container.set(ClassObject, mock_instance)
```

The classes that are injected must either have type annotations for class parameters on the class __init__ method (the class instances of those parameters must also be annotated correctly for them to be automatically constructed), have no input parameters, or must be manually set. Primitave methods can not be used with automatic injection (strings, numbers, etc). For example, the following two classes can be constructed correctly:

``` python
class MyClassWithNoParams(Object):
    def __init__(self):
        # Implementation details here
        ...
        
class MyClassWithParams(Object):
    def __init__(self, param: MyClassWithNoParams):
        # Implementation details here
        ...
```

Likewise, these classes can not be constructed automatically with this container:

``` python
class MyClassWithString(Object):
    def __init__(self, s: str):
        # Implementation details here
        ...
    
class MyClassWithFloat(Object):
    def __init__(self, f: float):
        # Implementation details here
        ...

class MyClassWithNonInjectedParams(Object):
    def __init__(self, s: MyClassWithString, f: MyClassWithFloat):
        # Implementation details here
        ...
```

If using instance of these containers with the depenency injector is desired, this can be done like this:

``` python
s = MyClassWithString("my string")
f = MyClassWithFloat(3.14159)
dependency_container.set(MyClassWithString, s)
dependency_container.set(MyClassWithString, f)

# at this point, the DI container knows about the available parameters for
# MyClassWithNonInjectedParameters, and it can be recovered from the container
m = dependency_container.get(MyClassWithNonInjectedParams)
```

# Full Example
``` python
class ParamObject(Object):
    def get_string(self):
        return "Some String"
    
class MockParamObject(Object):
    def get_string(self):
        return "Other String"

class MyClass(Object):
    def __init__(self, p: ParamObject):
        self.s = p.get_string()
        
    def get_s(self):
        return self.s
        
testing = False
if not testing:
    dependency_container = DependencyContainer()
    m = dependency_container.get(MyClass)
    print(m.get_s()) # Prints "Some String"
else:
   dependency_container = DependencyContainer()
   dependency_container.set(ParamObject, MockParamObject())
   m = dependency_container.get(MyClass)
   print(m.get_s()) # Prints "Other String"
```

