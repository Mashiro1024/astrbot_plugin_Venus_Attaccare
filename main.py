import asyncio
import random
import time

from astrbot.api import logger
from astrbot.api.all import (
    AstrBotConfig,
    AstrMessageEvent,
    Context,
    EventMessageType,
    Star,
    event_message_type,
)
import astrbot.api.message_components as Comp

# 兜底文案：仅当对应配置项为空列表时使用，正常情况下所有话术均来自 WebUI 配置
_FALLBACK = {
    "no_target_messages": "要先@一个目标才能发动攻击哦～",
    "self_poke_messages": "诶？让我打我自己？不要啦～",
    "cooldown_messages": "攻击频率过高，请稍后再来～",
    "confirm_messages": "收到！目标已锁定，开戳！",
    "poke_failed_messages": "呜…对方好像不接受戳一戳",
}


class VenusPlugin(Star):
    """发送"攻击 @用户"即可触发；发送"攻击！ @用户"触发加强模式（更多次戳一戳）。"""
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        # 冷却结束时间表：key 为群号；per_group_cooldown 关闭时统一使用 "global"
        self._cooldown_until: dict[str, float] = {}

    def _pick(self, key: str) -> str:
        """从配置的话术列表中随机取一条，列表为空时使用兜底文案。"""
        pool = self.config.get(key) or []
        return random.choice(pool) if pool else _FALLBACK.get(key, "")

    def _match_command(self, message: str) -> tuple[str, bool] | None:
        """匹配触发的指令，返回 (命中指令, 是否加强模式)；未命中返回 None。

        加强模式（如「攻击！」）优先匹配，命中后戳一戳次数更多。
        """
        for cmd in self.config.get("intensive_commands", []):
            if message.startswith(cmd):
                return cmd, True
        for cmd in self.config.get("commands", ["攻击"]):
            if message.startswith(cmd):
                return cmd, False
        return None

    def _in_cooldown(self, key: str) -> bool:
        """判断 key（群号或 global）是否处于冷却中，并顺手清理已过期的记录。"""
        until = self._cooldown_until.get(key, 0.0)
        if time.time() >= until:
            self._cooldown_until.pop(key, None)
            return False
        return True

    async def _fire_pokes(self, event: AstrMessageEvent, target_uid: str, group_id: str, times: int) -> bool:
        """连续发送戳一戳，返回是否全部成功。

        相邻两次戳之间按 poke_interval 配置停顿，避免触发平台风控。
        """
        payload = {"user_id": target_uid, "group_id": group_id}
        interval = max(0.0, float(self.config.get("poke_interval", 0.5)))
        for i in range(times):
            try:
                await event.bot.api.call_action("send_poke", **payload)
            except Exception as exc:
                logger.warning(f"[Venus] 发送戳一戳失败: {exc}")
                return False
            if interval > 0 and i < times - 1:
                await asyncio.sleep(interval)
        return True

    @event_message_type(EventMessageType.GROUP_MESSAGE)
    async def handle_group_message(self, event: AstrMessageEvent):
        if not self.config.get("enable", True):
            return

        message_str = event.message_obj.message_str
        group_id = str(event.message_obj.group_id)

        matched = self._match_command(message_str)
        if matched is None:
            return
        _, intensive = matched

        # 根据模式（普通/加强）计算本次戳一戳次数
        if intensive:
            lo = self.config.get("intensive_min_pokes", 5)
            hi = self.config.get("intensive_max_pokes", 10)
        else:
            lo = self.config.get("min_pokes", 1)
            hi = self.config.get("max_pokes", 3)
        lo, hi = max(1, int(lo)), max(1, int(hi))
        poke_times = random.randint(min(lo, hi), max(lo, hi))

        # 解析消息中被 @ 的目标
        target_uid = next(
            (str(seg.qq) for seg in event.get_messages() if isinstance(seg, Comp.At)),
            None,
        )
        if target_uid is None:
            if self.config.get("require_at", True):
                if self.config.get("reply_on_no_target", True):
                    yield event.plain_result(self._pick("no_target_messages"))
                return
            # 不要求 @ 时，默认对指令发送者本人发动攻击（戳一戳）
            target_uid = event.get_sender_id()

        # 不允许对机器人本体发动攻击
        if self.config.get("block_self_poke", True) and target_uid == event.get_self_id():
            yield event.plain_result(self._pick("self_poke_messages"))
            return

        # 冷却判定（按群或全局）
        cool_key = group_id if self.config.get("per_group_cooldown", True) else "global"
        if self._in_cooldown(cool_key):
            yield event.plain_result(self._pick("cooldown_messages"))
            return

        yield event.plain_result(self._pick("confirm_messages"))

        success = await self._fire_pokes(event, target_uid, group_id, poke_times)
        if not success and self.config.get("notify_poke_failure", True):
            yield event.plain_result(self._pick("poke_failed_messages"))

        # 无论成败都进入冷却，防止刷屏
        cooldown = max(0, float(self.config.get("cooldown_seconds", 5)))
        self._cooldown_until[cool_key] = time.time() + cooldown
