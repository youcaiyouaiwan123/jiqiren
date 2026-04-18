# jiqiren AI客服系统 — 完整测试报告

> 生成时间：2026-04-18 22:49:42

## 一、执行摘要

| 指标 | 数值 |
|------|------|
| 测试总数 | **218** |
| 通过 | **218** ✅ |
| 失败 | **0** |
| 错误 | **0** |
| 通过率 | **100.0%** |
| 总耗时 | **71.3s** |
| 测试文件 | **10** |

**测试结论：✅ 全部通过**

## 二、模块测试汇总

| 模块 | 描述 | 总数 | 通过 | 失败 | 通过率 |
|------|------|------|------|------|--------|
| `test_admin_auth.py` | 管理员认证模块（登录/锁定/IP限流） | 18 | 18 | 0 | ✅ 100% |
| `test_admin_llm_and_words.py` | 管理员LLM配置与敏感词模块 | 19 | 19 | 0 | ✅ 100% |
| `test_admin_users.py` | 管理员用户管理模块 | 19 | 19 | 0 | ✅ 100% |
| `test_auth.py` | 认证模块（注册/登录/Profile/验证码） | 26 | 26 | 0 | ✅ 100% |
| `test_bugs.py` | Bug回归与边界条件测试 | 31 | 31 | 0 | ✅ 100% |
| `test_chat.py` | 对话模块（会话/消息/图片上传/反馈） | 29 | 29 | 0 | ✅ 100% |
| `test_concurrency.py` | 并发与延迟测试（并发/幂等/延迟基准） | 10 | 10 | 0 | ✅ 100% |
| `test_persistence.py` | 数据持久性测试（事务/一致性/级联删除） | 14 | 14 | 0 | ✅ 100% |
| `test_security.py` | 系统安全测试（越权/注入/认证） | 28 | 28 | 0 | ✅ 100% |
| `test_subscribe.py` | 订阅模块（套餐/下单/兑换码/订单） | 24 | 24 | 0 | ✅ 100% |

## 三、各模块详细测试结果

### 管理员认证模块（登录/锁定/IP限流）

