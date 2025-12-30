# 考勤管理系统 (Attendance Management System)

## 📋 第一部分：项目功能 (Part 1: What Does This Project Do)

考勤管理系统是一个基于二维码的现代化考勤管理解决方案，专为管理员和员工设计。

### 核心功能
- 🔐 **安全认证**：基于令牌的安全登录系统
- 📱 **二维码考勤**：管理员生成二维码，员工扫描签到/签退
- 👥 **用户管理**：管理员可创建和管理用户账户
- ⏱️ **时间跟踪**：精确记录员工的工作时间
- ✅ **审批流程**：管理员审批员工的时间条目
- 📊 **月度报告**：完整的考勤摘要和统计数据
- 🌐 **中文界面**：完整的简体中文用户界面
- 📱 **移动友好**：响应式设计，支持手机和平板电脑

### 工作流程
1. **管理员**：登录系统 → 选择员工 → 生成二维码
2. **员工**：使用手机扫描二维码 → 系统自动记录签到/签退
3. **管理员**：查看待审批列表 → 批准或拒绝时间记录
4. **员工**：查看个人考勤记录和月度摘要

---

## 👤 第二部分：用户权限 (Part 2: User Roles & Privileges)

### 管理员 (Manager) 权限

管理员拥有以下权限：

| 功能 | 说明 | 权限 |
|------|------|------|
| **用户管理** | | |
| 创建新用户 | 可创建管理员或承包商账户 | ✅ 是 |
| 分配员工 | 将承包商分配到自己的管理范围 | ✅ 是 |
| 查看用户列表 | 查看所有系统用户 | ✅ 是 |
| **考勤管理** | | |
| 生成二维码 | 为员工生成签到/签退二维码 | ✅ 是 |
| 查看员工考勤 | 查看分配给自己的员工的所有时间记录 | ✅ 是 |
| 审批时间条目 | 批准或拒绝员工的考勤记录 | ✅ 是 |
| 查看待审批列表 | 查看需要审批的时间条目 | ✅ 是 |
| **个人操作** | | |
| 手动签到/签退 | 自己也可以签到签退 | ✅ 是 |
| 查看个人记录 | 查看自己的考勤记录 | ✅ 是 |
| 修改账户设置 | 更改密码等个人信息 | ✅ 是 |
| 删除自己账户 | 删除自己的账户（谨慎操作） | ✅ 是 |

### 承包商/员工 (Contractor) 权限

承包商拥有以下权限：

| 功能 | 说明 | 权限 |
|------|------|------|
| **用户管理** | | |
| 创建新用户 | 不能创建其他用户 | ❌ 否 |
| 分配员工 | 不能分配员工 | ❌ 否 |
| 查看用户列表 | 不能查看用户列表 | ❌ 否 |
| **考勤管理** | | |
| 扫描二维码 | 扫描管理员生成的二维码进行签到/签退 | ✅ 是 |
| 手动签到/签退 | 手动签到签退（需要管理员审批） | ✅ 是 |
| 查看个人记录 | 查看自己的所有考勤记录 | ✅ 是 |
| 查看月度摘要 | 查看自己的月度考勤摘要 | ✅ 是 |
| 查看他人记录 | 不能查看其他员工的记录 | ❌ 否 |
| 审批时间条目 | 不能审批任何记录 | ❌ 否 |
| **个人操作** | | |
| 修改账户设置 | 更改密码等个人信息 | ✅ 是 |
| 删除自己账户 | 删除自己的账户（谨慎操作） | ✅ 是 |

### 权限对比矩阵

| 操作 | 管理员 | 承包商 |
|------|:------:|:------:|
| 创建用户 | ✅ | ❌ |
| 分配员工到管理员 | ✅ | ❌ |
| 生成二维码 | ✅ | ❌ |
| 扫描二维码签到/签退 | ✅ | ✅ |
| 手动签到/签退 | ✅ | ✅ |
| 查看自己的考勤 | ✅ | ✅ |
| 查看他人的考勤 | ✅（仅分配的员工） | ❌ |
| 审批考勤记录 | ✅ | ❌ |
| 查看待审批列表 | ✅ | ❌ |
| 用户管理页面 | ✅ | ❌ |
| 月度摘要 | ✅ | ✅ |
| 修改个人设置 | ✅ | ✅ |

