# 部署指南 - Railway.app
## Deployment Guide for Attendance Management System

本指南将帮助您将考勤管理系统部署到 Railway.app，这是一个支持 Flask + MySQL 的云平台。

---

## 📋 部署前准备 (Prerequisites)

### 1. 创建 Railway 账户
- 访问 [Railway.app](https://railway.app)
- 使用 GitHub 账户登录（推荐）
- 免费套餐包含：
  - $5 免费额度/月
  - 500小时运行时间
  - 足够测试和小型项目使用

### 2. 准备 Git 仓库
您的代码需要托管在 Git 仓库（GitHub、GitLab 或 Bitbucket）

```bash
# 如果还没有初始化 Git 仓库
cd /home/yuchen/codespace/attendance-management-system
git init
git add .
git commit -m "Initial commit - Attendance Management System"

# 创建 GitHub 仓库并推送
# 1. 在 GitHub 上创建新仓库（不要初始化 README）
# 2. 运行以下命令（替换为您的仓库地址）：
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## 🚀 部署步骤 (Deployment Steps)

### 步骤 1：创建新项目 (Create New Project)

1. 登录 Railway.app
2. 点击 **"New Project"**
3. 选择 **"Deploy from GitHub repo"**
4. 授权 Railway 访问您的 GitHub 仓库
5. 选择 `attendance-management-system` 仓库

---

### 步骤 2：添加 MySQL 数据库 (Add MySQL Database)

1. 在项目中点击 **"+ New"**
2. 选择 **"Database"** → **"Add MySQL"**
3. Railway 会自动创建 MySQL 数据库
4. 数据库连接信息会自动生成（稍后配置）

---

### 步骤 3：配置后端服务 (Configure Backend Service)

#### 3.1 设置根目录
1. 点击后端服务（你的仓库名）
2. 进入 **"Settings"**
3. 找到 **"Root Directory"**
4. 设置为：`backend`
5. 点击保存

#### 3.2 配置环境变量 (Environment Variables)
1. 在服务页面点击 **"Variables"** 标签
2. 点击 **"+ New Variable"** 添加以下变量：

**Railway 会自动提供 MySQL 连接信息，点击 MySQL 数据库服务，复制以下变量：**

```bash
# 数据库配置（从 MySQL 服务复制）
DB_HOST=${{MySQL.MYSQLHOST}}
DB_PORT=${{MySQL.MYSQLPORT}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
DB_NAME=${{MySQL.MYSQLDATABASE}}

# Flask 配置（手动添加）
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
DEBUG=False
PORT=${{PORT}}
HOST=0.0.0.0

# CORS 配置（可选，根据您的前端域名）
CORS_ORIGINS=*
```

**重要提示：**
- `${{MySQL.MYSQLHOST}}` 等是 Railway 的变量引用语法
- Railway 会自动替换这些值为实际的数据库连接信息
- 不要使用引号包裹变量值

#### 3.3 设置启动命令（可选）
Railway 会自动检测 `Procfile`，但您也可以手动设置：

1. 进入 **"Settings"** → **"Deploy"**
2. 找到 **"Start Command"**
3. 输入：`gunicorn run:app --bind 0.0.0.0:$PORT`

---

### 步骤 4：初始化数据库 (Initialize Database)

数据库创建后，需要导入表结构和初始数据：

#### 方法 1：使用 Railway CLI（推荐）

```bash
# 1. 安装 Railway CLI
npm i -g @railway/cli
# 或使用 Homebrew (macOS)
brew install railway

# 2. 登录
railway login

# 3. 链接到您的项目
cd /home/yuchen/codespace/attendance-management-system
railway link

# 4. 连接到 MySQL 数据库
railway connect MySQL

# 5. 在 MySQL 提示符下，导入数据库
source backend/database/init_database.sql

# 或者退出后运行：
railway run mysql -h $MYSQLHOST -u $MYSQLUSER -p$MYSQLPASSWORD $MYSQLDATABASE < backend/database/init_database.sql
```

#### 方法 2：使用 MySQL 客户端

1. 在 Railway 项目中点击 MySQL 服务
2. 找到 **"Connect"** 标签，复制连接信息
3. 使用本地 MySQL 客户端连接：

```bash
mysql -h <MYSQLHOST> -P <MYSQLPORT> -u <MYSQLUSER> -p<MYSQLPASSWORD> <MYSQLDATABASE> < backend/database/init_database.sql
```

#### 方法 3：手动执行 SQL（如果文件较小）

1. 复制 `backend/database/init_database.sql` 的内容
2. 在 Railway 的 MySQL 服务中点击 **"Data"** → **"Query"**
3. 粘贴 SQL 并执行（删除第一行的 `USE attendance_system;`）

---

### 步骤 5：部署应用 (Deploy Application)

1. Railway 会自动检测到代码变化并开始部署
2. 查看部署日志：点击服务 → **"Deployments"** → 最新部署
3. 等待构建完成（通常 2-5 分钟）
4. 部署成功后，会显示绿色的 **"Success"** 状态

---

### 步骤 6：获取公共 URL (Get Public URL)

1. 在后端服务页面，点击 **"Settings"**
2. 找到 **"Networking"** 或 **"Domains"** 部分
3. 点击 **"Generate Domain"**
4. Railway 会生成一个公共 URL，类似：
   ```
   https://attendance-system-production.up.railway.app
   ```
5. 复制此 URL，这是您的 API 地址

---

### 步骤 7：部署前端 (Deploy Frontend)

您有两个选择：

#### 选项 A：与后端一起部署（简单）
Railway 已经在服务后端的同时提供前端文件（通过 Flask 的静态文件服务）

**访问应用：**
```
https://your-app.up.railway.app/
```

#### 选项 B：分离部署到 Netlify/Vercel（推荐用于生产）

**前端单独部署的优势：**
- 更快的加载速度（CDN）
- 独立扩展
- 更好的静态文件缓存

**步骤：**

1. **更新前端 API 地址**

编辑所有前端 JavaScript 文件中的 API URL：

```javascript
// 在 frontend/js/*.js 中查找类似这样的代码：
const API_URL = 'http://localhost:5001/api';

// 替换为您的 Railway 后端 URL：
const API_URL = 'https://your-app.up.railway.app/api';
```

需要更新的文件：
- `frontend/js/main.js`
- `frontend/js/employee.js`
- `frontend/js/manager.js`
- `frontend/js/register.js`
- `frontend/js/worker-scan.js`

2. **部署到 Netlify**

```bash
# 方法 1：拖放
# 1. 访问 https://app.netlify.com/drop
# 2. 拖放 frontend/ 文件夹

# 方法 2：使用 Netlify CLI
npm install -g netlify-cli
cd frontend
netlify deploy --prod
```

3. **更新 CORS 设置**

在 Railway 后端的环境变量中更新：
```bash
CORS_ORIGINS=https://your-frontend.netlify.app
```

---

## ✅ 验证部署 (Verify Deployment)

### 1. 检查后端健康状态

访问您的 Railway URL：
```
https://your-app.up.railway.app/
```

应该看到前端主页或 JSON 响应。

### 2. 测试 API 端点

```bash
# 测试注册
curl -X POST https://your-app.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "display_name": "Test User",
    "email": "test@example.com",
    "password": "testpass123",
    "user_level": "Contractor"
  }'

# 测试登录
curl -X POST https://your-app.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ylin",
    "password": "password!"
  }'