**文件**: `test_admin_auth.py` | **总数**: 18 | **通过**: 18 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_admin_login_success` | TestAdminLogin | ✅ passed | 0 |
| 2 | `test_admin_login_wrong_password` | TestAdminLogin | ✅ passed | 0 |
| 3 | `test_admin_login_nonexistent_user` | TestAdminLogin | ✅ passed | 0 |
| 4 | `test_admin_login_lockout_after_5_failures` | TestAdminLogin | ✅ passed | 0 |
| 5 | `test_admin_login_success_clears_fail_count` | TestAdminLogin | ✅ passed | 0 |
| 6 | `test_admin_login_lockout_tier_2_at_10_failures` | TestAdminLogin | ✅ passed | 0 |
| 7 | `test_admin_ip_rate_limit` | TestAdminLogin | ✅ passed | 0 |
| 8 | `test_admin_refresh_token` | TestAdminTokenRefresh | ✅ passed | 0 |
| 9 | `test_admin_refresh_with_user_token_rejected` | TestAdminTokenRefresh | ✅ passed | 0 |
| 10 | `test_admin_profile_returns_info` | TestAdminProfile | ✅ passed | 0 |
| 11 | `test_admin_profile_no_password_returned` | TestAdminProfile | ✅ passed | 0 |
| 12 | `test_change_password_success` | TestAdminChangePassword | ✅ passed | 0 |
| 13 | `test_change_password_wrong_old_rejected` | TestAdminChangePassword | ✅ passed | 0 |
| 14 | `test_change_password_same_as_old_rejected` | TestAdminChangePassword | ✅ passed | 0 |
| 15 | `test_admin_password_complexity_min_length` | TestAdminChangePassword | ✅ passed | 0 |
| 16 | `test_admin_password_must_have_special_char` | TestAdminChangePassword | ✅ passed | 0 |
| 17 | `test_super_admin_can_unlock` | TestAdminUnlock | ✅ passed | 0 |
| 18 | `test_normal_admin_cannot_unlock` | TestAdminUnlock | ✅ passed | 0 |

### 管理员LLM配置与敏感词模块

**文件**: `test_admin_llm_and_words.py` | **总数**: 19 | **通过**: 19 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_create_llm_provider` | TestLlmProviderCRUD | ✅ passed | 0 |
| 2 | `test_create_invalid_provider_rejected` | TestLlmProviderCRUD | ✅ passed | 0 |
| 3 | `test_list_llm_providers` | TestLlmProviderCRUD | ✅ passed | 0 |
| 4 | `test_api_key_not_in_list_response` | TestLlmProviderCRUD | ✅ passed | 0 |
| 5 | `test_update_llm_provider` | TestLlmProviderCRUD | ✅ passed | 0 |
| 6 | `test_update_nonexistent_llm_returns_1004` | TestLlmProviderCRUD | ✅ passed | 0 |
| 7 | `test_delete_llm_provider` | TestLlmProviderCRUD | ✅ passed | 0 |
| 8 | `test_only_one_default_at_a_time` | TestLlmDefaultProvider | ✅ passed | 0 |
| 9 | `test_cannot_set_inactive_as_default` | TestLlmDefaultProvider | ✅ passed | 0 |
| 10 | `test_cannot_create_inactive_default` | TestLlmDefaultProvider | ✅ passed | 0 |
| 11 | `test_disabling_default_clears_is_default` | TestLlmDefaultProvider | ✅ passed | 0 |
| 12 | `test_create_banned_word` | TestBannedWords | ✅ passed | 0 |
| 13 | `test_list_banned_words` | TestBannedWords | ✅ passed | 0 |
| 14 | `test_search_banned_words_by_keyword` | TestBannedWords | ✅ passed | 0 |
| 15 | `test_batch_import_banned_words` | TestBannedWords | ✅ passed | 0 |
| 16 | `test_batch_import_skips_duplicates` | TestBannedWords | ✅ passed | 0 |
| 17 | `test_batch_import_limit_500_words` | TestBannedWords | ✅ passed | 0 |
| 18 | `test_update_banned_word` | TestBannedWords | ✅ passed | 0 |
| 19 | `test_delete_banned_word` | TestBannedWords | ✅ passed | 0 |

### 管理员用户管理模块

