# 赛博朋克贪吃蛇游戏设计文档

**项目名称：** Snake Game - Cyberpunk Edition
**设计日期：** 2026-04-12
**技术栈：** Python + PyQt5
**包管理：** uv

---

## 1. 项目概述

### 1.1 项目目标

创建一个具有赛博朋克霓虹夜城风格的增强版贪吃蛇游戏，提供流畅的游戏体验和丰富的视觉效果。

### 1.2 核心特性

- **5个难度级别**：训练、新手、普通、困难、疯狂
- **赛博几何道具系统**：5种特殊道具（超频、防火墙、数据包、时间膨胀、能量电池）
- **粒子效果系统**：多种场景的视觉反馈
- **完整的UI系统**：主窗口+侧边栏布局
- **双重控制**：键盘和虚拟按键
- **音效和背景音乐**：Synthwave风格电子音乐
- **排行榜系统**：记录Top 10高分

---

## 2. 架构设计

### 2.1 模块化架构

```
snake_game/
├── main.py                 # 程序入口
├── config.py               # 配置文件
├── game_logic.py           # 游戏核心逻辑
├── powerup_system.py       # 道具系统
├── game_ui.py              # PyQt界面
├── particle_system.py      # 粒子效果系统
├── sound_manager.py        # 音频管理
├── leaderboard.py          # 排行榜系统
└── resources/
    ├── sounds/
    └── fonts/
```

### 2.2 核心数据结构

```python
from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

@dataclass
class Position:
    x: int
    y: int

@dataclass
class ActivePowerup:
    powerup_type: str
    remaining_frames: int
    total_frames: int

class Snake:
    def __init__(self):
        self.body: List[Position] = []
        self.direction: Direction = Direction.RIGHT
        self.next_direction: Direction = Direction.RIGHT
        self.speed: int = 150  # ms per frame
        self.invincible: bool = False
        self.effects: List[ActivePowerup] = []

class GameState:
    def __init__(self):
        self.snake: Snake = Snake()
        self.food: Position = Position(0, 0)
        self.powerups: List[Tuple[Position, str]] = []
        self.score: int = 0
        self.level: int = 0
        self.paused: bool = False
        self.game_over: bool = False
```

---

## 3. 游戏机制设计

### 3.1 难度级别配置

| 级别 | 索引 | 速度(ms) | 初始长度 | 道具生成率 | 障碍物 |
|------|------|----------|----------|------------|--------|
| 训练 | 0 | 250 | 3 | 30% | 无 |
| 新手 | 1 | 200 | 3 | 25% | 无 |
| 普通 | 2 | 150 | 3 | 20% | 无 |
| 困难 | 3 | 100 | 4 | 15% | 简单障碍 |
| 疯狂 | 4 | 60 | 5 | 10% | 复杂障碍 |

### 3.2 道具系统

#### 道具类型

| 道具 | 图标 | 效果 | 持续时间 | 颜色 |
|------|------|------|----------|------|
| 超频芯片 | ◈ | 速度提升30% | 8秒 | #00ffff |
| 防火墙护盾 | ⬡ | 穿墙+无敌 | 6秒 | #ff00ff |
| 数据包 | ✦ | 双倍得分 | 10秒 | #ffff00 |
| 时间膨胀 | ⧉ | 时间变慢50% | 7秒 | #ff6600 |
| 能量电池 | ⚡ | 延长道具50% | 消耗型 | #00ff00 |

#### 道具规则

- 场上最多同时存在2个道具
- 道具消失后5秒内不会在同位置生成
- 吃到普通食物有道具生成率的概率生成道具
- 不同类型的道具效果可以叠加（除了能量电池）

### 3.3 粒子系统

#### 粒子触发场景

- **吃食物**：爆炸粒子，青色，20个粒子，生命周期1秒
- **吃道具**：螺旋粒子，对应道具颜色，30个粒子，生命周期1.5秒
- **道具激活**：护盾粒子，围绕蛇身旋转，持续到道具过期
- **穿墙**：波纹粒子，紫色，从碰撞点扩散
- **游戏结束**：碎片粒子，蛇身颜色，100个粒子，生命周期2秒

#### 粒子属性

每个粒子包含：位置、速度、颜色、大小、生命周期、衰减率

---

## 4. 视觉设计

### 4.1 霓虹夜城配色

```python
COLORS = {
    'background': '#0f0c29',
    'grid': '#1a1533',
    'neon_cyan': '#00ffcc',
    'neon_magenta': '#ff00ff',
    'neon_purple': '#b026ff',
    'food': '#00ffcc',
    'food_glow': 'rgba(0, 255, 204, 0.5)',
    'powerup_speed': '#00ffff',
    'powerup_shield': '#ff00ff',
    'powerup_score': '#ffff00',
    'powerup_time': '#ff6600',
    'powerup_extend': '#00ff00',
}
```

### 4.2 发光效果

- **蛇身**：外发光 15px，强度 0.8
- **食物**：脉冲发光，周期 2s
- **道具**：旋转发光效果
- **粒子**：渐变透明度衰减

