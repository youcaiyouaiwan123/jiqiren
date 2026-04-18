# jiqiren AI客服系统 — 详细测试报告

> 生成时间：2026-04-18 22:55:58

## 一、执行摘要

| 指标 | 数值 |
|------|------|
| 测试总数 | **218** |
| 通过 | **218** ✅ |
| 失败 | **0** |
| 错误 | **0** |
| 通过率 | **100.0%** |
| 总耗时 | **71.35s** |
| 测试文件 | **10** |

**测试结论：✅ 全部通过**

## 二、模块汇总

| 模块 | 描述 | 总数 | 通过 | 失败 | 总耗时 | 通过率 |
|------|------|------|------|------|--------|--------|
| `test_admin_auth.py` | 管理员认证模块（登录/锁定/IP限流） | 18 | 18 | 0 | 9.64s | ✅ 100% |
| `test_admin_llm_and_words.py` | 管理员LLM配置与敏感词模块 | 19 | 19 | 0 | 5.61s | ✅ 100% |
| `test_admin_users.py` | 管理员用户管理模块 | 19 | 19 | 0 | 10.77s | ✅ 100% |
| `test_auth.py` | 认证模块（注册/登录/Profile/验证码） | 26 | 26 | 0 | 6.84s | ✅ 100% |
| `test_bugs.py` | Bug回归与边界条件测试 | 31 | 31 | 0 | 6.12s | ✅ 100% |
| `test_chat.py` | 对话模块（会话/消息/图片上传/反馈） | 29 | 29 | 0 | 8.27s | ✅ 100% |
| `test_concurrency.py` | 并发与延迟测试（并发/幂等/延迟基准） | 10 | 10 | 0 | 7.32s | ✅ 100% |
| `test_persistence.py` | 数据持久性测试（事务/一致性/级联删除） | 14 | 14 | 0 | 4.26s | ✅ 100% |
| `test_security.py` | 系统安全测试（越权/注入/认证） | 28 | 28 | 0 | 7.03s | ✅ 100% |
| `test_subscribe.py` | 订阅模块（套餐/下单/兑换码/订单） | 24 | 24 | 0 | 5.08s | ✅ 100% |

## 三、各模块详细测试结果

### 管理员认证模块（登录/锁定/IP限流）

**文件**: `test_admin_auth.py` | **总数**: 18 | **通过**: 18 | **失败**: 0 | **总耗时**: 9.64s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_admin_login_success` | TestAdminLogin | ✅ passed | 955 | 531 | 29 | 1515 |
| 2 | `test_admin_login_wrong_password` | TestAdminLogin | ✅ passed | 2 | 467 | 24 | 493 |
| 3 | `test_admin_login_nonexistent_user` | TestAdminLogin | ✅ passed | 2 | 6 | 24 | 32 |
| 4 | `test_admin_login_lockout_after_5_failures` | TestAdminLogin | ✅ passed | 2 | 1399 | 22 | 1423 |
| 5 | `test_admin_login_success_clears_fail_count` | TestAdminLogin | ✅ passed | 2 | 2107 | 22 | 2131 |
| 6 | `test_admin_login_lockout_tier_2_at_10_failures` | TestAdminLogin | ✅ passed | 2 | 468 | 25 | 495 |
| 7 | `test_admin_ip_rate_limit` | TestAdminLogin | ✅ passed | 2 | 3 | 24 | 29 |
| 8 | `test_admin_refresh_token` | TestAdminTokenRefresh | ✅ passed | 2 | 239 | 20 | 261 |
| 9 | `test_admin_refresh_with_user_token_rejected` | TestAdminTokenRefresh | ✅ passed | 2 | 2 | 23 | 27 |
| 10 | `test_admin_profile_returns_info` | TestAdminProfile | ✅ passed | 2 | 241 | 20 | 262 |
| 11 | `test_admin_profile_no_password_returned` | TestAdminProfile | ✅ passed | 1 | 234 | 20 | 256 |
| 12 | `test_change_password_success` | TestAdminChangePassword | ✅ passed | 1 | 683 | 27 | 712 |
| 13 | `test_change_password_wrong_old_rejected` | TestAdminChangePassword | ✅ passed | 1 | 460 | 20 | 482 |
| 14 | `test_change_password_same_as_old_rejected` | TestAdminChangePassword | ✅ passed | 1 | 459 | 24 | 484 |
| 15 | `test_admin_password_complexity_min_length` | TestAdminChangePassword | ✅ passed | 1 | 233 | 28 | 263 |
| 16 | `test_admin_password_must_have_special_char` | TestAdminChangePassword | ✅ passed | 1 | 240 | 23 | 264 |
| 17 | `test_super_admin_can_unlock` | TestAdminUnlock | ✅ passed | 1 | 234 | 25 | 260 |
| 18 | `test_normal_admin_cannot_unlock` | TestAdminUnlock | ✅ passed | 1 | 234 | 21 | 256 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_admin_login_success`**

```
[INFO] 日志系统初始化完成 | level=DEBUG | app=/app/logs/app.log | error=/app/logs/error.log | wecom=off
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理登录] 成功 | admin_id=1 username=testadmin ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 243.3ms
```

**2. ✅ `test_admin_login_wrong_password`**

```
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=testadmin ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 233.2ms
```

**3. ✅ `test_admin_login_nonexistent_user`**

```
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=ghost ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 4.9ms
```

**4. ✅ `test_admin_login_lockout_after_5_failures`**

```
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=lockme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 232.8ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=lockme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 231.6ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=lockme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 232.8ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=lockme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 230.9ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=lockme ip=127.0.0.1
[WARNING] [管理登录] 账号触发锁定 | username=lockme fail_count=5 lock=900s ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 232.4ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 账号已锁定 | username=lockme ttl=900s ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 1.3ms
```

**5. ✅ `test_admin_login_success_clears_fail_count`**

```
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=clearme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 237.2ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=clearme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 231.8ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=clearme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 232.7ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理登录] 成功 | admin_id=1 username=clearme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 230.3ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=clearme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 234.5ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=clearme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 233.8ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=clearme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 232.2ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理登录] 成功 | admin_id=1 username=clearme ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 233.8ms
```

**6. ✅ `test_admin_login_lockout_tier_2_at_10_failures`**

```
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=tier2 ip=127.0.0.1
[WARNING] [管理登录] 账号触发锁定 | username=tier2 fail_count=10 lock=3600s ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 233.5ms
```

**7. ✅ `test_admin_ip_rate_limit`**

```
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] IP 超频被拦截 | ip=127.0.0.1 count=41
[INFO] <<< POST /api/admin/login | 200 | 1.5ms
```

**8. ✅ `test_admin_refresh_token`**

```
[INFO] >>> POST /api/admin/refresh | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/refresh | 200 | 1.4ms
```

**9. ✅ `test_admin_refresh_with_user_token_rejected`**

```
[INFO] >>> POST /api/admin/refresh | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/refresh | 200 | 1.0ms
```

**10. ✅ `test_admin_profile_returns_info`**

```
[INFO] >>> GET /api/admin/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/profile | 200 | 1.3ms
```

**11. ✅ `test_admin_profile_no_password_returned`**

```
[INFO] >>> GET /api/admin/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/profile | 200 | 1.6ms
```

**12. ✅ `test_change_password_success`**

```
[INFO] >>> POST /api/admin/change-password | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理改密] 成功 | admin_id=1 username=admin
[INFO] <<< POST /api/admin/change-password | 200 | 451.9ms
```

**13. ✅ `test_change_password_wrong_old_rejected`**

```
[INFO] >>> POST /api/admin/change-password | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/change-password | 200 | 225.9ms
```

**14. ✅ `test_change_password_same_as_old_rejected`**

```
[INFO] >>> POST /api/admin/change-password | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/change-password | 200 | 228.2ms
```

**15. ✅ `test_admin_password_complexity_min_length`**

```
[INFO] >>> POST /api/admin/change-password | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/change-password | 200 | 1.5ms
```

**16. ✅ `test_admin_password_must_have_special_char`**

```
[INFO] >>> POST /api/admin/change-password | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/change-password | 200 | 1.6ms
```

**17. ✅ `test_super_admin_can_unlock`**

```
[INFO] >>> POST /api/admin/unlock-admin | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理解锁] admin_id=1 解锁账号 username=victim
[INFO] <<< POST /api/admin/unlock-admin | 200 | 1.8ms
```

**18. ✅ `test_normal_admin_cannot_unlock`**

```
[INFO] >>> POST /api/admin/unlock-admin | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | POST /api/admin/unlock-admin | code=1003 msg=仅超级管理员可操作
[INFO] <<< POST /api/admin/unlock-admin | 200 | 1.6ms
```

</details>

### 管理员LLM配置与敏感词模块

**文件**: `test_admin_llm_and_words.py` | **总数**: 19 | **通过**: 19 | **失败**: 0 | **总耗时**: 5.61s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_create_llm_provider` | TestLlmProviderCRUD | ✅ passed | 1 | 257 | 25 | 283 |
| 2 | `test_create_invalid_provider_rejected` | TestLlmProviderCRUD | ✅ passed | 2 | 253 | 28 | 283 |
| 3 | `test_list_llm_providers` | TestLlmProviderCRUD | ✅ passed | 2 | 363 | 23 | 387 |
| 4 | `test_api_key_not_in_list_response` | TestLlmProviderCRUD | ✅ passed | 1 | 241 | 22 | 264 |
| 5 | `test_update_llm_provider` | TestLlmProviderCRUD | ✅ passed | 1 | 239 | 21 | 262 |
| 6 | `test_update_nonexistent_llm_returns_1004` | TestLlmProviderCRUD | ✅ passed | 1 | 237 | 21 | 259 |
| 7 | `test_delete_llm_provider` | TestLlmProviderCRUD | ✅ passed | 1 | 240 | 19 | 261 |
| 8 | `test_only_one_default_at_a_time` | TestLlmDefaultProvider | ✅ passed | 2 | 245 | 23 | 269 |
| 9 | `test_cannot_set_inactive_as_default` | TestLlmDefaultProvider | ✅ passed | 1 | 235 | 19 | 256 |
| 10 | `test_cannot_create_inactive_default` | TestLlmDefaultProvider | ✅ passed | 2 | 234 | 21 | 257 |
| 11 | `test_disabling_default_clears_is_default` | TestLlmDefaultProvider | ✅ passed | 1 | 238 | 20 | 259 |
| 12 | `test_create_banned_word` | TestBannedWords | ✅ passed | 1 | 239 | 19 | 259 |
| 13 | `test_list_banned_words` | TestBannedWords | ✅ passed | 1 | 245 | 17 | 263 |
| 14 | `test_search_banned_words_by_keyword` | TestBannedWords | ✅ passed | 1 | 246 | 22 | 270 |
| 15 | `test_batch_import_banned_words` | TestBannedWords | ✅ passed | 1 | 238 | 23 | 263 |
| 16 | `test_batch_import_skips_duplicates` | TestBannedWords | ✅ passed | 2 | 243 | 23 | 267 |
| 17 | `test_batch_import_limit_500_words` | TestBannedWords | ✅ passed | 1 | 663 | 26 | 690 |
| 18 | `test_update_banned_word` | TestBannedWords | ✅ passed | 2 | 265 | 24 | 291 |
| 19 | `test_delete_banned_word` | TestBannedWords | ✅ passed | 2 | 242 | 21 | 264 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_create_llm_provider`**

```
[INFO] >>> POST /api/admin/llm-providers | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/llm-providers | 200 | 10.0ms
```

**2. ✅ `test_create_invalid_provider_rejected`**

```
[INFO] >>> POST /api/admin/llm-providers | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/llm-providers | 200 | 1.7ms
```

**3. ✅ `test_list_llm_providers`**

```
[INFO] >>> GET /api/admin/llm-providers | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/llm-providers | 200 | 121.2ms
```

**4. ✅ `test_api_key_not_in_list_response`**

```
[INFO] >>> GET /api/admin/llm-providers | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/llm-providers | 200 | 5.3ms
```

**5. ✅ `test_update_llm_provider`**

```
[INFO] >>> PUT /api/admin/llm-providers/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/llm-providers/1 | 200 | 4.8ms
```