**文件**: `test_admin_users.py` | **总数**: 19 | **通过**: 19 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_list_users` | TestAdminUserList | ✅ passed | 0 |
| 2 | `test_search_users_by_keyword` | TestAdminUserList | ✅ passed | 0 |
| 3 | `test_filter_users_by_status` | TestAdminUserList | ✅ passed | 0 |
| 4 | `test_pagination_works` | TestAdminUserList | ✅ passed | 0 |
| 5 | `test_create_user_success` | TestAdminCreateUser | ✅ passed | 0 |
| 6 | `test_create_user_duplicate_phone_rejected` | TestAdminCreateUser | ✅ passed | 0 |
| 7 | `test_create_user_invalid_subscribe_plan_rejected` | TestAdminCreateUser | ✅ passed | 0 |
| 8 | `test_update_user_nickname` | TestAdminUpdateUser | ✅ passed | 0 |
| 9 | `test_update_nonexistent_user` | TestAdminUpdateUser | ✅ passed | 0 |
| 10 | `test_ban_user` | TestAdminUserStatus | ✅ passed | 0 |
| 11 | `test_unban_user` | TestAdminUserStatus | ✅ passed | 0 |
| 12 | `test_invalid_status_rejected` | TestAdminUserStatus | ✅ passed | 0 |
| 13 | `test_update_subscription` | TestAdminSubscriptionManagement | ✅ passed | 0 |
| 14 | `test_invalid_subscribe_plan_rejected` | TestAdminSubscriptionManagement | ✅ passed | 0 |
| 15 | `test_batch_subscribe_override` | TestAdminSubscriptionManagement | ✅ passed | 0 |
| 16 | `test_batch_subscribe_add_days` | TestAdminSubscriptionManagement | ✅ passed | 0 |
| 17 | `test_set_trial_chats` | TestAdminTrialChats | ✅ passed | 0 |
| 18 | `test_increase_trial_chats` | TestAdminTrialChats | ✅ passed | 0 |
| 19 | `test_invalid_trial_mode_rejected` | TestAdminTrialChats | ✅ passed | 0 |

### 认证模块（注册/登录/Profile/验证码）

**文件**: `test_auth.py` | **总数**: 26 | **通过**: 26 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_register_requires_phone_or_email` | TestRegister | ✅ passed | 0 |
| 2 | `test_register_cannot_provide_both_phone_and_email` | TestRegister | ✅ passed | 0 |
| 3 | `test_register_invalid_phone_format` | TestRegister | ✅ passed | 0 |
| 4 | `test_register_password_min_length` | TestRegister | ✅ passed | 0 |
| 5 | `test_register_disabled` | TestRegister | ✅ passed | 0 |
| 6 | `test_register_duplicate_phone` | TestRegister | ✅ passed | 0 |
| 7 | `test_register_wrong_verify_code` | TestRegister | ✅ passed | 0 |
| 8 | `test_register_verify_code_consumed_after_use` | TestRegister | ✅ passed | 0 |
| 9 | `test_login_success` | TestLogin | ✅ passed | 0 |
| 10 | `test_login_wrong_password` | TestLogin | ✅ passed | 0 |
| 11 | `test_login_nonexistent_account` | TestLogin | ✅ passed | 0 |
| 12 | `test_login_banned_user_rejected` | TestLogin | ✅ passed | 0 |
| 13 | `test_login_by_email` | TestLogin | ✅ passed | 0 |
| 14 | `test_login_response_contains_masked_user_info` | TestLogin | ✅ passed | 0 |
| 15 | `test_refresh_token_generates_new_access_token` | TestTokenRefresh | ✅ passed | 0 |
| 16 | `test_invalid_refresh_token_rejected` | TestTokenRefresh | ✅ passed | 0 |
| 17 | `test_access_token_cannot_be_used_as_refresh` | TestTokenRefresh | ✅ passed | 0 |
| 18 | `test_get_profile_returns_user_info` | TestProfile | ✅ passed | 0 |
| 19 | `test_update_nickname` | TestProfile | ✅ passed | 0 |
| 20 | `test_update_empty_nickname_rejected` | TestProfile | ✅ passed | 0 |
| 21 | `test_update_too_long_nickname_rejected` | TestProfile | ✅ passed | 0 |
| 22 | `test_change_password_success` | TestChangePassword | ✅ passed | 0 |
| 23 | `test_change_password_wrong_old_password` | TestChangePassword | ✅ passed | 0 |
| 24 | `test_change_password_same_as_old_rejected` | TestChangePassword | ✅ passed | 0 |
| 25 | `test_change_password_complexity_enforced` | TestChangePassword | ✅ passed | 0 |
| 26 | `test_get_register_config_public_only` | TestRegisterConfig | ✅ passed | 0 |

### Bug回归与边界条件测试

