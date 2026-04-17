---
title: Claude Code 安装与排错指南
status: published
tags:
  - 安装
  - 配置
  - 报错
  - 环境变量
  - 令牌
aliases:
  - Claude Code安装
  - 安装步骤
  - 令牌配置
  - 400报错修复
  - Node.js安装
---

# Claude Code 安装与排错指南

## 遇到报错时的排查顺序

遇到各类报错，请按以下顺序排查：

1. 检查网络代理是否开启且连接稳定（"魔法"是否正常）。
2. 遇到"上下文断开"、"API 错误"、"400"、"429"等报错：网络正常的情况下，查阅官方文档寻找解决方法。
3. 遇到"503 报错"：打开浏览器访问 www.claudecc.top，进入"令牌管理"，点击"编辑"，切换一个可用分组即可。

## 第一步：安装 Node.js

在终端/CMD 窗口执行安装，完成后用以下命令验证：

```
node -v
```

提示：Mac 按 Command + 空格 搜索"终端"打开；Windows 按 Win + R，输入 cmd 回车。

## 第二步：安装 Git

安装完成后用以下命令验证：

```
git -v
```

## 第三步：安装 Claude Code

Mac 用户需在命令前加 `sudo`，Windows 用户直接执行：

```
sudo npm install -g @anthropic-ai/claude-code --registry=https://registry.npmmirror.com
```

验证安装：

```
claude -v
```

## 第四步：配置永久环境变量（令牌）

1. 浏览器访问 claudecc.top，注册账号。
2. 点击"创建令牌"，自定义名字，选择 aws 分组。
3. 复制生成的令牌，打开"一键安装文档页面"粘贴令牌。
4. 向下滚动页面，找到对应指令，选择"永久设置"并复制。
5. 回到终端窗口，右键粘贴指令，敲几次回车，等待约 1 分钟完成。

## 遇到 AWS 令牌 400 报错的修复方法

**Mac 用户**，在终端依次执行以下两行命令：

```
echo 'export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="1"' >> ~/.zshrc
source ~/.zshrc
```

**Windows 用户**，在 PowerShell 中执行：

```
[System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS", "1", [System.EnvironmentVariableTarget]::User)
```

## 第五步：测试 Claude 对话

1. 新开一个终端/CMD 窗口。
2. 输入 `claude` 并回车。
3. 一直按回车直到进入对话界面，即表示安装成功。

## 第六步：安装 VS Code 及插件

1. 安装代码编辑器 VS Code（Visual Studio Code）。
2. 打开 VS Code，安装汉化插件。
3. 安装 Claude Code 插件。
4. 在 VS Code 内测试对话是否正常。

## 第七步：安装其他依赖

1. 安装 Python 环境。
2. 根据个人需求安装"闪电说"等其他辅助工具。
