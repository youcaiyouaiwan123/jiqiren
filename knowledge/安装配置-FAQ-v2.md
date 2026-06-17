---
title: 安装配置 FAQ
status: published
tags:
  - 安装配置
  - 科学上网
  - Cursor
  - 飞书MCP
  - FAQ
aliases:
  - 开课准备
  - 工具配置
  - 环境搭建
  - 飞书配置
---
# 安装配置 FAQ


## Cursor 怎么安装和配置？

Cursor 是 AI 编程首选编辑器，免费，操作比 VS Code 更简洁。

安装步骤：

1. 如果官网打不开，先开科学上网
2. 访问 cursor.com/cn，选对应系统版本下载安装
3. 打开后点 SIGN UP 注册（按页面提示填写，姓名和手机号严格按要求格式填）
4. 返回 Cursor，连续两次点 Continue 完成初始化（默认配置就行）
5. 在电脑上新建一个「AI开发」文件夹，在 Cursor 点 Open 导入

重要提示：

- 不需要开通付费 Pro 版，免费功能完全够用
- 注册信息严格按要求填，否则可能注册失败

## Node.js 和 Git 怎么安装？

这两个是系统必备的基础工具，安装 Claude Code 之前必须先装好。

下载地址：

- Node.js 官网：nodejs.org（选 LTS 长期支持版）
- Git：课程群里有安装包，也可以去 git-scm.com 下载

Windows 系统：

- 下载 `node-windows.msi` 和 `Git-windows.exe`
- 双击运行，一路点 Next/下一步就行

Mac 系统：

- 下载对应的 `.pkg` 文件
- 双击安装，按提示操作

验证安装成功：

- 打开终端/命令行
- 输入 `node --version` 看到版本号就 OK
- 输入 `git --version` 看到版本号就 OK

装完这两个，就可以在编辑器（Cursor/VS Code）的终端里安装 Claude Code 了。

## 闪电说是什么？怎么安装使用？

闪电说是一款语音输入 + AI 交互工具，可以用说话代替打字来操作 AI，特别适合不想打字的场景。

费用：免费！官方赠送 500 万 tokens。

安装步骤：

1. 访问 shandianshuo.cn，选对应系统版本下载
2. 按安装向导一路下一步
3. 安装完会引导你测试快捷键：按键盘空格键右边的 Alt 键
4. 测试通过就进入主界面了

配置 API（用火山引擎的免费额度）：

- 打开闪电说 → 主页 → 点「查看完整教程」
- 按教程去火山引擎官网注册，获取 API Key
- 回闪电说填入 API 配置
- 官方赠送 500 万 tokens，够用很久

主界面 6 个模块：主页、记忆、技能、模型、设置、用户中心。有问题找老师帮忙配置。

## Excel 怎么接入 Claude？

可以在微软原生 Excel 里直接调用 Claude，让 AI 帮你处理表格数据。

必备条件：

- Claude Pro 账号（必须）
- 科学上网工具（全程开启）
- 微软 Office 365 账号（闲鱼约 5 元可买）
- 系统原生 Excel（不支持 WPS！）

安装步骤：

1. 开启科学上网 + 登录 Microsoft Office 365 账号
2. 打开 Excel，点右上角「加载项」
3. 搜索 `claude in excel` → 点安装 → 安装完关闭 Excel
4. 重新打开 Excel，点右上角 Claude 图标 → 点 Login
5. 输入 Claude Pro 邮箱 → 点继续 → 会进入验证码页面，先别动
6. 新开浏览器打开 mail.com → 登录 Claude 邮箱
7. 找到 Anthropic 发的验证码邮件 → 点黑色模块复制验证码
8. 回到 Excel 粘贴验证码 → 点确定 → 点授权
9. 关闭 Excel 重新打开，检查右侧 Claude 面板是否登录成功
10. 如果还显示 Login，重复 4-8 步（网络波动可能要多试几次）

注意：只支持微软原生 Excel，WPS 不行！

## 飞书MCP配置时，授权链接打不开（localhost:3000 无法访问）怎么办？

原因：MCP 服务没有正常启动。

解决方法：

1. 确保已安装 Node.js
2. 重启 Claude Code
3. 检查配置文件格式是否正确（JSON 格式要求严格）

## 飞书MCP提示 Token 过期怎么处理？

原因：授权已过期，需要重新授权。

解决方法：

1. 在 Claude Code 中触发任意飞书操作
2. 系统会生成新的授权链接
3. 在浏览器中打开链接完成授权

## 飞书MCP提示权限不足怎么解决？

原因：应用没有开通对应的 API 权限。

解决方法：

1. 回到飞书开放平台
2. 进入应用的「权限管理」→「API 权限」
3. 开通需要的权限
4. 重新发布应用版本

## 飞书MCP更换了 App Secret 后连接失败怎么办？

原因：配置文件中的 Secret 没有同步更新。

解决方法：

1. 打开 MCP 配置文件（通常在 `.claude/settings.json` 或 `settings.local.json` 中）
2. 找到 `mcpServers → lark-mcp → args` 中 `-s` 参数后面的值
3. 替换为新的 App Secret
4. 保存文件并重启 Claude Code
