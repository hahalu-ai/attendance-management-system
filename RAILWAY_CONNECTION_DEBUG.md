# Railway 连接问题排查 | Railway Connection Debug

## 🔴 问题：无法连接到服务

URL: `attendance-management-system-production-1f1a.up.railway.app`
错误：无法连接 / Connection refused / Timeout

---

## 🔍 排查步骤 (Debugging Steps)

### 步骤 1：检查部署状态 (Check Deployment Status)

在 Railway Dashboard 中：

1. 进入您的项目
2. 点击 **backend service**
3. 查看右上角的状态：
   - 🟢 **Active** = 正常运行 ✓
   - 🟡 **Deploying** = 正在部署（等待）
   - 🔴 **Crashed** = 崩溃了 ✗
   - ⚪ **Inactive** = 未运行 ✗

**如果状态不是 🟢 Active，应用可能崩溃了。**

---

### 步骤 2：检查部署日志 (Check Deploy Logs)

1. 在 Railway 中点击 **Deployments** 标签
2. 点击最新的部署
3. 查看 **Deploy Logs**（不是 Build Logs）

#### 查找以下错误信息：

**错误 1: 数据库连接失败**
```
Error connecting to MySQL
mysql.connector.errors.DatabaseError
Connection refused
```

**解决方法：** 数据库未配置或环境变量错误

**错误 2: 应用崩溃**
```
ModuleNotFoundError: No module named 'app'
ImportError: cannot import name 'create_app'
```

**解决方法：** Root Directory 设置错误

**错误 3: 端口问题**
```
Address already in use
failed to bind to 0.0.0.0:XXXX
```

**解决方法：** 端口配置问题

---

### 步骤 3：检查环境变量 (Check Environment Variables)

在 Railway 中：
1. 点击 backend service
2. 进入 **Variables** 标签
3. 确认以下变量存在：

**必需的变量：**
```
✓ DB_HOST
✓ DB_PORT
✓ DB_USER
✓ DB_PASSWORD
✓ DB_NAME
✓ PORT
✓ HOST
✓ SECRET_KEY
✓ DEBUG
✓ CORS_ORIGINS
```

**如果缺少任何数据库变量，应用会启动失败。**

---

### 步骤 4：检查 MySQL 数据库状态

1. 在 Railway 项目中找到 **MySQL** 服务
2. 查看状态是否为 🟢 **Active**
3. 如果 MySQL 未运行，启动它

---

## 🛠️ 常见问题及解决方案

### 问题 1：数据库连接失败

**症状：** 应用启动但立即崩溃

**原因：** 环境变量未正确配置

**解决方案：**

1. 进入 Railway → MySQL 服务
2. 点击 **Variables** 标签
3. 复制以下变量：
   - `MYSQLHOST`
   - `MYSQLPORT`
   - `MYSQLUSER`
   - `MYSQLPASSWORD`
   - `MYSQLDATABASE`

4. 进入 backend service → **Variables**
5. 添加（使用 Railway 引用语法）：
   ```
   DB_HOST=${{MySQL.MYSQLHOST}}
   DB_PORT=${{MySQL.MYSQLPORT}}
   DB_USER=${{MySQL.MYSQLUSER}}
   DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
   DB_NAME=${{MySQL.MYSQLDATABASE}}
   ```

**重要：** 必须使用 `${{MySQL.VARIABLENAME}}` 语法！

---

### 问题 2：域名生成但无响应

**症状：** URL 存在但浏览器显示 "无法连接" 或 "ERR_CONNECTION_REFUSED"

**原因：** 应用未正确监听端口

**解决方案：**

检查 Dockerfile 中的 CMD：
```dockerfile
CMD gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

确保使用 `$PORT` 变量（不是硬编码的 5001）

---

### 问题 3：Root Directory 错误

**症状：**
```
ModuleNotFoundError: No module named 'run'
```

**解决方案：**

1. Settings → Root Directory
2. 设置为：`backend` （不是 `/backend` 或 `./backend`）
3. 保存并重新部署

---

### 问题 4：数据库未初始化

**症状：** 应用启动但访问时显示错误

**解决方案：**

导入数据库架构：

```bash
# 方法 1: Railway CLI
railway login
railway link
railway connect MySQL

