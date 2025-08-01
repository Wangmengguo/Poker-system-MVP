# 🚀 并行执行指南

## 概述

基于对 `CORRECTED_FIX_PLAN.md` 的分析，我已将6步修正方案拆分为3个并行轨道，可以同时进行开发，将总时间从7小时缩短到3.5小时。

## 📋 轨道分配

| 轨道 | 负责人 | 时间 | 任务 | 文档 |
|------|--------|------|------|------|
| **Track 1** | AI助理A | 3小时 | 核心架构修正 | `TRACK1_CORE_ARCHITECTURE.md` |
| **Track 2** | AI助理B | 1.5小时 | 测试基础设施 | `TRACK2_TEST_INFRASTRUCTURE.md` |
| **Track 3** | AI助理C | 2小时 | UI重构和工具 | `TRACK3_UI_REFACTOR.md` |

## 🏗️ Worktree设置

### 1. 初始化Git仓库
```bash
cd /Users/arnoldwang/01_Active_Projects/Poker-system-MVP

# 如果还不是git仓库
git init
git add .
git commit -m "Initial MVP codebase before parallel development"
```

### 2. 创建并行工作树
```bash
# 创建测试轨道工作树
git worktree add ../poker-tests-track -b feature/test-infrastructure

# 创建UI重构轨道工作树  
git worktree add ../poker-ui-track -b feature/ui-refactor
```

### 3. 验证工作树设置
```bash
git worktree list
# 应该显示：
# /Users/arnoldwang/01_Active_Projects/Poker-system-MVP         (main)
# /Users/arnoldwang/01_Active_Projects/poker-tests-track       (feature/test-infrastructure)
# /Users/arnoldwang/01_Active_Projects/poker-ui-track          (feature/ui-refactor)
```

## 📁 工作目录分配

### Track 1 (主分支): 核心架构
- **工作目录**: `/Users/arnoldwang/01_Active_Projects/Poker-system-MVP/`
- **分支**: `main`
- **文件操作**:
  - 新建: `poker_system/l1_domain/rules.py`
  - 修改: `poker_system/l2_executor/pokerkit_executor.py`

### Track 2 (测试轨道): 测试基础设施
- **工作目录**: `/Users/arnoldwang/01_Active_Projects/poker-tests-track/`
- **分支**: `feature/test-infrastructure`
- **文件操作**:
  - 新建: `poker_system/tests/__init__.py`
  - 新建: `poker_system/tests/test_l1_rules.py`
  - 新建: `poker_system/tests/test_l2_translator.py`
  - 新建: `poker_system/tests/test_integration.py`
  - 修改: `poker_system/l1_domain/translator.py` (末尾添加)

### Track 3 (UI轨道): UI重构和工具
- **工作目录**: `/Users/arnoldwang/01_Active_Projects/poker-ui-track/`
- **分支**: `feature/ui-refactor`
- **文件操作**:
  - 新建: `poker_system/l3_driver/cli_runner.py`
  - 新建: `poker_system/l3_driver/analytics.py`
  - 重写: `poker_system/l5_cli/main.py`
  - 扩展: `poker_system/l3_driver/game_loop.py` (末尾添加)

## ⏱️ 时间表

### 小时 0-1: 启动阶段
- **所有轨道**: 阅读各自文档，开始开发
- **Track 1**: 开始创建L1规则层
- **Track 2**: 开始创建测试文件
- **Track 3**: 开始CLI重构

### 小时 1: 第一次同步检查
- **所有轨道**: 提交当前进度
- **Track 2**: 应该完成Mock修正和基本测试框架
- **Track 3**: 应该完成CLI分离

### 小时 2: 第二次同步检查
- **Track 1**: 应该完成L1规则层，开始L2修正
- **Track 2**: 应该完成所有测试文件
- **Track 3**: 应该完成统计和导出功能

### 小时 3: 第一轮合并
- **Track 1**: 完成所有核心架构修正
- **Track 2**: 完成测试基础设施
- **开始合并**: 先合并Track 1，再合并Track 2

### 小时 3.5: 最终合并
- **Track 3**: 完成UI重构和工具功能
- **最终合并**: 合并Track 3
- **集成验证**: 运行完整测试套件

## 🔄 合并策略

