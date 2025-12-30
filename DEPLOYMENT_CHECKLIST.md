# 部署检查清单 | Deployment Checklist

快速参考清单，确保所有部署步骤完成。

---

## ✅ 部署前准备

- [ ] 创建 Railway.app 账户
- [ ] 代码已推送到 GitHub/GitLab
- [ ] 已安装 Railway CLI（可选，用于数据库初始化）

---

## ✅ Railway 项目设置

- [ ] 创建新项目并连接 GitHub 仓库
- [ ] 添加 MySQL 数据库服务
- [ ] 设置后端 Root Directory 为 `backend`

---

## ✅ 环境变量配置

在后端服务的 Variables 页面添加：

```bash
# 数据库（从 MySQL 服务复制）
- [ ] DB_HOST=${{MySQL.MYSQLHOST}}
- [ ] DB_PORT=${{MySQL.MYSQLPORT}}
- [ ] DB_USER=${{MySQL.MYSQLUSER}}
- [ ] DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
- [ ] DB_NAME=${{MySQL.MYSQLDATABASE}}

# Flask 配置（手动输入）
- [ ] SECRET_KEY=<生成随机密钥>
- [ ] DEBUG=False
- [ ] PORT=${{PORT}}
- [ ] HOST=0.0.0.0
- [ ] CORS_ORIGINS=* （或您的前端域名）
```

---

## ✅ 数据库初始化

选择一种方法完成：

**方法 1: Railway CLI**
```bash
- [ ] railway login
- [ ] railway link
- [ ] railway connect MySQL
- [ ] source backend/database/init_database.sql
```

**方法 2: MySQL 客户端**
```bash
- [ ] 复制 Railway MySQL 连接信息
- [ ] 运行: mysql -h <HOST> -P <PORT> -u <USER> -p<PASS> <DB> < backend/database/init_database.sql
```

**方法 3: 手动执行**
```bash
- [ ] 复制 init_database.sql 内容
- [ ] 在 Railway MySQL Data → Query 中执行
```

---

## ✅ 部署验证

- [ ] 部署成功（绿色状态）
- [ ] 生成公共域名
- [ ] 访问 URL 显示主页
- [ ] 测试登录（ylin / password!）
- [ ] 检查日志无错误

---

## ✅ 测试核心功能

- [ ] 用户登录
- [ ] 用户注册
- [ ] Manager 生成 QR 码
- [ ] Contractor 扫描打卡
- [ ] 查看考勤记录
- [ ] Manager 审批记录

---

## ✅ 生产环境安全

- [ ] 更改默认用户密码
- [ ] 设置强 SECRET_KEY
- [ ] 确认 DEBUG=False
- [ ] 配置正确的 CORS_ORIGINS
- [ ] 不提交 .env 文件到 Git

---

## ✅ 前端部署（如果分离部署）

- [ ] 更新所有 JS 文件中的 API_URL
- [ ] 部署到 Netlify/Vercel
- [ ] 更新后端 CORS_ORIGINS 为前端域名
- [ ] 测试前端与后端通信

---

## ✅ 可选优化

- [ ] 添加自定义域名
- [ ] 配置 SSL（Railway 自动）
- [ ] 设置监控告警
- [ ] 配置备份策略
- [ ] 优化数据库索引

---

## 📊 部署后监控

定期检查：
- [ ] Railway 日志无错误
- [ ] 数据库连接正常
- [ ] 应用响应时间正常
- [ ] 免费额度使用情况

---

## 🆘 遇到问题？

参考详细部署指南：`DEPLOYMENT_GUIDE.md`

常见问题排查：
1. 检查 Railway 日志
2. 验证环境变量
3. 确认数据库连接
4. 测试 API 端点
5. 检查 CORS 配置

---

**完成所有检查后，您的应用就可以投入使用了！** 🎉
