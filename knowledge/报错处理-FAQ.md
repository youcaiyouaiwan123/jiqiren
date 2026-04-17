---
title: 报错处理 FAQ
status: published
tags:
  - 报错
  - API错误
  - 故障处理
  - FAQ
aliases:
  - 报错合集
  - 400错误
  - 503错误
  - Unable to connect
---

# 报错处理 FAQ

## API 有关的报错：400、503、Unable to connect 等问题

有一个报错合集飞书文档「（Error）红色报错问题合集 · 对照自查（附视频）」，可以对照自查。

若有其他报错也可以在微信社群艾特技术老师解决。

## 常见报错快速对照

| 报错信息 | 常见原因 | 处理方向 |
| --- | --- | --- |
| 400 Bad Request | 请求格式错误或 API 参数有误 | 检查 API Key 和模型名称是否正确 |
| 401 Unauthorized | API Key 无效或未设置 | 重新检查并设置正确的 API Key |
| 503 Service Unavailable | API 服务暂时不可用 | 稍等片刻后重试，或切换 API 供应商 |
| Unable to connect | 网络连接问题，或科学上网未开启 | 检查网络，确认科学上网已开启 |
| npm not found | Node.js 未安装或未配置到 PATH | 重新安装 Node.js |
| permission denied | 没有执行权限 | Mac 用户在命令前加 `sudo` |
| Failed to connect to MCP server | 杀毒软件拦截，或 MCP 服务未启动 | 添加白名单，重启 Claude Code |

如果遇到上述表格未覆盖的报错，截图报错完整信息后在社群艾特技术老师。
