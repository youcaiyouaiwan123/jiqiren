# AI 智能客服系统 — API 接口设计

> 基于飞书多维表格集成方案，所有接口统一前缀 `/api`

---

## 通用约定

### 基础 URL

```
http://localhost:8015/api
```

### 统一响应格式

```json
{
  "code": 0,
  "message": "ok",
  "data": {},
  "request_id": "uuid-v4"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | number | `0` 成功，非 `0` 失败 |
| `message` | string | 提示信息 |
| `data` | object/array/null | 业务数据 |
| `request_id` | string | 请求追踪 ID |

### 通用错误码

| code | 说明 | 触发场景 |
|------|------|----------|
| 0 | 成功 | — |
| 1001 | 参数校验失败 | 字段格式/范围/类型不合法 |
| 1002 | 未登录 / Token 无效 | JWT 过期、被注销、格式错误 |
| 1003 | 权限不足 | 普通用户访问管理端接口；normal 管理员访问 super 专属操作 |
| 1004 | 资源不存在 | 查询的 ID 不存在或已删除 |
| 1005 | 重复操作 | 手机号/邮箱已注册；兑换码已被使用 |
| 1006 | 注册功能已关闭 | register_config.register_enabled = false |
| 1007 | 注册方式不支持 | 提交的注册方式不在 register_methods 允许范围内 |
| 1008 | 邀请码无效 | invite_code_required=true 但提交的邀请码无效 |
| 2001 | 免费次数已用完 | free 用户 free_chats_left <= 0 |
| 2002 | 订阅已过期 | 订阅用户 subscribe_expire < now |
| 2003 | 账号已被封禁 | users.status = banned |
| 3001 | 禁用词命中（拒绝） | 消息命中 action=reject 的禁用词 |
| 3002 | 禁用词命中（警告） | 消息命中 action=warn 的禁用词（仅标记，不阻断） |
| 4001 | 删除被引用资源 | 删除正在使用的默认模型/已关联用户的套餐等 |
| 5001 | AI 服务异常 | 大模型 API 超时/返回错误 |
| 5002 | 飞书 API 异常 | 飞书接口调用失败（不阻断主流程，异步重试） |
| 5003 | 数据库异常 | MySQL 连接失败/写入失败 |

### 认证方式

请求头携带 JWT：

```
Authorization: Bearer <access_token>
```

### 分页参数（通用）

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `page` | int | 否 | 1 | 页码 |
| `page_size` | int | 否 | 20 | 每页条数，最大 100 |

分页响应结构：

```json
{
  "list": [],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

---

## 跨模块业务逻辑关系图

```
注册设置(register_config)
  │
  ├──▶ 用户注册：决定注册开关、注册方式、是否需邀请码、默认免费次数
  │       │
  │       └──▶ 用户表(users)：写入 free_chats_left = register_config.default_free_chats
  │
大模型配置(llm_providers) ──┐
AI 配置(ai_config) ─────────┤
FAQ 知识库(飞书) ───────────┤
文档索引(飞书) ─────────────┤
禁用词(banned_words) ───────┤
  │                         │
  └──────── 全部汇入 ───────▶ AI 对话(chat/send)
                                │
                                ├──▶ 配额检查：free 用户查 free_chats_left > 0
                                │              订阅用户查 subscribe_expire > now
                                │              封禁用户直接拒绝(code:2003)
                                │
                                ├──▶ 禁用词过滤：命中 action=reject → 返回 code:3001
                                │                命中 action=replace → 替换后继续
                                │                命中 action=warn → 正常处理+标记
                                │
                                ├──▶ 扣减配额（Redis 原子 DECR，异步同步 MySQL）
                                │
                                ├──▶ 调用 llm_providers.is_default=1 的模型
                                │    参数来自 ai_config（system_prompt/temperature/max_tokens）
                                │    FAQ/文档开关由 ai_config.faq_enabled/doc_recommend 控制
                                │
                                ├──▶ 同步写 MySQL：messages + token_usage
                                │    token_usage.cost_usd = f(模型定价, input_tokens, output_tokens)
                                │
                                └──▶ 异步写飞书：根据 feishu_routes 路由规则匹配目标表
                                     更新 messages.feishu_synced = 1

兑换码(redeem_codes)
  │
  ├── type=days  ──▶ 用户兑换后：users.subscribe_plan 升级
  │                  users.subscribe_expire = max(now, 原到期时间) + value 天
  │                  payments 表写入 type=redeem 记录
  │
  └── type=chats ──▶ 用户兑换后：users.free_chats_left += value
                     payments 表写入 type=redeem 记录

管理员修改订阅(PUT /users/{id}/subscribe)
  └──▶ payments 表写入 type=subscribe 记录（操作留痕）

到期提醒(expire_reminder_config)
  └──▶ 定时任务扫描 users 表：subscribe_expire - now <= days_before
       按 channel 推送：site=站内消息 / sms=短信 / email=邮件
       模板变量 {nickname}→users.nickname, {expire_date}→users.subscribe_expire

企微通知(wecom_config)
  └──▶ notify_types 对应系统事件：
       payment  → 用户付费/兑换成功时推送
       expire   → 用户订阅到期时推送
       alert    → AI 服务异常/飞书同步失败时推送
       daily_report → 每日定时汇总推送（用户数/对话数/Token消耗）

公告(announcements)
  └──▶ 用户端展示规则：status=published AND (publish_at<=now OR publish_at IS NULL)
       AND (expire_at>now OR expire_at IS NULL)
       排序：is_pinned DESC, publish_at DESC
```

---

## 一、用户认证模块

### 1.1 获取注册配置 `GET /api/auth/register-config`

> 无需认证，注册页加载时调用

> **数据来源**：`register_config` 表，Redis 缓存 key `register_config:cache`（10min TTL）

**响应 data：**

```json
{
  "register_enabled": true,
  "register_methods": ["phone", "email"],
  "invite_code_required": false,
  "default_free_chats": 3,
  "terms_url": "https://example.com/terms",
  "privacy_url": "https://example.com/privacy"
}
```

> **前端联动**：`register_enabled=false` 时隐藏注册入口；`register_methods` 决定表单显示手机/邮箱输入框；`invite_code_required=true` 时必须展示邀请码输入框。

---

### 1.2 用户注册 `POST /api/auth/register`

> **前置校验链**：register_config.register_enabled → register_methods → invite_code_required → 唯一性校验 → 写入 users 表

**请求体：**

```json
{
  "phone": "13800001111",
  "email": "test@example.com",
  "password": "Abc123456",
  "nickname": "测试用户A",
  "invite_code": "INV2026"
}
```

| 字段 | 类型 | 必填 | 校验规则 | 说明 |
|------|------|------|----------|------|
| `phone` | string | 条件 | 正则 `^1[3-9]\d{9}$`；register_methods 含 phone 时可传 | 手机号，与 email 至少传一个 |
| `email` | string | 条件 | 合法邮箱格式；register_methods 含 email 时可传 | 邮箱，与 phone 至少传一个 |
| `password` | string | 是 | 6-20 位，至少含字母+数字 | 明文密码，后端 bcrypt 哈希存储 |
| `nickname` | string | 否 | 最长 50 字符，不传则生成"用户"+随机4位 | 昵称 |
| `invite_code` | string | 条件 | 当 register_config.invite_code_required=true 时必填 | 邀请码 |

**后端处理流程：**

1. 检查 `register_config.register_enabled`，关闭则返回 `code:1006 注册功能已关闭`
2. 校验提交的注册方式是否在 `register_config.register_methods` 允许范围内
3. 若 `invite_code_required=true`，校验邀请码有效性
4. 校验 phone/email 唯一性（users 表 UNIQUE 约束）
5. 写入 users 表，`free_chats_left` = `register_config.default_free_chats`
6. 同步写 Redis `user:free_chats:{user_id}` = default_free_chats

**成功响应 data：**

```json
{
  "user_id": 1,
  "nickname": "测试用户A",
  "free_chats_left": 3
}
```

| 响应字段 | 来源 | 说明 |
|----------|------|------|
| `user_id` | users.id | 新建用户主键 |
| `nickname` | users.nickname | 昵称 |
| `free_chats_left` | register_config.default_free_chats → users.free_chats_left | 初始免费次数 |

**失败示例：**

```json
{ "code": 1005, "message": "该手机号已注册", "data": null }
{ "code": 1006, "message": "注册功能已关闭", "data": null }
{ "code": 1007, "message": "该注册方式暂不支持", "data": null }
{ "code": 1008, "message": "邀请码无效", "data": null }
```

---

### 1.3 用户登录 `POST /api/auth/login`

> **处理流程**：account 自动判断是手机号还是邮箱 → 查 users 表 → bcrypt 校验 → 检查 status → 生成 JWT → 写 Redis 会话

**请求体：**

```json
{
  "account": "13800001111",
  "password": "Abc123456"
}
```

| 字段 | 类型 | 必填 | 校验规则 | 说明 |
|------|------|------|----------|------|
| `account` | string | 是 | 自动识别：含 `@` 则按邮箱查，否则按手机号查 | 手机号或邮箱 |
| `password` | string | 是 | 与 users.password_hash bcrypt 比对 | 密码 |

**后端处理流程：**

1. 根据 account 格式查 users 表（phone 或 email）
2. 未找到 → `code:1004 账号不存在`
3. bcrypt 比对密码，失败 → `code:1001 密码错误`
4. 检查 `users.status`，`banned` → `code:2003 账号已被封禁`
5. 生成 JWT：access_token（2h）、refresh_token（7d），payload 含 `{user_id, role:"user"}`
6. 写 Redis `user:session:{user_id}` = access_token（TTL=2h），支持主动注销
7. phone/email 脱敏后返回（中间4位替换为 `****`）

**成功响应 data：**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 7200,
  "user": {
    "id": 1,
    "nickname": "测试用户A",
    "phone": "138****1111",
    "email": "te**@example.com",
    "avatar_url": null,
    "free_chats_left": 3,
    "subscribe_plan": "free",
    "subscribe_expire": null,
    "status": "active"
  }
}
```

| 响应字段 | 来源 | 说明 |
|----------|------|------|
| `access_token` | JWT 生成 | 有效期 2h，存 Redis |
| `refresh_token` | JWT 生成 | 有效期 7d |
| `expires_in` | 配置 JWT_ACCESS_EXPIRE_MINUTES×60 | 秒数 |
| `user.free_chats_left` | Redis `user:free_chats:{id}` 优先，降级查 MySQL | 剩余免费次数 |
| `user.subscribe_plan` | users.subscribe_plan | 当前订阅计划 |
| `user.subscribe_expire` | users.subscribe_expire | 到期时间，null 表示未订阅 |

---

### 1.4 刷新 Token `POST /api/auth/refresh`

**请求体：**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**成功响应 data：**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 7200
}
```

