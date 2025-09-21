"""
Unit tests for environment variable management use cases
"""
import pytest
from datetime import datetime

from ..domain.env_var import EnvVar, EnvVarType, ScopeRef, ScopeLevel, EnvVarStatus
from ..domain.env_var_version import EnvVarVersion
from ..usecases.env_var_management import (
    CreateEnvVarUseCase, CreateEnvVarRequest,
    UpdateEnvVarUseCase, UpdateEnvVarRequest,
    DeleteEnvVarUseCase,
    ListEnvVarsUseCase, ListEnvVarsRequest, ListEnvVarsResponse,
    DiffEnvironmentsUseCase
)
from ..adapters.mock_env_store import MockEnvStore
from ..adapters.mock_secret_cipher import MockSecretCipher
from ..adapters.mock_clock import MockClock
from ..adapters.mock_id_generator import MockIdGenerator


class TestCreateEnvVarUseCase:
    """Test cases for CreateEnvVarUseCase"""
    
    @pytest.fixture
    def use_case(self):
        """Create use case with mock dependencies"""
        env_store = MockEnvStore()
        secret_cipher = MockSecretCipher()
        clock = MockClock()
        id_generator = MockIdGenerator()
        
        return CreateEnvVarUseCase(env_store, secret_cipher, clock, id_generator)
    
    @pytest.mark.asyncio
    async def test_create_env_var_success(self, use_case):
        """Test successful environment variable creation"""
        request = CreateEnvVarRequest(
            key="DATABASE_URL",
            value="postgresql://user:pass@localhost/db",
            type=EnvVarType.STRING,
            scope=ScopeRef(ScopeLevel.GLOBAL, "default"),
            tags=["database", "production"],
            description="Database connection URL",
            is_secret=False,
            created_by="user1"
        )
        
        result = await use_case.execute(request)
        
        assert result.key == "DATABASE_URL"
        assert result.value == "postgresql://user:pass@localhost/db"
        assert result.type == EnvVarType.STRING
        assert result.scope.level == ScopeLevel.GLOBAL
        assert result.scope.ref_id == "default"
        assert result.tags == ["database", "production"]
        assert result.description == "Database connection URL"
        assert result.is_secret is False
        assert result.status == EnvVarStatus.ACTIVE
        assert result.created_by == "user1"
        assert result.updated_by == "user1"
    
    @pytest.mark.asyncio
    async def test_create_secret_env_var(self, use_case):
        """Test creating a secret environment variable"""
        request = CreateEnvVarRequest(
            key="API_SECRET",
            value="super-secret-key",
            type=EnvVarType.SECRET,
            scope=ScopeRef(ScopeLevel.GLOBAL, "default"),
            tags=["api", "secret"],
            description="API secret key",
            is_secret=True,
            created_by="user1"
        )
        
        result = await use_case.execute(request)
        
        assert result.key == "API_SECRET"
        assert result.is_secret is True
        # Value should be encrypted
        assert result.value.startswith("encrypted:")
        assert result.get_masked_value() == "***"
    
    @pytest.mark.asyncio
    async def test_create_env_var_duplicate_key(self, use_case):
        """Test creating environment variable with duplicate key"""
        # Create first env var
        request1 = CreateEnvVarRequest(
            key="DATABASE_URL",
            value="postgresql://user:pass@localhost/db1",
            type=EnvVarType.STRING,
            scope=ScopeRef(ScopeLevel.GLOBAL, "default"),
            tags=[],
            description="First database",
            is_secret=False,
            created_by="user1"
        )
        await use_case.execute(request1)
        
        # Try to create second env var with same key in same scope
        request2 = CreateEnvVarRequest(
            key="DATABASE_URL",
            value="postgresql://user:pass@localhost/db2",
            type=EnvVarType.STRING,
            scope=ScopeRef(ScopeLevel.GLOBAL, "default"),
            tags=[],
            description="Second database",
            is_secret=False,
            created_by="user1"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            await use_case.execute(request2)
    
    @pytest.mark.asyncio
    async def test_create_env_var_invalid_key(self, use_case):
        """Test creating environment variable with invalid key"""
        request = CreateEnvVarRequest(
            key="invalid-key",  # Should be uppercase
            value="some value",
            type=EnvVarType.STRING,
            scope=ScopeRef(ScopeLevel.GLOBAL, "default"),
            tags=[],
            description="Invalid key",
            is_secret=False,
            created_by="user1"
        )
        
        with pytest.raises(ValueError, match="Key must match pattern"):
            await use_case.execute(request)


class TestUpdateEnvVarUseCase:
    """Test cases for UpdateEnvVarUseCase"""
    
    @pytest.fixture
    def use_case(self):
        """Create use case with mock dependencies"""
        env_store = MockEnvStore()
        secret_cipher = MockSecretCipher()
        clock = MockClock()
        id_generator = MockIdGenerator()
        
        return UpdateEnvVarUseCase(env_store, secret_cipher, clock, id_generator)
    
    @pytest.fixture
    async def existing_env_var(self, use_case):
        """Create an existing environment variable"""
        # First create an env var
        create_request = CreateEnvVarRequest(
            key="DATABASE_URL",
            value="postgresql://user:pass@localhost/db",
            type=EnvVarType.STRING,
            scope=ScopeRef(ScopeLevel.GLOBAL, "default"),
            tags=["database"],
            description="Database URL",
            is_secret=False,
            created_by="user1"
        )
        
        create_use_case = CreateEnvVarUseCase(
            use_case.env_store, use_case.secret_cipher, 
            use_case.clock, use_case.id_generator
        )
        
        return await create_use_case.execute(create_request)
    
    @pytest.mark.asyncio
    async def test_update_env_var_success(self, use_case, existing_env_var):
        """Test successful environment variable update"""
        request = UpdateEnvVarRequest(
            env_var_id=existing_env_var.id,
            value="postgresql://user:newpass@localhost/db",
            type=None,
            tags=["database", "updated"],
            description="Updated database URL",
            updated_by="user2"
        )
        
        result = await use_case.execute(request)
        
        assert result.id == existing_env_var.id
        assert result.key == existing_env_var.key
        assert result.value == "postgresql://user:newpass@localhost/db"
        assert result.tags == ["database", "updated"]
        assert result.description == "Updated database URL"
        assert result.updated_by == "user2"
        assert result.updated_at > existing_env_var.updated_at
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_env_var(self, use_case):
        """Test updating non-existent environment variable"""
        request = UpdateEnvVarRequest(
            env_var_id="nonexistent-id",
            value="new value",
            type=None,
            tags=None,
            description=None,
            updated_by="user1"
        )
        
        with pytest.raises(ValueError, match="not found"):
            await use_case.execute(request)


class TestDeleteEnvVarUseCase:
    """Test cases for DeleteEnvVarUseCase"""
    
    @pytest.fixture
    def use_case(self):
        """Create use case with mock dependencies"""
        env_store = MockEnvStore()
        clock = MockClock()
        id_generator = MockIdGenerator()
        
        return DeleteEnvVarUseCase(env_store, clock, id_generator)
    
    @pytest.fixture
    async def existing_env_var(self, use_case):
        """Create an existing environment variable"""
        # First create an env var
        create_request = CreateEnvVarRequest(
            key="DATABASE_URL",
            value="postgresql://user:pass@localhost/db",
            type=EnvVarType.STRING,
            scope=ScopeRef(ScopeLevel.GLOBAL, "default"),
            tags=["database"],
            description="Database URL",
            is_secret=False,
            created_by="user1"
        )
        
        create_use_case = CreateEnvVarUseCase(
            use_case.env_store, MockSecretCipher(), 
            use_case.clock, use_case.id_generator
        )
        
        return await create_use_case.execute(create_request)
    
    @pytest.mark.asyncio
    async def test_delete_env_var_success(self, use_case, existing_env_var):
        """Test successful environment variable deletion"""
        result = await use_case.execute(existing_env_var.id, "user2")
        
        assert result is True
        
        # Verify env var is deleted
        deleted_env_var = await use_case.env_store.get_by_id(existing_env_var.id)
        assert deleted_env_var is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_env_var(self, use_case):
        """Test deleting non-existent environment variable"""
        with pytest.raises(ValueError, match="not found"):
            await use_case.execute("nonexistent-id", "user1")


class TestListEnvVarsUseCase:
    """Test cases for ListEnvVarsUseCase"""
    
    @pytest.fixture
    def use_case(self):
        """Create use case with mock dependencies"""
        env_store = MockEnvStore()
        return ListEnvVarsUseCase(env_store)
    
    @pytest.fixture
    async def sample_env_vars(self, use_case):
        """Create sample environment variables"""
        # Create multiple env vars for testing
        env_vars = []
        
        # Global env vars
        for i in range(3):
            env_var = EnvVar(
                id=f"global-{i}",
                key=f"GLOBAL_VAR_{i}",
                value=f"global_value_{i}",
                type=EnvVarType.STRING,
                scope=ScopeRef(ScopeLevel.GLOBAL, "default"),
                tags=["global"],
                description=f"Global variable {i}",
                is_secret=False,
                status=EnvVarStatus.ACTIVE,
                created_by="user1",
                created_at=datetime.now(),
                updated_by="user1",
                updated_at=datetime.now()
            )
            await use_case.env_store.create(env_var)
            env_vars.append(env_var)
        
        # Project env vars
        for i in range(2):
            env_var = EnvVar(
                id=f"project-{i}",
                key=f"PROJECT_VAR_{i}",
                value=f"project_value_{i}",
                type=EnvVarType.STRING,
                scope=ScopeRef(ScopeLevel.PROJECT, "project1"),
                tags=["project"],
                description=f"Project variable {i}",
                is_secret=False,
                status=EnvVarStatus.ACTIVE,
                created_by="user1",
                created_at=datetime.now(),
                updated_by="user1",
                updated_at=datetime.now()
            )
            await use_case.env_store.create(env_var)
            env_vars.append(env_var)
        
        return env_vars
    
    @pytest.mark.asyncio
    async def test_list_all_env_vars(self, use_case, sample_env_vars):
        """Test listing all environment variables"""
        request = ListEnvVarsRequest(
            scope_level=None,
            scope_ref_id=None,
            key_filter=None,
            tag_filter=None,
            type_filter=None,
            status_filter=None,
            page=1,
            size=10
        )
        
        result = await use_case.execute(request)
        
        assert isinstance(result, ListEnvVarsResponse)
        assert len(result.env_vars) == 5  # 3 global + 2 project
        assert result.total == 5
        assert result.page == 1
        assert result.size == 10
    
    @pytest.mark.asyncio
    async def test_list_env_vars_with_scope_filter(self, use_case, sample_env_vars):
        """Test listing environment variables with scope filter"""
        request = ListEnvVarsRequest(
            scope_level=ScopeLevel.GLOBAL,
            scope_ref_id=None,
            key_filter=None,
            tag_filter=None,
            type_filter=None,
            status_filter=None,
            page=1,
            size=10
        )
        
        result = await use_case.execute(request)
        
        assert len(result.env_vars) == 3  # Only global vars
        assert result.total == 3
        for env_var in result.env_vars:
            assert env_var.scope.level == ScopeLevel.GLOBAL
    
    @pytest.mark.asyncio
    async def test_list_env_vars_with_pagination(self, use_case, sample_env_vars):
        """Test listing environment variables with pagination"""
        request = ListEnvVarsRequest(
            scope_level=None,
            scope_ref_id=None,
            key_filter=None,
            tag_filter=None,
            type_filter=None,
            status_filter=None,
            page=1,
            size=2
        )
        
        result = await use_case.execute(request)
        
        assert len(result.env_vars) == 2  # Page size is 2
        assert result.total == 5  # Total count
        assert result.page == 1
        assert result.size == 2


class TestDiffEnvironmentsUseCase:
    """Test cases for DiffEnvironmentsUseCase"""
    
    @pytest.fixture
    def use_case(self):
        """Create use case with mock dependencies"""
        env_store = MockEnvStore()
        return DiffEnvironmentsUseCase(env_store)
    
    @pytest.fixture
    async def sample_env_vars(self, use_case):
        """Create sample environment variables for two environments"""
        # Environment 1 variables
        env1_vars = []
        for i in range(3):
            env_var = EnvVar(
                id=f"env1-{i}",
                key=f"ENV_VAR_{i}",
                value=f"env1_value_{i}",
                type=EnvVarType.STRING,
                scope=ScopeRef(ScopeLevel.ENV, "env1"),
                tags=["env1"],
                description=f"Environment 1 variable {i}",
                is_secret=False,
                status=EnvVarStatus.ACTIVE,
                created_by="user1",
                created_at=datetime.now(),
                updated_by="user1",
                updated_at=datetime.now()
            )
            await use_case.env_store.create(env_var)
            env1_vars.append(env_var)
        
        # Environment 2 variables
        env2_vars = []
        for i in range(2):
            env_var = EnvVar(
                id=f"env2-{i}",
                key=f"ENV_VAR_{i}",
                value=f"env2_value_{i}",
                type=EnvVarType.STRING,
                scope=ScopeRef(ScopeLevel.ENV, "env2"),
                tags=["env2"],
                description=f"Environment 2 variable {i}",
                is_secret=False,
                status=EnvVarStatus.ACTIVE,
                created_by="user1",
                created_at=datetime.now(),
                updated_by="user1",
                updated_at=datetime.now()
            )
            await use_case.env_store.create(env_var)
            env2_vars.append(env_var)
        
        return env1_vars, env2_vars
    
    @pytest.mark.asyncio
    async def test_diff_environments(self, use_case, sample_env_vars):
        """Test comparing two environments"""
        env1_vars, env2_vars = sample_env_vars
        
        result = await use_case.execute("env1", "env2")
        
        assert result['env1'] == "env1"
        assert result['env2'] == "env2"
        assert len(result['missing_in_env2']) == 1  # ENV_VAR_2 only in env1
        assert len(result['missing_in_env1']) == 0  # All env2 vars exist in env1
        assert len(result['different_values']) == 2  # ENV_VAR_0 and ENV_VAR_1 have different values
        assert result['summary']['total_keys'] == 3
        assert result['summary']['missing_in_env2_count'] == 1
        assert result['summary']['missing_in_env1_count'] == 0
        assert result['summary']['different_count'] == 2