**6. ✅ `test_update_nonexistent_llm_returns_1004`**

```
[INFO] >>> PUT /api/admin/llm-providers/999999 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/llm-providers/999999 | 200 | 4.5ms
```

**7. ✅ `test_delete_llm_provider`**

```
[INFO] >>> DELETE /api/admin/llm-providers/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< DELETE /api/admin/llm-providers/1 | 200 | 1.4ms
```

**8. ✅ `test_only_one_default_at_a_time`**

```
[INFO] >>> PUT /api/admin/llm-providers/2/default | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/llm-providers/2/default | 200 | 5.2ms
```

**9. ✅ `test_cannot_set_inactive_as_default`**

```
[INFO] >>> PUT /api/admin/llm-providers/1/default | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/llm-providers/1/default | 200 | 1.4ms
```

**10. ✅ `test_cannot_create_inactive_default`**

```
[INFO] >>> POST /api/admin/llm-providers | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/llm-providers | 200 | 1.7ms
```

**11. ✅ `test_disabling_default_clears_is_default`**

```
[INFO] >>> PUT /api/admin/llm-providers/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/llm-providers/1 | 200 | 4.4ms
```

**12. ✅ `test_create_banned_word`**

```
[INFO] >>> POST /api/admin/banned-words | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/banned-words | 200 | 7.4ms
```

**13. ✅ `test_list_banned_words`**

```
[INFO] >>> POST /api/admin/banned-words | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/banned-words | 200 | 5.6ms
[INFO] >>> GET /api/admin/banned-words | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/banned-words | 200 | 6.1ms
```

**14. ✅ `test_search_banned_words_by_keyword`**

```
[INFO] >>> POST /api/admin/banned-words | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/banned-words | 200 | 5.0ms
[INFO] >>> GET /api/admin/banned-words | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/banned-words | 200 | 7.1ms
```

**15. ✅ `test_batch_import_banned_words`**

```
[INFO] >>> POST /api/admin/banned-words/batch | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/banned-words/batch | 200 | 6.7ms
```

**16. ✅ `test_batch_import_skips_duplicates`**

```
[INFO] >>> POST /api/admin/banned-words/batch | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/banned-words/batch | 200 | 4.5ms
[INFO] >>> POST /api/admin/banned-words/batch | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/banned-words/batch | 200 | 3.9ms
```

**17. ✅ `test_batch_import_limit_500_words`**

```
[INFO] >>> POST /api/admin/banned-words/batch | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/banned-words/batch | 200 | 429.1ms
```

**18. ✅ `test_update_banned_word`**

```
[INFO] >>> POST /api/admin/banned-words | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/banned-words | 200 | 5.2ms
[INFO] >>> PUT /api/admin/banned-words/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/banned-words/1 | 200 | 6.6ms
```

**19. ✅ `test_delete_banned_word`**

```
[INFO] >>> POST /api/admin/banned-words | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/banned-words | 200 | 5.9ms
[INFO] >>> DELETE /api/admin/banned-words/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< DELETE /api/admin/banned-words/1 | 200 | 2.9ms
```

</details>

### 管理员用户管理模块

**文件**: `test_admin_users.py` | **总数**: 19 | **通过**: 19 | **失败**: 0 | **总耗时**: 10.77s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_list_users` | TestAdminUserList | ✅ passed | 2 | 709 | 22 | 732 |
| 2 | `test_search_users_by_keyword` | TestAdminUserList | ✅ passed | 1 | 706 | 23 | 730 |
| 3 | `test_filter_users_by_status` | TestAdminUserList | ✅ passed | 1 | 700 | 20 | 722 |
| 4 | `test_pagination_works` | TestAdminUserList | ✅ passed | 1 | 1404 | 22 | 1427 |
| 5 | `test_create_user_success` | TestAdminCreateUser | ✅ passed | 2 | 469 | 22 | 493 |
| 6 | `test_create_user_duplicate_phone_rejected` | TestAdminCreateUser | ✅ passed | 1 | 471 | 21 | 494 |
| 7 | `test_create_user_invalid_subscribe_plan_rejected` | TestAdminCreateUser | ✅ passed | 2 | 246 | 30 | 278 |
| 8 | `test_update_user_nickname` | TestAdminUpdateUser | ✅ passed | 2 | 480 | 23 | 505 |
| 9 | `test_update_nonexistent_user` | TestAdminUpdateUser | ✅ passed | 1 | 239 | 26 | 267 |
| 10 | `test_ban_user` | TestAdminUserStatus | ✅ passed | 1 | 464 | 20 | 486 |
| 11 | `test_unban_user` | TestAdminUserStatus | ✅ passed | 1 | 463 | 20 | 485 |
| 12 | `test_invalid_status_rejected` | TestAdminUserStatus | ✅ passed | 1 | 463 | 21 | 485 |
| 13 | `test_update_subscription` | TestAdminSubscriptionManagement | ✅ passed | 1 | 465 | 23 | 489 |
| 14 | `test_invalid_subscribe_plan_rejected` | TestAdminSubscriptionManagement | ✅ passed | 2 | 462 | 20 | 484 |
| 15 | `test_batch_subscribe_override` | TestAdminSubscriptionManagement | ✅ passed | 1 | 702 | 38 | 741 |
| 16 | `test_batch_subscribe_add_days` | TestAdminSubscriptionManagement | ✅ passed | 2 | 466 | 23 | 490 |
| 17 | `test_set_trial_chats` | TestAdminTrialChats | ✅ passed | 1 | 467 | 19 | 488 |
| 18 | `test_increase_trial_chats` | TestAdminTrialChats | ✅ passed | 2 | 468 | 22 | 492 |
| 19 | `test_invalid_trial_mode_rejected` | TestAdminTrialChats | ✅ passed | 2 | 464 | 22 | 487 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_list_users`**

```
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/users | 200 | 12.0ms
```

**2. ✅ `test_search_users_by_keyword`**

```
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/users | 200 | 10.3ms
```

**3. ✅ `test_filter_users_by_status`**

```
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/users | 200 | 8.3ms
```

**4. ✅ `test_pagination_works`**

```
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/users | 200 | 7.1ms
```

**5. ✅ `test_create_user_success`**

```
[INFO] >>> POST /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理端-用户] 新建用户 | admin_id=1 user_id=1
[INFO] <<< POST /api/admin/users | 200 | 236.4ms
```

**6. ✅ `test_create_user_duplicate_phone_rejected`**

```
[INFO] >>> POST /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/users | 200 | 4.9ms
```

**7. ✅ `test_create_user_invalid_subscribe_plan_rejected`**

```
[INFO] >>> POST /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/admin/users | 200 | 1.6ms
```

**8. ✅ `test_update_user_nickname`**

```
[INFO] >>> PUT /api/admin/users/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理端-用户] 更新资料 | admin_id=1 user_id=1
[INFO] <<< PUT /api/admin/users/1 | 200 | 4.8ms
```

**9. ✅ `test_update_nonexistent_user`**

```
[INFO] >>> PUT /api/admin/users/999999 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/users/999999 | 200 | 5.1ms
```

**10. ✅ `test_ban_user`**

```
[INFO] >>> PUT /api/admin/users/1/status | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理端-用户] 更新状态 | admin_id=1 user_id=1 status=banned
[INFO] <<< PUT /api/admin/users/1/status | 200 | 2.6ms
```

**11. ✅ `test_unban_user`**

```
[INFO] >>> PUT /api/admin/users/1/status | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理端-用户] 更新状态 | admin_id=1 user_id=1 status=active
[INFO] <<< PUT /api/admin/users/1/status | 200 | 2.1ms
```

**12. ✅ `test_invalid_status_rejected`**

```
[INFO] >>> PUT /api/admin/users/1/status | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/users/1/status | 200 | 3.1ms
```

**13. ✅ `test_update_subscription`**

```
[INFO] >>> PUT /api/admin/users/1/subscribe | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理端-用户] 更新会员 | admin_id=1 user_id=1
[INFO] <<< PUT /api/admin/users/1/subscribe | 200 | 2.4ms
```

**14. ✅ `test_invalid_subscribe_plan_rejected`**

```
[INFO] >>> PUT /api/admin/users/1/subscribe | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/users/1/subscribe | 200 | 1.9ms
```

**15. ✅ `test_batch_subscribe_override`**

```
[INFO] >>> PUT /api/admin/users/batch-subscribe | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理端-用户] 批量授权 | admin_id=1 mode=override count=2
[INFO] <<< PUT /api/admin/users/batch-subscribe | 200 | 5.1ms
```

**16. ✅ `test_batch_subscribe_add_days`**

```
[INFO] >>> PUT /api/admin/users/batch-subscribe | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理端-用户] 批量授权 | admin_id=1 mode=add_days count=1
[INFO] <<< PUT /api/admin/users/batch-subscribe | 200 | 3.9ms
```

**17. ✅ `test_set_trial_chats`**

```
[INFO] >>> PUT /api/admin/users/1/trial | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理端-用户] 更新试用次数 | admin_id=1 user_id=1 mode=set value=10 result=10
[INFO] <<< PUT /api/admin/users/1/trial | 200 | 3.8ms
```

**18. ✅ `test_increase_trial_chats`**

```
[INFO] >>> PUT /api/admin/users/1/trial | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [管理端-用户] 更新试用次数 | admin_id=1 user_id=1 mode=increase value=5 result=8
[INFO] <<< PUT /api/admin/users/1/trial | 200 | 4.4ms
```

**19. ✅ `test_invalid_trial_mode_rejected`**

```
[INFO] >>> PUT /api/admin/users/1/trial | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/admin/users/1/trial | 200 | 1.9ms
```

</details>

### 认证模块（注册/登录/Profile/验证码）

**文件**: `test_auth.py` | **总数**: 26 | **通过**: 26 | **失败**: 0 | **总耗时**: 6.84s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_register_requires_phone_or_email` | TestRegister | ✅ passed | 2 | 9 | 22 | 33 |
| 2 | `test_register_cannot_provide_both_phone_and_email` | TestRegister | ✅ passed | 1 | 7 | 20 | 28 |
| 3 | `test_register_invalid_phone_format` | TestRegister | ✅ passed | 2 | 24 | 22 | 48 |
| 4 | `test_register_password_min_length` | TestRegister | ✅ passed | 1 | 6 | 27 | 34 |
| 5 | `test_register_disabled` | TestRegister | ✅ passed | 1 | 8 | 22 | 31 |
| 6 | `test_register_duplicate_phone` | TestRegister | ✅ passed | 1 | 243 | 20 | 264 |
| 7 | `test_register_wrong_verify_code` | TestRegister | ✅ passed | 1 | 14 | 20 | 35 |
| 8 | `test_register_verify_code_consumed_after_use` | TestRegister | ✅ passed | 1 | 249 | 22 | 272 |
| 9 | `test_login_success` | TestLogin | ✅ passed | 1 | 458 | 25 | 485 |
| 10 | `test_login_wrong_password` | TestLogin | ✅ passed | 2 | 464 | 22 | 488 |
| 11 | `test_login_nonexistent_account` | TestLogin | ✅ passed | 1 | 4 | 139 | 144 |
| 12 | `test_login_banned_user_rejected` | TestLogin | ✅ passed | 1 | 460 | 21 | 482 |
| 13 | `test_login_by_email` | TestLogin | ✅ passed | 1 | 463 | 20 | 484 |
| 14 | `test_login_response_contains_masked_user_info` | TestLogin | ✅ passed | 1 | 463 | 23 | 487 |
| 15 | `test_refresh_token_generates_new_access_token` | TestTokenRefresh | ✅ passed | 1 | 235 | 21 | 257 |
| 16 | `test_invalid_refresh_token_rejected` | TestTokenRefresh | ✅ passed | 2 | 2 | 22 | 26 |
| 17 | `test_access_token_cannot_be_used_as_refresh` | TestTokenRefresh | ✅ passed | 1 | 233 | 19 | 253 |
| 18 | `test_get_profile_returns_user_info` | TestProfile | ✅ passed | 1 | 234 | 21 | 257 |
| 19 | `test_update_nickname` | TestProfile | ✅ passed | 1 | 234 | 21 | 256 |
| 20 | `test_update_empty_nickname_rejected` | TestProfile | ✅ passed | 1 | 235 | 24 | 260 |
| 21 | `test_update_too_long_nickname_rejected` | TestProfile | ✅ passed | 2 | 236 | 19 | 256 |
| 22 | `test_change_password_success` | TestChangePassword | ✅ passed | 1 | 686 | 23 | 711 |
| 23 | `test_change_password_wrong_old_password` | TestChangePassword | ✅ passed | 2 | 467 | 22 | 491 |
| 24 | `test_change_password_same_as_old_rejected` | TestChangePassword | ✅ passed | 1 | 457 | 20 | 479 |
| 25 | `test_change_password_complexity_enforced` | TestChangePassword | ✅ passed | 1 | 234 | 18 | 253 |
| 26 | `test_get_register_config_public_only` | TestRegisterConfig | ✅ passed | 1 | 6 | 20 | 27 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_register_requires_phone_or_email`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 5.1ms
```

**2. ✅ `test_register_cannot_provide_both_phone_and_email`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 3.3ms
```