# 在 MySQL 提示符中：
source backend/database/init_database.sql

# 方法 2: 一行命令
railway run mysql -h $MYSQLHOST -u $MYSQLUSER -p$MYSQLPASSWORD $MYSQLDATABASE < backend/database/init_database.sql
```

---

## 🔧 立即诊断清单

请按顺序检查以下项目：

### ✅ 检查清单

- [ ] Railway 后端服务状态是 🟢 Active
- [ ] Railway MySQL 服务状态是 🟢 Active
- [ ] Root Directory = `backend`
- [ ] 环境变量已配置（DB_HOST, DB_PORT, 等）
- [ ] Deploy Logs 中没有错误信息
- [ ] 数据库已导入 init_database.sql

---

## 🧪 测试命令

### 测试 1：检查域名是否可达

```bash
curl -I https://attendance-management-system-production-1f1a.up.railway.app
```

**期望结果：** 返回 HTTP 200 或显示 HTML
**如果超时：** 应用未运行或崩溃了

### 测试 2：检查端口

```bash
curl https://attendance-management-system-production-1f1a.up.railway.app/
```

**期望结果：** 返回 HTML（登录页面）
**如果返回错误：** 查看具体错误信息

### 测试 3：测试 API

```bash
curl https://attendance-management-system-production-1f1a.up.railway.app/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"ylin","password":"password!"}'
```

**期望结果：** 返回 JSON 用户数据或错误信息

---

## 📊 Railway 日志分析

### 健康的日志应该是：

```
✓ [INFO] Starting gunicorn 21.2.0
✓ [INFO] Listening at: http://0.0.0.0:8080
✓ [INFO] Booting worker with pid: 3
✓ [INFO] Booting worker with pid: 4
✓ (没有后续错误)
```

### 不健康的日志：

```
✗ Error connecting to MySQL
✗ Connection refused
✗ [CRITICAL] Worker timeout
✗ Application startup failed
```

---

## 🚨 紧急修复步骤

如果应用一直崩溃，尝试以下快速修复：

### 1. 临时禁用数据库连接测试

修改 `backend/run.py`，添加错误处理：

```python
if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 5001))

    try:
        print(f"Starting server on port {port}...")
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False
        )
    except Exception as e:
        print(f"Error starting app: {e}")
        import traceback
        traceback.print_exc()
```

### 2. 检查配置

创建一个诊断端点来查看环境变量：

在 `backend/app/__init__.py` 中添加：

```python
@app.route('/debug')
def debug():
    import os
    return {
        "DB_HOST": os.getenv('DB_HOST', 'NOT SET'),
        "DB_PORT": os.getenv('DB_PORT', 'NOT SET'),
        "DB_NAME": os.getenv('DB_NAME', 'NOT SET'),
        "PORT": os.getenv('PORT', 'NOT SET'),
    }
```

然后访问：
```
https://attendance-management-system-production-1f1a.up.railway.app/debug
```

**注意：** 部署到生产后记得删除此端点！

---

## 📞 需要查看的信息

如果问题仍未解决，请提供以下信息：

1. **Railway 部署日志**
   - Deployments → 最新部署 → Deploy Logs（完整复制）

2. **服务状态**
   - Backend service 状态（Active/Crashed/Inactive）
   - MySQL service 状态

3. **环境变量截图**
   - Variables 标签的截图（隐藏敏感信息）

4. **错误信息**
   - 浏览器中显示的具体错误
   - 或 curl 命令返回的错误

---

## ✅ 最可能的原因

根据您的情况（日志显示启动成功但无法连接），最可能的原因是：

1. **数据库连接失败** → 应用启动后立即崩溃
2. **环境变量缺失** → 应用无法连接数据库
3. **健康检查失败** → Railway 认为应用不健康

**立即检查：** Deploy Logs 中在 "Booting worker" 之后是否有错误信息。

---

**下一步：请查看 Railway Deploy Logs 并告诉我具体的错误信息！** 🔍
