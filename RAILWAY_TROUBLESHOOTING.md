# Railway 部署问题排查 | Railway Deployment Troubleshooting

## ⚠️ 常见错误：Script start.sh not found

### 错误信息 (Error Message)
```
⚠ Script start.sh not found
✖ Railpack could not determine how to build the app.
```

### 原因 (Cause)
Railway 无法检测到如何构建和启动您的 Python 应用。

---

## ✅ 解决方案 (Solutions)

### 方案 1：确认项目结构正确 (Verify Project Structure)

**重要：** 确保在 Railway 中设置了正确的 Root Directory

1. 进入 Railway 项目 → 点击后端服务
2. 进入 **Settings** 标签
3. 找到 **Root Directory**
4. 设置为：`backend`
5. 保存并重新部署

**正确的目录结构应该是：**
```
attendance-management-system/
├── backend/                    ← Railway Root Directory 应该设置为这里
│   ├── Procfile               ✓ 已创建
│   ├── railway.json           ✓ 已创建
│   ├── nixpacks.toml          ✓ 已创建
│   ├── start.sh               ✓ 已创建
│   ├── runtime.txt            ✓ 已创建
│   ├── requirements.txt       ✓ 已创建
│   ├── run.py                 ✓ 应用入口
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       └── ...
└── frontend/
```

---

### 方案 2：检查所有必需文件 (Check Required Files)

确保 `backend/` 目录下有以下文件：

#### 1. ✅ requirements.txt
```txt
Flask==3.0.0
mysql-connector-python==8.2.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

#### 2. ✅ runtime.txt
```txt
python-3.10.12
```

#### 3. ✅ Procfile
```
web: gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

#### 4. ✅ start.sh
```bash
#!/bin/bash
pip install -r requirements.txt
exec gunicorn run:app --bind 0.0.0.0:${PORT:-5001} --workers 2 --timeout 60
```

#### 5. ✅ railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "bash start.sh",
    "healthcheckPath": "/",
    "restartPolicyType": "ON_FAILURE",
    "healthcheckTimeout": 300
  }
}
```

#### 6. ✅ nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python310", "pip"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["echo 'Build phase complete'"]

[start]
cmd = "bash start.sh"
```

---

### 方案 3：手动设置启动命令 (Manual Start Command)

如果自动检测仍然失败：

1. 进入 Railway → **Settings** → **Deploy**
2. 找到 **Start Command**
3. 输入以下命令之一：

**选项 A (推荐):**
```bash
bash start.sh
```

**选项 B (简单):**
```bash
gunicorn run:app --bind 0.0.0.0:$PORT --workers 2
```

**选项 C (直接使用 Python):**
```bash
python run.py
```

4. 保存并重新部署

---

### 方案 4：检查 Git 提交 (Check Git Commits)

确保所有新创建的文件都已提交到 Git：

```bash
cd /home/yuchen/codespace/attendance-management-system

# 查看状态
git status

# 添加所有新文件
git add backend/Procfile
git add backend/railway.json
git add backend/nixpacks.toml
git add backend/start.sh
git add backend/runtime.txt
git add backend/.railwayignore
git add backend/requirements.txt

# 提交
git commit -m "Add Railway deployment configuration files"

# 推送到 GitHub
git push origin main
```

Railway 会自动检测到新提交并重新部署。

---

## 🔍 验证部署文件 (Verify Deployment Files)

### 本地检查清单 (Local Checklist)

运行以下命令验证所有文件存在：

```bash
cd /home/yuchen/codespace/attendance-management-system/backend

# 检查所有必需文件
echo "Checking deployment files..."
files=("Procfile" "railway.json" "nixpacks.toml" "start.sh" "runtime.txt" "requirements.txt")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file MISSING!"
    fi
done

# 检查 start.sh 是否可执行
if [ -x "start.sh" ]; then
    echo "✓ start.sh is executable"
else
    echo "⚠ start.sh is not executable - fixing..."
    chmod +x start.sh
fi
```

---

## 📊 部署流程说明 (Deployment Process)

Railway 的部署流程：

1. **检测** → Railway 读取 `railway.json` 和 `nixpacks.toml`
2. **构建** → 安装 Python 3.10 和依赖（requirements.txt）
3. **启动** → 执行 `start.sh` 或 Procfile 中的命令
4. **健康检查** → 访问根路径 `/` 确认应用运行

---

## 🆘 其他常见错误 (Other Common Errors)

### Error: "Module not found"

**原因：** Root Directory 未设置为 `backend`

**解决：**
- Settings → Root Directory → 设置为 `backend`

---

### Error: "Application failed to respond"

**原因：** 应用未绑定到正确的端口

**解决：** 确保使用环境变量 `$PORT`
```python
# 在 run.py 中
app.run(host='0.0.0.0', port=Config.PORT)

# 在 config.py 中
PORT = int(os.getenv('PORT', 5001))
```

---

### Error: "Database connection failed"

**原因：** 环境变量未正确配置

**解决：**
1. 进入 Railway → MySQL 服务
2. 复制所有连接变量
3. 在后端服务中添加：
   ```
   DB_HOST=${{MySQL.MYSQLHOST}}
   DB_PORT=${{MySQL.MYSQLPORT}}
   DB_USER=${{MySQL.MYSQLUSER}}
   DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
   DB_NAME=${{MySQL.MYSQLDATABASE}}
   ```

---

## 🎯 推荐的部署步骤 (Recommended Deployment Steps)

### 完整流程 (Complete Process)

```bash
# 1. 确保所有文件已提交
cd /home/yuchen/codespace/attendance-management-system
git add .
git commit -m "Add Railway deployment configuration"
git push origin main

# 2. 在 Railway 中：
# - 设置 Root Directory = "backend"
# - 添加 MySQL 数据库
# - 配置环境变量
# - 等待自动部署

# 3. 初始化数据库
railway login
railway link
railway connect MySQL
source backend/database/init_database.sql

# 4. 访问生成的 URL 测试
```

---

## 📞 获取更多帮助 (Get More Help)

如果问题仍然存在：

1. **查看部署日志**
   - Railway → 服务 → Deployments → 点击最新部署 → 查看日志

2. **检查构建日志**
   - 查找红色错误信息
   - 特别注意 "Error" 和 "Failed" 关键词

3. **Railway 文档**
   - https://docs.railway.app/deploy/deployments
   - https://docs.railway.app/deploy/builds

4. **Railway Discord**
   - https://discord.gg/railway
   - 活跃的社区支持

---

## ✅ 成功部署的标志 (Signs of Successful Deployment)

部署成功后，您应该看到：

```
✓ Build completed successfully
✓ Deployment live
✓ Status: Active
```

在日志中：
```
Starting application...
✓ Gunicorn started with 2 workers
✓ Listening on 0.0.0.0:$PORT
```

访问 URL：
- 应该显示前端主页
- API 端点应该响应（如 /api/auth/login）

---

**所有配置文件已更新并准备就绪！** 🚀

如果您仍然遇到问题，请检查：
1. Root Directory = `backend` ✓
2. 所有文件已提交到 Git ✓
3. 环境变量已正确配置 ✓
4. MySQL 数据库已创建 ✓