**文件**: `test_bugs.py` | **总数**: 31 | **通过**: 31 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_phone_with_spaces_normalized` | TestEdgeCasesRegistration | ✅ passed | 0 |
| 2 | `test_email_normalized_to_lowercase` | TestEdgeCasesRegistration | ✅ passed | 0 |
| 3 | `test_chinese_conversation_title` | TestEdgeCasesUnicode | ✅ passed | 0 |
| 4 | `test_emoji_in_title` | TestEdgeCasesUnicode | ✅ passed | 0 |
| 5 | `test_null_bytes_in_message_handled` | TestEdgeCasesUnicode | ✅ passed | 0 |
| 6 | `test_page_size_zero_handled` | TestEdgeCasesPagination | ✅ passed | 0 |
| 7 | `test_page_beyond_total` | TestEdgeCasesPagination | ✅ passed | 0 |
| 8 | `test_negative_page_handled` | TestEdgeCasesPagination | ✅ passed | 0 |
| 9 | `test_page_size_exceeds_max` | TestEdgeCasesPagination | ✅ passed | 0 |
| 10 | `test_deleted_user_token_rejected` | TestDeletedAccountBehavior | ✅ passed | 0 |
| 11 | `test_bcrypt_cost_factor` | TestPasswordSecurity | ✅ passed | 0 |
| 12 | `test_different_passwords_produce_different_hashes` | TestPasswordSecurity | ✅ passed | 0 |
| 13 | `test_verify_password_correct` | TestPasswordSecurity | ✅ passed | 0 |
| 14 | `test_verify_password_wrong` | TestPasswordSecurity | ✅ passed | 0 |
| 15 | `test_redeem_code_case_insensitive_not_applied` | TestRedeemEdgeCases | ✅ passed | 0 |
| 16 | `test_redeem_empty_code_rejected` | TestRedeemEdgeCases | ✅ passed | 0 |
| 17 | `test_redeem_code_value_zero_not_created` | TestRedeemEdgeCases | ✅ passed | 0 |
| 18 | `test_admin_access_token_not_usable_for_user_endpoints` | TestTokenTypeConfusion | ✅ passed | 0 |
| 19 | `test_user_access_token_not_usable_for_admin_endpoints` | TestTokenTypeConfusion | ✅ passed | 0 |
| 20 | `test_all_responses_have_code_field` | TestResponseFormat | ✅ passed | 0 |
| 21 | `test_all_responses_have_request_id` | TestResponseFormat | ✅ passed | 0 |
| 22 | `test_health_check_always_200` | TestResponseFormat | ✅ passed | 0 |
| 23 | `test_biz_exception_returns_200_not_500` | TestResponseFormat | ✅ passed | 0 |
| 24 | `test_invite_code_required_when_configured` | TestInviteCode | ✅ passed | 0 |
| 25 | `test_invalid_invite_code_rejected` | TestInviteCode | ✅ passed | 0 |
| 26 | `test_normalize_provider_aliases` | TestAiServiceUrlNormalization | ✅ passed | 0 |
| 27 | `test_normalize_api_base_strips_endpoint_suffix` | TestAiServiceUrlNormalization | ✅ passed | 0 |
| 28 | `test_normalize_api_base_keeps_clean_url` | TestAiServiceUrlNormalization | ✅ passed | 0 |
| 29 | `test_parse_float_safe` | TestAiServiceUrlNormalization | ✅ passed | 0 |
| 30 | `test_parse_int_safe` | TestAiServiceUrlNormalization | ✅ passed | 0 |
| 31 | `test_parse_bool` | TestAiServiceUrlNormalization | ✅ passed | 0 |

### 对话模块（会话/消息/图片上传/反馈）

**文件**: `test_chat.py` | **总数**: 29 | **通过**: 29 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_create_conversation` | TestConversationCRUD | ✅ passed | 0 |
| 2 | `test_create_conversation_default_title` | TestConversationCRUD | ✅ passed | 0 |
| 3 | `test_list_conversations_only_own` | TestConversationCRUD | ✅ passed | 0 |
| 4 | `test_rename_conversation` | TestConversationCRUD | ✅ passed | 0 |
| 5 | `test_rename_trims_whitespace` | TestConversationCRUD | ✅ passed | 0 |
| 6 | `test_rename_conversation_truncates_to_200` | TestConversationCRUD | ✅ passed | 0 |
| 7 | `test_delete_conversation_and_messages` | TestConversationCRUD | ✅ passed | 0 |
| 8 | `test_delete_nonexistent_conversation` | TestConversationCRUD | ✅ passed | 0 |
| 9 | `test_conversations_paginate` | TestConversationCRUD | ✅ passed | 0 |
| 10 | `test_conversations_page2` | TestConversationCRUD | ✅ passed | 0 |
| 11 | `test_get_messages_in_order` | TestMessages | ✅ passed | 0 |
| 12 | `test_get_messages_includes_feedback` | TestMessages | ✅ passed | 0 |
| 13 | `test_user_message_has_no_rating` | TestMessages | ✅ passed | 0 |
| 14 | `test_send_message_deducts_free_chats` | TestSendMessage | ✅ passed | 0 |
| 15 | `test_send_message_quota_exhausted` | TestSendMessage | ✅ passed | 0 |
| 16 | `test_send_message_banned_user_rejected` | TestSendMessage | ✅ passed | 0 |
| 17 | `test_send_message_with_subscription_no_quota_check` | TestSendMessage | ✅ passed | 0 |
| 18 | `test_send_message_expired_subscription_treated_as_free` | TestSendMessage | ✅ passed | 0 |
| 19 | `test_send_message_to_nonexistent_conversation` | TestSendMessage | ✅ passed | 0 |
| 20 | `test_upload_valid_image` | TestImageUpload | ✅ passed | 0 |
| 21 | `test_upload_unsupported_format_rejected` | TestImageUpload | ✅ passed | 0 |
| 22 | `test_upload_too_large_image_rejected` | TestImageUpload | ✅ passed | 0 |
| 23 | `test_upload_too_small_image_rejected` | TestImageUpload | ✅ passed | 0 |
| 24 | `test_upload_unsupported_audio_format_rejected` | TestAudioUpload | ✅ passed | 0 |
| 25 | `test_upload_too_large_audio_rejected` | TestAudioUpload | ✅ passed | 0 |
| 26 | `test_feedback_like` | TestMessageFeedback | ✅ passed | 0 |
| 27 | `test_feedback_dislike` | TestMessageFeedback | ✅ passed | 0 |
| 28 | `test_feedback_invalid_rating_rejected` | TestMessageFeedback | ✅ passed | 0 |
| 29 | `test_cannot_feedback_user_message` | TestMessageFeedback | ✅ passed | 0 |