### 第一轮合并 (3小时后)
```bash
cd /Users/arnoldwang/01_Active_Projects/Poker-system-MVP

# 1. 确保主分支已提交Track 1的所有修改
git status
git add .
git commit -m "Track 1 complete: L1 rules + L2 boundary fix"

# 2. 合并测试轨道
git merge feature/test-infrastructure
# 可能的冲突：translator.py (只是末尾添加，应该自动合并)

# 3. 验证核心功能
python l5_cli/main.py --players 2 --sb 5 --bb 10 --stack 200
python -m pytest tests/test_l1_rules.py -v
```

### 第二轮合并 (3.5小时后)
```bash
# 合并UI重构轨道
git merge feature/ui-refactor
# 可能的冲突：
# - main.py (完全重写，使用新版本)
# - game_loop.py (末尾添加，应该自动合并)

# 最终验证
python -m pytest tests/ -v
python l5_cli/main.py --players 2  # 完整功能测试
```

## ⚠️ 风险控制

### 文件冲突预防

#### 1. translator.py
- **Track 2**: 只在文件末尾添加MockTranslator
- **其他轨道**: 不修改此文件
- **冲突概率**: 🟢 极低

#### 2. main.py  
- **Track 3**: 完全重写文件
- **其他轨道**: 不修改此文件
- **冲突概率**: 🟢 无冲突

#### 3. game_loop.py
- **Track 3**: 只在类末尾添加方法
- **其他轨道**: 不修改此文件
- **冲突概率**: 🟢 极低

### 依赖管理

#### Track 2 对 Track 1 的依赖
- **问题**: 某些测试需要L1规则
- **解决**: 使用条件跳过 `@unittest.skipUnless`
- **合并后**: 自动启用完整测试

#### Track 3 对 Track 1 的依赖
- **问题**: 统计功能依赖获胜者逻辑
- **解决**: 优雅降级，显示"待完善"信息
- **合并后**: 自动启用完整功能

### 回滚保护
```bash
# 每个轨道的提交点
git commit -m "Track 1 checkpoint: L1 rules complete"
git commit -m "Track 2 checkpoint: Tests infrastructure complete"  
git commit -m "Track 3 checkpoint: UI refactor complete"

# 出问题时单独回滚
git revert <commit-hash>
```

## ✅ 验证检查表

### Track 1 完成标准
- [ ] `l1_domain/rules.py` 创建完成
- [ ] `l2_executor/pokerkit_executor.py` 修改完成
- [ ] 游戏能正确显示获胜者
- [ ] L1规则可独立运行

### Track 2 完成标准
- [ ] 所有测试文件创建完成
- [ ] MockTranslator正确实现
- [ ] L1测试可独立运行（无需PokerKit）
- [ ] 测试框架完整

### Track 3 完成标准
- [ ] CLI职责分离完成
- [ ] 导出功能工作正常
- [ ] 统计分析工具可用
- [ ] 用户体验改善

### 集成验证标准
- [ ] 所有单元测试通过
- [ ] 完整游戏流程正常
- [ ] 导出功能生成正确数据
- [ ] CLI参数解析正确

## 🎯 成功指标

### 时间效率
- **传统顺序**: 7小时
- **并行开发**: 3.5小时  
- **效率提升**: 50%

### 质量保证
- **测试覆盖**: L1独立测试 + 集成测试
- **架构清晰**: 四层边界明确
- **功能完整**: 获胜者逻辑 + 导出分析

### 扩展性
- **L1纯化**: 引擎无关的规则层
- **测试基础**: 完整的测试基础设施  
- **工具支持**: 数据分析和导出能力

## 📞 沟通协调

### 每小时检查点
各轨道负责人在每小时整点发布进度：
- ✅ 已完成的任务
- 🚧 正在进行的任务  
- ⚠️ 遇到的问题
- 📋 下一步计划

### 问题上报
遇到阻塞问题时：
1. 立即在群组中报告
2. 描述具体问题和错误信息
3. 说明是否影响其他轨道
4. 提供可能的解决方案

### 合并协调
- **3小时**: Track 1负责人主导第一轮合并
- **3.5小时**: Track 3负责人协助最终合并
- **冲突解决**: 优先保证核心功能正常

---

## 🚀 开始执行

**准备就绪后，各轨道负责人可以立即开始并行开发！**

1. 设置好worktree环境
2. 阅读各自的详细文档  
3. 按照文档中的具体步骤执行
4. 保持每小时的进度同步
5. 3.5小时后完成所有架构修正

**预期结果**: 一个架构清晰、功能完整、测试覆盖的Poker System MVP!