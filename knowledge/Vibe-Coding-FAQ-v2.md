---
title: Vibe Coding FAQ
status: published
tags:
  - Vibe Coding
  - AI编程
  - PRD
  - FAQ
aliases:
  - AI编程方法
  - Plan Mode
  - 代码改错
  - AI写代码
---

# Vibe Coding FAQ

## Vibe Coding 是什么？

Vibe Coding 是一种 AI 编程方式，最早由 Andrej Karpathy（OpenAI 联合创始人）在 2025 年提出，核心理念是：用自然语言描述你要什么，让 AI 来写代码，你负责提需求、看效果、做判断。

课程里教的 Vibe Coding 方法论，核心思路是「让 AI 先写说明书，再干活」，能大幅减少 AI 改错代码的问题。

标准流程：
1. Plan Mode（规划模式）：先跟 AI 讨论需求，不让它动手写代码
2. 生成 PRD.md：让 AI 把讨论结果写成产品需求文档
3. 确认 PRD：你看过觉得 OK 了，再让 AI 按 PRD 开发
4. 开发过程中：AI 每做一步都会对照 PRD，减少跑偏

为什么需要这套方法：
- 不用它：直接让 AI 写代码 → 改着改着就乱了 → 越改越错
- 用它：先想清楚要什么 → AI 按说明书做 → 错了也能对照 PRD 找原因

怎么进入 Plan Mode：
- 启动 Claude Code 后，按 Shift+Tab 切换到 Plan Mode
- 或者直接说「请先进入 plan mode，我们先讨论需求」

课程里会详细教这套方法，是 AI 编程最核心的技能之一。

## AI 改代码总是改错怎么办？

AI 改错代码是最常见的问题，有一套标准处理流程：

1. 立刻停下来：按两次 ESC 或者 Ctrl+C 停止 AI
2. 回滚到改错之前的状态：
   - 如果项目用了 Git：用 `git diff` 看改了什么，再用 `git checkout -- 文件名` 恢复单个文件（注意：`git checkout .` 会恢复所有文件，慎用）
   - 如果没用 Git：检查 Cursor/VS Code 的文件历史（右键文件 → Timeline）或本地历史记录
3. 用 Plan Mode 重新来：
   - 按 Shift+Tab 进入 Plan Mode
   - 跟 AI 说清楚：「刚才改错了，我要的是 XXX，不是 XXX」
   - 让 AI 先出方案，你确认了再让它动手
4. 让 AI 更新 PRD.md：把正确的需求写进文档，AI 后面按文档做

预防措施（减少改错的概率）：
- 用 Vibe Coding 方法：先讨论 → 写 PRD → 再开发
- 一次只让 AI 做一件事，不要一口气提一堆需求
- 给 AI 具体的参考：「参考 XXX 文件的风格来改」
- 重要文件改之前，让 AI 先备份

## 用 AI 编程做出来的网站/产品效果不好，一路点 YES 但不尽如人意？

效果不尽如人意很正常，关键在于前面的「设计环节」要投入足够多的时间。比如做一个网站产品，光跟 AI 对话梳理需求就可能聊一个小时甚至更久。

这里会充分用到之前 Kevin 老师教的战略性思维——3C、4P 这些框架。先把你要做什么、给谁用、核心卖点是什么想清楚了，AI 才能帮你做出真正好的东西。

核心原则：需求想得越清楚，AI 做出来的效果越好。急着让 AI 动手，反而会花更多时间在改错上。