### 重要说明

1. **管理员-员工关系**：
   - 管理员只能查看和管理分配给自己的员工
   - 一个员工可以被分配给多个管理员
   - 员工的时间记录需要分配的管理员审批

2. **二维码工作流**：
   - 通过二维码签到/签退的记录会自动批准
   - 手动签到/签退的记录需要管理员审批
   - 二维码有效期为5分钟

3. **账户创建权限**：
   - 只有管理员可以创建新用户
   - 管理员可以创建管理员或承包商账户
   - 新创建的承包商需要手动分配给管理员

---

## 🚀 第三部分：启动服务器和测试 (Part 3: Start Server & Test)

### 前置要求

- **Python 3.8 或更高版本**
- **MySQL 8.0 或更高版本**
- **现代浏览器**（Chrome、Firefox、Safari、Edge）
- **移动设备浏览器**（用于二维码扫描）

### 步骤 1：初始化 MySQL 数据库

```bash
# 1. 登录 MySQL（根据提示输入密码）
mysql -u root -p

# 2. 创建数据库
CREATE DATABASE attendance_system;

# 3. 退出 MySQL
EXIT;

# 4. 导入数据库架构（从项目根目录执行）
mysql -u root -p attendance_system < backend/database/init_database.sql
```

**数据库配置详情：**
- 数据库名：`attendance_system`
- 默认用户：`root`
- 默认主机：`localhost`
- 默认端口：`3306`

### 步骤 2：安装 Python 依赖

```bash
# 进入后端目录
cd backend

# 推荐：创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

**所需 Python 包：**
- Flask（Web 框架）
- Flask-CORS（跨域支持）
- PyMySQL（MySQL 连接）
- python-dotenv（环境变量管理）
- hashlib（密码加密）

### 步骤 3：配置环境变量（可选）

如需修改默认配置，在 `backend` 目录创建 `.env` 文件：

```bash
# backend/.env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_NAME=attendance_system

PORT=5001
HOST=0.0.0.0
DEBUG=True
SECRET_KEY=你的密钥

CORS_ORIGINS=*
```

### 步骤 4：启动后端服务器

```bash
# 方法 1：直接运行（从 backend 目录）
cd backend
python run.py

# 方法 2：使用脚本（从项目根目录）
./scripts/start.sh
```

**后端服务器信息：**
- 📡 **地址**: `http://localhost:5001`
- 🔌 **API 端点**: `http://localhost:5001/api`
- 🛠 **调试模式**: 默认启用

**启动成功标志：**
```
╔══════════════════════════════════════════════════════╗
║   Attendance Management System - Backend Server     ║
╠══════════════════════════════════════════════════════╣
║   Server running on: http://0.0.0.0:5001            ║
║   Database: attendance_system                       ║
║   Debug Mode: True                                  ║
╚══════════════════════════════════════════════════════╝
```

### 步骤 5：启动前端服务器

**打开新的终端窗口**，执行以下命令：

```bash
# 进入前端目录
cd frontend

# 启动 HTTP 服务器
python3 -m http.server 8080

# 或者在 Windows 上：
python -m http.server 8080
```

**前端服务器信息：**
- 🌐 **桌面访问**: `http://localhost:8080`
- 📱 **移动访问**: `http://[你的电脑IP]:8080`
- 🔌 **端口**: `8080`

**查找你的IP地址：**
```bash
# Linux/Mac:
ifconfig | grep inet

# Windows:
ipconfig
```

### 步骤 6：访问系统

#### 桌面/电脑访问

在浏览器中打开以下页面：

