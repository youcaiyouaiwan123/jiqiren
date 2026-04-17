---
title: Codex FAQ
status: published
tags:
  - Codex
  - OpenAI
  - API配置
  - FAQ
aliases:
  - OpenAI Codex
  - Codex CLI
  - Codex报错
---

# Codex FAQ

## OpenAI Codex CLI 是什么？和 Claude Code 有什么关系？

两个完全独立的 AI 编程工具，来自不同公司：
- Claude Code（Anthropic）：用 Claude API
- Codex CLI（OpenAI）：用 OpenAI API

可以双开并行使用，互不干扰。

## Codex 报 401 Unauthorized 错误？

说明 Codex 直接连的是 OpenAI 官方，没走中转 API。需要设置环境变量让 Codex 走本地代理。

## 怎么让 Codex 使用云雾等中转 API？

1. CC Switch 添加供应商（云雾-Codex）
2. CC Switch 设置 → 高级 → 本地代理 → 打开
3. 终端设置：
   ```
   $env:OPENAI_BASE_URL = "http://127.0.0.1:5000/v1"
   ```
4. 然后输入 `codex`

## 每次新开终端都要重新设置环境变量？

可以永久设置。在 PowerShell 中运行：
```
[Environment]::SetEnvironmentVariable("OPENAI_BASE_URL", "http://127.0.0.1:5000/v1", "User")
```

设置后完全关闭编辑器再重新打开才生效。
