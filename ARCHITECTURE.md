# 🏗️ System Architecture

## Tổng quan kiến trúc

Hệ thống quản lý biến môi trường được xây dựng theo kiến trúc **Clean Architecture** với **Domain-Driven Design (DDD)** principles.

## 🎯 Core Principles

### 1. **Separation of Concerns**
- **Domain Layer**: Business logic và entities
- **Application Layer**: Use cases và business rules
- **Infrastructure Layer**: External dependencies
- **Presentation Layer**: UI và API endpoints

### 2. **Dependency Inversion**
- High-level modules không phụ thuộc vào low-level modules
- Sử dụng interfaces (ports) để decouple dependencies
- Dependency injection cho testability

### 3. **Single Responsibility**
- Mỗi class/function có một trách nhiệm duy nhất
- Clear boundaries giữa các layers

## 📁 Project Structure

```
AI-Agent-Tool/
├── be/                          # Backend (FastAPI)
│   ├── app/
│   │   ├── core/               # Domain Layer
│   │   │   ├── domain/         # Business Entities
│   │   │   ├── ports/          # Interfaces (Abstractions)
│   │   │   ├── usecases/       # Business Logic
│   │   │   └── adapters/       # Mock Implementations
│   │   ├── routers/            # API Endpoints
│   │   ├── model/              # Database Models
│   │   ├── adapters/           # Infrastructure Adapters
│   │   └── db/                 # Database Configuration
│   ├── migrations/             # Database Migrations
│   └── requirements.txt
├── fe/                          # Frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/         # Reusable Components
│   │   ├── pages/             # Page Components
│   │   ├── services/          # API Services
│   │   ├── hooks/             # Custom Hooks
│   │   ├── contexts/          # React Contexts
│   │   ├── layouts/           # Layout Components
│   │   └── router/            # Routing
│   └── package.json
└── README.md
```

## 🔄 Data Flow

### 1. **Request Flow**

```mermaid
graph TD
    A[Frontend Request] --> B[API Router]
    B --> C[Use Case]
    C --> D[Domain Logic]
    D --> E[Port Interface]
    E --> F[Adapter Implementation]
    F --> G[Database/External Service]
    G --> H[Response]
    H --> I[Frontend Update]
```

### 2. **Error Handling Flow**

```mermaid
graph TD
    A[Error Occurs] --> B[Adapter Layer]
    B --> C[Use Case Layer]
    C --> D[Router Layer]
    D --> E[Frontend Interceptor]
    E --> F[Toast Notification]
    E --> G[Log Console]
```

## 🏛️ Domain Layer

### Core Entities

```python
# Environment Variable Entity
class EnvVar:
    id: str
    key: str
    value: str  # Encrypted if secret
    type: EnvVarType
    scope: Scope
    tags: List[str]
    description: str
    is_secret: bool
    status: EnvVarStatus
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime

# Release Entity
class Release:
    id: str
    service_id: str
    environment: str
    title: str
    description: str
    changes: List[Change]
    status: ReleaseStatus
    created_by: str
    created_at: datetime
    applied_by: Optional[str]
    applied_at: Optional[datetime]

# Audit Event Entity
class AuditEvent:
    id: str
    actor: str
    action: str
    target_type: str
    target_id: str
    before_json: Optional[dict]
    after_json: Optional[dict]
    reason: Optional[str]
    timestamp: datetime
```

### Value Objects

```python
# Scope Value Object
class Scope:
    level: ScopeLevel  # GLOBAL, PROJECT, SERVICE, ENV
    ref_id: str

# EnvVarType Enum
class EnvVarType(Enum):
    STRING = "STRING"
    JSON = "JSON"
    SECRET = "SECRET"
    URL = "URL"

# ReleaseStatus Enum
class ReleaseStatus(Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
```

## 🔌 Ports (Interfaces)

### Repository Ports