| 页面 | URL | 说明 |
|------|-----|------|
| 主页 | http://localhost:8080 | 系统入口，选择角色 |
| 管理员门户 | http://localhost:8080/manager/portal.html | 管理员登录和操作 |
| 员工仪表板 | http://localhost:8080/employee/dashboard.html | 员工登录和考勤 |
| 创建账户 | http://localhost:8080/register.html | 管理员创建新用户 |
| 用户管理 | http://localhost:8080/manager/user-management.html | 查看所有用户 |

#### 移动设备访问

**用于二维码扫描：**
```
http://[你的电脑IP]:8080/worker/scan.html
```

**示例：**
```
http://192.168.1.100:8080/worker/scan.html
```

**确保：**
- 手机和电脑在同一WiFi网络
- 电脑防火墙允许8080端口
- 浏览器允许相机权限

---

## 🧪 测试端口和 API

### 端口配置

| 服务 | 端口 | 协议 | 用途 |
|------|------|------|------|
| **前端** | 8080 | HTTP | 网页界面 |
| **后端API** | 5001 | HTTP | REST API服务 |
| **MySQL** | 3306 | TCP | 数据库 |

### 快速测试

#### 1. 测试后端连接

```bash
# 检查后端是否运行
curl http://localhost:5001/api/health

# 预期输出：
# {"status": "ok", "message": "API is running"}
```

#### 2. 测试用户登录

```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ylin",
    "password": "你设置的密码"
  }'

# 预期输出：
# {"user": {"username": "ylin", "display_name": "Yuchen Lin", ...}}
```

#### 3. 测试二维码生成

```bash
curl -X POST http://localhost:5001/api/attendance/qr/generate \
  -H "Content-Type: application/json" \
  -d '{
    "manager_username": "ylin",
    "worker_username": "xlu",
    "action": "check-in"
  }'

# 预期输出：
# {"token": "...", "expires_in_seconds": 300, ...}
```

#### 4. 测试二维码验证

```bash
curl -X POST http://localhost:5001/api/attendance/qr/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "从上一步获取的token"
  }'

# 预期输出：
# {"message": "Check-in successful", ...}
```

### 完整的 API 端点列表

#### 认证 API (Authentication)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/login` | POST | 用户登录 |

#### 用户 API (Users)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/users/` | POST | 创建新用户（仅管理员） |
| `/api/users/<username>` | GET | 获取用户信息 |
| `/api/users/<username>/contractors` | GET | 获取管理员的员工列表 |
| `/api/users/assign-manager` | POST | 分配员工给管理员 |
| `/api/users/<username>` | DELETE | 删除用户账户 |
| `/api/users/<username>/change-password` | POST | 修改密码 |

#### 考勤 API (Attendance)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/attendance/check-in` | POST | 手动签到 |
| `/api/attendance/check-out` | POST | 手动签退 |
| `/api/attendance/my-entries` | GET | 获取个人考勤记录 |
| `/api/attendance/pending-approvals` | GET | 获取待审批列表 |
| `/api/attendance/approve` | POST | 审批考勤记录 |
| `/api/attendance/monthly-summary` | GET | 获取月度摘要 |
| `/api/attendance/qr/generate` | POST | 生成二维码 |
| `/api/attendance/qr/verify` | POST | 验证二维码 |
| `/api/attendance/qr/status/<token>` | GET | 查询二维码状态 |

### 测试账户

系统包含以下预设测试账户（首次使用需设置密码）：

| 用户名 | 显示名称 | 角色 | 用途 |
|--------|----------|------|------|
| `ylin` | Yuchen Lin | 管理员 | 测试管理员功能 |
| `xlu` | Xuanyu Lu | 承包商 | 测试员工功能 1 |
| `jsmith` | John Smith | 承包商 | 测试员工功能 2 |

**注意**：这些账户的密码在 `init_database.sql` 中是加密的，建议创建新账户进行测试。

### 完整测试流程

#### 场景 1：管理员创建员工并生成二维码

