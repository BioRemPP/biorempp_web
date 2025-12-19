"""
Unit tests for Dependency Injection Container module.
"""

import pytest
from src.infrastructure.config.dependency_injection import DIContainer


class TestDIContainer:
    """Test suite for DIContainer."""

    @pytest.fixture
    def container(self):
        """Create fresh container for each test."""
        return DIContainer()

    def test_register_singleton(self, container):
        """Test registering singleton dependency."""
        class MyService:
            def __init__(self):
                self.value = 42
        
        service = MyService()
        container.register_singleton('my_service', service)
        
        assert container.is_registered('my_service')

    def test_resolve_singleton(self, container):
        """Test resolving singleton returns same instance."""
        class MyService:
            def __init__(self):
                self.value = 42
        
        service = MyService()
        container.register_singleton('my_service', service)
        
        instance1 = container.resolve('my_service')
        instance2 = container.resolve('my_service')
        
        assert instance1 is instance2

    def test_register_factory(self, container):
        """Test registering factory dependency."""
        class MyService:
            def __init__(self):
                self.value = 42
        
        container.register_factory('my_service', MyService)
        
        assert container.is_registered('my_service')

    def test_resolve_factory(self, container):
        """Test resolving factory returns new instances."""
        class MyService:
            def __init__(self):
                self.value = 42
        
        container.register_factory('my_service', MyService)
        
        instance1 = container.resolve('my_service')
        instance2 = container.resolve('my_service')
        
        assert instance1 is not instance2

    def test_register_type(self, container):
        """Test registering type dependency."""
        class MyInterface:
            pass
        
        class MyImplementation(MyInterface):
            pass
        
        container.register_type(MyInterface, MyImplementation)
        
        assert container.is_registered(MyInterface)

    def test_resolve_type(self, container):
        """Test resolving type dependency."""
        class MyInterface:
            pass
        
        class MyImplementation(MyInterface):
            pass
        
        container.register_type(MyInterface, MyImplementation)
        
        instance = container.resolve(MyInterface)
        
        assert isinstance(instance, MyImplementation)

    def test_register_instance(self, container):
        """Test registering existing instance."""
        class MyService:
            def __init__(self, value):
                self.value = value
        
        instance = MyService(42)
        container.register_singleton('my_service', instance)
        
        resolved = container.resolve('my_service')
        
        assert resolved is instance
        assert resolved.value == 42

    def test_resolve_unregistered(self, container):
        """Test error when resolving unregistered dependency."""
        with pytest.raises(ValueError, match="Dependency not found"):
            container.resolve('nonexistent')

    def test_is_registered(self, container):
        """Test checking if dependency is registered."""
        class MyService:
            pass
        
        assert not container.is_registered('my_service')
        
        service = MyService()
        container.register_singleton('my_service', service)
        
        assert container.is_registered('my_service')

    def test_clear(self, container):
        """Test clearing all registrations."""
        class MyService:
            pass
        
        service = MyService()
        container.register_singleton('service1', service)
        container.register_factory('service2', MyService)
        
        assert container.is_registered('service1')
        assert container.is_registered('service2')
        
        container.clear()
        
        assert not container.is_registered('service1')
        assert not container.is_registered('service2')

    def test_register_with_dependencies(self, container):
        """Test registering service with dependencies."""
        class DatabaseService:
            pass
        
        class UserService:
            def __init__(self, db_service):
                self.db_service = db_service
        
        db = DatabaseService()
        container.register_singleton('database', db)
        
        # Manual dependency injection in this simple test
        db_resolved = container.resolve('database')
        user_service = UserService(db_resolved)
        
        assert isinstance(user_service.db_service, DatabaseService)

    def test_multiple_registrations_same_key(self, container):
        """Test that re-registration replaces previous."""
        class Service1:
            pass
        
        class Service2:
            pass
        
        service1 = Service1()
        container.register_singleton('service', service1)
        instance1 = container.resolve('service')
        
        service2 = Service2()
        container.register_singleton('service', service2)
        instance2 = container.resolve('service')
        
        assert isinstance(instance1, Service1)
        assert isinstance(instance2, Service2)