使用 `QGraphicsDropShadowEffect` 和定时器实现动态发光。

### 4.3 UI 组件设计

#### 主窗口

- 深色半透明背景：`rgba(15, 12, 41, 0.95)`
- 霓虹边框：2px 渐变（青→紫→洋红）
- 圆角设计：10px

#### 游戏区域

- 网格：20x20 或 25x20
- 格子大小：25px（可配置）
- 网格线：半透明紫色 `rgba(176, 38, 255, 0.2)`

#### 侧边栏

- **分数显示**：大号霓虹字体，带发光
- **当前道具**：图标+倒计时进度条
- **控制按钮**：虚拟方向键，带发光反馈
- **排行榜**：Top 10 显示，滚动列表

---

## 5. 交互设计

### 5.1 控制系统

#### 键盘控制

- 方向键 / WASD：控制蛇的方向
- 空格：暂停/继续
- ESC：打开菜单
- R：重新开始

#### 虚拟按键

- 4个方向按钮（箭头图标）
- 霓虹边框，点击时发光反馈
- 支持长按连续转向
- 禁用反向移动（不能直接掉头）

### 5.2 游戏循环

```
Timer (每 difficulty.speed ms)
    ↓
game_loop_tick()
    ├─ 处理输入（方向）
    ├─ 更新蛇的位置
    ├─ 检测碰撞（墙壁/自身/食物/道具）
    ├─ 更新道具状态
    ├─ 更新粒子系统
    ├─ 更新UI显示
    └─ 检查游戏结束条件
    ↓
redraw_game_canvas()
    ├─ 清空画布
    ├─ 绘制网格
    ├─ 绘制粒子（底层）
    ├─ 绘制食物和道具
    ├─ 绘制蛇身
    └─ 绘制粒子（顶层）
```

### 5.3 状态机

```
MENU → PLAYING → PAUSED
                ↓
           GAME_OVER
                ↓
           LEADERBOARD
                ↓
                MENU
```

---

## 6. 音效设计

### 6.1 音效清单

| 场景 | 音效类型 | 音色 | 时长 |
|------|----------|------|------|
| 吃普通食物 | 上升音阶 | 电子叮声 | 0.3s |
| 吃道具 | 激活音效 | 充能声 | 0.5s |
| 碰撞墙壁 | 爆炸音效 | 低频碰撞 | 0.8s |
| 碰撞自身 | 失败音效 | 失败提示 | 1.0s |
| 游戏开始 | 启动音效 | 系统启动 | 2.0s |
| 暂停 | 暂停音效 | 短暂停顿 | 0.2s |
| 道具过期 | 过期提示 | 渐弱音 | 0.4s |

### 6.2 背景音乐

- **风格**：Synthwave / Cyberpunk 电子音乐
- **节奏**：120-140 BPM
- **音色**：合成器贝斯、琶音、鼓机
- **播放**：循环播放，支持静音切换

### 6.3 技术实现

使用 `PyQt5.QtMultimedia`：
- `QMediaPlayer` - 播放背景音乐
- `QSoundEffect` - 播放短音效
- 音量可调节（0-100%）
- 支持静音切换

---

## 7. 模块间通信

### 7.1 信号槽连接

```python
# game_ui.py
self.key_pressed.connect(game_logic.handle_input)
self.pause_requested.connect(self.toggle_pause)

# game_logic.py
self.game_over.connect(game_ui.show_game_over)
self.score_changed.connect(game_ui.update_score)
self.food_eaten.connect(sound_manager.play_eat_sound)

# powerup_system.py
self.powerup_activated.connect(game_ui.show_powerup)
self.powerup_activated.connect(particle_system.spawn_particles)
```

### 7.2 数据流

1. **用户输入** → game_ui → game_logic
2. **逻辑更新** → game_logic → game_ui（状态更新）
3. **视觉反馈** → game_logic → particle_system
4. **声音反馈** → game_logic → sound_manager
5. **分数更新** → game_logic → leaderboard

---

## 8. 错误处理与边界情况

### 8.1 边界情况处理

| 情况 | 处理方式 |
|------|----------|
| 快速按键导致的自杀 | 使用 next_direction 缓冲，每帧只接受一次方向改变 |
| 反向移动指令 | 忽略无效方向（不能直接掉头） |
| 音效文件缺失 | 降级到静音模式，不中断游戏 |
| 排行榜文件损坏 | 重建默认排行榜，保留备份 |
| 窗口最小化 | 自动暂停游戏，恢复后可选继续 |
| 资源加载失败 | 显示错误对话框，优雅退出 |

### 8.2 配置管理

**config.py 功能：**
- 集中管理所有配置
- 支持运行时修改（音量、难度等）
- 保存用户偏好到本地 JSON 文件
- 支持恢复默认设置

---

## 9. 依赖项

```toml
[dependencies]
pyqt5 = "^5.15.0"
```

---

## 10. 未来扩展方向

- 网络多人对战
- 自定义皮肤系统
- 关卡编辑器
- 成就系统
- Steam 创意工坊集成

---

**设计版本：** 1.0
**最后更新：** 2026-04-12