```bash
# 1. 管理员登录
# 访问: http://localhost:8080/manager/portal.html

# 2. 创建新员工
# 访问: http://localhost:8080/register.html

# 3. 选择员工并生成二维码
# 在管理员门户中选择员工 → 点击"生成签到二维码"

# 4. 员工扫描二维码
# 手机访问: http://[IP]:8080/worker/scan.html
# 点击"启动相机" → 扫描二维码
```

#### 场景 2：员工手动签到并等待审批

```bash
# 1. 员工登录
# 访问: http://localhost:8080/employee/dashboard.html

# 2. 点击"签到"按钮

# 3. 管理员登录并审批
# 访问: http://localhost:8080/manager/portal.html
# 点击"待审批" → 批准或拒绝
```

---

## 📱 移动设备使用指南

系统完全支持移动设备，特别为手机优化了二维码扫描功能。

### 移动端访问步骤

1. **确保手机和电脑在同一WiFi网络**

2. **查找电脑IP地址**：
   ```bash
   # Mac/Linux
   ifconfig | grep inet

   # Windows
   ipconfig
   ```

3. **在手机浏览器中打开**：
   ```
   http://[电脑IP]:8080/worker/scan.html
   ```

4. **允许相机权限**

5. **扫描管理员生成的二维码**

### 移动端支持的功能

| 功能 | 支持 | 说明 |
|------|:----:|------|
| 二维码扫描 | ✅ | 使用手机相机扫描 |
| 手动输入令牌 | ✅ | 相机不可用时的备选方案 |
| 员工仪表板 | ✅ | 查看个人考勤记录 |
| 签到/签退 | ✅ | 手动签到签退 |
| 月度摘要 | ✅ | 查看月度统计 |
| 账户设置 | ✅ | 修改密码等 |
| 管理员功能 | ✅ | 平板电脑可正常使用 |

### 支持的移动浏览器

- ✅ iOS Safari (iOS 13+)
- ✅ Android Chrome (Android 8+)
- ✅ Android Firefox
- ✅ Samsung Internet

### 移动端优化特性

- 📱 响应式布局适配所有屏幕尺寸
- 👆 大号按钮便于触摸操作
- 📷 原生相机API集成
- 🔄 自动屏幕旋转支持
- ⚡ 快速加载和响应

---

## 🛠 常见问题解决

### 数据库相关

**问题：无法连接到MySQL**
```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 启动MySQL服务
sudo systemctl start mysql

# 重启MySQL服务
sudo systemctl restart mysql
```

**问题：数据库不存在**
```bash
# 手动创建数据库
mysql -u root -p -e "CREATE DATABASE attendance_system;"

# 导入架构
mysql -u root -p attendance_system < backend/database/init_database.sql
```

### 端口相关

**问题：端口被占用**
```bash
# 查找占用端口的进程
lsof -i :5001  # 后端
lsof -i :8080  # 前端

# 终止进程
kill -9 [进程ID]

# 或使用其他端口
python run.py --port 5002
python -m http.server 8081
```

### 权限相关

**问题：相机权限被拒绝**
- 在浏览器设置中允许相机访问
- 使用 HTTPS（本地开发可忽略）
- 尝试使用"手动输入"功能

**问题：无法创建用户**
- 确认是以管理员身份登录
- 检查后端日志查看错误信息

### 连接相关

**问题：移动设备无法访问**
- 确认在同一WiFi网络
- 检查防火墙设置
- 尝试关闭电脑防火墙测试

**问题：API返回CORS错误**
- 检查 `backend/app/config.py` 中的 CORS 设置
- 确保后端服务器正在运行

---

## 📞 技术支持

如有问题或建议，请：
- 📧 发送邮件至技术支持
- 🐛 在GitHub提交Issue
- 📖 查阅项目文档

---

**版本**: 2.0
**最后更新**: 2025年12月
**技术栈**: Python Flask + MySQL + Vanilla JavaScript