**3. ✅ `test_register_invalid_phone_format`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 5.8ms
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 2.4ms
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 2.3ms
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 2.6ms
```

**4. ✅ `test_register_password_min_length`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 3.0ms
```

**5. ✅ `test_register_disabled`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 3.7ms
```

**6. ✅ `test_register_duplicate_phone`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 5.5ms
```

**7. ✅ `test_register_wrong_verify_code`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 4.2ms
```

**8. ✅ `test_register_verify_code_consumed_after_use`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [注册] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/register | 200 | 233.9ms
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 4.9ms
```

**9. ✅ `test_login_success`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [登录] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/login | 200 | 228.8ms
```

**10. ✅ `test_login_wrong_password`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [登录] 密码错误 | ip=127.0.0.1 account=13800000001
[INFO] <<< POST /api/auth/login | 200 | 231.1ms
```

**11. ✅ `test_login_nonexistent_account`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/login | 200 | 3.2ms
```

**12. ✅ `test_login_banned_user_rejected`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/login | 200 | 229.3ms
```

**13. ✅ `test_login_by_email`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [登录] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/login | 200 | 232.2ms
```

**14. ✅ `test_login_response_contains_masked_user_info`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [登录] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/login | 200 | 230.9ms
```

**15. ✅ `test_refresh_token_generates_new_access_token`**

```
[INFO] >>> POST /api/auth/refresh | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/refresh | 200 | 1.6ms
```

**16. ✅ `test_invalid_refresh_token_rejected`**

```
[INFO] >>> POST /api/auth/refresh | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/refresh | 200 | 1.0ms
```

**17. ✅ `test_access_token_cannot_be_used_as_refresh`**

```
[INFO] >>> POST /api/auth/refresh | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/refresh | 200 | 1.0ms
```

**18. ✅ `test_get_profile_returns_user_info`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/auth/profile | 200 | 1.3ms
```

**19. ✅ `test_update_nickname`**

```
[INFO] >>> PUT /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [个人中心] 更新信息 | user_id=1
[INFO] <<< PUT /api/auth/profile | 200 | 2.1ms
```

**20. ✅ `test_update_empty_nickname_rejected`**

```
[INFO] >>> PUT /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/auth/profile | 200 | 1.9ms
```

**21. ✅ `test_update_too_long_nickname_rejected`**

```
[INFO] >>> PUT /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/auth/profile | 200 | 1.6ms
```

**22. ✅ `test_change_password_success`**

```
[INFO] >>> POST /api/auth/change-password | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [个人中心] 修改密码 | user_id=1
[INFO] <<< POST /api/auth/change-password | 200 | 454.4ms
```

**23. ✅ `test_change_password_wrong_old_password`**

```
[INFO] >>> POST /api/auth/change-password | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/change-password | 200 | 231.6ms
```

**24. ✅ `test_change_password_same_as_old_rejected`**

```
[INFO] >>> POST /api/auth/change-password | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/change-password | 200 | 226.2ms
```

**25. ✅ `test_change_password_complexity_enforced`**

```
[INFO] >>> POST /api/auth/change-password | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/change-password | 200 | 1.4ms
```

**26. ✅ `test_get_register_config_public_only`**

```
[INFO] >>> GET /api/auth/register-config | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/auth/register-config | 200 | 2.0ms
```

</details>

### Bug回归与边界条件测试

**文件**: `test_bugs.py` | **总数**: 31 | **通过**: 31 | **失败**: 0 | **总耗时**: 6.12s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_phone_with_spaces_normalized` | TestEdgeCasesRegistration | ✅ passed | 2 | 249 | 22 | 273 |
| 2 | `test_email_normalized_to_lowercase` | TestEdgeCasesRegistration | ✅ passed | 2 | 463 | 21 | 486 |
| 3 | `test_chinese_conversation_title` | TestEdgeCasesUnicode | ✅ passed | 2 | 241 | 20 | 262 |
| 4 | `test_emoji_in_title` | TestEdgeCasesUnicode | ✅ passed | 1 | 239 | 22 | 263 |
| 5 | `test_null_bytes_in_message_handled` | TestEdgeCasesUnicode | ✅ passed | 1 | 233 | 22 | 256 |
| 6 | `test_page_size_zero_handled` | TestEdgeCasesPagination | ✅ passed | 1 | 239 | 20 | 260 |
| 7 | `test_page_beyond_total` | TestEdgeCasesPagination | ✅ passed | 1 | 245 | 21 | 267 |
| 8 | `test_negative_page_handled` | TestEdgeCasesPagination | ✅ passed | 1 | 235 | 22 | 258 |
| 9 | `test_page_size_exceeds_max` | TestEdgeCasesPagination | ✅ passed | 2 | 237 | 20 | 259 |
| 10 | `test_deleted_user_token_rejected` | TestDeletedAccountBehavior | ✅ passed | 2 | 240 | 27 | 269 |
| 11 | `test_bcrypt_cost_factor` | TestPasswordSecurity | ✅ passed | 1 | 228 | 24 | 253 |
| 12 | `test_different_passwords_produce_different_hashes` | TestPasswordSecurity | ✅ passed | 1 | 452 | 23 | 476 |
| 13 | `test_verify_password_correct` | TestPasswordSecurity | ✅ passed | 1 | 452 | 22 | 474 |
| 14 | `test_verify_password_wrong` | TestPasswordSecurity | ✅ passed | 1 | 452 | 25 | 478 |
| 15 | `test_redeem_code_case_insensitive_not_applied` | TestRedeemEdgeCases | ✅ passed | 2 | 243 | 19 | 264 |
| 16 | `test_redeem_empty_code_rejected` | TestRedeemEdgeCases | ✅ passed | 2 | 236 | 22 | 260 |
| 17 | `test_redeem_code_value_zero_not_created` | TestRedeemEdgeCases | ✅ passed | 1 | 0 | 20 | 21 |
| 18 | `test_admin_access_token_not_usable_for_user_endpoints` | TestTokenTypeConfusion | ✅ passed | 2 | 233 | 22 | 257 |
| 19 | `test_user_access_token_not_usable_for_admin_endpoints` | TestTokenTypeConfusion | ✅ passed | 1 | 232 | 23 | 257 |
| 20 | `test_all_responses_have_code_field` | TestResponseFormat | ✅ passed | 2 | 7 | 22 | 30 |
| 21 | `test_all_responses_have_request_id` | TestResponseFormat | ✅ passed | 1 | 234 | 21 | 256 |
| 22 | `test_health_check_always_200` | TestResponseFormat | ✅ passed | 1 | 1 | 22 | 24 |
| 23 | `test_biz_exception_returns_200_not_500` | TestResponseFormat | ✅ passed | 2 | 2 | 20 | 23 |
| 24 | `test_invite_code_required_when_configured` | TestInviteCode | ✅ passed | 1 | 15 | 20 | 36 |
| 25 | `test_invalid_invite_code_rejected` | TestInviteCode | ✅ passed | 1 | 16 | 20 | 37 |
| 26 | `test_normalize_provider_aliases` | TestAiServiceUrlNormalization | ✅ passed | 1 | 0 | 19 | 20 |
| 27 | `test_normalize_api_base_strips_endpoint_suffix` | TestAiServiceUrlNormalization | ✅ passed | 1 | 0 | 18 | 19 |
| 28 | `test_normalize_api_base_keeps_clean_url` | TestAiServiceUrlNormalization | ✅ passed | 1 | 0 | 19 | 20 |
| 29 | `test_parse_float_safe` | TestAiServiceUrlNormalization | ✅ passed | 1 | 0 | 18 | 19 |
| 30 | `test_parse_int_safe` | TestAiServiceUrlNormalization | ✅ passed | 1 | 0 | 19 | 19 |
| 31 | `test_parse_bool` | TestAiServiceUrlNormalization | ✅ passed | 1 | 0 | 20 | 20 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_phone_with_spaces_normalized`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [注册] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/register | 200 | 239.3ms
```

**2. ✅ `test_email_normalized_to_lowercase`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [登录] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/login | 200 | 229.5ms
```

**3. ✅ `test_chinese_conversation_title`**

```
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=1
[INFO] <<< POST /api/chat/conversations | 200 | 4.4ms
```

**4. ✅ `test_emoji_in_title`**

```
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=1
[INFO] <<< POST /api/chat/conversations | 200 | 3.8ms
```

**5. ✅ `test_null_bytes_in_message_handled`**

```
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [对话] 配额不足 | user_id=1 free_left=0
[INFO] <<< POST /api/chat/send | 200 | 4.1ms
```

**6. ✅ `test_page_size_zero_handled`**

```
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] <<< GET /api/chat/conversations | 422 | 1.8ms
```

**7. ✅ `test_page_beyond_total`**

```
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations | 200 | 8.4ms
```

**8. ✅ `test_negative_page_handled`**

```
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] <<< GET /api/chat/conversations | 422 | 1.8ms
```

**9. ✅ `test_page_size_exceeds_max`**

```
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] <<< GET /api/admin/users | 422 | 1.6ms
```

**10. ✅ `test_deleted_user_token_rejected`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=账号不存在或已注销
[INFO] <<< GET /api/auth/profile | 200 | 1.5ms
```

**11. ✅ `test_bcrypt_cost_factor`**

*(无请求日志)*

**12. ✅ `test_different_passwords_produce_different_hashes`**

*(无请求日志)*

**13. ✅ `test_verify_password_correct`**

*(无请求日志)*

**14. ✅ `test_verify_password_wrong`**

*(无请求日志)*

**15. ✅ `test_redeem_code_case_insensitive_not_applied`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 无效兑换码 | user_id=1 code=upper001
[INFO] <<< POST /api/subscribe/redeem | 200 | 3.8ms
```

**16. ✅ `test_redeem_empty_code_rejected`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 无效兑换码 | user_id=1 code=
[INFO] <<< POST /api/subscribe/redeem | 200 | 3.7ms
```

**17. ✅ `test_redeem_code_value_zero_not_created`**

*(无请求日志)*

**18. ✅ `test_admin_access_token_not_usable_for_user_endpoints`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=Token 无效
[INFO] <<< GET /api/auth/profile | 200 | 1.4ms
```

**19. ✅ `test_user_access_token_not_usable_for_admin_endpoints`**

```
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/admin/users | code=1003 msg=权限不足
[INFO] <<< GET /api/admin/users | 200 | 1.3ms
```

**20. ✅ `test_all_responses_have_code_field`**

```
[INFO] >>> GET /api/auth/register-config | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/auth/register-config | 200 | 1.8ms
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/login | 200 | 2.9ms
```

**21. ✅ `test_all_responses_have_request_id`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/auth/profile | 200 | 1.3ms
```

**22. ✅ `test_health_check_always_200`**

*(无请求日志)*

**23. ✅ `test_biz_exception_returns_200_not_500`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=未登录
[INFO] <<< GET /api/auth/profile | 200 | 1.1ms
```

**24. ✅ `test_invite_code_required_when_configured`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 3.2ms
```

