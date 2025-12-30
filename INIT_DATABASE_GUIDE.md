# 初始化 Railway 数据库指南
# Railway Database Initialization Guide

您的应用现在显示 "Application failed to respond" 的主要原因是 **数据库未初始化**。

---

## 🎯 三种初始化方法（选一种）

### 方法 1: 使用自动化脚本（最简单）⭐⭐⭐

我已经创建了一个自动化脚本来帮您完成所有步骤。

#### 步骤 1: 安装 Railway CLI

```bash
npm i -g @railway/cli
```

如果没有 npm，先安装 Node.js:
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install nodejs npm

# macOS
brew install node
```

#### 步骤 2: 运行初始化脚本

```bash
cd /home/yuchen/codespace/attendance-management-system

# 使用 Bash 脚本
./scripts/init-railway-database.sh

# 或使用 Python 脚本
python3 scripts/init-railway-database-python.py
```

脚本会自动：
- ✅ 检查 Railway CLI 是否安装
- ✅ 登录 Railway（如果需要）
- ✅ 链接到您的项目（如果需要）
- ✅ 导入数据库架构
- ✅ 创建默认用户

---

### 方法 2: 手动使用 Railway CLI

如果脚本不工作，手动执行这些命令：

```bash
# 1. 安装 Railway CLI
npm i -g @railway/cli

# 2. 登录
railway login

# 3. 链接项目
cd /home/yuchen/codespace/attendance-management-system
railway link

# 4. 导入数据库
railway run mysql -h $MYSQLHOST -u $MYSQLUSER -p$MYSQLPASSWORD $MYSQLDATABASE < backend/database/init_database.sql
```

---

### 方法 3: 使用 Railway Web UI（不需要 CLI）

如果您不想安装 Railway CLI：

#### 步骤 1: 获取 SQL 文件内容

```bash
cat backend/database/init_database.sql
```

复制所有输出内容。

#### 步骤 2: 在 Railway 中执行

1. 进入 Railway Dashboard
2. 点击 **MySQL** 服务
3. 点击 **"Data"** 或 **"Query"** 标签
4. **删除第一行** `USE attendance_system;`（因为 Railway 的数据库名是 `railway`）
5. 粘贴剩余的 SQL 内容
6. 点击 **Execute** 或 **Run**

---

## ✅ 验证数据库已初始化

初始化后，验证表已创建：

### 使用 Railway CLI:

```bash
railway connect MySQL
```

然后在 MySQL 提示符中：
```sql
SHOW TABLES;
```

您应该看到：
```
+----------------------------+
| Tables_in_railway          |
+----------------------------+
| manager_assignments        |
| qr_requests                |
| time_entries               |
| users                      |
+----------------------------+
```

检查用户：
```sql
SELECT username, display_name, user_level FROM users;
```

应该显示：
```
+----------+--------------+------------+
| username | display_name | user_level |
+----------+--------------+------------+
| ylin     | Yuchen Lin   | Manager    |
| xlu      | Xuanyu Lu    | Contractor |
| jsmith   | John Smith   | Contractor |
+----------+--------------+------------+
```

退出：
```sql
exit
```

---

## 🧪 测试应用

数据库初始化后：

### 1. 等待 2 分钟让部署完成

Railway 会在您添加调试端点后自动重新部署。

### 2. 测试健康检查端点

访问：
```
https://attendance-management-system-production-1f1a.up.railway.app/health
```

应该返回：
```json
{
  "status": "ok",
  "message": "Application is running"
}
```

### 3. 测试配置端点

访问：
```
https://attendance-management-system-production-1f1a.up.railway.app/debug-config
```

检查是否有 "NOT SET" 的值。

### 4. 访问主页

访问：
```
https://attendance-management-system-production-1f1a.up.railway.app/
```

应该看到登录页面！✅

### 5. 登录测试

使用默认凭据：
- **用户名:** `ylin`
- **密码:** `password!`

---

## 🔧 故障排除

### 问题 1: "railway: command not found"

**解决方案:** 安装 Railway CLI
```bash
npm i -g @railway/cli
```

### 问题 2: "Not logged in"

**解决方案:** 登录 Railway
```bash
railway login
```

### 问题 3: "Not linked to project"

**解决方案:** 链接项目
```bash
railway link
```

### 问题 4: "Can't connect to MySQL server"

**可能原因:**
- MySQL 服务未在 Railway 中运行
- 环境变量未正确配置

**解决方案:**
1. 检查 Railway 中 MySQL 服务状态（应为 🟢 Active）
2. 确认环境变量已正确配置

### 问题 5: "Table already exists"

这不是错误！说明表已经创建过了。

**验证:**
```bash
railway connect MySQL
SHOW TABLES;
```

---

## 📋 完整操作流程

按顺序执行：

1. ✅ **安装 Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. ✅ **运行初始化脚本**
   ```bash
   cd /home/yuchen/codespace/attendance-management-system
   ./scripts/init-railway-database.sh
   ```

3. ✅ **等待部署完成**（约 2 分钟）

4. ✅ **测试健康检查**
   ```
   https://your-app.up.railway.app/health
   ```

5. ✅ **访问登录页**
   ```
   https://your-app.up.railway.app/
   ```

6. ✅ **登录测试**
   - 用户名: `ylin`
   - 密码: `password!`

---

## 🎉 成功标志

当一切正常时，您应该：

✅ /health 返回 `{"status": "ok"}`
✅ /debug-config 显示所有配置（无 "NOT SET"）
✅ 主页显示登录界面
✅ 可以使用 ylin/password! 登录
✅ 登录后看到 Manager 仪表板

---

## 📞 仍然有问题？

如果初始化数据库后仍然无法访问：

1. **检查 Deploy Logs** - 查找错误信息
2. **访问 /debug-config** - 确认环境变量正确
3. **确认 MySQL 服务运行** - Railway 中 MySQL 状态为 Active
4. **验证表存在** - 使用 `railway connect MySQL` 和 `SHOW TABLES;`

把具体的错误信息告诉我，我会帮您解决！

---

**现在运行初始化脚本：**
```bash
./scripts/init-railway-database.sh
```

这应该能解决 "Application failed to respond" 的问题！