```

### 3. 测试前端功能

1. 打开浏览器访问您的应用
2. 使用默认账户登录：
   - 用户名：`ylin`
   - 密码：`password!`
3. 测试核心功能：
   - 登录/注册
   - 生成 QR 码
   - 扫描打卡
   - 查看考勤记录

---

## 🔧 常见问题 (Troubleshooting)

### 问题 1：应用无法启动 - "Module not found"

**原因：** Root Directory 设置错误

**解决方案：**
1. 进入 Service Settings
2. 设置 Root Directory 为 `backend`
3. 重新部署

---

### 问题 2：数据库连接失败

**原因：** 环境变量配置错误

**解决方案：**
1. 检查 MySQL 服务是否正在运行
2. 验证环境变量是否正确引用：
   ```
   DB_HOST=${{MySQL.MYSQLHOST}}
   ```
3. 确保变量名大小写正确（Railway 区分大小写）
4. 重新部署服务

---

### 问题 3：CORS 错误

**错误信息：**
```
Access to fetch at 'https://...' from origin 'https://...' has been blocked by CORS policy
```

**解决方案：**

更新后端环境变量：
```bash
CORS_ORIGINS=https://your-frontend-domain.com
# 或允许所有来源（仅用于开发）
CORS_ORIGINS=*
```

---

### 问题 4：应用运行但显示 404

**原因：** 前端文件路径问题

**解决方案：**

检查 `backend/app/__init__.py` 中的静态文件配置：
```python
app = Flask(__name__, static_folder='../../frontend')
```

确保路径正确指向前端文件夹。

---

### 问题 5：数据库表不存在

**错误信息：**
```
Table 'attendance_system.users' doesn't exist
```

**解决方案：**

重新导入数据库架构：
```bash
railway connect MySQL
source backend/database/init_database.sql
```

或使用完整命令：
```bash
railway run mysql -h $MYSQLHOST -u $MYSQLUSER -p$MYSQLPASSWORD $MYSQLDATABASE < backend/database/init_database.sql
```

---

## 📊 监控和日志 (Monitoring & Logs)

### 查看应用日志

1. 进入 Railway 项目
2. 点击后端服务
3. 点击 **"Logs"** 标签
4. 实时查看应用输出和错误

### 查看数据库

1. 点击 MySQL 服务
2. 点击 **"Data"** 标签
3. 可以查看表和执行查询

### 监控资源使用

1. 在服务页面点击 **"Metrics"**
2. 查看：
   - CPU 使用率
   - 内存使用
   - 网络流量

---

## 💰 成本估算 (Cost Estimation)

Railway 免费套餐：
- **每月 $5 免费额度**
- **500 小时执行时间**

小型项目（<100 用户）通常在免费套餐内运行。

超出免费套餐后：
- **Hobby Plan**: $5/月（包含更多资源）
- **Pro Plan**: $20/月（用于生产环境）

---

## 🔄 持续部署 (Continuous Deployment)

Railway 支持自动部署：

1. **启用自动部署（默认开启）**
   - 每次推送到 GitHub main 分支
   - Railway 自动构建并部署

2. **触发手动部署**
   - 在 Deployments 页面
   - 点击 **"Deploy Now"**

3. **回滚到之前版本**
   - 在 Deployments 历史中
   - 点击任何之前的部署
   - 选择 **"Redeploy"**

---

## 🌐 自定义域名 (Custom Domain)

### 添加自定义域名

1. 在服务的 **"Settings"** → **"Domains"**
2. 点击 **"Custom Domain"**
3. 输入您的域名（如 `app.yourdomain.com`）
4. 在您的 DNS 提供商添加 CNAME 记录：
   ```
   CNAME app.yourdomain.com -> your-app.up.railway.app
   ```
5. 等待 DNS 传播（通常 5-30 分钟）

Railway 自动提供免费 SSL 证书。

---

## 🔐 生产环境安全建议 (Production Security)

### 1. 更改默认密码
```bash
# 登录 MySQL 并更新
railway connect MySQL