---

### 1.5 获取用户信息 `GET /api/user/profile`

> 需认证

**响应 data：**

```json
{
  "id": 1,
  "nickname": "测试用户A",
  "phone": "138****1111",
  "email": "te**@example.com",
  "avatar_url": null,
  "free_chats_left": 2,
  "subscribe_plan": "free",
  "subscribe_expire": null,
  "status": "active",
  "created_at": "2026-04-01 10:00:00"
}
```

---

## 二、AI 对话模块

### 2.1 获取会话列表 `GET /api/chat/conversations`

> 需认证

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | int | 否 | 页码 |
| `page_size` | int | 否 | 每页条数 |

**响应 data：**

```json
{
  "list": [
    {
      "id": 1001,
      "title": "账号登录问题",
      "message_count": 6,
      "last_message_at": "2026-04-09 14:30:00",
      "created_at": "2026-04-09 14:00:00"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

---

### 2.2 新建会话 `POST /api/chat/conversations`

> 需认证

**请求体：**

```json
{
  "title": "新对话"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 否 | 标题，不传则由首条消息自动生成 |

**响应 data：**

```json
{
  "id": 1002,
  "title": "新对话",
  "created_at": "2026-04-09 15:00:00"
}
```

---

### 2.3 获取历史消息 `GET /api/chat/conversations/{id}/messages`

> 需认证

**Path 参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | int | 会话 ID |

**Query 参数：**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `page` | int | 否 | 1 | 页码 |
| `page_size` | int | 否 | 50 | 每页条数 |

**响应 data：**

```json
{
  "conversation_id": 1001,
  "list": [
    {
      "id": 5001,
      "role": "user",
      "content": "账号登录不了怎么办？",
      "images": [],
      "docs": [],
      "created_at": "2026-04-09 14:00:00"
    },
    {
      "id": 5002,
      "role": "assistant",
      "content": "请先确认您输入的账号是否正确...",
      "images": [
        { "url": "/api/image/file_xxx", "name": "登录问题方案截图.png" }
      ],
      "docs": [
        { "title": "账号登录操作指南", "link": "https://xxx.feishu.cn/wiki/...", "tip": "建议查看第2节" }
      ],
      "created_at": "2026-04-09 14:00:05"
    }
  ],
  "total": 6,
  "page": 1,
  "page_size": 50
}
```

---

### 2.4 发送消息 `POST /api/chat/send`（SSE 流式）

> 需认证，响应为 `text/event-stream`
>
> **核心接口，串联 6 个子系统**：配额系统 → 禁用词系统 → 大模型系统 → FAQ/文档系统 → 数据存储 → 飞书同步

**请求体：**

```json
{
  "conversation_id": 1001,
  "message": "账号登录不了怎么办？",
  "images": [
    { "file_token": "img_xxx" }
  ]
}
```

| 字段 | 类型 | 必填 | 校验规则 | 说明 |
|------|------|------|----------|------|
| `conversation_id` | int | 否 | 必须属于当前用户（防越权） | 不传则自动创建新会话 |
| `message` | string | 是 | 不为空，最长 5000 字符 | 用户消息内容 |
| `images` | array | 否 | 每项含 file_token 字符串，最多 5 张 | 用户上传图片的 file_token 列表 |

**后端完整处理流程（10 步）：**

```
1. JWT 鉴权 → 获取 user_id
2. 用户状态检查 → users.status = banned → code:2003
3. 配额检查（Redis 原子操作）：
   ├── subscribe_plan != free AND subscribe_expire > now → 订阅用户放行
   ├── free_chats_left > 0 → Redis DECR user:free_chats:{user_id}
   └── 均不满足 → code:2001 或 code:2002
4. 禁用词过滤（Redis 缓存 banned_words:cache）：
   ├── 遍历 is_active=1 的禁用词
   ├── match_type=exact: 完全匹配
   ├── match_type=contains: 包含匹配
   ├── match_type=regex: 正则匹配
   └── 命中后按 action 处理（reject→code:3001 / replace→替换 / warn→标记）
5. 若 conversation_id 为空 → 新建 conversations 记录
6. 写入用户消息到 messages 表（role=user）
7. 构建 AI 请求上下文：
   ├── system_prompt ← ai_config.system_prompt
   ├── temperature ← ai_config.temperature（默认 0.7）
   ├── max_tokens ← ai_config.max_tokens（默认 2048）
   ├── FAQ 上下文 ← 飞书 FAQ 表（ai_config.faq_enabled=true 时加载，Redis 缓存 faq:cache）
   ├── 文档候选 ← 飞书文档索引表（ai_config.doc_recommend=true 时加载，Redis 缓存 docs:cache）
   └── 模型选择 ← llm_providers 表 is_default=1 且 is_active=1 的记录
8. 调用大模型 API（streaming），SSE 逐 chunk 推送前端
9. 流结束后写入：
   ├── messages 表：role=assistant 的完整回复 + images/docs JSON
   ├── token_usage 表：model, input_tokens, output_tokens, cost_usd
   ├── 更新 conversations.updated_at
   └── 异步扣减同步 MySQL：users.free_chats_left（与 Redis 对齐）
10. 异步写飞书（Redis 队列 feishu:sync:queue）：
    ├── 根据 feishu_routes.route_rule 匹配目标表
    ├── 写入成功 → messages.feishu_synced = 1
    └── 失败重试 3 次（1s → 5s → 30s），仍失败则通知企微 alert
```

**SSE 事件流：**

**event: chunk**（流式文本片段，可能收到多次）

```
event: chunk
data: {"text":"请先确认"}
```

**event: done**（完成，仅一次，包含完整结构化数据）

```
event: done
data: {
  "conversation_id": 1001,
  "user_message_id": 5001,
  "assistant_message_id": 5002,
  "text": "请先确认您输入的账号是否正确，如忘记密码可点击找回密码。",
  "images": [
    { "url": "/api/image/file_xxx", "name": "登录问题方案截图.png" }
  ],
  "docs": [
    { "title": "账号登录操作指南", "link": "https://xxx.feishu.cn/wiki/...", "tip": "建议重点查看第2节" }
  ],
  "usage": {
    "model": "claude-sonnet-4-20250514",
    "input_tokens": 1200,
    "output_tokens": 380,
    "cost_usd": 0.0123
  },
  "quota": {
    "free_chats_left": 2,
    "subscribe_plan": "free",
    "subscribe_expire": null
  }
}
```

| done 响应字段 | 来源 | 说明 |
|---------------|------|------|
| `conversation_id` | conversations.id | 会话 ID（新建则为新 ID） |
| `user_message_id` | messages.id (role=user) | 用户消息记录 ID |
| `assistant_message_id` | messages.id (role=assistant) | AI 回复记录 ID |
| `images` | FAQ 知识库 → 方案截图字段 → 图片代理 URL | 匹配到的 FAQ 方案截图 |
| `docs` | 文档索引表 → title/link/tip | AI 推荐的文档链接 |
| `usage.model` | llm_providers.model (is_default=1) | 实际使用的模型 |
| `usage.cost_usd` | 按模型定价计算 | input×单价 + output×单价 |
| `quota.*` | Redis 实时查询 | 用户当前配额状态，前端据此展示提示 |

**event: error**（异常，AI 失败时不扣费）

```
event: error
data: {"code":5001,"message":"AI 暂时繁忙，请稍后重试"}
```

> **降级策略**：AI 超时/失败 → 回滚 Redis 配额（INCR 恢复），不写 token_usage，返回友好提示。

---

### 2.5 图片代理 `GET /api/image/{file_token}`

> 需认证，返回二进制图片流
>
> **依赖链**：file_token → feishu_routes.app_id/app_secret → Redis `feishu:token:{app_id}` → 飞书下载 API

**Path 参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `file_token` | string | 飞书附件 file_token，来源于 FAQ 知识库的方案截图字段 |

**后端处理流程：**

1. 从 Redis `feishu:token:{app_id}` 获取 `tenant_access_token`（115min TTL，提前 5 分钟刷新）
2. 若缓存 miss → 用 feishu_routes.app_id + app_secret 调用飞书 API 获取新 token
3. 携带 token 请求飞书文件下载 API → pipe 二进制流返回前端
4. 设置响应头 `Cache-Control: private, max-age=3600`（浏览器缓存 1 小时减少重复请求）

**响应：**

- Content-Type: `image/png` 或 `image/jpeg`（从飞书响应头获取）
- Body: 图片二进制流
- 失败时返回 404（token 无效或文件不存在）

---

## 三、用户端其他接口

### 3.1 获取生效公告 `GET /api/announcements`

> 无需认证
>
> **数据来源**：Redis 缓存 `announcements:active`（5min TTL），miss 时查 MySQL
>
> **查询条件**：`status='published' AND (publish_at <= NOW() OR publish_at IS NULL) AND (expire_at > NOW() OR expire_at IS NULL)`
>
> **排序规则**：`is_pinned DESC, publish_at DESC`

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "title": "系统升级通知",
      "content": "系统将于今晚 22:00-23:00 进行维护升级...",
      "type": "maintenance",
      "is_pinned": true,
      "publish_at": "2026-04-09 10:00:00"
    }
  ]
}
```

> **前端展示**：置顶公告用醒目标识，`type=maintenance` 显示橙色警告，`type=update` 显示蓝色信息。

---

### 3.2 获取套餐列表 `GET /api/plans`

> 无需认证

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "name": "月度会员",
      "type": "monthly",
      "price": 29.90,
      "duration_days": 30,
      "chat_limit": -1,
      "description": "每月不限次数对话",
      "sort_order": 1
    },
    {
      "id": 2,
      "name": "年度会员",
      "type": "yearly",
      "price": 199.00,
      "duration_days": 365,
      "chat_limit": -1,
      "description": "全年不限次数对话，最划算",
      "sort_order": 2
    }
  ]
}
```