```python
# Environment Variable Store
class EnvStore(ABC):
    @abstractmethod
    async def create(self, env_var: EnvVar) -> EnvVar:
        pass
    
    @abstractmethod
    async def get_by_id(self, env_var_id: str) -> Optional[EnvVar]:
        pass
    
    @abstractmethod
    async def get_by_unique_key(self, scope_level: str, scope_ref_id: str, key: str) -> Optional[EnvVar]:
        pass
    
    @abstractmethod
    async def update(self, env_var: EnvVar) -> EnvVar:
        pass
    
    @abstractmethod
    async def delete(self, env_var_id: str) -> bool:
        pass
    
    @abstractmethod
    async def list(self, filters: Dict[str, Any]) -> List[EnvVar]:
        pass

# Secret Cipher
class SecretCipher(ABC):
    @abstractmethod
    async def encrypt(self, value: str) -> str:
        pass
    
    @abstractmethod
    async def decrypt(self, encrypted_value: str) -> str:
        pass

# ID Generator
class IdGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        pass

# Clock
class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass

# Notifier
class Notifier(ABC):
    @abstractmethod
    async def send(self, message: str, recipients: List[str]) -> bool:
        pass
```

## 🎯 Use Cases

### Environment Variable Management

```python
class CreateEnvVarUseCase:
    def __init__(self, env_store: EnvStore, secret_cipher: SecretCipher, 
                 clock: Clock, id_generator: IdGenerator):
        self.env_store = env_store
        self.secret_cipher = secret_cipher
        self.clock = clock
        self.id_generator = id_generator
    
    async def execute(self, request: CreateEnvVarRequest) -> EnvVar:
        # 1. Validate business rules
        # 2. Check for duplicates
        # 3. Encrypt if secret
        # 4. Create entity
        # 5. Save to store
        # 6. Create audit event
        pass

class UpdateEnvVarUseCase:
    async def execute(self, request: UpdateEnvVarRequest) -> EnvVar:
        # 1. Get existing env var
        # 2. Validate changes
        # 3. Create version
        # 4. Update entity
        # 5. Save changes
        # 6. Create audit event
        pass

class DeleteEnvVarUseCase:
    async def execute(self, request: DeleteEnvVarRequest) -> bool:
        # 1. Get existing env var
        # 2. Validate deletion rules
        # 3. Soft delete
        # 4. Create audit event
        pass
```

### Release Management

```python
class CreateReleaseUseCase:
    async def execute(self, request: CreateReleaseRequest) -> Release:
        # 1. Validate changes
        # 2. Create release entity
        # 3. Save to store
        # 4. Create audit event
        pass

class ApproveReleaseUseCase:
    async def execute(self, request: ApproveReleaseRequest) -> Release:
        # 1. Get release
        # 2. Validate approval rules
        # 3. Update status
        # 4. Create audit event
        pass

class ApplyReleaseUseCase:
    async def execute(self, request: ApplyReleaseRequest) -> Release:
        # 1. Get approved release
        # 2. Apply changes
        # 3. Update status
        # 4. Create audit event
        pass
```

## 🔧 Adapters (Infrastructure)

### Database Adapter

```python
class SqlAlchemyEnvStore(EnvStore):
    def __init__(self, session: Session):
        self.session = session
    
    async def create(self, env_var: EnvVar) -> EnvVar:
        # Convert domain entity to SQLAlchemy model
        # Save to database
        # Return domain entity
        pass
    
    async def get_by_id(self, env_var_id: str) -> Optional[EnvVar]:
        # Query database
        # Convert SQLAlchemy model to domain entity
        # Return domain entity
        pass
```

### Encryption Adapter

```python
class CryptoCipher(SecretCipher):
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    async def encrypt(self, value: str) -> str:
        return self.cipher.encrypt(value.encode()).decode()
    
    async def decrypt(self, encrypted_value: str) -> str:
        return self.cipher.decrypt(encrypted_value.encode()).decode()
```

### ID Generator Adapter

```python
class MockIdGenerator(IdGenerator):
    def __init__(self):
        self.counter = 0
    
    def generate(self) -> str:
        self.counter += 1
        return f"mock-id-{self.counter}"
    
    def generate_uuid(self) -> str:
        return str(uuid.uuid4())
```