### 并发与延迟测试（并发/幂等/延迟基准）

**文件**: `test_concurrency.py` | **总数**: 10 | **通过**: 10 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_concurrent_redeem_same_code_only_one_succeeds` | TestConcurrentRedeemCode | ✅ passed | 0 |
| 2 | `test_concurrent_checkout_creates_unique_order_nos` | TestConcurrentRedeemCode | ✅ passed | 0 |
| 3 | `test_concurrent_conversation_creation` | TestConcurrentConversations | ✅ passed | 0 |
| 4 | `test_concurrent_messages_quota_not_over_deducted` | TestConcurrentQuotaDeduction | ✅ passed | 0 |
| 5 | `test_health_check_latency_under_50ms` | TestResponseLatency | ✅ passed | 0 |
| 6 | `test_user_login_latency_under_500ms` | TestResponseLatency | ✅ passed | 0 |
| 7 | `test_list_conversations_latency_with_data` | TestResponseLatency | ✅ passed | 0 |
| 8 | `test_admin_user_list_latency_with_1000_users` | TestResponseLatency | ✅ passed | 0 |
| 9 | `test_delete_already_deleted_conversation` | TestIdempotency | ✅ passed | 0 |
| 10 | `test_multiple_profile_updates_last_wins` | TestIdempotency | ✅ passed | 0 |

### 数据持久性测试（事务/一致性/级联删除）

**文件**: `test_persistence.py` | **总数**: 14 | **通过**: 14 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_user_data_persists_after_create` | TestWriteThenRead | ✅ passed | 0 |
| 2 | `test_conversation_data_persists` | TestWriteThenRead | ✅ passed | 0 |
| 3 | `test_message_persists_with_correct_user` | TestWriteThenRead | ✅ passed | 0 |
| 4 | `test_api_create_conversation_persists` | TestWriteThenRead | ✅ passed | 0 |
| 5 | `test_profile_update_persists` | TestWriteThenRead | ✅ passed | 0 |
| 6 | `test_redeem_code_status_update_persists` | TestWriteThenRead | ✅ passed | 0 |
| 7 | `test_delete_conversation_removes_messages` | TestCascadeDelete | ✅ passed | 0 |
| 8 | `test_delete_conversation_removes_token_usage` | TestCascadeDelete | ✅ passed | 0 |
| 9 | `test_redeem_atomicity_free_chats_updated` | TestTransactionIntegrity | ✅ passed | 0 |
| 10 | `test_user_free_chats_not_negative` | TestTransactionIntegrity | ✅ passed | 0 |
| 11 | `test_user_id_in_messages_matches_user` | TestDataConsistency | ✅ passed | 0 |
| 12 | `test_conversation_belongs_to_correct_user` | TestDataConsistency | ✅ passed | 0 |
| 13 | `test_banned_user_status_persists_across_login` | TestDataConsistency | ✅ passed | 0 |
| 14 | `test_subscription_days_stack_correctly` | TestDataConsistency | ✅ passed | 0 |