---

### 3.3 兑换码兑换 `POST /api/subscribe/redeem`

> 需认证
>
> **涉及表**：redeem_codes → users → payments（一次兑换触发 3 表联动写入）

**请求体：**

```json
{
  "code": "ABCD-1234-EFGH"
}
```

| 字段 | 类型 | 必填 | 校验规则 | 说明 |
|------|------|------|----------|------|
| `code` | string | 是 | 格式 `XXXX-XXXX-XXXX`，查 redeem_codes 表 | 兑换码 |

**后端处理流程：**

```
1. 查 redeem_codes 表：WHERE code=? AND status='unused' AND (expire_at IS NULL OR expire_at > now)
2. 未找到 → code:1004 兑换码无效或已过期
3. 根据兑换码 type 更新 users 表：
   ├── type=days：
   │   ├── users.subscribe_plan → 'monthly'（或保持原有更高级别）
   │   └── users.subscribe_expire = MAX(now, 原到期时间) + value 天
   └── type=chats：
       └── users.free_chats_left += value（同步更新 Redis）
4. 更新 redeem_codes：status='used', used_by=user_id, used_at=now
5. 写入 payments 表：type='redeem', redeem_code=code, status='success'
6. 若企微配置 notify_types 含 'payment' → 异步推送通知
```

