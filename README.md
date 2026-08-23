# astrbot_plugin_Venus_Attaccare

群聊「攻击」插件：在群里发送可配置的指令（默认「攻击」）并 @ 目标，机器人会通过 AstrBot 统一接口向目标发送戳一戳（poke）。

## 关于本项目

- 本插件使用 AI 辅助开发。
- 功能创意受社区同类「戳一戳」功能启发，但代码完全基于 AstrBot 配置化架构独立重构实现，未使用任何第三方插件的源代码。
- 功能形态参考了社区同类戳一戳插件 [astrbot_plugin_PockAttack](https://github.com/LouieKH359/astrbot_plugin_PockAttack) 的设计与功能创意，特此致谢。
- 本插件基于 [MIT 许可证](LICENSE) 开源。

## 功能特点

- **指令可配置**：默认指令为「攻击 / 戳一戳」，可在 WebUI 中任意增删改。
- **加强模式**：「攻击！」（可配置）会触发更多次戳一戳。
- **冷却可配置**：默认冷却 5 秒，按群独立计算（也可切换为全局冷却）。
- **全部话术可配置**：确认、冷却、自攻、无目标、失败提示等所有回复文案均可在 WebUI 中修改（支持列表随机）。
- **多次戳间隔可配置**：避免短时间连发被平台风控。
- **智能兜底**：话术列表为空时使用内置兜底文案，插件不会因配置缺失而崩溃。

## 使用方法

1. 将插件目录放入 AstrBot 的 `data/plugins/` 下并重载插件。
2. 群聊中发送 `攻击 @某人`（或 `戳一戳 @某人`），机器人会先回复确认话术，再向对方发送 1~3 次戳一戳。
3. 发送 `攻击！ @某人`（或 `戳一戳！ @某人`）触发加强模式，发送 5~10 次戳一戳。
4. 冷却期间（默认 5 秒）再次触发会收到冷却话术。

## 配置说明

插件安装后，可在 AstrBot WebUI 的插件配置页面对以下项目进行自定义：

| 配置项 | 说明 |
| --- | --- |
| `enable` | 插件总开关 |
| `commands` | 触发攻击的普通指令列表 |
| `intensive_commands` | 加强模式指令列表 |
| `cooldown_seconds` | 冷却时间（秒），默认 5 |
| `per_group_cooldown` | 冷却是否按群独立计算 |
| `min_pokes` / `max_pokes` | 普通模式戳一戳次数范围 |
| `intensive_min_pokes` / `intensive_max_pokes` | 加强模式戳一戳次数范围 |
| `poke_interval` | 多次戳之间的间隔（秒） |
| `require_at` | 是否必须 @ 目标；关闭时未 @ 则对发送者本人发动戳一戳 |
| `reply_on_no_target` | 未 @ 目标时是否回复提示 |
| `no_target_messages` | 未 @ 目标时的回复话术列表 |
| `block_self_poke` | 是否禁止对机器人本体戳一戳 |
| `self_poke_messages` | 对机器人本体发动攻击时的回复话术列表 |
| `cooldown_messages` | 冷却期间的回复话术列表 |
| `confirm_messages` | 触发成功后的确认话术列表 |
| `notify_poke_failure` | 戳一戳失败时是否提示 |
| `poke_failed_messages` | 戳一戳失败时的回复话术列表 |

所有话术类配置均为列表，插件每次随机取一条回复；留空则使用内置兜底文案。

## 许可证

[MIT License](LICENSE) — Copyright (c) 2026 Mashiro1024

## 开发文档

- [AstrBot 插件开发指南](https://docs.astrbot.app/dev/star/plugin-new.html)
- [插件配置](https://docs.astrbot.app/dev/star/guides/plugin-config.html)
