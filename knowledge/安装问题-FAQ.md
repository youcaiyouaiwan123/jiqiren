---
title: 安装问题 FAQ
status: published
tags:
  - 安装
  - Claude Code
  - FAQ
  - 故障处理
aliases:
  - 安装报错
  - 装不上
  - 安装失败
  - npm报错
---

# 安装问题 FAQ

## Claude Code 怎么安装？

安装前提：先装好 Node.js 和 Git（系统必备），以及科学上网工具。

安装 Claude Code 可以用以下任一编辑器，选一个自己顺手的就好：

方法一：用 VS Code 安装（课程主推）
1. 打开 VS Code 终端
2. 输入：`npm install -g @anthropic-ai/claude-code`
3. 课程演示以 VS Code 为主，跟着课程走最方便

方法二：用 Cursor 安装
1. 打开 Cursor 终端（Ctrl+`）
2. 输入同样的安装命令
3. 课程中也会切换 Cursor 做演示

方法三：用 Trae 安装
1. 下载 Trae IDE（trae.ai 或国内版 trae.cn）
2. 打开 Trae 终端，输入同样的安装命令

安装完成后：
- 终端输入 `claude` 就能启动
- 首次需要配置 API 连接（用 CC Switch 最方便，或手动设环境变量）
- 看到对话界面就说明安装成功了

常见报错：
- `npm not found` → Node.js 没装好，重装 Node.js
- `permission denied` → Mac 用户在命令前加 `sudo`
- 安装卡住不动 → 检查网络，可能需要开科学上网

详细步骤可以看《阿宝姐-AI课工具安装手册》，里面有完整说明。

## 登录时出现错误怎么办？

如果 Claude Code 登录时报错，大概率是配置文件问题。

解决方法：
1. 找到 `.claude.json` 文件：
   - Windows：打开文件资源管理器，地址栏输入 `C:\Users\你的用户名\` 回车
   - Mac：打开访达，按 Cmd+Shift+G，输入 `~/.claude/` 回车
2. 用记事本或 Cursor 打开 `.claude.json`
3. 在文件最后一行加上：`"hasCompletedOnboarding": true`
4. 保存文件，重新启动 Claude Code

如果文件里内容很乱或者找不到这个文件，也可以直接删掉整个 `.claude` 文件夹，然后重新运行 `claude` 命令，它会重新初始化。

## 需要输入密码但看不到？

这是正常的安全机制，密码不会显示，盲打后回车即可。

## 输入内容后报错「无法将 xxx 项识别为 cmdlet」

这是因为还没有启动 Claude Code。

错误1：直接在终端光标后面输入文字——终端不是聊天窗口，直接输入文字会被当成命令执行。
错误2：输入 `/claude`（带了斜杠）——斜杠开头会被识别为路径。

正确做法：
1. 打开终端
2. 输入 `claude`（不带斜杠）
3. 按回车
4. 看到小人图标出现才算启动成功
5. 然后才可以开始对话

一句话：先输入 `claude` 启动，再开始聊天。

## Claude Code 显示 might not be available in your country 连不上？

看到这个界面，说明 Claude Code 已经安装成功了，只是最后连接没通。

第一步：把截图发给 AI 对话框，问它怎么解决。
第二步：如果还是不行，联系合作的 API 供应商，他们支持远程技术支持，几分钟就能搞定。

## Claude Code 里没有看到填 API 密钥的地方，该怎么连接？

Claude Code 没有填写/选择 API 的界面，需要通过设置环境变量来配置 API key。

连接方式：
- 直连：设置 Anthropic 官方 API key
- 通过 CC Switch：使用工具切换不同 API 服务商

建议直接问 Claude："我是 Windows/Mac 用户，请一步步教我如何设置环境变量，让 Claude Code 连接到我的 API"

## 杀毒软件拦截 Claude Code，报错 Failed to connect to MCP server

这是杀毒软件把 Claude Code 的连接给拦了。

解决方法：
1. 打开你的杀毒软件（比如 360、火绒、Windows Defender）
2. 把 Claude Code 和 Cursor/Trae 的进程添加到「白名单」或「信任程序」
3. 如果不会加白名单，临时关闭杀毒软件也行
4. 改完后重启编辑器

重启之后就好了。

## OpenClaw（龙虾）如何安装？

OpenClaw 的初版安装教材已上传到班级学习导航里，在学习导航里找到对应文档，按步骤操作即可。

如果现在还处于课程初期阶段，可以先把 Claude Code 用好——它已经能实现大部分功能了。等积累了业务场景和底层数据之后，未来迁移到 OpenClaw 也会非常快。