**成功响应 data：**

```json
{
  "type": "days",
  "value": 30,
  "message": "兑换成功，已增加 30 天会员时长",
  "subscribe_plan": "monthly",
  "subscribe_expire": "2026-05-09 21:00:00",
  "free_chats_left": 2
}
```

| 响应字段 | 来源 | 说明 |
|----------|------|------|
| `type` | redeem_codes.type | 兑换类型 |
| `value` | redeem_codes.value | 增加的天数或次数 |
| `subscribe_plan` | users.subscribe_plan（更新后） | 当前订阅计划 |
| `subscribe_expire` | users.subscribe_expire（更新后） | 新的到期时间 |
| `free_chats_left` | users.free_chats_left（更新后） | 剩余免费次数 |

**失败示例：**

```json
{ "code": 1004, "message": "兑换码无效或已过期", "data": null }
{ "code": 1005, "message": "该兑换码已被使用", "data": null }
```

---

## 四、管理端 — 认证

### 4.1 管理员登录 `POST /api/admin/login`

**请求体：**

```json
{
  "username": "admin",
  "password": "Admin123456"
}
```

**成功响应 data：**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 7200,
  "admin": {
    "id": 1,
    "username": "admin",
    "role": "super"
  }
}
```

---

## 五、管理端 — 数据分析

### 5.1 总览数据 `GET /api/admin/analytics/overview`

**响应 data：**

```json
{
  "user_total": 1200,
  "user_today": 18,
  "active_users_today": 186,
  "conversation_total": 5321,
  "conversation_today": 230,
  "message_total": 18220,
  "token_input_total": 1280000,
  "token_output_total": 460000,
  "cost_usd_total": 56.78
}
```

---

### 5.2 趋势数据 `GET /api/admin/analytics/trends`

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `period` | string | 否 | `day`(默认) / `week` / `month` |
| `start_date` | string | 否 | 起始日期 YYYY-MM-DD |
| `end_date` | string | 否 | 结束日期 YYYY-MM-DD |

**响应 data：**

```json
{
  "period": "day",
  "items": [
    {
      "date": "2026-04-01",
      "new_users": 12,
      "active_users": 180,
      "conversations": 210,
      "messages": 620,
      "input_tokens": 45000,
      "output_tokens": 18000
    }
  ]
}
```

---

### 5.3 热门问题 TOP N `GET /api/admin/analytics/hot-questions`

**Query 参数：**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `top_n` | int | 否 | 10 | 返回前 N 条 |
| `days` | int | 否 | 7 | 最近 N 天 |

**响应 data：**

```json
{
  "list": [
    { "rank": 1, "question": "登录不了怎么办", "count": 86, "category": "账号问题" },
    { "rank": 2, "question": "如何修改密码", "count": 52, "category": "账号问题" }
  ]
}
```

---

### 5.4 分类分布 `GET /api/admin/analytics/categories`

**响应 data：**

```json
{
  "list": [
    { "category": "账号问题", "count": 320, "percentage": 38.5 },
    { "category": "课程问题", "count": 210, "percentage": 25.3 },
    { "category": "支付问题", "count": 150, "percentage": 18.1 },
    { "category": "其他", "count": 150, "percentage": 18.1 }
  ]
}
```

---

## 六、管理端 — Token 计费

### 6.1 Token 用量统计 `GET /api/admin/token-usage`

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `period` | string | 否 | `day` / `week` / `month` |
| `start_date` | string | 否 | YYYY-MM-DD |
| `end_date` | string | 否 | YYYY-MM-DD |
| `model` | string | 否 | 按模型筛选 |

**响应 data：**

```json
{
  "summary": {
    "total_input_tokens": 1280000,
    "total_output_tokens": 460000,
    "total_cost_usd": 56.78,
    "total_requests": 3200
  },
  "by_model": [
    {
      "model": "claude-sonnet-4-20250514",
      "input_tokens": 1000000,
      "output_tokens": 380000,
      "cost_usd": 48.50,
      "requests": 2800
    }
  ],
  "trend": [
    {
      "date": "2026-04-01",
      "input_tokens": 45000,
      "output_tokens": 18000,
      "cost_usd": 2.10,
      "requests": 120
    }
  ]
}
```

---

### 6.2 Token 用量明细 `GET /api/admin/token-usage/detail`

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | int | 否 | 页码 |
| `page_size` | int | 否 | 每页条数 |
| `user_id` | int | 否 | 按用户筛选 |
| `model` | string | 否 | 按模型筛选 |
| `start_date` | string | 否 | YYYY-MM-DD |
| `end_date` | string | 否 | YYYY-MM-DD |

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "user_id": 1,
      "nickname": "测试用户A",
      "message_id": 5002,
      "model": "claude-sonnet-4-20250514",
      "input_tokens": 1200,
      "output_tokens": 380,
      "cost_usd": 0.0123,
      "created_at": "2026-04-09 14:00:05"
    }
  ],
  "total": 3200,
  "page": 1,
  "page_size": 20
}
```