UPDATE users SET password = SHA2('your-new-secure-password', 256)
WHERE username = 'ylin';
```

### 2. 设置强密钥
```bash
# 在环境变量中设置
SECRET_KEY=<使用 64 位随机字符串>

# 生成随机密钥（本地运行）：
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. 禁用 DEBUG 模式
```bash
DEBUG=False
```

### 4. 限制 CORS
```bash
# 不要在生产环境使用 *
CORS_ORIGINS=https://your-frontend-domain.com
```

### 5. 使用环境变量
- ✅ 永远不要在代码中硬编码密码
- ✅ 使用 Railway 的环境变量功能
- ✅ 不要提交 `.env` 文件到 Git

---

## 📚 其他部署选项 (Alternative Platforms)

如果 Railway 不适合，可以考虑：

### 1. **Render.com**
- 类似 Railway
- 免费 PostgreSQL（如果愿意切换数据库）
- 免费套餐有限制

### 2. **Heroku**
- 老牌 PaaS 平台
- 需要添加 ClearDB/JawsDB 插件（MySQL）
- 免费套餐已取消，最低 $5/月

### 3. **DigitalOcean App Platform**
- $5/月起
- 更多控制权
- 需要单独的数据库服务

### 4. **AWS Elastic Beanstalk**
- 强大但复杂
- 需要配置 RDS（MySQL）
- 适合大型应用

---

## 📞 获取帮助 (Get Help)

- **Railway 文档**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **项目问题**: 在您的 GitHub 仓库创建 Issue

---

## ✨ 总结 (Summary)

完成以上步骤后，您的考勤管理系统将：

✅ 在云端运行（24/7 可访问）
✅ 拥有独立的 MySQL 数据库
✅ 自动部署（每次 Git 推送）
✅ 拥有 HTTPS 安全连接
✅ 可以通过公共 URL 访问

**默认登录凭据：**
- 用户名：`ylin`
- 密码：`password!`
- 角色：Manager

**记得在生产环境中更改默认密码！**

---

🎉 **祝部署顺利！Good luck with your deployment!**