## 🌐 API Layer

### Router Structure

```python
# Environment Variables Router
@router.post("/", response_model=Dict[str, Any])
async def create_env_var(
    key: str = Body(...),
    value: str = Body(...),
    type: str = Body(...),
    scope_level: str = Body(...),
    scope_ref_id: str = Body(...),
    tags: List[str] = Body(default=[]),
    description: Optional[str] = Body(None),
    is_secret: bool = Body(False),
    created_by: str = Body(...),
    env_store: SqlAlchemyEnvStore = Depends(get_env_store),
    secret_cipher: CryptoCipher = Depends(get_secret_cipher),
    clock: MockClock = Depends(get_clock),
    id_generator: MockIdGenerator = Depends(get_id_generator)
):
    # 1. Create use case
    # 2. Execute use case
    # 3. Return response
    pass
```

### Dependency Injection

```python
# Dependency providers
def get_env_store() -> SqlAlchemyEnvStore:
    return SqlAlchemyEnvStore(get_db_session())

def get_secret_cipher() -> CryptoCipher:
    key = os.getenv('ENCRYPTION_KEY')
    return CryptoCipher(key.encode())

def get_clock() -> MockClock:
    return MockClock()

def get_id_generator() -> MockIdGenerator:
    return MockIdGenerator()
```

## 🎨 Frontend Architecture

### Component Structure

```
components/
├── Toast.tsx              # Toast notifications
├── ConfirmDialog.tsx      # Confirmation dialogs
├── DataTable.tsx          # Generic data table
└── MatrixDataTable.tsx    # Advanced data table

pages/
├── envvars/
│   └── EnvVarsPage.tsx    # Environment variables management
├── releases/
│   └── ReleasesPage.tsx  # Release management
├── audit/
│   └── AuditPage.tsx     # Audit events
└── logs/
    └── LogsPage.tsx      # Real-time logs

services/
├── api.ts                # API client
├── logger.ts            # Logging service
└── api-with-toast.ts    # API with toast integration

hooks/
├── useToastNotification.ts  # Toast hook
├── useFilterParams.ts       # Filter parameters
├── usePagination.ts         # Pagination logic
└── useTableParams.ts        # Table parameters

contexts/
└── ToastContext.tsx     # Toast context provider
```

### State Management

```typescript
// Toast Context
interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

// Toast Hook
export const useToastNotification = () => {
  const { addToast } = useToast();
  
  const showSuccess = (title: string, message?: string) => {
    addToast({ type: 'success', title, message });
  };
  
  const showError = (title: string, message?: string) => {
    addToast({ type: 'error', title, message });
  };
  
  // ... other methods
};
```

### API Integration

```typescript
// API Client with Interceptors
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request Interceptor
apiClient.interceptors.request.use((config) => {
  const startTime = Date.now();
  (config as any).startTime = startTime;
  
  // Log request
  loggerService.addLog({
    method: config.method?.toUpperCase() || 'GET',
    url: config.url || '',
    type: 'request'
  });
  
  return config;
});

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Log successful response
    loggerService.addLog({
      method: response.config.method?.toUpperCase() || 'GET',
      url: response.config.url || '',
      status: response.status,
      type: 'response'
    });
    
    return response;
  },
  (error) => {
    // Log error response
    loggerService.addLog({
      method: error.config?.method?.toUpperCase() || 'UNKNOWN',
      url: error.config?.url || 'UNKNOWN',
      status: error.response?.status,
      error: error.message,
      type: 'error'
    });
    
    return Promise.reject(error);
  }
);
```

## 🔒 Security Architecture

### Encryption Flow

```mermaid
graph TD
    A[User Input] --> B[Validation]
    B --> C{Is Secret?}
    C -->|Yes| D[Encrypt with Fernet]
    C -->|No| E[Store as Plain Text]
    D --> F[Store Encrypted]
    E --> F
    F --> G[Database]
```

### Access Control

