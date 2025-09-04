# RBAC + ABAC System Implementation

## Tổng quan

Hệ thống này đã được thiết kế lại để sử dụng **RBAC (Role-Based Access Control)** và **ABAC (Attribute-Based Access Control)** cho việc quản lý quyền truy cập.

## Kiến trúc hệ thống

### Backend (FastAPI)

#### RBAC Components
- **Role**: Vai trò người dùng (Admin, Manager, User, etc.)
- **Permission**: Quyền cụ thể (read, write, delete, etc.)
- **Resource**: Tài nguyên hệ thống (user, feature, report, etc.)
- **User-Role Assignment**: Gán vai trò cho người dùng
- **Role-Permission Assignment**: Gán quyền cho vai trò

#### ABAC Components
- **Policy**: Quy tắc dựa trên thuộc tính
- **Attribute**: Thuộc tính của user, resource, action, environment
- **Policy Assignment**: Gán policy cho user/role/resource
- **Policy Engine**: Engine đánh giá policy và đưa ra quyết định

### Frontend (React + TypeScript)

#### UI Components
- **Role Management**: Quản lý vai trò
- **Permission Management**: Quản lý quyền
- **Policy Management**: Quản lý chính sách ABAC
- **User Management**: Quản lý người dùng với vai trò

## Cài đặt và chạy

### Backend

1. **Cài đặt dependencies:**
```bash
cd be
pip install -r requirements.txt
```

2. **Cấu hình database:**
```bash
cp env.example .env
# Chỉnh sửa file .env với thông tin database
```

3. **Khởi tạo database:**
```bash
python init_rbac_abac.py
```

4. **Chạy server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

1. **Cài đặt dependencies:**
```bash
cd fe
npm install
```

2. **Cấu hình environment:**
```bash
cp env.example .env
# Chỉnh sửa VITE_API_BASE_URL nếu cần
```

3. **Chạy development server:**
```bash
npm run dev
```

## API Endpoints

### RBAC Endpoints

#### Roles
- `GET /rbac/roles` - Lấy danh sách roles
- `POST /rbac/roles` - Tạo role mới
- `GET /rbac/roles/{id}` - Lấy role theo ID
- `PUT /rbac/roles/{id}` - Cập nhật role
- `DELETE /rbac/roles/{id}` - Xóa role

#### Permissions
- `GET /rbac/permissions` - Lấy danh sách permissions
- `POST /rbac/permissions` - Tạo permission mới
- `GET /rbac/permissions/{id}` - Lấy permission theo ID
- `PUT /rbac/permissions/{id}` - Cập nhật permission
- `DELETE /rbac/permissions/{id}` - Xóa permission

#### Resources
- `GET /rbac/resources` - Lấy danh sách resources
- `POST /rbac/resources` - Tạo resource mới
- `GET /rbac/resources/{id}` - Lấy resource theo ID
- `PUT /rbac/resources/{id}` - Cập nhật resource
- `DELETE /rbac/resources/{id}` - Xóa resource

#### Assignments
- `POST /rbac/users/{user_id}/roles` - Gán roles cho user
- `GET /rbac/users/{user_id}/roles` - Lấy roles của user
- `GET /rbac/users/{user_id}/permissions` - Lấy permissions của user
- `POST /rbac/roles/{role_id}/permissions` - Gán permissions cho role
- `GET /rbac/roles/{role_id}/permissions` - Lấy permissions của role

### ABAC Endpoints

#### Policies
- `GET /abac/policies` - Lấy danh sách policies
- `POST /abac/policies` - Tạo policy mới
- `GET /abac/policies/{id}` - Lấy policy theo ID
- `PUT /abac/policies/{id}` - Cập nhật policy
- `DELETE /abac/policies/{id}` - Xóa policy

#### Attributes
- `GET /abac/attributes` - Lấy danh sách attributes
- `POST /abac/attributes` - Tạo attribute mới
- `GET /abac/attributes/{id}` - Lấy attribute theo ID

#### User Attributes
- `POST /abac/users/{user_id}/attributes` - Set user attribute
- `GET /abac/users/{user_id}/attributes` - Lấy attributes của user
- `GET /abac/users/{user_id}/attributes/{name}` - Lấy giá trị attribute cụ thể

#### Authorization
- `POST /abac/authorize` - Kiểm tra quyền truy cập

## Sử dụng hệ thống

### 1. Quản lý Roles

1. Truy cập `/iam/roles` để xem danh sách roles
2. Click "Create Role" để tạo role mới
3. Chỉnh sửa role bằng cách click vào icon edit
4. Xóa role (trừ system roles)

### 2. Quản lý Permissions

1. Truy cập `/iam/permissions` để xem danh sách permissions
2. Sử dụng filter để lọc theo resource
3. Tạo permission mới với resource và action cụ thể
4. Chỉnh sửa hoặc xóa permissions

### 3. Quản lý Policies (ABAC)

1. Truy cập `/iam/policies` để xem danh sách policies
2. Tạo policy mới với các điều kiện JSON
3. Xem chi tiết policy để hiểu logic
4. Chỉnh sửa hoặc xóa policies

### 4. Gán quyền cho User

1. Truy cập `/iam/users` để xem danh sách users
2. Click vào user để xem chi tiết
3. Gán roles cho user
4. Xem permissions của user

## Ví dụ Policy ABAC

### Policy 1: Department Access
```json
{
  "name": "Department Access Policy",
  "description": "Users can only access resources from their own department",
  "policy_type": "conditional",
  "priority": 10,
  "subject_conditions": {
    "user.department": {"operator": "eq", "value": "{{resource.owner}}"}
  },
  "resource_conditions": {
    "resource.owner": {"operator": "exists"}
  },
  "effect": "allow"
}
```

### Policy 2: Clearance Level
```json
{
  "name": "Clearance Level Policy",
  "description": "Users can only access resources at or below their clearance level",
  "policy_type": "conditional",
  "priority": 20,
  "subject_conditions": {
    "user.clearance_level": {"operator": "gte", "value": "{{resource.sensitivity}}"}
  },
  "resource_conditions": {
    "resource.sensitivity": {"operator": "exists"}
  },
  "effect": "allow"
}
```

## Testing

Chạy script test để kiểm tra hệ thống:

```bash
cd be
python test_rbac_abac.py
```

## Lưu ý quan trọng

1. **System Roles**: Không thể xóa các system roles
2. **Policy Priority**: Số nhỏ hơn = ưu tiên cao hơn
3. **JSON Conditions**: Phải đúng format JSON
4. **Attribute Names**: Sử dụng dot notation (user.department)
5. **Operators**: Hỗ trợ eq, ne, gt, lt, in, not_in, regex, exists

## Mở rộng

Hệ thống có thể được mở rộng thêm:
- Thêm operators mới cho policy conditions
- Tích hợp với external identity providers
- Thêm audit logging chi tiết hơn
- Tạo policy templates
- Thêm policy simulation/testing tools
