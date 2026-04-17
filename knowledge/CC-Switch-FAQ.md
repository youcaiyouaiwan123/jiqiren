---
title: CC Switch FAQ
status: published
tags:
  - CC Switch
  - API
  - 模型切换
  - FAQ
aliases:
  - CCSwitch
  - API切换
  - 模型配置
  - 云雾API
---

# CC Switch FAQ

## CC Switch 是什么？怎么用？

CC Switch 是一款免费的 API 一键切换工具，不用手动改环境变量，一键切换不同的 API 供应商（云雾、悠悠等）。

下载安装：
1. 访问 GitHub 下载页（如果打不开就开科学上网）
2. 找到 Assets 区域，选对应系统版本：
   - Windows：选 `.msi`（安装版）或 `.zip`（便携版）
   - Mac：选 `.tar.gz` 或 `.zip`
3. 安装后打开，如果提示环境变量冲突 → 点查看详情 → 勾选全部 → 删除选中

添加 API 供应商（以悠悠 uucode 为例）：
1. 首页点左上角 + 号 → 选「添加统一供应商」
2. 选「自定义网关」，填写：
   - 名称：uucode（方便识别）
   - API 地址：https://api.uucode.org
   - API Key：填你的 SK 密钥
   - 官网地址：清空不填
3. 往下拉，关闭「Claude Code」和「OpenAI Codex」开关
4. 模型配置：清空原有内容，填写：
   - Haiku：claude-haiku-4-20250514
   - Sonnet：claude-sonnet-4-20250514
   - Opus：claude-sonnet-4-20250514
5. 点底部「添加」完成

添加云雾：操作同上，只改两项：
- API 地址：https://yunwu.ai
- API Key：填云雾的 SK 密钥

切换使用：
回首页 → 点左上角刷新 → 看到所有供应商 → 点谁的「启用」按钮就用谁，一键切换，不需要其他操作。

注意：下载时选带版本号的安装包，别下载 Source code 源码包。

## 推荐用什么模型？

看你的需求和预算，分三档：

省钱首选——国产模型：
- Kimi K2、MiniMax M2、GLM4.6
- 优点：便宜，国内直连不需要科学上网
- 缺点：复杂编程任务不如 Claude
- 适合：日常对话、简单任务、练手

性价比之选——第三方中转 API：
- 云雾 API（yunwu.ai）：约官方价 1/14，课程里最多人用
- 悠悠（uucode.org）：稳定性好
- 优点：用的是 Claude 真模型，但价格便宜很多
- 缺点：偶尔不稳定，高峰期可能排队
- 适合：日常开发、课程作业

效果最好——Claude 官方 API：
- 直接在 Anthropic 官网充值
- 优点：最稳定、响应最快
- 缺点：贵，需要科学上网
- 适合：重要项目、对稳定性要求高的场景

建议：先用云雾或悠悠练手，课程作业完全够用。等用熟了、项目重要了，再考虑官方 API。用 CC Switch 可以一键切换不同供应商，不用手动改配置。

## 云雾 API 怎么配置？

方法一：用 CC Switch 配置（推荐，最简单）
1. 打开 CC Switch，点左上角 + 号
2. 选「添加统一供应商」→「自定义网关」
3. 填写：名称=云雾，API 地址=https://yunwu.ai，API Key=你的 SK 密钥
4. 官网地址清空，关闭 Claude Code 和 OpenAI Codex 开关
5. 模型配置填：Sonnet=claude-sonnet-4-20250514
6. 点添加 → 回首页刷新 → 点启用

方法二：手动配置环境变量
1. 注册 yunwu.ai，充值（先充几十块试试）
2. 创建令牌，分组选「Claude Code专属」
3. 复制 SK 密钥
4. 在终端设置环境变量（Windows PowerShell）：
   ```
   $env:ANTHROPIC_API_KEY="你的SK密钥"
   $env:ANTHROPIC_BASE_URL="https://yunwu.ai"
   ```