```python
# RBAC Implementation
class Permission:
    CREATE_ENV_VAR = "create_env_var"
    UPDATE_ENV_VAR = "update_env_var"
    DELETE_ENV_VAR = "delete_env_var"
    REVEAL_SECRET = "reveal_secret"
    CREATE_RELEASE = "create_release"
    APPROVE_RELEASE = "approve_release"
    APPLY_RELEASE = "apply_release"

class Role:
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

# Permission Matrix
PERMISSIONS = {
    Role.ADMIN: [
        Permission.CREATE_ENV_VAR,
        Permission.UPDATE_ENV_VAR,
        Permission.DELETE_ENV_VAR,
        Permission.REVEAL_SECRET,
        Permission.CREATE_RELEASE,
        Permission.APPROVE_RELEASE,
        Permission.APPLY_RELEASE,
    ],
    Role.DEVELOPER: [
        Permission.CREATE_ENV_VAR,
        Permission.UPDATE_ENV_VAR,
        Permission.CREATE_RELEASE,
    ],
    Role.VIEWER: [
        # Read-only access
    ]
}
```

## 📊 Monitoring Architecture

### Logging Flow

```mermaid
graph TD
    A[API Request] --> B[Router]
    B --> C[Use Case]
    C --> D[Domain Logic]
    D --> E[Adapter]
    E --> F[Database]
    F --> G[Response]
    G --> H[Frontend]
    H --> I[Toast Notification]
    H --> J[Log Console]
```

### Audit Trail

```python
# Audit Event Creation
class AuditEvent:
    def __init__(self, actor: str, action: str, target_type: str, 
                 target_id: str, before_json: dict = None, 
                 after_json: dict = None, reason: str = None):
        self.id = id_generator.generate()
        self.actor = actor
        self.action = action
        self.target_type = target_type
        self.target_id = target_id
        self.before_json = before_json
        self.after_json = after_json
        self.reason = reason
        self.timestamp = clock.now()

# Audit Event Types
class AuditAction:
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    REVEAL = "REVEAL"
    APPROVE = "APPROVE"
    APPLY = "APPLY"
    ROLLBACK = "ROLLBACK"
```

## 🚀 Deployment Architecture

### Production Setup

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: env_vars_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./be
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/env_vars_db
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
    depends_on:
      - postgres
    ports:
      - "8000:8000"

  frontend:
    build: ./fe
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Environment Variables

```bash
# Production Environment
DATABASE_URL=postgresql://admin:password@localhost:5432/env_vars_db
ENCRYPTION_KEY=your-32-byte-encryption-key
SECRET_KEY=your-secret-key
DEBUG=False
LOG_LEVEL=INFO
```

## 🔄 Data Flow Examples

### 1. Create Environment Variable

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Router
    participant UC as Use Case
    participant D as Domain
    participant DB as Database
    participant E as Encryption

    U->>F: Fill form
    F->>A: POST /envvars
    A->>UC: CreateEnvVarUseCase
    UC->>D: Validate business rules
    D->>E: Encrypt if secret
    E->>D: Return encrypted value
    D->>DB: Save to database
    DB->>A: Return created entity
    A->>F: Return response
    F->>U: Show success toast
```

### 2. Release Workflow

```mermaid
sequenceDiagram
    participant D as Developer
    participant F as Frontend
    participant A as API
    participant UC as Use Case
    participant DB as Database
    participant AP as Approver

    D->>F: Create release
    F->>A: POST /releases
    A->>UC: CreateReleaseUseCase
    UC->>DB: Save release
    DB->>A: Return release
    A->>F: Return response
    F->>D: Show success
    
    AP->>F: Approve release
    F->>A: POST /releases/{id}/approve
    A->>UC: ApproveReleaseUseCase
    UC->>DB: Update status
    DB->>A: Return updated release
    A->>F: Return response
    F->>AP: Show success
