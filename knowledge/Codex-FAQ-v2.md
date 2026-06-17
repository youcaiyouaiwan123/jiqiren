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

可以双开并行使用，互不干扰。在终端里分别输入 `claude` 和 `codex` 就能各自启动，用 Split Terminal 分屏可以同时看两边。

## Codex 报 401 Unauthorized 错误？

401 表示认证失败，常见原因：
1. API Key 没设置或已过期
2. API Key 填写错误（多了空格、少了字符）
3. Codex 直接连了 OpenAI 官方，没走中转 API（国内网络环境下连不上官方）

排查方法：先确认 CC Switch 里 Codex 相关的供应商已启用，再检查环境变量 `OPENAI_BASE_URL` 是否设置正确。

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

## Codex 和 Claude Code 怎么选？

日常使用建议以 Claude Code 为主：
- Claude Code 对中文支持更好，课程和社群里的资料都围绕它
- Codex 适合作为补充，比如想同时跑两个任务时一个用 claude 一个用 codex

两个工具的能力各有侧重，但学习阶段专注一个效率更高。
