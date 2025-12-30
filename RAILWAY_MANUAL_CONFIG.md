# Railway 手动配置方法 | Railway Manual Configuration

## 🎯 最可靠的部署方法 (Most Reliable Method)

如果自动检测失败，使用手动配置是最可靠的方法。

---

## 📋 手动配置步骤 (Manual Configuration Steps)

### 步骤 1：删除自动检测文件（可选）

如果您遇到 "start.sh not found" 错误，可以暂时禁用自动检测：

1. 进入 Railway 项目
2. 点击您的服务
3. 进入 **Settings** 标签

---

### 步骤 2：设置根目录 (Set Root Directory)

**最重要的设置！**

1. 在 Settings 中找到 **Root Directory**
2. 输入：`backend`
3. 点击保存

```
Root Directory: backend
```

---

### 步骤 3：手动设置启动命令 (Set Start Command Manually)

这是关键步骤，绕过所有自动检测问题。

1. 在 Settings 中找到 **Deploy** 部分
2. 找到 **Start Command** 或 **Custom Start Command**
3. 输入以下命令：

```bash
gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

4. 点击保存

**截图指引：**
```
Settings → Deploy Section
┌─────────────────────────────────────────┐
│ Start Command                           │
│ ┌─────────────────────────────────────┐ │
│ │ gunicorn run:app --bind 0.0.0.0:$P │ │
│ │ ORT --workers 2 --timeout 60       │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Save]                                  │
└─────────────────────────────────────────┘
```

---

### 步骤 4：设置构建命令（如果需要）

1. 在同一个 Deploy 部分
2. 找到 **Build Command** 或 **Custom Build Command**
3. 输入：

```bash
pip install -r requirements.txt
```

---

### 步骤 5：验证 Python 版本

1. 在 Settings 中找到 **Environment**
2. 确认 Python 版本（应该自动检测为 3.10+）

如果需要手动指定：
- 创建 `runtime.txt` 文件（已创建）
- 内容：`python-3.10.12`

---

### 步骤 6：配置环境变量

在 **Variables** 标签中添加：

```bash
# 数据库配置（从 MySQL 服务复制）
DB_HOST=${{MySQL.MYSQLHOST}}
DB_PORT=${{MySQL.MYSQLPORT}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
DB_NAME=${{MySQL.MYSQLDATABASE}}

# Flask 配置
SECRET_KEY=<生成随机64字符密钥>
DEBUG=False
PORT=${{PORT}}
HOST=0.0.0.0
CORS_ORIGINS=*
```

**生成 SECRET_KEY：**
```bash
# 本地运行生成随机密钥
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

### 步骤 7：触发重新部署

1. 进入 **Deployments** 标签
2. 点击 **Deploy** 或 **Redeploy**
3. 选择最新的 commit
4. 等待部署完成

---

## ✅ 验证配置正确

### 检查清单：

- [ ] Root Directory = `backend` ✓
- [ ] Start Command = `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60` ✓
- [ ] 环境变量已配置（DB_HOST, DB_PORT, etc.）✓
- [ ] MySQL 数据库已添加 ✓
- [ ] 已触发新的部署 ✓

---

## 🔍 查看部署日志

部署过程中，查看日志确认：

1. 进入 **Deployments** 标签
2. 点击正在进行的部署
3. 查看 **Build Logs** 和 **Deploy Logs**

### 期望看到的日志：

**Build Logs:**
```
✓ Installing Python 3.10
✓ Installing dependencies
Collecting Flask==3.0.0
Collecting mysql-connector-python==8.2.0
Collecting gunicorn==21.2.0
✓ Successfully installed Flask-3.0.0 gunicorn-21.2.0 ...
```

**Deploy Logs:**
```
Starting gunicorn...
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:XXXX
[INFO] Using worker: sync
[INFO] Booting worker with pid: XXXX
```

---

## 🆘 常见错误及解决方案

### 错误 1: "Module 'run' not found"

**原因：** Root Directory 未设置或设置错误

**解决：**
```
Root Directory 必须是: backend
不是: /backend
不是: ./backend
不是: 留空
```

---

### 错误 2: "Address already in use"

**原因：** 端口冲突（通常不会在 Railway 发生）

**解决：** 确保使用 `$PORT` 环境变量
```bash
--bind 0.0.0.0:$PORT  # 正确
--bind 0.0.0.0:5001   # 错误（硬编码端口）
```

---

### 错误 3: "No module named 'app'"

**原因：** Python 找不到 app 模块

**解决：**
1. 确认 `backend/app/__init__.py` 存在
2. 确认 Root Directory = `backend`
3. 确认 `backend/run.py` 存在

---

### 错误 4: "Database connection failed"

**原因：** 环境变量配置错误

**解决：**
1. 检查 MySQL 服务是否运行（在 Railway 项目中）
2. 验证环境变量引用语法：
   ```
   正确: DB_HOST=${{MySQL.MYSQLHOST}}
   错误: DB_HOST=${MySQL.MYSQLHOST}
   错误: DB_HOST={{MySQL.MYSQLHOST}}
   ```

---

## 🎯 完整的手动配置示例

### Railway Service Settings:

```yaml
Service Name: attendance-backend
Root Directory: backend

Build:
  Build Command: pip install -r requirements.txt

Deploy:
  Start Command: gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60

Environment Variables:
  DB_HOST: ${{MySQL.MYSQLHOST}}
  DB_PORT: ${{MySQL.MYSQLPORT}}
  DB_USER: ${{MySQL.MYSQLUSER}}
  DB_PASSWORD: ${{MySQL.MYSQLPASSWORD}}
  DB_NAME: ${{MySQL.MYSQLDATABASE}}
  SECRET_KEY: <your-secret-key>
  DEBUG: False
  PORT: ${{PORT}}
  HOST: 0.0.0.0
  CORS_ORIGINS: *
```

---

## 🔄 如果还是失败

### 方法 1：完全删除配置文件

有时 Railway 会被配置文件混淆。尝试：

1. 暂时重命名或删除这些文件（本地）：
   ```bash
   mv backend/railway.json backend/railway.json.bak
   mv backend/nixpacks.toml backend/nixpacks.toml.bak
   mv backend/start.sh backend/start.sh.bak
   ```

2. 只保留 `Procfile` 和 `requirements.txt`

3. Commit 和 push

4. 在 Railway 手动设置启动命令（见上面步骤 3）

---

### 方法 2：使用 Python 直接运行

如果 gunicorn 有问题，尝试直接使用 Python：

**Start Command:**
```bash
python run.py
```

但需要修改 `run.py`：

```python
if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 5001))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # 生产环境必须 False
    )
```

---

### 方法 3：联系 Railway 支持

如果所有方法都失败：

1. 访问 Railway Discord: https://discord.gg/railway
2. 在 #help 频道询问
3. 提供：
   - 部署日志截图
   - 配置截图
   - 错误信息

---

## 📱 快速参考卡片

### 最简配置（复制粘贴）:

```
# Railway Settings
Root Directory: backend

# Start Command
gunicorn run:app --bind 0.0.0.0:$PORT --workers 2

# Environment Variables
DB_HOST=${{MySQL.MYSQLHOST}}
DB_PORT=${{MySQL.MYSQLPORT}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
DB_NAME=${{MySQL.MYSQLDATABASE}}
SECRET_KEY=<random-64-char-string>
DEBUG=False
PORT=${{PORT}}
HOST=0.0.0.0
CORS_ORIGINS=*
```

---

## ✅ 成功部署的标志

当您看到这些信息时，说明部署成功：

**在 Railway Dashboard:**
```
✓ Build successful
✓ Deploy successful
🟢 Active
```

**在 Deploy Logs:**
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:XXXX
[INFO] Using worker: sync
[INFO] Booting worker with pid: XXXX
```

**访问 URL:**
- 显示前端页面
- 可以登录（ylin / password!）
- 无 500 错误

---

**使用此手动方法应该可以绕过所有自动检测问题！** 🚀

如果仍有问题，请查看部署日志并告诉我具体的错误信息。