```

## 🧪 Testing Strategy

### Unit Tests

```python
# Domain Layer Tests
class TestEnvVar:
    def test_create_env_var(self):
        env_var = EnvVar(
            id="test-id",
            key="TEST_KEY",
            value="test-value",
            type=EnvVarType.STRING,
            scope=Scope(ScopeLevel.GLOBAL, "default"),
            tags=["test"],
            description="Test variable",
            is_secret=False,
            status=EnvVarStatus.ACTIVE,
            created_by="test-user",
            created_at=datetime.now(),
            updated_by="test-user",
            updated_at=datetime.now()
        )
        assert env_var.key == "TEST_KEY"
        assert env_var.type == EnvVarType.STRING

# Use Case Tests
class TestCreateEnvVarUseCase:
    def test_execute_success(self):
        # Mock dependencies
        # Execute use case
        # Assert results
        pass
```

### Integration Tests

```python
# API Integration Tests
class TestEnvVarAPI:
    def test_create_env_var_success(self):
        response = client.post("/envvars", json={
            "key": "TEST_KEY",
            "value": "test-value",
            "type": "STRING",
            "scope_level": "GLOBAL",
            "scope_ref_id": "default",
            "created_by": "test-user"
        })
        assert response.status_code == 200
        assert response.json()["key"] == "TEST_KEY"
```

### Frontend Tests

```typescript
// Component Tests
describe('EnvVarsPage', () => {
  it('should create environment variable', async () => {
    render(<EnvVarsPage />);
    
    fireEvent.click(screen.getByText('Create'));
    fireEvent.change(screen.getByLabelText('Key'), { target: { value: 'TEST_KEY' } });
    fireEvent.change(screen.getByLabelText('Value'), { target: { value: 'test-value' } });
    fireEvent.click(screen.getByText('Save'));
    
    await waitFor(() => {
      expect(screen.getByText('Environment Variable Created')).toBeInTheDocument();
    });
  });
});
```

## 📈 Performance Considerations

### Database Optimization

```sql
-- Indexes for performance
CREATE INDEX idx_env_vars_scope ON env_vars(scope_level, scope_ref_id);
CREATE INDEX idx_env_vars_key ON env_vars(key);
CREATE INDEX idx_audit_events_actor ON audit_events(actor);
CREATE INDEX idx_audit_events_timestamp ON audit_events(timestamp);

-- Partitioning for large tables
CREATE TABLE audit_events_2024 PARTITION OF audit_events
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### Caching Strategy

```python
# Redis Caching
class CachedEnvStore(EnvStore):
    def __init__(self, env_store: EnvStore, cache: Redis):
        self.env_store = env_store
        self.cache = cache
    
    async def get_by_id(self, env_var_id: str) -> Optional[EnvVar]:
        # Check cache first
        cached = await self.cache.get(f"env_var:{env_var_id}")
        if cached:
            return EnvVar.from_dict(json.loads(cached))
        
        # Fallback to database
        env_var = await self.env_store.get_by_id(env_var_id)
        if env_var:
            await self.cache.setex(f"env_var:{env_var_id}", 300, json.dumps(env_var.to_dict()))
        
        return env_var
```

### Frontend Optimization

```typescript
// Lazy Loading
const EnvVarsPage = lazy(() => import('./pages/envvars/EnvVarsPage'));

// Memoization
const MemoizedEnvVarRow = memo(({ envVar, onEdit, onDelete }) => {
  return (
    <Table.Row>
      <Table.Cell>{envVar.key}</Table.Cell>
      <Table.Cell>{envVar.value}</Table.Cell>
      {/* ... */}
    </Table.Row>
  );
});

// Virtual Scrolling for large lists
import { FixedSizeList as List } from 'react-window';

const VirtualizedTable = ({ items }) => (
  <List
    height={600}
    itemCount={items.length}
    itemSize={50}
    itemData={items}
  >
    {({ index, style, data }) => (
      <div style={style}>
        <EnvVarRow envVar={data[index]} />
      </div>
    )}
  </List>
);
```

---

**Lưu ý**: Kiến trúc này được thiết kế để dễ dàng mở rộng và bảo trì. Mỗi layer có trách nhiệm rõ ràng và có thể được test độc lập.
