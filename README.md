# 贪吃蛇 — 赛博朋克版

一款基于 Python + PyQt5 构建的赛博朋克霓虹风格贪吃蛇游戏，包含 5 个难度级别、道具系统、粒子特效、音效以及持久化排行榜。

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-41CD52?logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

## 功能特性

- **5 个难度级别** — 训练、新手、普通、困难、疯狂（不同速度、初始长度和障碍物复杂度）
- **赛博道具系统** — 5 种独特道具：超频芯片、防火墙护盾、数据包、时间膨胀、能量电池
- **粒子特效** — 吃食物、拾取道具、穿墙和游戏结束时触发爆炸、螺旋、波纹等粒子动画
- **霓虹视觉风格** — 深色背景搭配青色/洋红/紫色霓虹发光效果
- **双重操控** — 键盘（方向键 / WASD）+ 侧边栏虚拟按钮
- **音效与音乐** — Synthwave 风格音效和背景音乐（缺少音频文件时自动静音）
- **排行榜** — 持久化存储 Top 10 高分（JSON 格式）

## 快速开始

### 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 包管理工具

### 安装与运行

```bash
# 克隆仓库
git clone https://github.com/your-username/Snake-Game.git
cd Snake-Game

# 安装依赖
uv sync

# 启动游戏
uv run snake-game
```

## 操作方式

| 按键 | 功能 |
|------|------|
| 方向键 / WASD | 控制蛇的移动方向 |
| 空格键 | 暂停 / 继续 |
| R | 重新开始 |
| Esc | 打开菜单 |

侧边栏还提供了虚拟方向按钮，支持鼠标点击操控。

## 道具系统

| 道具 | 图标 | 效果 | 持续时间 | 颜色 |
|------|------|------|----------|------|
| 超频芯片 | ◈ | 速度提升 30% | 8 秒 | 青色 |
| 防火墙护盾 | ⬡ | 无敌 + 穿墙 | 6 秒 | 洋红 |
| 数据包 | ✦ | 双倍得分 | 10 秒 | 黄色 |
| 时间膨胀 | ⧉ | 时间减慢 50% | 7 秒 | 橙色 |
| 能量电池 | ⚡ | 延长当前道具 50% | 即时 | 绿色 |

吃到普通食物时有概率随机生成道具，场上最多同时存在 2 个。不同类型的效果可以叠加。

## 难度级别

| 级别 | 速度 | 初始长度 | 道具生成率 | 障碍物 |
|------|------|----------|------------|--------|
| 训练 | 250ms | 3 | 30% | 无 |
| 新手 | 200ms | 3 | 25% | 无 |
| 普通 | 150ms | 3 | 20% | 无 |
| 困难 | 100ms | 4 | 15% | 简单 |
| 疯狂 | 60ms | 5 | 10% | 复杂 |

## 项目结构

```
snake_game/
├── main.py              # 程序入口
├── config.py            # 常量、配色、难度配置
├── game_logic.py        # 核心逻辑：蛇移动、碰撞、计分
├── powerup_system.py    # 道具类型、激活、过期管理
├── particle_system.py   # 粒子特效（爆炸、螺旋、波纹）
├── game_ui.py           # PyQt5 主窗口、画布、侧边栏
├── sound_manager.py     # 音频播放（QtMultimedia）
├── leaderboard.py       # Top 10 排行榜（JSON 持久化）
tests/
├── test_config.py
├── test_game_logic.py
├── test_powerup_system.py
├── test_particle_system.py
└── test_leaderboard.py
resources/
└── sounds/              # 音频资源（WAV/MP3）
```

## 开发

### 运行测试

```bash
uv run pytest tests/ -v
```

### 技术栈

- **语言：** Python 3.12+
- **GUI 框架：** PyQt5
- **包管理：** [uv](https://docs.astral.sh/uv/)
- **测试：** pytest
- **构建系统：** hatchling

## 许可证

本项目基于 MIT 许可证开源 — 详见 [LICENSE](LICENSE) 文件。
