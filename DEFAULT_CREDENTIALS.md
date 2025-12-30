# 默认登录凭据 | Default Login Credentials

## ✅ 已验证的测试账户 (Verified Test Accounts)

您的数据库已经初始化了以下测试用户，可以直接使用：

---

### 👤 Manager 账户 (管理员)

```
用户名 (Username):    ylin
密码 (Password):      password!
显示名称 (Display):    Yuchen Lin
邮箱 (Email):         yuchen.lin@example.com
角色 (Role):          Manager
```

**权限 (Permissions):**
- ✅ 生成 QR 码供员工打卡
- ✅ 查看所有下属的考勤记录
- ✅ 审批/拒绝考勤记录
- ✅ 管理用户（分配员工）
- ✅ 修改个人账户设置

---

### 👤 Contractor 账户 (员工)

```
用户名 (Username):    xlu
密码 (Password):      password!
显示名称 (Display):    Xuanyu Lu
邮箱 (Email):         xuanyu.lu@example.com
角色 (Role):          Contractor
```

**权限 (Permissions):**
- ✅ 扫描 QR 码打卡（签到/签退）
- ✅ 查看个人考勤记录
- ✅ 修改个人账户设置
- ❌ 不能查看其他员工信息
- ❌ 不能审批考勤

---

### 👤 额外测试账户 (Bonus Test Account)

```
用户名 (Username):    jsmith
密码 (Password):      password!
显示名称 (Display):    John Smith
邮箱 (Email):         john.smith@example.com
角色 (Role):          Contractor
```

---

## 🔐 密码技术细节 (Password Technical Details)

所有默认用户的密码都是 `password!` (注意末尾的感叹号)

**密码存储方式:**
- 明文密码: `password!`
- 哈希算法: SHA256
- 存储的哈希值: `f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7`

---

## 📊 用户关系 (User Relationships)

Manager `ylin` 管理以下员工:
- ✓ `xlu` (Xuanyu Lu)
- ✓ `jsmith` (John Smith)

这意味着:
- ylin 可以为 xlu 和 jsmith 生成 QR 码
- ylin 可以查看和审批 xlu 和 jsmith 的考勤记录
- xlu 和 jsmith 只能看到自己的记录

---

## 🧪 测试登录 (Test Login)

### 本地测试 (Local Testing)

```bash
cd backend
python3 test_login.py
```

应该显示:
```
✓ ylin       | Password: password!       | Role: Manager    | ✓ WORKING
✓ xlu        | Password: password!       | Role: Contractor | ✓ WORKING
```

### API 测试 (API Testing)

```bash
# 测试 Manager 登录
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ylin","password":"password!"}'

# 测试 Contractor 登录
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"xlu","password":"password!"}'
```

### 浏览器测试 (Browser Testing)

1. 启动服务器: `cd backend && python3 run.py`
2. 访问: `http://localhost:5001`
3. 使用上述任一账户登录
4. 应该能成功进入对应的仪表板

---

## ⚠️ 生产环境安全警告 (Production Security Warning)

**重要提醒:** 这些是测试账户，请在部署到生产环境后立即更改密码！

### 部署到生产后必须做的事:

#### 1. 更改所有默认密码

```bash
# 连接到生产数据库
railway connect MySQL  # 或其他方式连接

# 更新 ylin 的密码（示例：改为 "NewSecurePass123!"）
UPDATE users
SET password = SHA2('NewSecurePass123!', 256)
WHERE username = 'ylin';

# 更新 xlu 的密码
UPDATE users
SET password = SHA2('AnotherSecurePass456!', 256)
WHERE username = 'xlu';

# 更新 jsmith 的密码
UPDATE users
SET password = SHA2('ThirdSecurePass789!', 256)
WHERE username = 'jsmith';
```

#### 2. 或者删除测试账户，创建真实账户

```bash
# 删除所有测试账户
DELETE FROM users WHERE username IN ('ylin', 'xlu', 'jsmith');

# 通过注册页面创建真实的管理员和员工账户
```

#### 3. 设置强密码策略

建议密码要求:
- ✓ 至少 12 个字符
- ✓ 包含大小写字母
- ✓ 包含数字和特殊字符
- ✓ 不使用常见密码
- ✓ 定期更换

---

## 📝 初始数据库状态 (Initial Database State)

### 用户表 (users)
- 3 个用户: ylin, xlu, jsmith
- 所有密码: `password!` (SHA256 哈希)

### 管理关系表 (manager_assignments)
- ylin → xlu
- ylin → jsmith

### 考勤记录表 (time_entries)
- xlu 有 1 条已批准的记录 (2025-12-15)
- jsmith 有 1 条待审批的记录 (2025-12-15)

### QR 请求表 (qr_requests)
- 空表（等待生成 QR 码）

---

## ✅ 验证清单 (Verification Checklist)

在部署前，请确认:

- [x] 数据库包含 ylin 用户（Manager）
- [x] 数据库包含 xlu 用户（Contractor）
- [x] 两个用户的密码都是 `password!`
- [x] 密码已正确哈希（SHA256）
- [x] 用户可以成功登录
- [x] Manager 可以访问管理功能
- [x] Contractor 只能访问员工功能

---

## 🔗 相关文档 (Related Documentation)

- 完整部署指南: `DEPLOYMENT_GUIDE.md`
- 部署检查清单: `DEPLOYMENT_CHECKLIST.md`
- 数据库迁移指南: `DATABASE_MIGRATION_GUIDE.md`
- 项目说明文档: `README.md`

---

**最后更新时间**: 2025-12-29

**状态**: ✅ 已验证并可以使用