**25. ✅ `test_invalid_invite_code_rejected`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/register | 200 | 5.8ms
```

**26. ✅ `test_normalize_provider_aliases`**

*(无请求日志)*

**27. ✅ `test_normalize_api_base_strips_endpoint_suffix`**

*(无请求日志)*

**28. ✅ `test_normalize_api_base_keeps_clean_url`**

*(无请求日志)*

**29. ✅ `test_parse_float_safe`**

*(无请求日志)*

**30. ✅ `test_parse_int_safe`**

*(无请求日志)*

**31. ✅ `test_parse_bool`**

*(无请求日志)*

</details>

### 对话模块（会话/消息/图片上传/反馈）

**文件**: `test_chat.py` | **总数**: 29 | **通过**: 29 | **失败**: 0 | **总耗时**: 8.27s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_create_conversation` | TestConversationCRUD | ✅ passed | 1 | 235 | 19 | 256 |
| 2 | `test_create_conversation_default_title` | TestConversationCRUD | ✅ passed | 1 | 235 | 21 | 257 |
| 3 | `test_list_conversations_only_own` | TestConversationCRUD | ✅ passed | 1 | 473 | 24 | 498 |
| 4 | `test_rename_conversation` | TestConversationCRUD | ✅ passed | 1 | 239 | 18 | 259 |
| 5 | `test_rename_trims_whitespace` | TestConversationCRUD | ✅ passed | 2 | 238 | 19 | 259 |
| 6 | `test_rename_conversation_truncates_to_200` | TestConversationCRUD | ✅ passed | 2 | 239 | 23 | 264 |
| 7 | `test_delete_conversation_and_messages` | TestConversationCRUD | ✅ passed | 2 | 256 | 25 | 282 |
| 8 | `test_delete_nonexistent_conversation` | TestConversationCRUD | ✅ passed | 2 | 234 | 18 | 254 |
| 9 | `test_conversations_paginate` | TestConversationCRUD | ✅ passed | 1 | 306 | 21 | 328 |
| 10 | `test_conversations_page2` | TestConversationCRUD | ✅ passed | 1 | 282 | 20 | 304 |
| 11 | `test_get_messages_in_order` | TestMessages | ✅ passed | 1 | 252 | 21 | 274 |
| 12 | `test_get_messages_includes_feedback` | TestMessages | ✅ passed | 2 | 248 | 21 | 271 |
| 13 | `test_user_message_has_no_rating` | TestMessages | ✅ passed | 1 | 246 | 22 | 269 |
| 14 | `test_send_message_deducts_free_chats` | TestSendMessage | ✅ passed | 2 | 292 | 22 | 316 |
| 15 | `test_send_message_quota_exhausted` | TestSendMessage | ✅ passed | 2 | 235 | 21 | 258 |
| 16 | `test_send_message_banned_user_rejected` | TestSendMessage | ✅ passed | 1 | 234 | 21 | 257 |
| 17 | `test_send_message_with_subscription_no_quota_check` | TestSendMessage | ✅ passed | 2 | 272 | 23 | 297 |
| 18 | `test_send_message_expired_subscription_treated_as_free` | TestSendMessage | ✅ passed | 1 | 238 | 25 | 264 |
| 19 | `test_send_message_to_nonexistent_conversation` | TestSendMessage | ✅ passed | 1 | 236 | 25 | 262 |
| 20 | `test_upload_valid_image` | TestImageUpload | ✅ passed | 3 | 237 | 25 | 265 |
| 21 | `test_upload_unsupported_format_rejected` | TestImageUpload | ✅ passed | 2 | 236 | 21 | 259 |
| 22 | `test_upload_too_large_image_rejected` | TestImageUpload | ✅ passed | 1 | 311 | 24 | 337 |
| 23 | `test_upload_too_small_image_rejected` | TestImageUpload | ✅ passed | 1 | 235 | 20 | 256 |
| 24 | `test_upload_unsupported_audio_format_rejected` | TestAudioUpload | ✅ passed | 1 | 236 | 21 | 258 |
| 25 | `test_upload_too_large_audio_rejected` | TestAudioUpload | ✅ passed | 2 | 351 | 21 | 374 |
| 26 | `test_feedback_like` | TestMessageFeedback | ✅ passed | 1 | 246 | 23 | 270 |
| 27 | `test_feedback_dislike` | TestMessageFeedback | ✅ passed | 1 | 264 | 25 | 291 |
| 28 | `test_feedback_invalid_rating_rejected` | TestMessageFeedback | ✅ passed | 2 | 239 | 22 | 262 |
| 29 | `test_cannot_feedback_user_message` | TestMessageFeedback | ✅ passed | 1 | 240 | 24 | 265 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_create_conversation`**

```
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=1
[INFO] <<< POST /api/chat/conversations | 200 | 3.5ms
```

**2. ✅ `test_create_conversation_default_title`**

```
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=1
[INFO] <<< POST /api/chat/conversations | 200 | 3.5ms
```

**3. ✅ `test_list_conversations_only_own`**

```
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations | 200 | 6.0ms
```

**4. ✅ `test_rename_conversation`**

```
[INFO] >>> PUT /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 重命名 | user_id=1 conv_id=1 title=新名称
[INFO] <<< PUT /api/chat/conversations/1 | 200 | 4.2ms
```

**5. ✅ `test_rename_trims_whitespace`**

```
[INFO] >>> PUT /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 重命名 | user_id=1 conv_id=1 title=有空格
[INFO] <<< PUT /api/chat/conversations/1 | 200 | 3.6ms
```

**6. ✅ `test_rename_conversation_truncates_to_200`**

```
[INFO] >>> PUT /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 重命名 | user_id=1 conv_id=1 title=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
[INFO] <<< PUT /api/chat/conversations/1 | 200 | 4.0ms
```

**7. ✅ `test_delete_conversation_and_messages`**

```
[INFO] >>> DELETE /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 删除 | user_id=1 conv_id=1
[INFO] <<< DELETE /api/chat/conversations/1 | 200 | 7.5ms
```

**8. ✅ `test_delete_nonexistent_conversation`**

```
[INFO] >>> DELETE /api/chat/conversations/999999 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< DELETE /api/chat/conversations/999999 | 200 | 3.0ms
```

**9. ✅ `test_conversations_paginate`**

```
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations | 200 | 6.5ms
```

**10. ✅ `test_conversations_page2`**

```
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations | 200 | 5.5ms
```

**11. ✅ `test_get_messages_in_order`**

```
[INFO] >>> GET /api/chat/conversations/1/messages | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations/1/messages | 200 | 9.3ms
```

**12. ✅ `test_get_messages_includes_feedback`**

```
[INFO] >>> GET /api/chat/conversations/1/messages | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations/1/messages | 200 | 6.8ms
```

**13. ✅ `test_user_message_has_no_rating`**

```
[INFO] >>> GET /api/chat/conversations/1/messages | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations/1/messages | 200 | 5.8ms
```

**14. ✅ `test_send_message_deducts_free_chats`**

```
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [对话] 发送 | user_id=1 conv_id=1 msg_len=2 has_sub=False
[INFO] <<< POST /api/chat/send | 200 | 11.1ms
```

**15. ✅ `test_send_message_quota_exhausted`**

```
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [对话] 配额不足 | user_id=1 free_left=0
[INFO] <<< POST /api/chat/send | 200 | 3.7ms
```

**16. ✅ `test_send_message_banned_user_rejected`**

```
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | POST /api/chat/send | code=1002 msg=账号已被封禁
[INFO] <<< POST /api/chat/send | 200 | 1.8ms
```

**17. ✅ `test_send_message_with_subscription_no_quota_check`**

```
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [对话] 发送 | user_id=1 conv_id=1 msg_len=2 has_sub=True
[INFO] <<< POST /api/chat/send | 200 | 7.1ms
[ERROR] Exception terminating connection <AdaptedConnection <aiomysql.connection.Connection object at 0x7f45d1d72190>>
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 1301, in _checkout
    result = pool._dialect._do_ping_w_event(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 720, in _do_ping_w_event
    return self.do_ping(dbapi_connection)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/pymysql.py", line 106, in do_ping
    dbapi_connection.ping(False)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/aiomysql.py", line 188, in ping
    return self.await_(self._connection.ping(reconnect))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 494, in ping
    await self._read_ok_packet()
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 372, in _read_ok_packet
    pkt = await self._read_packet()
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 609, in _read_packet
    packet_header = await self._read_bytes(4)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 657, in _read_bytes
    data = await self._reader.readexactly(num_bytes)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/streams.py", line 750, in readexactly
    await self._wait_for_data('readexactly')
  File "/usr/local/lib/python3.11/asyncio/streams.py", line 543, in _wait_for_data
    await self._waiter
RuntimeError: Task <Task pending name='starlette.responses.StreamingResponse.__call__.<locals>.wrap' coro=<StreamingResponse.__call__.<locals>.wrap() running at /usr/local/lib/python3.11/site-packages/starlette/responses.py:266> cb=[TaskGroup._spawn.<locals>.task_done() at /usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:821]> got Future <Future pending> attached to a different loop

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 374, in _close_connection
    self._dialect.do_terminate(connection)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/aiomysql.py", line 312, in do_terminate
    dbapi_connection.terminate()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/aiomysql.py", line 210, in terminate
    self._connection.close()
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 339, in close
    self._writer.transport.close()
  File "/usr/local/lib/python3.11/asyncio/selector_events.py", line 864, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/usr/local/lib/python3.11/asyncio/base_events.py", line 762, in call_soon
    self._check_closed()
  File "/usr/local/lib/python3.11/asyncio/base_events.py", line 520, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
[ERROR] [对话] AI响应异常 | user_id=1 conv_id=1
Traceback (most recent call last):
  File "/app/app/routers/chat_v2.py", line 352, in event_stream
    await sse_db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn
    result = context.throw(*sys.exc_info())
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4353, in flush
    self._flush(objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4488, in _flush
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4449, in _flush
    flush_context.execute()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/unitofwork.py", line 466, in execute
    rec.execute(self)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/unitofwork.py", line 642, in execute
    util.preloaded.orm_persistence.save_obj(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/persistence.py", line 60, in save_obj
    for (
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/persistence.py", line 223, in _organize_states_for_save
    for state, dict_, mapper, connection in _connections_for_states(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/persistence.py", line 1753, in _connections_for_states
    connection = uowtransaction.transaction.connection(base_mapper)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 2, in connection
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go
    ret_value = fn(self, *arg, **kw)
                ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 1039, in connection
    return self._connection_for_bind(bind, execution_options)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 2, in _connection_for_bind
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go
    ret_value = fn(self, *arg, **kw)
                ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 1175, in _connection_for_bind
    conn = self._parent._connection_for_bind(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 2, in _connection_for_bind
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go
    ret_value = fn(self, *arg, **kw)
                ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 1189, in _connection_for_bind
    conn = bind.connect()
           ^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 3274, in connect
    return self._connection_cls(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 146, in __init__
    self._dbapi_connection = engine.raw_connection()
                             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 3298, in raw_connection
    return self.pool.connect()
           ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 449, in connect
    return _ConnectionFairy._checkout(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 1363, in _checkout
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 1301, in _checkout
    result = pool._dialect._do_ping_w_event(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 720, in _do_ping_w_event
    return self.do_ping(dbapi_connection)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/pymysql.py", line 106, in do_ping
    dbapi_connection.ping(False)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/aiomysql.py", line 188, in ping
    return self.await_(self._connection.ping(reconnect))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 494, in ping
    await self._read_ok_packet()
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 372, in _read_ok_packet
    pkt = await self._read_packet()
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 609, in _read_packet
    packet_header = await self._read_bytes(4)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 657, in _read_bytes
    data = await self._reader.readexactly(num_bytes)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/streams.py", line 750, in readexactly
    await self._wait_for_data('readexactly')
  File "/usr/local/lib/python3.11/asyncio/streams.py", line 543, in _wait_for_data
    await self._waiter
RuntimeError: Task <Task pending name='starlette.responses.StreamingResponse.__call__.<locals>.wrap' coro=<StreamingResponse.__call__.<locals>.wrap() running at /usr/local/lib/python3.11/site-packages/starlette/responses.py:266> cb=[TaskGroup._spawn.<locals>.task_done() at /usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:821]> got Future <Future pending> attached to a different loop
```

**18. ✅ `test_send_message_expired_subscription_treated_as_free`**

```
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [对话] 配额不足 | user_id=1 free_left=0
[INFO] <<< POST /api/chat/send | 200 | 4.1ms
```

**19. ✅ `test_send_message_to_nonexistent_conversation`**

```
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/chat/send | 200 | 3.5ms
```

**20. ✅ `test_upload_valid_image`**

```
[INFO] >>> POST /api/chat/upload-image | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [图片] 上传成功 | user_id=1 size=3400 url=/api/chat/uploads/214420cee1ff4a3aa418f202bb4c66bb.png
[INFO] <<< POST /api/chat/upload-image | 200 | 5.2ms
```

**21. ✅ `test_upload_unsupported_format_rejected`**

```
[INFO] >>> POST /api/chat/upload-image | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [图片] 格式不支持 | user_id=1 type=application/pdf
[INFO] <<< POST /api/chat/upload-image | 200 | 3.5ms
```

**22. ✅ `test_upload_too_large_image_rejected`**

```
[INFO] >>> POST /api/chat/upload-image | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [图片] 文件过大 | user_id=1 size=10485761
[INFO] <<< POST /api/chat/upload-image | 200 | 62.8ms
```

**23. ✅ `test_upload_too_small_image_rejected`**

```
[INFO] >>> POST /api/chat/upload-image | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [图片] 文件异常 | user_id=1 size=10
[INFO] <<< POST /api/chat/upload-image | 200 | 3.1ms
```

**24. ✅ `test_upload_unsupported_audio_format_rejected`**

```
[INFO] >>> POST /api/chat/transcribe | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/chat/transcribe | 200 | 3.1ms
```

**25. ✅ `test_upload_too_large_audio_rejected`**

```
[INFO] >>> POST /api/chat/transcribe | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/chat/transcribe | 200 | 103.1ms
```

**26. ✅ `test_feedback_like`**

```
[INFO] >>> POST /api/chat/messages/1/feedback | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [满意度] 用户反馈 | user_id=1 msg_id=1 rating=like level=satisfied
[INFO] <<< POST /api/chat/messages/1/feedback | 200 | 2.1ms
```

**27. ✅ `test_feedback_dislike`**

```
[INFO] >>> POST /api/chat/messages/1/feedback | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [满意度] 用户反馈 | user_id=1 msg_id=1 rating=dislike level=dissatisfied
[INFO] <<< POST /api/chat/messages/1/feedback | 200 | 2.0ms
```

**28. ✅ `test_feedback_invalid_rating_rejected`**

```
[INFO] >>> POST /api/chat/messages/1/feedback | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/chat/messages/1/feedback | 200 | 1.9ms
```

**29. ✅ `test_cannot_feedback_user_message`**

```
[INFO] >>> POST /api/chat/messages/1/feedback | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/chat/messages/1/feedback | 200 | 1.8ms
```

</details>

### 并发与延迟测试（并发/幂等/延迟基准）

**文件**: `test_concurrency.py` | **总数**: 10 | **通过**: 10 | **失败**: 0 | **总耗时**: 7.32s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_concurrent_redeem_same_code_only_one_succeeds` | TestConcurrentRedeemCode | ✅ passed | 1 | 2444 | 20 | 2466 |
| 2 | `test_concurrent_checkout_creates_unique_order_nos` | TestConcurrentRedeemCode | ✅ passed | 1 | 287 | 25 | 314 |
| 3 | `test_concurrent_conversation_creation` | TestConcurrentConversations | ✅ passed | 2 | 247 | 20 | 269 |
| 4 | `test_concurrent_messages_quota_not_over_deducted` | TestConcurrentQuotaDeduction | ✅ passed | 2 | 306 | 23 | 331 |
| 5 | `test_health_check_latency_under_50ms` | TestResponseLatency | ✅ passed | 2 | 7 | 25 | 33 |
| 6 | `test_user_login_latency_under_500ms` | TestResponseLatency | ✅ passed | 2 | 927 | 23 | 952 |
| 7 | `test_list_conversations_latency_with_data` | TestResponseLatency | ✅ passed | 2 | 574 | 25 | 601 |
| 8 | `test_admin_user_list_latency_with_1000_users` | TestResponseLatency | ✅ passed | 2 | 1725 | 34 | 1760 |
| 9 | `test_delete_already_deleted_conversation` | TestIdempotency | ✅ passed | 2 | 257 | 24 | 283 |
| 10 | `test_multiple_profile_updates_last_wins` | TestIdempotency | ✅ passed | 2 | 285 | 22 | 308 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_concurrent_redeem_same_code_only_one_succeeds`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[ERROR] !!! POST /api/subscribe/redeem middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/subscribe/redeem middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/subscribe/redeem middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/subscribe/redeem middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/subscribe/redeem middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/subscribe/redeem middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/subscribe/redeem middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/subscribe/redeem | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/subscribe/redeem | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/subscribe/redeem | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/subscribe/redeem | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/subscribe/redeem | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/subscribe/redeem | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/subscribe/redeem | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/subscribe/redeem middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/subscribe/redeem | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/subscribe/redeem middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/subscribe/redeem | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/subscribe/redeem middleware error: This transaction is closed
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 203, in greenlet_spawn
    result = context.switch(value)
             ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4353, in flush
    self._flush(objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4488, in _flush
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 150, in __exit__
    raise value.with_traceback(traceback)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4489, in _flush
    transaction.rollback(_capture_exception=True)
  File "<string>", line 2, in rollback
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/state_changes.py", line 103, in _go
    self._raise_for_prerequisite_state(fn.__name__, current_state)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 988, in _raise_for_prerequisite_state
    raise sa_exc.ResourceClosedError("This transaction is closed")
sqlalchemy.exc.ResourceClosedError: This transaction is closed
[ERROR] UnhandledException | POST /api/subscribe/redeem | ResourceClosedError: This transaction is closed
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 203, in greenlet_spawn
    |     result = context.switch(value)
    |              ^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4353, in flush
    |     self._flush(objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4488, in _flush
    |     with util.safe_reraise():
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 150, in __exit__
    |     raise value.with_traceback(traceback)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4489, in _flush
    |     transaction.rollback(_capture_exception=True)
    |   File "<string>", line 2, in rollback
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/state_changes.py", line 103, in _go
    |     self._raise_for_prerequisite_state(fn.__name__, current_state)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 988, in _raise_for_prerequisite_state
    |     raise sa_exc.ResourceClosedError("This transaction is closed")
    | sqlalchemy.exc.ResourceClosedError: This transaction is closed
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/subscribe_v2.py", line 245, in redeem
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 203, in greenlet_spawn
    result = context.switch(value)
             ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4353, in flush
    self._flush(objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4488, in _flush
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 150, in __exit__
    raise value.with_traceback(traceback)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4489, in _flush
    transaction.rollback(_capture_exception=True)
  File "<string>", line 2, in rollback
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/state_changes.py", line 103, in _go
    self._raise_for_prerequisite_state(fn.__name__, current_state)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 988, in _raise_for_prerequisite_state
    raise sa_exc.ResourceClosedError("This transaction is closed")
sqlalchemy.exc.ResourceClosedError: This transaction is closed
```

**2. ✅ `test_concurrent_checkout_creates_unique_order_nos`**

```
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [订阅下单] 创建成功 | user_id=1 plan_id=1 channel=wechat payment_id=1 order_no=SUB20260418144452A67AD69433AB49FD
[INFO] <<< POST /api/subscribe/checkout | 200 | 8.4ms
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [订阅下单] 创建成功 | user_id=1 plan_id=1 channel=wechat payment_id=2 order_no=SUB202604181444523A30F444A04B4753
[INFO] <<< POST /api/subscribe/checkout | 200 | 6.2ms
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [订阅下单] 创建成功 | user_id=1 plan_id=1 channel=wechat payment_id=3 order_no=SUB20260418144452B011E5AEBC2E4C77
[INFO] <<< POST /api/subscribe/checkout | 200 | 7.1ms
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [订阅下单] 创建成功 | user_id=1 plan_id=1 channel=wechat payment_id=4 order_no=SUB2026041814445204A90D768A6D4A1B
[INFO] <<< POST /api/subscribe/checkout | 200 | 9.9ms
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [订阅下单] 创建成功 | user_id=1 plan_id=1 channel=wechat payment_id=5 order_no=SUB202604181444520C7C663C0D0F4DB6
[INFO] <<< POST /api/subscribe/checkout | 200 | 6.6ms
```

**3. ✅ `test_concurrent_conversation_creation`**

```
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=1
[INFO] <<< POST /api/chat/conversations | 200 | 3.5ms
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=2
[INFO] <<< POST /api/chat/conversations | 200 | 2.8ms
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=3
[INFO] <<< POST /api/chat/conversations | 200 | 2.4ms
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=4
[INFO] <<< POST /api/chat/conversations | 200 | 2.6ms
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=5
[INFO] <<< POST /api/chat/conversations | 200 | 3.0ms
```

**4. ✅ `test_concurrent_messages_quota_not_over_deducted`**

```
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [对话] 配额不足 | user_id=1 free_left=0
[INFO] [对话] 配额不足 | user_id=1 free_left=0
[ERROR] !!! POST /api/chat/send middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/chat_v2.py", line 304, in send_message
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] !!! POST /api/chat/send middleware error: Session is already flushing
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 148, in call_next
    message = await recv_stream.receive()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/anyio/streams/memory.py", line 132, in receive
    raise EndOfStream from None
anyio.EndOfStream

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/chat_v2.py", line 304, in send_message
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/chat/send | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/chat_v2.py", line 304, in send_message
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/chat_v2.py", line 304, in send_message
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[ERROR] UnhandledException | POST /api/chat/send | InvalidRequestError: Session is already flushing
  + Exception Group Traceback (most recent call last):
  |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 76, in collapse_excgroups
  |     yield
  |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 177, in __call__
  |     async with anyio.create_task_group() as task_group:
  |   File "/usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 799, in __aexit__
  |     raise BaseExceptionGroup(
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    |     await self.app(scope, receive, _send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |   File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    |     self.gen.throw(typ, value, traceback)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    |     raise app_exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    |     await route.handle(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    |     await self.app(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/app/app/routers/chat_v2.py", line 304, in send_message
    |     await db.flush()
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    |     await greenlet_spawn(self.sync_session.flush, objects=objects)
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    |     result = context.switch(*args, **kwargs)
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    |     raise sa_exc.InvalidRequestError("Session is already flushing")
    | sqlalchemy.exc.InvalidRequestError: Session is already flushing
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 176, in __call__
    with recv_stream, send_stream, collapse_excgroups():
  File "/usr/local/lib/python3.11/contextlib.py", line 158, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/usr/local/lib/python3.11/site-packages/starlette/_utils.py", line 82, in collapse_excgroups
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 178, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/main_v2.py", line 203, in trace_and_log_middleware
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 156, in call_next
    raise app_exc
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/base.py", line 141, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/cors.py", line 85, in __call__
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "/usr/local/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "/usr/local/lib/python3.11/site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/fastapi/routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/app/routers/chat_v2.py", line 304, in send_message
    await db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 190, in greenlet_spawn
    result = context.switch(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4347, in flush
    raise sa_exc.InvalidRequestError("Session is already flushing")
sqlalchemy.exc.InvalidRequestError: Session is already flushing
[INFO] <<< POST /api/chat/send | 200 | 29.5ms
[INFO] <<< POST /api/chat/send | 200 | 29.6ms
[INFO] [对话] 发送 | user_id=1 conv_id=1 msg_len=3 has_sub=False
[INFO] <<< POST /api/chat/send | 200 | 39.3ms
```

**5. ✅ `test_health_check_latency_under_50ms`**

*(无请求日志)*

**6. ✅ `test_user_login_latency_under_500ms`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [登录] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/login | 200 | 232.7ms
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [登录] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/login | 200 | 231.1ms
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [登录] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/login | 200 | 229.9ms
```

**7. ✅ `test_list_conversations_latency_with_data`**

```
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations | 200 | 6.0ms
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations | 200 | 4.9ms
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations | 200 | 5.1ms
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations | 200 | 5.0ms
[INFO] >>> GET /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations | 200 | 5.4ms
```

**8. ✅ `test_admin_user_list_latency_with_1000_users`**

```
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/users | 200 | 8.8ms
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/users | 200 | 7.1ms
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/users | 200 | 8.2ms
```

**9. ✅ `test_delete_already_deleted_conversation`**

```
[INFO] >>> DELETE /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 删除 | user_id=1 conv_id=1
[INFO] <<< DELETE /api/chat/conversations/1 | 200 | 6.3ms
[INFO] >>> DELETE /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< DELETE /api/chat/conversations/1 | 200 | 2.4ms
```

**10. ✅ `test_multiple_profile_updates_last_wins`**

```
[INFO] >>> PUT /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> PUT /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] >>> PUT /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [个人中心] 更新信息 | user_id=1
[INFO] [个人中心] 更新信息 | user_id=1
[INFO] [个人中心] 更新信息 | user_id=1
[INFO] <<< PUT /api/auth/profile | 200 | 8.8ms
[INFO] <<< PUT /api/auth/profile | 200 | 8.2ms
[INFO] <<< PUT /api/auth/profile | 200 | 7.7ms
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/auth/profile | 200 | 1.2ms
```

</details>

### 数据持久性测试（事务/一致性/级联删除）

**文件**: `test_persistence.py` | **总数**: 14 | **通过**: 14 | **失败**: 0 | **总耗时**: 4.26s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_user_data_persists_after_create` | TestWriteThenRead | ✅ passed | 2 | 242 | 24 | 268 |
| 2 | `test_conversation_data_persists` | TestWriteThenRead | ✅ passed | 2 | 253 | 21 | 276 |
| 3 | `test_message_persists_with_correct_user` | TestWriteThenRead | ✅ passed | 1 | 245 | 28 | 275 |
| 4 | `test_api_create_conversation_persists` | TestWriteThenRead | ✅ passed | 2 | 240 | 24 | 265 |
| 5 | `test_profile_update_persists` | TestWriteThenRead | ✅ passed | 2 | 237 | 23 | 262 |
| 6 | `test_redeem_code_status_update_persists` | TestWriteThenRead | ✅ passed | 1 | 252 | 26 | 280 |
| 7 | `test_delete_conversation_removes_messages` | TestCascadeDelete | ✅ passed | 2 | 253 | 21 | 276 |
| 8 | `test_delete_conversation_removes_token_usage` | TestCascadeDelete | ✅ passed | 1 | 251 | 20 | 273 |
| 9 | `test_redeem_atomicity_free_chats_updated` | TestTransactionIntegrity | ✅ passed | 1 | 246 | 22 | 270 |
| 10 | `test_user_free_chats_not_negative` | TestTransactionIntegrity | ✅ passed | 2 | 270 | 23 | 295 |
| 11 | `test_user_id_in_messages_matches_user` | TestDataConsistency | ✅ passed | 2 | 239 | 22 | 262 |
| 12 | `test_conversation_belongs_to_correct_user` | TestDataConsistency | ✅ passed | 2 | 465 | 21 | 487 |
| 13 | `test_banned_user_status_persists_across_login` | TestDataConsistency | ✅ passed | 1 | 464 | 24 | 490 |
| 14 | `test_subscription_days_stack_correctly` | TestDataConsistency | ✅ passed | 2 | 259 | 19 | 279 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_user_data_persists_after_create`**

*(无请求日志)*

**2. ✅ `test_conversation_data_persists`**

*(无请求日志)*

**3. ✅ `test_message_persists_with_correct_user`**

*(无请求日志)*

**4. ✅ `test_api_create_conversation_persists`**

```
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=1
[INFO] <<< POST /api/chat/conversations | 200 | 3.9ms
```

**5. ✅ `test_profile_update_persists`**

```
[INFO] >>> PUT /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [个人中心] 更新信息 | user_id=1
[INFO] <<< PUT /api/auth/profile | 200 | 1.9ms
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/auth/profile | 200 | 0.9ms
```

**6. ✅ `test_redeem_code_status_update_persists`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 成功 | user_id=1 code=PERSIST001 type=chats value=5
[INFO] <<< POST /api/subscribe/redeem | 200 | 10.0ms
```

**7. ✅ `test_delete_conversation_removes_messages`**

```
[INFO] >>> DELETE /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 删除 | user_id=1 conv_id=1
[INFO] <<< DELETE /api/chat/conversations/1 | 200 | 5.9ms
```

**8. ✅ `test_delete_conversation_removes_token_usage`**

```
[INFO] >>> DELETE /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 删除 | user_id=1 conv_id=1
[INFO] <<< DELETE /api/chat/conversations/1 | 200 | 5.2ms
```

**9. ✅ `test_redeem_atomicity_free_chats_updated`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 成功 | user_id=1 code=ATOMIC001 type=chats value=8
[INFO] <<< POST /api/subscribe/redeem | 200 | 9.1ms
```

**10. ✅ `test_user_free_chats_not_negative`**

```
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [对话] 发送 | user_id=1 conv_id=1 msg_len=6 has_sub=False
[INFO] <<< POST /api/chat/send | 200 | 9.7ms
[ERROR] Exception terminating connection <AdaptedConnection <aiomysql.connection.Connection object at 0x7f45d102b750>>
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 1301, in _checkout
    result = pool._dialect._do_ping_w_event(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 720, in _do_ping_w_event
    return self.do_ping(dbapi_connection)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/pymysql.py", line 106, in do_ping
    dbapi_connection.ping(False)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/aiomysql.py", line 188, in ping
    return self.await_(self._connection.ping(reconnect))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 494, in ping
    await self._read_ok_packet()
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 372, in _read_ok_packet
    pkt = await self._read_packet()
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 609, in _read_packet
    packet_header = await self._read_bytes(4)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 657, in _read_bytes
    data = await self._reader.readexactly(num_bytes)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/streams.py", line 750, in readexactly
    await self._wait_for_data('readexactly')
  File "/usr/local/lib/python3.11/asyncio/streams.py", line 543, in _wait_for_data
    await self._waiter
RuntimeError: Task <Task pending name='starlette.responses.StreamingResponse.__call__.<locals>.wrap' coro=<StreamingResponse.__call__.<locals>.wrap() running at /usr/local/lib/python3.11/site-packages/starlette/responses.py:266> cb=[TaskGroup._spawn.<locals>.task_done() at /usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:821]> got Future <Future pending> attached to a different loop

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 374, in _close_connection
    self._dialect.do_terminate(connection)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/aiomysql.py", line 312, in do_terminate
    dbapi_connection.terminate()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/aiomysql.py", line 210, in terminate
    self._connection.close()
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 339, in close
    self._writer.transport.close()
  File "/usr/local/lib/python3.11/asyncio/selector_events.py", line 864, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/usr/local/lib/python3.11/asyncio/base_events.py", line 762, in call_soon
    self._check_closed()
  File "/usr/local/lib/python3.11/asyncio/base_events.py", line 520, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
[ERROR] [对话] AI响应异常 | user_id=1 conv_id=1
Traceback (most recent call last):
  File "/app/app/routers/chat_v2.py", line 352, in event_stream
    await sse_db.flush()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/ext/asyncio/session.py", line 802, in flush
    await greenlet_spawn(self.sync_session.flush, objects=objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn
    result = context.throw(*sys.exc_info())
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4353, in flush
    self._flush(objects)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4488, in _flush
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 4449, in _flush
    flush_context.execute()
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/unitofwork.py", line 466, in execute
    rec.execute(self)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/unitofwork.py", line 642, in execute
    util.preloaded.orm_persistence.save_obj(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/persistence.py", line 60, in save_obj
    for (
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/persistence.py", line 223, in _organize_states_for_save
    for state, dict_, mapper, connection in _connections_for_states(
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/persistence.py", line 1753, in _connections_for_states
    connection = uowtransaction.transaction.connection(base_mapper)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 2, in connection
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go
    ret_value = fn(self, *arg, **kw)
                ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 1039, in connection
    return self._connection_for_bind(bind, execution_options)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 2, in _connection_for_bind
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go
    ret_value = fn(self, *arg, **kw)
                ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 1175, in _connection_for_bind
    conn = self._parent._connection_for_bind(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 2, in _connection_for_bind
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/state_changes.py", line 139, in _go
    ret_value = fn(self, *arg, **kw)
                ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/orm/session.py", line 1189, in _connection_for_bind
    conn = bind.connect()
           ^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 3274, in connect
    return self._connection_cls(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 146, in __init__
    self._dbapi_connection = engine.raw_connection()
                             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 3298, in raw_connection
    return self.pool.connect()
           ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 449, in connect
    return _ConnectionFairy._checkout(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 1363, in _checkout
    with util.safe_reraise():
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/langhelpers.py", line 146, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/pool/base.py", line 1301, in _checkout
    result = pool._dialect._do_ping_w_event(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 720, in _do_ping_w_event
    return self.do_ping(dbapi_connection)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/pymysql.py", line 106, in do_ping
    dbapi_connection.ping(False)
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/dialects/mysql/aiomysql.py", line 188, in ping
    return self.await_(self._connection.ping(reconnect))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 494, in ping
    await self._read_ok_packet()
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 372, in _read_ok_packet
    pkt = await self._read_packet()
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 609, in _read_packet
    packet_header = await self._read_bytes(4)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/aiomysql/connection.py", line 657, in _read_bytes
    data = await self._reader.readexactly(num_bytes)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/asyncio/streams.py", line 750, in readexactly
    await self._wait_for_data('readexactly')
  File "/usr/local/lib/python3.11/asyncio/streams.py", line 543, in _wait_for_data
    await self._waiter
RuntimeError: Task <Task pending name='starlette.responses.StreamingResponse.__call__.<locals>.wrap' coro=<StreamingResponse.__call__.<locals>.wrap() running at /usr/local/lib/python3.11/site-packages/starlette/responses.py:266> cb=[TaskGroup._spawn.<locals>.task_done() at /usr/local/lib/python3.11/site-packages/anyio/_backends/_asyncio.py:821]> got Future <Future pending> attached to a different loop
[INFO] >>> POST /api/chat/send | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [对话] 配额不足 | user_id=1 free_left=0
[INFO] <<< POST /api/chat/send | 200 | 3.3ms
```

**11. ✅ `test_user_id_in_messages_matches_user`**

*(无请求日志)*

**12. ✅ `test_conversation_belongs_to_correct_user`**

*(无请求日志)*

**13. ✅ `test_banned_user_status_persists_across_login`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/login | 200 | 230.7ms
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=账号已被封禁
[INFO] <<< GET /api/auth/profile | 200 | 1.8ms
```

**14. ✅ `test_subscription_days_stack_correctly`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 成功 | user_id=1 code=STACK001 type=days value=10
[INFO] <<< POST /api/subscribe/redeem | 200 | 8.6ms
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 成功 | user_id=1 code=STACK002 type=days value=20
[INFO] <<< POST /api/subscribe/redeem | 200 | 8.3ms
```

</details>

### 系统安全测试（越权/注入/认证）

**文件**: `test_security.py` | **总数**: 28 | **通过**: 28 | **失败**: 0 | **总耗时**: 7.03s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_no_token_returns_1002` | TestJWTSecurity | ✅ passed | 1 | 2 | 19 | 22 |
| 2 | `test_malformed_token` | TestJWTSecurity | ✅ passed | 2 | 2 | 23 | 27 |
| 3 | `test_wrong_secret_token` | TestJWTSecurity | ✅ passed | 1 | 6 | 19 | 26 |
| 4 | `test_expired_token` | TestJWTSecurity | ✅ passed | 1 | 2 | 17 | 21 |
| 5 | `test_refresh_token_cannot_access_protected_routes` | TestJWTSecurity | ✅ passed | 1 | 233 | 20 | 254 |
| 6 | `test_admin_token_cannot_access_user_routes` | TestJWTSecurity | ✅ passed | 1 | 235 | 23 | 259 |
| 7 | `test_user_token_cannot_access_admin_routes` | TestJWTSecurity | ✅ passed | 2 | 234 | 22 | 257 |
| 8 | `test_forged_user_id_in_token` | TestJWTSecurity | ✅ passed | 1 | 4 | 21 | 26 |
| 9 | `test_bearer_prefix_required` | TestJWTSecurity | ✅ passed | 2 | 234 | 25 | 260 |
| 10 | `test_user_cannot_read_other_users_conversation` | TestIDOR | ✅ passed | 1 | 470 | 22 | 493 |
| 11 | `test_user_cannot_delete_other_users_conversation` | TestIDOR | ✅ passed | 1 | 472 | 23 | 497 |
| 12 | `test_user_cannot_rename_other_users_conversation` | TestIDOR | ✅ passed | 2 | 466 | 21 | 489 |
| 13 | `test_user_cannot_feedback_other_users_message` | TestIDOR | ✅ passed | 1 | 470 | 18 | 490 |
| 14 | `test_phone_masked_in_profile` | TestSensitiveDataMasking | ✅ passed | 1 | 231 | 18 | 250 |
| 15 | `test_email_masked_in_profile` | TestSensitiveDataMasking | ✅ passed | 1 | 232 | 21 | 254 |
| 16 | `test_llm_api_key_not_in_list_response` | TestSensitiveDataMasking | ✅ passed | 2 | 242 | 21 | 265 |
| 17 | `test_password_hash_not_in_user_response` | TestSensitiveDataMasking | ✅ passed | 2 | 233 | 27 | 262 |
| 18 | `test_xss_in_nickname_stored_safely` | TestInjectionDefense | ✅ passed | 2 | 238 | 21 | 260 |
| 19 | `test_sql_injection_in_login` | TestInjectionDefense | ✅ passed | 2 | 13 | 20 | 34 |
| 20 | `test_sql_injection_in_conversation_title` | TestInjectionDefense | ✅ passed | 1 | 236 | 21 | 258 |
| 21 | `test_extremely_long_input_handled` | TestInjectionDefense | ✅ passed | 2 | 252 | 19 | 273 |
| 22 | `test_honeypot_website_field_returns_fake_success` | TestHoneypot | ✅ passed | 2 | 2 | 18 | 22 |
| 23 | `test_fast_form_submission_rejected` | TestHoneypot | ✅ passed | 1 | 2 | 21 | 24 |
| 24 | `test_normal_form_submission_not_rejected` | TestHoneypot | ✅ passed | 2 | 244 | 24 | 269 |
| 25 | `test_normal_admin_cannot_unlock_accounts` | TestAdminPrivilegeEscalation | ✅ passed | 2 | 233 | 22 | 257 |
| 26 | `test_unauthenticated_cannot_access_admin_api` | TestAdminPrivilegeEscalation | ✅ passed | 1 | 4 | 21 | 27 |
| 27 | `test_admin_login_brute_force_lockout` | TestRateLimiting | ✅ passed | 2 | 1392 | 22 | 1416 |
| 28 | `test_ip_rate_limit_on_verify_code` | TestRateLimiting | ✅ passed | 2 | 15 | 19 | 36 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_no_token_returns_1002`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=未登录
[INFO] <<< GET /api/auth/profile | 200 | 1.0ms
```

**2. ✅ `test_malformed_token`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=Token 无效或已过期
[INFO] <<< GET /api/auth/profile | 200 | 1.2ms
```

**3. ✅ `test_wrong_secret_token`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=Token 无效或已过期
[INFO] <<< GET /api/auth/profile | 200 | 5.1ms
```

**4. ✅ `test_expired_token`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=Token 无效或已过期
[INFO] <<< GET /api/auth/profile | 200 | 1.2ms
```

**5. ✅ `test_refresh_token_cannot_access_protected_routes`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=Token 无效或已过期
[INFO] <<< GET /api/auth/profile | 200 | 1.3ms
```

**6. ✅ `test_admin_token_cannot_access_user_routes`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=Token 无效
[INFO] <<< GET /api/auth/profile | 200 | 1.8ms
```

**7. ✅ `test_user_token_cannot_access_admin_routes`**

```
[INFO] >>> GET /api/admin/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/admin/profile | code=1003 msg=权限不足
[INFO] <<< GET /api/admin/profile | 200 | 1.5ms
```

**8. ✅ `test_forged_user_id_in_token`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=账号不存在或已注销
[INFO] <<< GET /api/auth/profile | 200 | 2.7ms
```

**9. ✅ `test_bearer_prefix_required`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/auth/profile | code=1002 msg=未登录
[INFO] <<< GET /api/auth/profile | 200 | 1.1ms
```

**10. ✅ `test_user_cannot_read_other_users_conversation`**

```
[INFO] >>> GET /api/chat/conversations/1/messages | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/chat/conversations/1/messages | 200 | 2.7ms
```

**11. ✅ `test_user_cannot_delete_other_users_conversation`**

```
[INFO] >>> DELETE /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< DELETE /api/chat/conversations/1 | 200 | 1.8ms
```

**12. ✅ `test_user_cannot_rename_other_users_conversation`**

```
[INFO] >>> PUT /api/chat/conversations/1 | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/chat/conversations/1 | 200 | 1.9ms
```

**13. ✅ `test_user_cannot_feedback_other_users_message`**

```
[INFO] >>> POST /api/chat/messages/1/feedback | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/chat/messages/1/feedback | 200 | 1.6ms
```

**14. ✅ `test_phone_masked_in_profile`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/auth/profile | 200 | 1.2ms
```

**15. ✅ `test_email_masked_in_profile`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/auth/profile | 200 | 1.2ms
```

**16. ✅ `test_llm_api_key_not_in_list_response`**

```
[INFO] >>> GET /api/admin/llm-providers | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/admin/llm-providers | 200 | 5.3ms
```

**17. ✅ `test_password_hash_not_in_user_response`**

```
[INFO] >>> GET /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/auth/profile | 200 | 1.1ms
```

**18. ✅ `test_xss_in_nickname_stored_safely`**

```
[INFO] >>> PUT /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [个人中心] 更新信息 | user_id=1
[INFO] <<< PUT /api/auth/profile | 200 | 2.5ms
```

**19. ✅ `test_sql_injection_in_login`**

```
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/login | 200 | 3.3ms
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/login | 200 | 2.4ms
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/login | 200 | 2.2ms
[INFO] >>> POST /api/auth/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/login | 200 | 2.0ms
```

**20. ✅ `test_sql_injection_in_conversation_title`**

```
[INFO] >>> POST /api/chat/conversations | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [会话] 新建 | user_id=1 conv_id=1
[INFO] <<< POST /api/chat/conversations | 200 | 3.6ms
```

**21. ✅ `test_extremely_long_input_handled`**

```
[INFO] >>> PUT /api/auth/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< PUT /api/auth/profile | 200 | 2.0ms
```

**22. ✅ `test_honeypot_website_field_returns_fake_success`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [注册] 蜜罐触发 | ip=127.0.0.1
[INFO] <<< POST /api/auth/register | 200 | 1.0ms
```

**23. ✅ `test_fast_form_submission_rejected`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [注册] 提交过快 | ip=127.0.0.1 ft=500ms
[INFO] <<< POST /api/auth/register | 200 | 0.9ms
```

**24. ✅ `test_normal_form_submission_not_rejected`**

```
[INFO] >>> POST /api/auth/register | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [注册] 成功 | user_id=1 ip=127.0.0.1
[INFO] <<< POST /api/auth/register | 200 | 232.6ms
```

**25. ✅ `test_normal_admin_cannot_unlock_accounts`**

```
[INFO] >>> POST /api/admin/unlock-admin | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | POST /api/admin/unlock-admin | code=1003 msg=仅超级管理员可操作
[INFO] <<< POST /api/admin/unlock-admin | 200 | 1.9ms
```

**26. ✅ `test_unauthenticated_cannot_access_admin_api`**

```
[INFO] >>> GET /api/admin/profile | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/admin/profile | code=1002 msg=未登录
[INFO] <<< GET /api/admin/profile | 200 | 1.0ms
[INFO] >>> GET /api/admin/users | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/admin/users | code=1002 msg=未登录
[INFO] <<< GET /api/admin/users | 200 | 0.7ms
[INFO] >>> GET /api/admin/llm-providers | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/admin/llm-providers | code=1002 msg=未登录
[INFO] <<< GET /api/admin/llm-providers | 200 | 0.7ms
```

**27. ✅ `test_admin_login_brute_force_lockout`**

```
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=locktest ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 230.6ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=locktest ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 230.4ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=locktest ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 231.0ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=locktest ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 229.3ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 认证失败 | username=locktest ip=127.0.0.1
[WARNING] [管理登录] 账号触发锁定 | username=locktest fail_count=5 lock=900s ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 232.4ms
[INFO] >>> POST /api/admin/login | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] [管理登录] 账号已锁定 | username=locktest ttl=900s ip=127.0.0.1
[INFO] <<< POST /api/admin/login | 200 | 1.4ms
```

**28. ✅ `test_ip_rate_limit_on_verify_code`**

```
[INFO] >>> POST /api/auth/send-code | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/auth/send-code | 200 | 5.0ms
```

</details>

### 订阅模块（套餐/下单/兑换码/订单）

**文件**: `test_subscribe.py` | **总数**: 24 | **通过**: 24 | **失败**: 0 | **总耗时**: 5.08s

| # | 测试用例 | 测试类 | 结果 | setup(ms) | call(ms) | teardown(ms) | 合计(ms) |
|---|---------|--------|------|-----------|----------|--------------|---------|
| 1 | `test_subscribe_info_free_user` | TestSubscribeInfo | ✅ passed | 1 | 237 | 21 | 260 |
| 2 | `test_subscribe_info_subscribed_user` | TestSubscribeInfo | ✅ passed | 1 | 244 | 20 | 265 |
| 3 | `test_subscribe_info_requires_auth` | TestSubscribeInfo | ✅ passed | 1 | 2 | 20 | 24 |
| 4 | `test_catalog_returns_active_plans_only` | TestSubscribeCatalog | ✅ passed | 2 | 246 | 155 | 402 |
| 5 | `test_catalog_returns_active_channels_only` | TestSubscribeCatalog | ✅ passed | 2 | 243 | 22 | 267 |
| 6 | `test_checkout_creates_pending_payment` | TestCheckout | ✅ passed | 2 | 244 | 19 | 266 |
| 7 | `test_checkout_inactive_plan_rejected` | TestCheckout | ✅ passed | 2 | 242 | 21 | 265 |
| 8 | `test_checkout_inactive_channel_rejected` | TestCheckout | ✅ passed | 1 | 243 | 22 | 267 |
| 9 | `test_checkout_nonexistent_plan_rejected` | TestCheckout | ✅ passed | 2 | 247 | 19 | 268 |
| 10 | `test_checkout_order_no_is_unique` | TestCheckout | ✅ passed | 1 | 250 | 22 | 274 |
| 11 | `test_redeem_chats_code_increases_free_chats` | TestRedeem | ✅ passed | 2 | 244 | 19 | 264 |
| 12 | `test_redeem_days_code_extends_subscription` | TestRedeem | ✅ passed | 1 | 242 | 23 | 267 |
| 13 | `test_redeem_days_stacks_on_existing_subscription` | TestRedeem | ✅ passed | 1 | 240 | 19 | 260 |
| 14 | `test_redeem_used_code_rejected` | TestRedeem | ✅ passed | 2 | 238 | 20 | 260 |
| 15 | `test_redeem_expired_code_rejected` | TestRedeem | ✅ passed | 1 | 240 | 23 | 264 |
| 16 | `test_redeem_nonexistent_code_rejected` | TestRedeem | ✅ passed | 2 | 234 | 21 | 256 |
| 17 | `test_redeem_marks_code_as_used` | TestRedeem | ✅ passed | 1 | 241 | 21 | 264 |
| 18 | `test_redeem_free_plan_upgraded_to_monthly_on_days_code` | TestRedeem | ✅ passed | 2 | 243 | 21 | 265 |
| 19 | `test_list_orders_only_subscribe_type` | TestSubscribeOrders | ✅ passed | 1 | 248 | 19 | 268 |
| 20 | `test_apply_subscription_from_scratch` | TestSubscriptionService | ✅ passed | 1 | 0 | 18 | 20 |
| 21 | `test_apply_subscription_stacks_on_existing` | TestSubscriptionService | ✅ passed | 1 | 0 | 18 | 19 |
| 22 | `test_resolve_checkout_url_substitutes_placeholders` | TestSubscriptionService | ✅ passed | 1 | 0 | 21 | 22 |
| 23 | `test_create_order_no_is_unique` | TestSubscriptionService | ✅ passed | 1 | 1 | 21 | 22 |
| 24 | `test_create_order_no_starts_with_sub` | TestSubscriptionService | ✅ passed | 1 | 0 | 74 | 75 |

<details>
<summary>展开查看每个测试的请求日志</summary>

**1. ✅ `test_subscribe_info_free_user`**

```
[INFO] >>> GET /api/subscribe/info | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/subscribe/info | 200 | 4.5ms
```

**2. ✅ `test_subscribe_info_subscribed_user`**

```
[INFO] >>> GET /api/subscribe/info | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/subscribe/info | 200 | 2.8ms
```

**3. ✅ `test_subscribe_info_requires_auth`**

```
[INFO] >>> GET /api/subscribe/info | ip=127.0.0.1 ua=python-httpx/0.28.1
[WARNING] BizException | GET /api/subscribe/info | code=1002 msg=未登录
[INFO] <<< GET /api/subscribe/info | 200 | 1.0ms
```

**4. ✅ `test_catalog_returns_active_plans_only`**

```
[INFO] >>> GET /api/subscribe/catalog | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/subscribe/catalog | 200 | 6.9ms
```

**5. ✅ `test_catalog_returns_active_channels_only`**

```
[INFO] >>> GET /api/subscribe/catalog | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/subscribe/catalog | 200 | 3.9ms
```

**6. ✅ `test_checkout_creates_pending_payment`**

```
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [订阅下单] 创建成功 | user_id=1 plan_id=1 channel=wechat payment_id=1 order_no=SUB2026041814450984CD1165D10F4D98
[INFO] <<< POST /api/subscribe/checkout | 200 | 6.5ms
```

**7. ✅ `test_checkout_inactive_plan_rejected`**

```
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/subscribe/checkout | 200 | 3.6ms
```

**8. ✅ `test_checkout_inactive_channel_rejected`**

```
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/subscribe/checkout | 200 | 4.7ms
```

**9. ✅ `test_checkout_nonexistent_plan_rejected`**

```
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< POST /api/subscribe/checkout | 200 | 3.5ms
```

**10. ✅ `test_checkout_order_no_is_unique`**

```
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [订阅下单] 创建成功 | user_id=1 plan_id=1 channel=wechat payment_id=1 order_no=SUB20260418144510194946A18F734764
[INFO] <<< POST /api/subscribe/checkout | 200 | 6.0ms
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [订阅下单] 创建成功 | user_id=1 plan_id=1 channel=wechat payment_id=2 order_no=SUB20260418144510648C16C3B32545F6
[INFO] <<< POST /api/subscribe/checkout | 200 | 5.6ms
```

**11. ✅ `test_redeem_chats_code_increases_free_chats`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 成功 | user_id=1 code=CHAT10 type=chats value=10
[INFO] <<< POST /api/subscribe/redeem | 200 | 7.6ms
```

**12. ✅ `test_redeem_days_code_extends_subscription`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 成功 | user_id=1 code=DAYS30 type=days value=30
[INFO] <<< POST /api/subscribe/redeem | 200 | 7.9ms
```

**13. ✅ `test_redeem_days_stacks_on_existing_subscription`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 成功 | user_id=1 code=DAYS10 type=days value=10
[INFO] <<< POST /api/subscribe/redeem | 200 | 7.1ms
```

**14. ✅ `test_redeem_used_code_rejected`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 无效兑换码 | user_id=1 code=USED001
[INFO] <<< POST /api/subscribe/redeem | 200 | 3.6ms
```

**15. ✅ `test_redeem_expired_code_rejected`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 无效兑换码 | user_id=1 code=EXP001
[INFO] <<< POST /api/subscribe/redeem | 200 | 3.7ms
```

**16. ✅ `test_redeem_nonexistent_code_rejected`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 无效兑换码 | user_id=1 code=NOTEXIST
[INFO] <<< POST /api/subscribe/redeem | 200 | 3.4ms
```

**17. ✅ `test_redeem_marks_code_as_used`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 成功 | user_id=1 code=MARK001 type=chats value=10
[INFO] <<< POST /api/subscribe/redeem | 200 | 6.8ms
```

**18. ✅ `test_redeem_free_plan_upgraded_to_monthly_on_days_code`**

```
[INFO] >>> POST /api/subscribe/redeem | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [兑换] 成功 | user_id=1 code=UPGRADE30 type=days value=30
[INFO] <<< POST /api/subscribe/redeem | 200 | 7.5ms
```

**19. ✅ `test_list_orders_only_subscribe_type`**

```
[INFO] >>> POST /api/subscribe/checkout | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] [订阅下单] 创建成功 | user_id=1 plan_id=1 channel=wechat payment_id=1 order_no=SUB20260418144513DD46D3CD84134451
[INFO] <<< POST /api/subscribe/checkout | 200 | 6.0ms
[INFO] >>> GET /api/subscribe/orders | ip=127.0.0.1 ua=python-httpx/0.28.1
[INFO] <<< GET /api/subscribe/orders | 200 | 3.7ms
```

**20. ✅ `test_apply_subscription_from_scratch`**

*(无请求日志)*

**21. ✅ `test_apply_subscription_stacks_on_existing`**

*(无请求日志)*

**22. ✅ `test_resolve_checkout_url_substitutes_placeholders`**

*(无请求日志)*

**23. ✅ `test_create_order_no_is_unique`**

*(无请求日志)*

**24. ✅ `test_create_order_no_starts_with_sub`**

*(无请求日志)*

</details>

## 四、耗时 TOP 20 用例

> 单用例从 setup 到 teardown 全程耗时

| 排名 | 测试用例 | 模块 | 总耗时(ms) | call(ms) |
|------|---------|------|------------|---------|
| 1 | ✅ `test_concurrent_redeem_same_code_only_one_succeeds` | `test_concurrency.py` | 2466 | 2444 |
| 2 | ✅ `test_admin_login_success_clears_fail_count` | `test_admin_auth.py` | 2131 | 2107 |
| 3 | ✅ `test_admin_user_list_latency_with_1000_users` | `test_concurrency.py` | 1760 | 1725 |
| 4 | ✅ `test_admin_login_success` | `test_admin_auth.py` | 1515 | 531 |
| 5 | ✅ `test_pagination_works` | `test_admin_users.py` | 1427 | 1404 |
| 6 | ✅ `test_admin_login_lockout_after_5_failures` | `test_admin_auth.py` | 1423 | 1399 |
| 7 | ✅ `test_admin_login_brute_force_lockout` | `test_security.py` | 1416 | 1392 |
| 8 | ✅ `test_user_login_latency_under_500ms` | `test_concurrency.py` | 952 | 927 |
| 9 | ✅ `test_batch_subscribe_override` | `test_admin_users.py` | 741 | 702 |
| 10 | ✅ `test_list_users` | `test_admin_users.py` | 732 | 709 |
| 11 | ✅ `test_search_users_by_keyword` | `test_admin_users.py` | 730 | 706 |
| 12 | ✅ `test_filter_users_by_status` | `test_admin_users.py` | 722 | 700 |
| 13 | ✅ `test_change_password_success` | `test_admin_auth.py` | 712 | 683 |
| 14 | ✅ `test_change_password_success` | `test_auth.py` | 711 | 686 |
| 15 | ✅ `test_batch_import_limit_500_words` | `test_admin_llm_and_words.py` | 690 | 663 |
| 16 | ✅ `test_list_conversations_latency_with_data` | `test_concurrency.py` | 601 | 574 |
| 17 | ✅ `test_update_user_nickname` | `test_admin_users.py` | 505 | 480 |
| 18 | ✅ `test_list_conversations_only_own` | `test_chat.py` | 498 | 473 |
| 19 | ✅ `test_user_cannot_delete_other_users_conversation` | `test_security.py` | 497 | 472 |
| 20 | ✅ `test_admin_login_lockout_tier_2_at_10_failures` | `test_admin_auth.py` | 495 | 468 |

## 五、安全测试专项

### 管理员权限提升防护

| 测试用例 | 结果 | call耗时(ms) |
|---------|------|-------------|
| `test_normal_admin_cannot_unlock_accounts` | ✅ | 233 |
| `test_unauthenticated_cannot_access_admin_api` | ✅ | 4 |

### 蜜罐机制（爬虫/机器人检测）

| 测试用例 | 结果 | call耗时(ms) |
|---------|------|-------------|
| `test_honeypot_website_field_returns_fake_success` | ✅ | 2 |
| `test_fast_form_submission_rejected` | ✅ | 2 |
| `test_normal_form_submission_not_rejected` | ✅ | 244 |

### 水平越权（IDOR）防护

| 测试用例 | 结果 | call耗时(ms) |
|---------|------|-------------|
| `test_user_cannot_read_other_users_conversation` | ✅ | 470 |
| `test_user_cannot_delete_other_users_conversation` | ✅ | 472 |
| `test_user_cannot_rename_other_users_conversation` | ✅ | 466 |
| `test_user_cannot_feedback_other_users_message` | ✅ | 470 |

### 注入攻击防护（SQL/XSS/特殊字符）

| 测试用例 | 结果 | call耗时(ms) |
|---------|------|-------------|
| `test_xss_in_nickname_stored_safely` | ✅ | 238 |
| `test_sql_injection_in_login` | ✅ | 13 |
| `test_sql_injection_in_conversation_title` | ✅ | 236 |
| `test_extremely_long_input_handled` | ✅ | 252 |

### JWT Token 安全（伪造/篡改/过期/算法混淆）

| 测试用例 | 结果 | call耗时(ms) |
|---------|------|-------------|
| `test_no_token_returns_1002` | ✅ | 2 |
| `test_malformed_token` | ✅ | 2 |
| `test_wrong_secret_token` | ✅ | 6 |
| `test_expired_token` | ✅ | 2 |
| `test_refresh_token_cannot_access_protected_routes` | ✅ | 233 |
| `test_admin_token_cannot_access_user_routes` | ✅ | 235 |
| `test_user_token_cannot_access_admin_routes` | ✅ | 234 |
| `test_forged_user_id_in_token` | ✅ | 4 |
| `test_bearer_prefix_required` | ✅ | 234 |

### 频率限制（暴力破解/IP封锁）

| 测试用例 | 结果 | call耗时(ms) |
|---------|------|-------------|
| `test_admin_login_brute_force_lockout` | ✅ | 1392 |
| `test_ip_rate_limit_on_verify_code` | ✅ | 15 |

### 敏感数据脱敏

| 测试用例 | 结果 | call耗时(ms) |
|---------|------|-------------|
| `test_phone_masked_in_profile` | ✅ | 231 |
| `test_email_masked_in_profile` | ✅ | 232 |
| `test_llm_api_key_not_in_list_response` | ✅ | 242 |
| `test_password_hash_not_in_user_response` | ✅ | 233 |

## 六、测试环境

| 项目 | 说明 |
|------|------|
| 测试框架 | pytest 8.x + pytest-asyncio |
| HTTP客户端 | httpx.AsyncClient + ASGITransport |
| 数据库 | SQLite in-memory（StaticPool）|
| Redis | fakeredis.aioredis + 自定义Lua脚本支持 |
| 应用框架 | FastAPI + SQLAlchemy 2.x async |
| 运行环境 | Docker 容器 abaojie-backend |
| Python | 3.11+ |

---

*详细报告，涵盖 **218** 个测试用例每条的 setup/call/teardown 耗时及请求日志，通过率 **100%**。*