5. 然后输入 `claude` 启动

注意：手动设的环境变量关掉终端就没了。想永久保存可以用 CC Switch，或者设置系统环境变量。

## Claude Code 能用 GPT、DeepSeek、Kimi 等其他模型吗？怎么配置？

可以搭载各种模型。步骤：
1. Trae 不用管，它只是编辑器
2. 去模型官网买 API（注意选适配 Claude 的）
3. 用 CC Switch 配置：添加供应商→选模型→填 API Key→启用
4. 启用后新开终端才生效

建议先充几十块试试。

## 什么是环境变量？什么时候需要配？

用 CC Switch：不需要手动配，自动处理。
不用 CC Switch：需要手动在终端设置。

结论：用 CC Switch 就不用管环境变量。

## Trae、Claude Code、CC Switch 是什么关系？

- Trae：IDE 编辑器，提供终端和文件管理
- Claude Code：在终端里运行的 AI 编程工具
- CC Switch：切换 Claude Code 使用哪个模型

Trae 自带的 AI 和 Claude Code 是独立的，互不影响。

## CC Switch 里 GPT/Codex 一直开着，但调不出来怎么办？

需要在终端里输入 `codex` 才能调出来，不是输入 `claude`。

`claude` 和 `codex` 是两个独立工具：
- 终端输入 `claude` → 启动 Claude Code
- 终端输入 `codex` → 启动 OpenAI Codex

想同时用？Split Terminal 分屏，左边跑 claude，右边跑 codex。

## CC Switch 切换到 Kimi 等其他模型后，CC 还是说自己是 Claude Code，正常吗？

正常的，不用担心。

CC Switch 切换后，实际调用的确实是 Kimi（或你选的那个模型）的 API，但 Claude Code 这个工具本身的界面和自我介绍不会变——它是 Anthropic 做的工具，自我介绍还是会说 Claude Code。

简单理解：壳（界面）是 Claude Code，芯（计算）是你切换的那个模型。

如果想验证：让它做一件事，看回答的风格和能力，或者直接问它现在调用的 API 是什么，它会告诉你的。

## CC Switch 里选 Kimi 作为 Claude 的供应商，用的到底是 Claude 还是 Kimi？

用的是 Kimi，不是 Claude。Claude Code 是「壳」，Kimi 是「芯」。就像用美团 App 点外卖，但实际送餐的是饿了么骑手。

确认方法：在 Claude Code 里问「你是谁？你是什么模型？」

## 为什么 CC Switch 必须要开着魔法才能用？

原因：第一次打通终端和 CC Switch 时如果开着代理，终端会「记住」必须通过代理才能连 CC Switch，关了代理反而连不上了。

完整恢复步骤：
1. 删除旧脚本：找到最开始连接 CC Switch 时生成的脚本文件，删掉它
2. 重装 Claude Code：按照群里的「Claude Code 安装文档」重新安装一遍，相当于恢复到初始状态
3. 关闭所有代理：确保魔法、代理全部关闭
4. 让 Cursor 智能体帮你打通：不开任何代理的情况下，告诉 Cursor 自带的智能体：「请帮我把 Claude Code 和 CC Switch 打通」，让它自动配置
5. 验证：打通后，不开代理直接在终端输入 `claude`，能正常启动就 OK 了

核心原则：第一次打通时不要开代理，否则后续会一直依赖代理才能用。

## uucode 如何获取 SK 密钥？

uucode 已经迁移到 cloudcc.top 了。在 cloudcc.top 中获取 SK 密钥的步骤：
1. 进入 cloudcc.top 后台
2. 找到令牌管理
3. 在左上角点击添加令牌
4. 设置令牌名称
5. 设置分组（按实际需要选择即可）
6. 系统会生成一个密钥，通常以 SK 开头
7. 直接复制即可使用
