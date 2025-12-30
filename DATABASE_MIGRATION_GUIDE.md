# 数据库迁移指南 (Database Migration Guide)

## 从 practice_db 迁移到 attendance_system

如果您已经在使用旧的数据库名 `practice_db`，可以通过以下方法迁移到新的数据库名 `attendance_system`。

---

## 方法 1：重命名现有数据库（推荐，保留数据）

这个方法会保留您的所有现有数据。

```bash
# 1. 登录 MySQL
mysql -u root -p

# 2. 创建新数据库
CREATE DATABASE attendance_system;

# 3. 获取所有表名并复制
USE practice_db;
SHOW TABLES;

# 4. 将所有表重命名到新数据库
# 对每个表执行以下命令（替换 table_name）：
RENAME TABLE practice_db.users TO attendance_system.users;
RENAME TABLE practice_db.manager_assignments TO attendance_system.manager_assignments;
RENAME TABLE practice_db.time_entries TO attendance_system.time_entries;
RENAME TABLE practice_db.qr_requests TO attendance_system.qr_requests;

# 5. 验证数据已迁移
USE attendance_system;
SHOW TABLES;

# 6. 删除旧数据库（可选，建议先备份）
# DROP DATABASE practice_db;

# 7. 退出 MySQL
EXIT;
```

---

## 方法 2：使用 mysqldump 迁移（最安全）

这个方法会先备份，然后导入到新数据库。

```bash
# 1. 备份旧数据库
mysqldump -u root -p practice_db > practice_db_backup.sql

# 2. 登录 MySQL 创建新数据库
mysql -u root -p
CREATE DATABASE attendance_system;
EXIT;

# 3. 导入数据到新数据库
mysql -u root -p attendance_system < practice_db_backup.sql

# 4. 验证数据
mysql -u root -p
USE attendance_system;
SHOW TABLES;
SELECT COUNT(*) FROM users;
EXIT;

# 5. 删除旧数据库（确认数据正确后）
# mysql -u root -p -e "DROP DATABASE practice_db;"
```

---

## 方法 3：创建全新数据库（不保留数据）

如果您不需要保留现有数据，可以直接创建新数据库。

```bash
# 1. 登录 MySQL
mysql -u root -p

# 2. 删除旧数据库（会丢失所有数据！）
DROP DATABASE practice_db;

# 3. 创建新数据库
CREATE DATABASE attendance_system;

# 4. 退出 MySQL
EXIT;

# 5. 导入架构
mysql -u root -p attendance_system < backend/database/init_database.sql
```

---

## 更新配置文件

迁移数据库后，需要更新配置（已自动完成）：

### ✅ 已自动更新的文件：

1. **backend/app/config.py**
   - 默认数据库名已改为 `attendance_system`

2. **backend/database/init_database.sql**
   - 所有 `USE practice_db` 已改为 `USE attendance_system`

3. **README.md**
   - 所有文档已更新

4. **scripts/setup.sh**
   - 安装脚本默认数据库名已更新

### 🔧 需要手动检查的文件：

1. **backend/.env** (如果存在)
   ```bash
   # 修改这一行：
   DB_NAME=attendance_system
   ```

2. **任何自定义配置文件**
   - 检查是否有硬编码的 `practice_db`

---

## 验证迁移

运行以下命令验证迁移成功：

```bash
# 1. 检查数据库是否存在
mysql -u root -p -e "SHOW DATABASES LIKE 'attendance_system';"

# 2. 检查表是否存在
mysql -u root -p attendance_system -e "SHOW TABLES;"

# 3. 检查数据（如果从旧数据库迁移）
mysql -u root -p attendance_system -e "SELECT COUNT(*) FROM users;"
mysql -u root -p attendance_system -e "SELECT COUNT(*) FROM time_entries;"

# 4. 测试应用连接
cd backend
python run.py
# 检查启动信息中显示：Database: attendance_system
```

---

## 常见问题

### 问题 1：迁移后应用无法连接数据库

**解决方案：**
```bash
# 检查 .env 文件
cat backend/.env | grep DB_NAME

# 如果显示 practice_db，修改为：
echo "DB_NAME=attendance_system" >> backend/.env
```

### 问题 2：旧数据库还在占用空间

**解决方案：**
```bash
# 确认新数据库数据完整后，删除旧数据库
mysql -u root -p -e "DROP DATABASE practice_db;"
```

### 问题 3：表重命名失败

**解决方案：**
```bash
# 使用 mysqldump 方法（方法 2）
# 这是最可靠的方法
```

---

## 推荐步骤总结

对于生产环境或有重要数据的情况：

1. ✅ **备份**：使用 mysqldump 备份旧数据库
2. ✅ **创建**：创建新数据库 `attendance_system`
3. ✅ **导入**：导入备份到新数据库
4. ✅ **验证**：检查所有表和数据
5. ✅ **测试**：运行应用并测试功能
6. ✅ **清理**：确认无误后删除旧数据库

---

## 需要帮助？

如有问题，请检查：
- MySQL 错误日志
- 应用启动日志
- 数据库连接配置

**现在数据库名称已更改为 `attendance_system` - 更专业、更规范！** 🎉