---

## 七、管理端 — 用户与订阅管理

### 7.1 用户列表 `GET /api/admin/users`

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | int | 否 | 页码 |
| `page_size` | int | 否 | 每页条数 |
| `keyword` | string | 否 | 搜索昵称/手机/邮箱 |
| `status` | string | 否 | `active` / `banned` |
| `subscribe_plan` | string | 否 | `free` / `monthly` / `yearly` |

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "nickname": "测试用户A",
      "phone": "13800001111",
      "email": "test@example.com",
      "free_chats_left": 2,
      "subscribe_plan": "free",
      "subscribe_expire": null,
      "status": "active",
      "conversation_count": 15,
      "message_count": 86,
      "created_at": "2026-04-01 10:00:00"
    }
  ],
  "total": 1200,
  "page": 1,
  "page_size": 20
}
```

---

### 7.2 修改用户订阅 `PUT /api/admin/users/{id}/subscribe`

> **涉及表**：users + payments（操作留痕）+ Redis 同步
>
> 需管理员认证，`role=super` 或 `role=normal` 均可操作

**请求体：**

```json
{
  "subscribe_plan": "monthly",
  "subscribe_expire": "2026-05-09 23:59:59",
  "free_chats_left": 10,
  "remark": "客服手动开通月度会员"
}
```

| 字段 | 类型 | 必填 | 校验规则 | 说明 |
|------|------|------|----------|------|
| `subscribe_plan` | string | 否 | 枚举 `free`/`monthly`/`yearly` | 订阅计划 |
| `subscribe_expire` | string | 否 | 格式 `YYYY-MM-DD HH:mm:ss`，不能早于当前时间 | 到期时间 |
| `free_chats_left` | int | 否 | ≥ 0 | 剩余免费次数 |
| `remark` | string | 否 | 最长 200 字符 | 操作备注（写入 payments 记录） |

**后端处理流程：**

1. 更新 users 表对应字段
2. 若修改了 `free_chats_left` → 同步更新 Redis `user:free_chats:{user_id}`
3. 写入 payments 表：`type='subscribe'`，`status='success'`，`plan=subscribe_plan`（管理员操作留痕）
4. 若企微配置 notify_types 含 `payment` → 异步推送

**响应 data：**

```json
{
  "id": 1,
  "subscribe_plan": "monthly",
  "subscribe_expire": "2026-05-09 23:59:59",
  "free_chats_left": 10
}
```

---

### 7.3 封禁/解封用户 `PUT /api/admin/users/{id}/status`

> **副作用**：封禁时立即失效该用户登录态；解封后用户需重新登录

**请求体：**

```json
{
  "status": "banned",
  "reason": "违规发言"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status` | string | 是 | `active` / `banned` |
| `reason` | string | 否 | 封禁原因（仅封禁时有效，管理端留痕） |

**后端处理流程：**

1. 更新 users.status
2. 若 `status=banned` → 删除 Redis `user:session:{user_id}`（立即踢出登录态）
3. 若企微配置 notify_types 含 `alert` → 推送封禁/解封通知

**响应 data：**

```json
{
  "id": 1,
  "status": "banned"
}
```

---

## 八、管理端 — 大模型 API 设置

### 8.1 大模型配置列表 `GET /api/admin/llm-providers`

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "name": "Claude",
      "provider": "claude",
      "api_url": "https://api.anthropic.com/v1/messages",
      "api_key_masked": "sk-ant-***...***abc",
      "model": "claude-sonnet-4-20250514",
      "is_default": true,
      "is_active": true,
      "extra_config": {
        "temperature": 0.7,
        "max_tokens": 2048
      },
      "updated_at": "2026-04-09 10:00:00"
    }
  ]
}
```

---

### 8.2 新增大模型 `POST /api/admin/llm-providers`

**请求体：**

```json
{
  "name": "GPT-4o",
  "provider": "openai",
  "api_url": "https://api.openai.com/v1/chat/completions",
  "api_key": "sk-xxx",
  "model": "gpt-4o",
  "is_active": true,
  "extra_config": {
    "temperature": 0.7,
    "max_tokens": 2048
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 显示名称 |
| `provider` | string | 是 | 标识：`claude` / `openai` / `zhipu` |
| `api_url` | string | 是 | API 端点 |
| `api_key` | string | 是 | API Key |
| `model` | string | 是 | 模型名称 |
| `is_active` | bool | 否 | 是否启用 |
| `extra_config` | object | 否 | 扩展参数 |

**响应 data：** 返回创建后的完整对象（同 8.1 列表项）

---

### 8.3 修改大模型配置 `PUT /api/admin/llm-providers/{id}`

请求体同 8.2，所有字段非必填（仅更新传入字段）。

---

### 8.4 设为默认模型 `PUT /api/admin/llm-providers/{id}/default`

> 无请求体
>
> **副作用**：将其他所有 provider 的 `is_default` 置为 0（同一时刻只有一个默认模型）；清除 Redis `llm_provider:default` 缓存，下次 AI 对话时重新加载

**后端处理：**

1. `UPDATE llm_providers SET is_default=0 WHERE is_default=1`（清除旧默认）
2. `UPDATE llm_providers SET is_default=1 WHERE id=?`
3. 校验该 provider `is_active=1`，否则返回 `code:1001 该模型未启用，无法设为默认`
4. 删除 Redis key `llm_provider:default`

**响应 data：**

```json
{
  "id": 2,
  "is_default": true
}
```

---

### 8.5 删除大模型 `DELETE /api/admin/llm-providers/{id}`

**响应：**

```json
{ "code": 0, "message": "删除成功", "data": null }
```

---

## 九、管理端 — AI 配置

### 9.1 AI 配置列表 `GET /api/admin/ai/config`

**响应 data：**

```json
{
  "list": [
    { "config_key": "system_prompt", "config_value": "你是一个智能客服助手...", "description": "系统提示词" },
    { "config_key": "temperature", "config_value": "0.7", "description": "温度参数" },
    { "config_key": "max_tokens", "config_value": "2048", "description": "最大输出 Token" },
    { "config_key": "faq_enabled", "config_value": "true", "description": "FAQ 知识库开关" },
    { "config_key": "doc_recommend", "config_value": "true", "description": "文档推荐开关" }
  ]
}
```

---

### 9.2 修改 AI 配置 `PUT /api/admin/ai/config/{key}`

> **副作用**：更新后立即清除 Redis `ai_config:cache`，下次 AI 对话使用新配置
>
> **合法 key 值**：`system_prompt` / `temperature` / `max_tokens` / `faq_enabled` / `doc_recommend`

**请求体：**

```json
{
  "value": "你是一个专业的教务客服助手，请优先依据 FAQ 与文档库回答。"
}
```

| 参数 | 类型 | 校验规则 |
|------|------|----------|
| `key`（path） | string | 必须是合法 config_key，否则 code:1004 |
| `value` | string | temperature 需为 0-2 的浮点数字符串；max_tokens 需为正整数字符串；faq_enabled/doc_recommend 需为 `true`/`false` |

**响应 data：**

```json
{
  "config_key": "system_prompt",
  "config_value": "你是一个专业的教务客服助手...",
  "updated_at": "2026-04-09 15:00:00"
}
```

---

## 十、管理端 — 公告管理

### 10.1 公告列表 `GET /api/admin/announcements`

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | int | 否 | 页码 |
| `page_size` | int | 否 | 每页条数 |
| `status` | string | 否 | `draft` / `published` / `archived` |

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "title": "系统升级通知",
      "content": "系统将于今晚 22:00-23:00 维护...",
      "type": "maintenance",
      "is_pinned": true,
      "status": "published",
      "publish_at": "2026-04-09 10:00:00",
      "expire_at": "2026-04-10 10:00:00",
      "created_by": 1,
      "created_at": "2026-04-09 09:00:00"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

---

### 10.2 新增公告 `POST /api/admin/announcements`

**请求体：**

```json
{
  "title": "系统升级通知",
  "content": "系统将于今晚 22:00-23:00 进行维护升级...",
  "type": "maintenance",
  "is_pinned": false,
  "status": "draft",
  "publish_at": "2026-04-09 22:00:00",
  "expire_at": "2026-04-10 22:00:00"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 标题 |
| `content` | string | 是 | 正文（支持 Markdown） |
| `type` | string | 否 | `notice`(默认) / `maintenance` / `update` |
| `is_pinned` | bool | 否 | 是否置顶 |
| `status` | string | 否 | `draft`(默认) / `published` |
| `publish_at` | string | 否 | 定时发布时间，null 表示立即发布 |
| `expire_at` | string | 否 | 自动下架时间 |

---

### 10.3 编辑公告 `PUT /api/admin/announcements/{id}`

请求体同 10.2，所有字段非必填。

---

### 10.4 发布/下架公告 `PUT /api/admin/announcements/{id}/status`

**请求体：**

```json
{
  "status": "published"
}
```

---

### 10.5 删除公告 `DELETE /api/admin/announcements/{id}`

**响应：**

```json
{ "code": 0, "message": "删除成功", "data": null }
```

---

## 十一、管理端 — 禁用词管理

### 11.1 禁用词列表 `GET /api/admin/banned-words`

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | int | 否 | 页码 |
| `page_size` | int | 否 | 每页条数 |
| `is_active` | bool | 否 | 筛选启用状态 |

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "word": "某敏感词",
      "match_type": "contains",
      "action": "reject",
      "replace_with": "***",
      "is_active": true,
      "created_at": "2026-04-01 10:00:00"
    }
  ],
  "total": 30,
  "page": 1,
  "page_size": 20
}
```

---

### 11.2 新增禁用词 `POST /api/admin/banned-words`

**请求体：**

```json
{
  "word": "某敏感词",
  "match_type": "contains",
  "action": "reject",
  "replace_with": "***",
  "is_active": true
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `word` | string | 是 | 敏感词 |
| `match_type` | string | 否 | `exact` / `contains`(默认) / `regex` |
| `action` | string | 否 | `reject`(默认) / `replace` / `warn` |
| `replace_with` | string | 否 | 替换文本，action=replace 时生效 |
| `is_active` | bool | 否 | 是否启用，默认 true |

---

### 11.3 批量导入禁用词 `POST /api/admin/banned-words/batch`

> **去重逻辑**：与 banned_words 表已有 word 比对，重复的跳过并计入 skipped
>
> **副作用**：导入完成后清除 Redis `banned_words:cache`，下次 AI 对话时重新加载

**请求体：**

```json
{
  "words": ["敏感词A", "敏感词B", "敏感词C"],
  "match_type": "contains",
  "action": "reject"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `words` | array | 是 | 字符串数组，最多 500 条 |
| `match_type` | string | 否 | 统一匹配方式，默认 `contains` |
| `action` | string | 否 | 统一命中动作，默认 `reject` |

**响应 data：**

```json
{
  "imported": 3,
  "skipped": 0,
  "skipped_words": []
}
```

---

### 11.4 修改禁用词 `PUT /api/admin/banned-words/{id}`

请求体同 11.2，所有字段非必填。

---

### 11.5 删除禁用词 `DELETE /api/admin/banned-words/{id}`

**响应：**

```json
{ "code": 0, "message": "删除成功", "data": null }
```

---

## 十二、管理端 — 兑换码管理

### 12.1 兑换码列表 `GET /api/admin/redeem-codes`

**Query 参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | int | 否 | 页码 |
| `page_size` | int | 否 | 每页条数 |
| `status` | string | 否 | `unused` / `used` / `expired` |
| `type` | string | 否 | `days` / `chats` |

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "code": "ABCD-1234-EFGH",
      "type": "days",
      "value": 30,
      "status": "unused",
      "created_by": 1,
      "used_by": null,
      "used_at": null,
      "expire_at": "2026-12-31 23:59:59",
      "created_at": "2026-04-01 10:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

---

### 12.2 批量生成兑换码 `POST /api/admin/redeem-codes/batch`

**请求体：**

```json
{
  "type": "days",
  "value": 30,
  "count": 100,
  "expire_at": "2026-12-31 23:59:59"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | 是 | `days` 增天数 / `chats` 增次数 |
| `value` | int | 是 | 天数或次数值 |
| `count` | int | 是 | 生成数量，最大 500 |
| `expire_at` | string | 否 | 兑换码过期时间 |

**响应 data：**

```json
{
  "generated": 100,
  "codes": ["ABCD-1234-EFGH", "IJKL-5678-MNOP"]
}
```

---

### 12.3 删除兑换码 `DELETE /api/admin/redeem-codes/{id}`

**响应：**

```json
{ "code": 0, "message": "删除成功", "data": null }
```

---

## 十三、管理端 — 订阅管理

> 复用 七、用户与订阅管理 的接口（7.1 用户列表、7.2 修改订阅、7.3 封禁/解封）

---

## 十四、管理端 — 飞书接口设置

### 14.1 飞书路由列表 `GET /api/admin/feishu/routes`

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "name": "默认对话记录表",
      "app_id": "cli_xxx",
      "app_secret_masked": "***...***",
      "app_token": "YG7ZbcyjKa24hxsOtjGcguJlnwc",
      "table_id": "tblQ9FwqAVoH2KNP",
      "route_rule": { "user_tags": ["vip"], "categories": ["退款"] },
      "is_active": true,
      "updated_at": "2026-04-09 10:00:00"
    }
  ]
}
```

---

### 14.2 新增飞书路由 `POST /api/admin/feishu/routes`

**请求体：**

```json
{
  "name": "VIP 用户对话记录",
  "app_id": "cli_xxx",
  "app_secret": "secret_xxx",
  "app_token": "YG7ZbcyjKa24hxsOtjGcguJlnwc",
  "table_id": "tblQ9FwqAVoH2KNP",
  "route_rule": { "user_tags": ["vip"] },
  "is_active": true
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 配置名称 |
| `app_id` | string | 是 | 飞书 App ID |
| `app_secret` | string | 是 | 飞书 App Secret |
| `app_token` | string | 是 | 多维表格 App Token |
| `table_id` | string | 是 | 表格 ID |
| `route_rule` | object | 否 | 路由规则 |
| `is_active` | bool | 否 | 是否启用 |

---

### 14.3 修改飞书路由 `PUT /api/admin/feishu/routes/{id}`

请求体同 14.2，所有字段非必填。

---

### 14.4 删除飞书路由 `DELETE /api/admin/feishu/routes/{id}`

**响应：**

```json
{ "code": 0, "message": "删除成功", "data": null }
```

---

## 十五、管理端 — 注册设置

### 15.1 注册配置列表 `GET /api/admin/register/config`

**响应 data：**

```json
{
  "list": [
    { "config_key": "register_enabled", "config_value": "true", "description": "注册总开关" },
    { "config_key": "register_methods", "config_value": "phone,email", "description": "允许的注册方式" },
    { "config_key": "invite_code_required", "config_value": "false", "description": "是否需要邀请码" },
    { "config_key": "default_free_chats", "config_value": "3", "description": "新用户默认免费次数" },
    { "config_key": "terms_url", "config_value": "", "description": "用户协议链接" },
    { "config_key": "privacy_url", "config_value": "", "description": "隐私政策链接" }
  ]
}
```

---

### 15.2 修改注册配置 `PUT /api/admin/register/config/{key}`

**请求体：**

```json
{
  "value": "phone"
}
```

**响应 data：**

```json
{
  "config_key": "register_methods",
  "config_value": "phone",
  "updated_at": "2026-04-09 15:00:00"
}
```

---

## 十六、管理端 — 支付设置

### 16.1 支付渠道配置列表 `GET /api/admin/payment/config`

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "channel": "wechat",
      "merchant_id": "160000****",
      "api_key_masked": "***...***",
      "notify_url": "https://example.com/api/pay/notify/wechat",
      "is_active": true,
      "extra_config": {},
      "updated_at": "2026-04-09 10:00:00"
    }
  ]
}
```

---

### 16.2 修改支付渠道 `PUT /api/admin/payment/config/{id}`

**请求体：**

```json
{
  "merchant_id": "1600001234",
  "api_key": "new_key",
  "api_secret": "new_secret",
  "notify_url": "https://example.com/api/pay/notify/wechat",
  "is_active": true,
  "extra_config": {}
}
```

---

### 16.3 套餐列表 `GET /api/admin/plans`

**响应 data：** 同用户端 3.2

---

### 16.4 新增套餐 `POST /api/admin/plans`

**请求体：**

```json
{
  "name": "月度会员",
  "type": "monthly",
  "price": 29.90,
  "duration_days": 30,
  "chat_limit": -1,
  "description": "每月不限次数对话",
  "is_active": true,
  "sort_order": 1
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 套餐名称 |
| `type` | string | 是 | `monthly` / `yearly` / `custom` |
| `price` | number | 是 | 价格（元） |
| `duration_days` | int | 是 | 有效天数 |
| `chat_limit` | int | 否 | 对话次数限制，-1 = 无限 |
| `description` | string | 否 | 描述 |
| `is_active` | bool | 否 | 是否启用 |
| `sort_order` | int | 否 | 排序权重 |

---

### 16.5 修改套餐 `PUT /api/admin/plans/{id}`

请求体同 16.4，所有字段非必填。

---

### 16.6 删除套餐 `DELETE /api/admin/plans/{id}`

**响应：**

```json
{ "code": 0, "message": "删除成功", "data": null }
```

---

## 十七、管理端 — 到期提醒设置

### 17.1 提醒规则列表 `GET /api/admin/expire-reminders`

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "days_before": 3,
      "channel": "site",
      "template": "亲爱的 {nickname}，您的订阅将于 {expire_date} 到期，请及时续费。",
      "is_active": true,
      "updated_at": "2026-04-09 10:00:00"
    }
  ]
}
```

---

### 17.2 新增提醒规则 `POST /api/admin/expire-reminders`

**请求体：**

```json
{
  "days_before": 3,
  "channel": "site",
  "template": "亲爱的 {nickname}，您的订阅将于 {expire_date} 到期，请及时续费。",
  "is_active": true
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `days_before` | int | 是 | 到期前 N 天提醒 |
| `channel` | string | 是 | `site` / `sms` / `email` |
| `template` | string | 是 | 提醒文案，支持 `{nickname}` `{expire_date}` 占位符 |
| `is_active` | bool | 否 | 是否启用 |

---

### 17.3 修改提醒规则 `PUT /api/admin/expire-reminders/{id}`

请求体同 17.2，所有字段非必填。

---

### 17.4 删除提醒规则 `DELETE /api/admin/expire-reminders/{id}`

**响应：**

```json
{ "code": 0, "message": "删除成功", "data": null }
```

---

## 十八、管理端 — 企微接口设置

### 18.1 企微配置列表 `GET /api/admin/wecom/config`

**响应 data：**

```json
{
  "list": [
    {
      "id": 1,
      "name": "运营告警群",
      "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
      "notify_types": ["payment", "alert", "daily_report"],
      "is_active": true,
      "updated_at": "2026-04-09 10:00:00"
    }
  ]
}
```

---

### 18.2 新增企微机器人 `POST /api/admin/wecom/config`

**请求体：**

```json
{
  "name": "运营告警群",
  "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
  "notify_types": ["payment", "alert", "daily_report"],
  "is_active": true
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 配置名称 |
| `webhook_url` | string | 是 | Webhook URL |
| `notify_types` | array | 是 | 通知类型：`payment` / `expire` / `alert` / `daily_report` |
| `is_active` | bool | 否 | 是否启用 |

---

### 18.3 修改企微配置 `PUT /api/admin/wecom/config/{id}`

请求体同 18.2，所有字段非必填。

---

### 18.4 删除企微配置 `DELETE /api/admin/wecom/config/{id}`

**响应：**

```json
{ "code": 0, "message": "删除成功", "data": null }
```

---

### 18.5 测试企微推送 `POST /api/admin/wecom/test/{id}`

> 无请求体，向对应 Webhook 发送测试消息

**响应 data：**

```json
{
  "success": true,
  "message": "测试消息发送成功"
}
```

---

## 接口统计

| 模块 | 接口数 |
|------|--------|
| 用户认证 | 5 |
| AI 对话 | 5 |
| 用户端其他 | 3 |
| 管理端认证 | 1 |
| 数据分析 | 4 |
| Token 计费 | 2 |
| 用户与订阅 | 3 |
| 大模型 API | 5 |
| AI 配置 | 2 |
| 公告管理 | 5 |
| 禁用词管理 | 5 |
| 兑换码管理 | 3 |
| 飞书接口 | 4 |
| 注册设置 | 2 |
| 支付设置 | 6 |
| 到期提醒 | 4 |
| 企微接口 | 5 |
| **合计** | **64** |
