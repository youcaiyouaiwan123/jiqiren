---
title: Agent Teams FAQ
status: published
tags:
  - Agent Teams
  - MCP
  - Skills
  - CLAUDE.md
  - FAQ
aliases:
  - 多智能体
  - Agent协作
  - Skills配置
  - MCP配置
---

# Agent Teams FAQ

## 最近很火的 Agent Teams 是什么？Claude Code 里怎么用？

让你的 Claude Code 同时拥有多个不同角色的 AI 并行干活。

三个层级：Project（项目文件夹）> Agent（角色身份）> Skills（具体工作流）

三种落地方式：
1. CLAUDE.md 定义角色（最基础）
2. Skills 文件一键切换（推荐，输入 `/助教` 就能切换）
3. 命令行启动独立 Agent（进阶，可保存为 .bat 双击启动）

大多数同学用方式 1+2 就够了。

## MCP 和 Skills 有什么区别？

MCP 和 Skills 是两个不同的概念，很容易搞混。

MCP（Model Context Protocol）是一种连接外部工具的协议。比如连接微信、连接飞书、连接本地电脑。一般也就 3-4 个，不需要很多。

Skills 是封装好的工作流，是你日常工作中真正需要大量积累的东西。比如输入 `/助教` 就切换到答疑模式，输入 `/课程设计` 就切换到设计模式。Skills 才是 AI 使用稳定后需要沉淀的核心资产。

简单说：MCP = 连接外部工具的管道，Skills = 封装好的工作流程。大多数同学缺的是 Skills，不是 MCP。

## CLAUDE.md 文件应该怎么写？是不是要把所有方法论知识都写进去？

CLAUDE.md 不是用来当知识库的，是用来告诉 AI「这是啥项目、需要啥就去哪读」。

更省力的思路：
1. CLAUDE.md 只写项目定位 + 调取规则（150 行就够）
2. 10 大方法论、话术库这些拆成单独文件存
3. AI 需要时自己去读，不用每次全加载
4. 让 AI 在工作中自己总结经验沉淀下来

说白了：你现在是在「手写百科全书」，其实应该让 AI「按需查字典 + 自己做笔记」。

好处：
- 多个项目复用同一套知识库
- 改话术一次，所有项目自动生效
- 每次不用加载大量内容，省 token 省钱
- 每个项目有自己的专属记忆