### 系统安全测试（越权/注入/认证）

**文件**: `test_security.py` | **总数**: 28 | **通过**: 28 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_no_token_returns_1002` | TestJWTSecurity | ✅ passed | 0 |
| 2 | `test_malformed_token` | TestJWTSecurity | ✅ passed | 0 |
| 3 | `test_wrong_secret_token` | TestJWTSecurity | ✅ passed | 0 |
| 4 | `test_expired_token` | TestJWTSecurity | ✅ passed | 0 |
| 5 | `test_refresh_token_cannot_access_protected_routes` | TestJWTSecurity | ✅ passed | 0 |
| 6 | `test_admin_token_cannot_access_user_routes` | TestJWTSecurity | ✅ passed | 0 |
| 7 | `test_user_token_cannot_access_admin_routes` | TestJWTSecurity | ✅ passed | 0 |
| 8 | `test_forged_user_id_in_token` | TestJWTSecurity | ✅ passed | 0 |
| 9 | `test_bearer_prefix_required` | TestJWTSecurity | ✅ passed | 0 |
| 10 | `test_user_cannot_read_other_users_conversation` | TestIDOR | ✅ passed | 0 |
| 11 | `test_user_cannot_delete_other_users_conversation` | TestIDOR | ✅ passed | 0 |
| 12 | `test_user_cannot_rename_other_users_conversation` | TestIDOR | ✅ passed | 0 |
| 13 | `test_user_cannot_feedback_other_users_message` | TestIDOR | ✅ passed | 0 |
| 14 | `test_phone_masked_in_profile` | TestSensitiveDataMasking | ✅ passed | 0 |
| 15 | `test_email_masked_in_profile` | TestSensitiveDataMasking | ✅ passed | 0 |
| 16 | `test_llm_api_key_not_in_list_response` | TestSensitiveDataMasking | ✅ passed | 0 |
| 17 | `test_password_hash_not_in_user_response` | TestSensitiveDataMasking | ✅ passed | 0 |
| 18 | `test_xss_in_nickname_stored_safely` | TestInjectionDefense | ✅ passed | 0 |
| 19 | `test_sql_injection_in_login` | TestInjectionDefense | ✅ passed | 0 |
| 20 | `test_sql_injection_in_conversation_title` | TestInjectionDefense | ✅ passed | 0 |
| 21 | `test_extremely_long_input_handled` | TestInjectionDefense | ✅ passed | 0 |
| 22 | `test_honeypot_website_field_returns_fake_success` | TestHoneypot | ✅ passed | 0 |
| 23 | `test_fast_form_submission_rejected` | TestHoneypot | ✅ passed | 0 |
| 24 | `test_normal_form_submission_not_rejected` | TestHoneypot | ✅ passed | 0 |
| 25 | `test_normal_admin_cannot_unlock_accounts` | TestAdminPrivilegeEscalation | ✅ passed | 0 |
| 26 | `test_unauthenticated_cannot_access_admin_api` | TestAdminPrivilegeEscalation | ✅ passed | 0 |
| 27 | `test_admin_login_brute_force_lockout` | TestRateLimiting | ✅ passed | 0 |
| 28 | `test_ip_rate_limit_on_verify_code` | TestRateLimiting | ✅ passed | 0 |

### 订阅模块（套餐/下单/兑换码/订单）

**文件**: `test_subscribe.py` | **总数**: 24 | **通过**: 24 | **失败**: 0

| # | 测试用例 | 类 | 结果 | 耗时(ms) |
|---|---------|-----|------|----------|
| 1 | `test_subscribe_info_free_user` | TestSubscribeInfo | ✅ passed | 0 |
| 2 | `test_subscribe_info_subscribed_user` | TestSubscribeInfo | ✅ passed | 0 |
| 3 | `test_subscribe_info_requires_auth` | TestSubscribeInfo | ✅ passed | 0 |
| 4 | `test_catalog_returns_active_plans_only` | TestSubscribeCatalog | ✅ passed | 0 |
| 5 | `test_catalog_returns_active_channels_only` | TestSubscribeCatalog | ✅ passed | 0 |
| 6 | `test_checkout_creates_pending_payment` | TestCheckout | ✅ passed | 0 |
| 7 | `test_checkout_inactive_plan_rejected` | TestCheckout | ✅ passed | 0 |
| 8 | `test_checkout_inactive_channel_rejected` | TestCheckout | ✅ passed | 0 |
| 9 | `test_checkout_nonexistent_plan_rejected` | TestCheckout | ✅ passed | 0 |
| 10 | `test_checkout_order_no_is_unique` | TestCheckout | ✅ passed | 0 |
| 11 | `test_redeem_chats_code_increases_free_chats` | TestRedeem | ✅ passed | 0 |
| 12 | `test_redeem_days_code_extends_subscription` | TestRedeem | ✅ passed | 0 |
| 13 | `test_redeem_days_stacks_on_existing_subscription` | TestRedeem | ✅ passed | 0 |
| 14 | `test_redeem_used_code_rejected` | TestRedeem | ✅ passed | 0 |
| 15 | `test_redeem_expired_code_rejected` | TestRedeem | ✅ passed | 0 |
| 16 | `test_redeem_nonexistent_code_rejected` | TestRedeem | ✅ passed | 0 |
| 17 | `test_redeem_marks_code_as_used` | TestRedeem | ✅ passed | 0 |
| 18 | `test_redeem_free_plan_upgraded_to_monthly_on_days_code` | TestRedeem | ✅ passed | 0 |
| 19 | `test_list_orders_only_subscribe_type` | TestSubscribeOrders | ✅ passed | 0 |
| 20 | `test_apply_subscription_from_scratch` | TestSubscriptionService | ✅ passed | 0 |
| 21 | `test_apply_subscription_stacks_on_existing` | TestSubscriptionService | ✅ passed | 0 |
| 22 | `test_resolve_checkout_url_substitutes_placeholders` | TestSubscriptionService | ✅ passed | 0 |
| 23 | `test_create_order_no_is_unique` | TestSubscriptionService | ✅ passed | 0 |
| 24 | `test_create_order_no_starts_with_sub` | TestSubscriptionService | ✅ passed | 0 |

## 四、安全测试专项

安全测试覆盖以下威胁向量：

- **管理员权限提升防护**: 2/2 通过 ✅
- **蜜罐接口检测**: 3/3 通过 ✅
- **水平越权（IDOR）防护**: 4/4 通过 ✅
- **注入攻击防护（SQL/特殊字符）**: 4/4 通过 ✅
- **JWT Token 安全（伪造/篡改/算法混淆）**: 9/9 通过 ✅
- **频率限制（登录锁定、IP 封锁）**: 2/2 通过 ✅
- **敏感数据脱敏**: 4/4 通过 ✅

## 五、持久性与事务完整性专项

| 测试场景 | 类别 | 结果 |
|---------|------|------|
| `test_user_data_persists_after_create` | TestWriteThenRead | ✅ |
| `test_conversation_data_persists` | TestWriteThenRead | ✅ |
| `test_message_persists_with_correct_user` | TestWriteThenRead | ✅ |
| `test_api_create_conversation_persists` | TestWriteThenRead | ✅ |
| `test_profile_update_persists` | TestWriteThenRead | ✅ |
| `test_redeem_code_status_update_persists` | TestWriteThenRead | ✅ |
| `test_delete_conversation_removes_messages` | TestCascadeDelete | ✅ |
| `test_delete_conversation_removes_token_usage` | TestCascadeDelete | ✅ |
| `test_redeem_atomicity_free_chats_updated` | TestTransactionIntegrity | ✅ |
| `test_user_free_chats_not_negative` | TestTransactionIntegrity | ✅ |
| `test_user_id_in_messages_matches_user` | TestDataConsistency | ✅ |
| `test_conversation_belongs_to_correct_user` | TestDataConsistency | ✅ |
| `test_banned_user_status_persists_across_login` | TestDataConsistency | ✅ |
| `test_subscription_days_stack_correctly` | TestDataConsistency | ✅ |

## 六、并发与延迟基准

| 接口 | 测试场景 | 基准要求 | 结果 |
|------|---------|---------|------|
| `GET /api/health` | 10次连续请求平均延迟 | < 50ms | ✅ 通过 |
| `POST /api/auth/login` | 3次登录含bcrypt | < 500ms | ✅ 通过 |
| `GET /api/chat/conversations` | 100条会话列表 | < 200ms | ✅ 通过 |
| `GET /api/admin/users` | 1000用户列表分页 | < 500ms | ✅ 通过 |
| 并发兑换码双花 | 10并发请求同一码 | 最多1次成功 | ✅ 通过 |
| 幂等性-重复删除 | 重复删除已删除会话 | 返回1004不崩溃 | ✅ 通过 |
| 并发Profile更新 | 3并发更新昵称 | 最终态合法不崩溃 | ✅ 通过 |

## 七、Bug回归与边界条件

| 类别 | 覆盖内容 | 状态 |
|------|---------|------|
| Unicode/中文 | 中文标题、Emoji、null字节 | ✅ 全部通过 |
| 分页边界 | page=0/-1/999/超大page_size | ✅ 全部通过 |
| 密码安全 | bcrypt成本因子≥10、salt随机性、正误校验 | ✅ 全部通过 |
| Token混用 | admin token用于user端点（反之亦然） | ✅ 全部通过 |
| 兑换码边界 | 空码/大小写敏感/已用/已过期/不存在 | ✅ 全部通过 |
| 响应格式 | 所有响应含code字段、含request_id、HTTP 200 | ✅ 全部通过 |
| AI服务URL规范化 | provider别名/URL清洗/float/int/bool解析 | ✅ 全部通过 |
| 注册边界 | 手机号空格、邮箱大小写、邀请码模式 | ✅ 全部通过 |
| 软删除账号 | 已删除用户Token被拒 | ✅ 全部通过 |

## 八、测试环境

| 项目 | 说明 |
|------|------|
| 测试框架 | pytest 8.x + pytest-asyncio |
| HTTP客户端 | httpx.AsyncClient + ASGITransport |
| 数据库 | SQLite in-memory（StaticPool，替代MySQL）|
| Redis | fakeredis.aioredis + 自定义Lua脚本支持 |
| 应用框架 | FastAPI + SQLAlchemy 2.x async |
| 运行环境 | Docker 容器 abaojie-backend |
| Python | 3.11+ |

---

*本报告由自动化测试套件生成，涵盖认证、对话、订阅、管理、安全、持久性、并发及边界条件共 **218** 个测试用例，通过率 **100%**。*