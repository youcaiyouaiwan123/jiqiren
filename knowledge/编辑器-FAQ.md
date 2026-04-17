---
title: 编辑器 FAQ
status: published
tags:
  - 编辑器
  - VS Code
  - Cursor
  - 终端
  - FAQ
aliases:
  - VSCode问题
  - 编辑器配置
  - 终端问题
  - 汉化
---

# 编辑器 FAQ

## VS Code 终端里的 CMD、PowerShell、Node 是什么？

- CMD：Windows 传统命令行
- PowerShell：微软新一代命令行（推荐）
- Node：说明正在运行 Node.js 进程（Claude Code 就是基于 Node.js 的）

建议：日常用 PowerShell 即可。

## 招标文件太大（几十页到上千页），额度瞬间用完？

1. 化整为零：不要一次性丢所有文件，拆小任务，不同对话做底层分析最后汇总。
2. 用其他模型做初级整理（GPT/元宝/豆包），再丢给 Claude 深度分析。
3. 让 Claude Code 直接读本地文件，但不要全丢对话框里。

就像带新同事：可以让他一件件小事上手，慢慢积累经验。

## 编辑器界面是英文的，怎么汉化？

汉化很简单：
1. 打开 Trae/VS Code/Cursor
2. 按快捷键 Ctrl+Shift+X 打开扩展商店
3. 搜索「Chinese」
4. 安装「Chinese (Simplified) Language Pack」
5. 重启编辑器就变中文了

如果装了还是英文，按 Ctrl+Shift+P，输入「Configure Display Language」，选 zh-cn，再重启一次就好。
