#!/usr/bin/env python3
"""
实时预警服务模块
功能：舆情预警规则引擎、阈值检测、情感突变检测
"""

import json
import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class AlertType(Enum):
    """预警类型"""
    VOLUME_SPIKE = "volume_spike"
    NEGATIVE_SURGE = "negative_surge"
    SENTIMENT_SHIFT = "sentiment_shift"
    KEYWORD_MATCH = "keyword_match"
    HOT_TOPIC = "hot_topic"
    CUSTOM = "custom"


@dataclass
class AlertRule:
    """预警规则"""
    id: str
    name: str
    alert_type: AlertType
    level: AlertLevel
    enabled: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    cooldown_minutes: int = 30
    last_triggered: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'alert_type': self.alert_type.value,
            'level': self.level.value,
            'enabled': self.enabled,
            'conditions': self.conditions,
            'cooldown_minutes': self.cooldown_minutes,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None
        }


@dataclass
class Alert:
    """预警消息"""
    id: str
    rule_id: str
    rule_name: str
    alert_type: AlertType
    level: AlertLevel
    title: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    is_read: bool = False

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'alert_type': self.alert_type.value,
            'level': self.level.value,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read
        }


class AlertRuleEngine:
    """预警规则引擎"""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alert_history: List[Alert] = []
        self.max_history = 1000
        self._lock = threading.Lock()
        self._callbacks: List[Callable[[Alert], None]] = []

        self._init_default_rules()

    def _init_default_rules(self):
        """初始化默认预警规则"""
        default_rules = [
            AlertRule(
                id="negative_surge",
                name="负面舆情激增",
                alert_type=AlertType.NEGATIVE_SURGE,
                level=AlertLevel.DANGER,
                conditions={
                    "threshold": 50,
                    "time_window_minutes": 30,
                    "comparison": "greater_than"
                },
                cooldown_minutes=30
            ),
            AlertRule(
                id="volume_spike",
                name="讨论量异常增长",
                alert_type=AlertType.VOLUME_SPIKE,
                level=AlertLevel.WARNING,
                conditions={
                    "multiplier": 3.0,
                    "time_window_minutes": 60,
                    "min_baseline": 10
                },
                cooldown_minutes=60
            ),
            AlertRule(
                id="sentiment_shift",
                name="情感倾向突变",
                alert_type=AlertType.SENTIMENT_SHIFT,
                level=AlertLevel.WARNING,
                conditions={
                    "change_threshold": 0.3,
                    "time_window_minutes": 30
                },
                cooldown_minutes=30
            ),
            AlertRule(
                id="hot_topic",
                name="热点话题出现",
                alert_type=AlertType.HOT_TOPIC,
                level=AlertLevel.INFO,
                conditions={
                    "min_mentions": 100,
                    "time_window_minutes": 60
                },
                cooldown_minutes=60
            )
        ]

        for rule in default_rules:
            self.rules[rule.id] = rule

        logger.info(f"已加载 {len(self.rules)} 条默认预警规则")

    def add_rule(self, rule: AlertRule):
        """添加预警规则"""
        with self._lock:
            self.rules[rule.id] = rule
            logger.info(f"添加预警规则: {rule.name}")

    def remove_rule(self, rule_id: str) -> bool:
        """移除预警规则"""
        with self._lock:
            if rule_id in self.rules:
                del self.rules[rule_id]
                logger.info(f"移除预警规则: {rule_id}")
                return True
            return False

    def update_rule(self, rule_id: str, **kwargs) -> bool:
        """更新预警规则"""
        with self._lock:
            if rule_id not in self.rules:
                return False

            rule = self.rules[rule_id]
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)

            logger.info(f"更新预警规则: {rule_id}")
            return True

    def register_callback(self, callback: Callable[[Alert], None]):
        """注册预警回调函数"""
        self._callbacks.append(callback)

    def _trigger_callbacks(self, alert: Alert):
        """触发回调函数"""
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"预警回调执行失败: {e}")

    def check_cooldown(self, rule: AlertRule) -> bool:
        """检查规则冷却时间"""
        if rule.last_triggered is None:
            return True

        elapsed = datetime.now() - rule.last_triggered
        return elapsed >= timedelta(minutes=rule.cooldown_minutes)

    def _create_alert(self, rule: AlertRule, title: str, message: str, data: Dict = None) -> Alert:
        """创建预警消息"""
        import uuid

        alert = Alert(
            id=str(uuid.uuid4()),
            rule_id=rule.id,
            rule_name=rule.name,
            alert_type=rule.alert_type,
            level=rule.level,
            title=title,
            message=message,
            data=data or {}
        )

        return alert

    def evaluate_volume_spike(self, current_count: int, baseline_count: int, time_window: int = 60) -> Optional[Alert]:
        """评估讨论量异常增长"""
        rule = self.rules.get("volume_spike")
        if not rule or not rule.enabled:
            return None

        if not self.check_cooldown(rule):
            return None

        conditions = rule.conditions
        multiplier = conditions.get("multiplier", 3.0)
        min_baseline = conditions.get("min_baseline", 10)

        if baseline_count < min_baseline:
            baseline_count = min_baseline

        if current_count >= baseline_count * multiplier:
            rule.last_triggered = datetime.now()

            alert = self._create_alert(
                rule,
                title="讨论量异常增长",
                message=f"过去{time_window}分钟内讨论量达到{current_count}条，是基线{baseline_count}的{current_count/max(baseline_count,1):.1f}倍",
                data={
                    "current_count": current_count,
                    "baseline_count": baseline_count,
                    "multiplier": current_count / max(baseline_count, 1),
                    "time_window": time_window
                }
            )

            self._add_to_history(alert)
            self._trigger_callbacks(alert)
            return alert

        return None

    def evaluate_negative_surge(self, negative_count: int, total_count: int, time_window: int = 30) -> Optional[Alert]:
        """评估负面舆情激增"""
        rule = self.rules.get("negative_surge")
        if not rule or not rule.enabled:
            return None

        if not self.check_cooldown(rule):
            return None

        conditions = rule.conditions
        threshold = conditions.get("threshold", 50)

        if negative_count >= threshold:
            rule.last_triggered = datetime.now()

            negative_ratio = negative_count / max(total_count, 1) * 100

            alert = self._create_alert(
                rule,
                title="负面舆情激增",
                message=f"过去{time_window}分钟内检测到{negative_count}条负面评论，占比{negative_ratio:.1f}%",
                data={
                    "negative_count": negative_count,
                    "total_count": total_count,
                    "negative_ratio": negative_ratio,
                    "time_window": time_window
                }
            )

            self._add_to_history(alert)
            self._trigger_callbacks(alert)
            return alert

        return None

    def evaluate_sentiment_shift(self, current_sentiment: float, previous_sentiment: float, time_window: int = 30) -> Optional[Alert]:
        """评估情感倾向突变"""
        rule = self.rules.get("sentiment_shift")
        if not rule or not rule.enabled:
            return None

        if not self.check_cooldown(rule):
            return None

        conditions = rule.conditions
        change_threshold = conditions.get("change_threshold", 0.3)

        sentiment_change = abs(current_sentiment - previous_sentiment)

        if sentiment_change >= change_threshold:
            rule.last_triggered = datetime.now()

            direction = "下降" if current_sentiment < previous_sentiment else "上升"

            alert = self._create_alert(
                rule,
                title="情感倾向突变",
                message=f"过去{time_window}分钟内情感指数{direction}{sentiment_change:.2f}，当前情感指数{current_sentiment:.2f}",
                data={
                    "current_sentiment": current_sentiment,
                    "previous_sentiment": previous_sentiment,
                    "sentiment_change": sentiment_change,
                    "direction": direction,
                    "time_window": time_window
                }
            )

            self._add_to_history(alert)
            self._trigger_callbacks(alert)
            return alert

        return None

    def evaluate_keyword_match(self, text: str, keywords: List[str]) -> Optional[Alert]:
        """评估关键词匹配"""
        rule = self.rules.get("keyword_match")
        if not rule or not rule.enabled:
            return None

        if not self.check_cooldown(rule):
            return None

        matched_keywords = [kw for kw in keywords if kw in text]

        if matched_keywords:
            rule.last_triggered = datetime.now()

            alert = self._create_alert(
                rule,
                title="敏感关键词匹配",
                message=f"检测到敏感关键词: {', '.join(matched_keywords)}",
                data={
                    "matched_keywords": matched_keywords,
                    "text_preview": text[:100]
                }
            )

            self._add_to_history(alert)
            self._trigger_callbacks(alert)
            return alert

        return None

    def evaluate_hot_topic(self, topic_mentions: int, topic_name: str, time_window: int = 60) -> Optional[Alert]:
        """评估热点话题"""
        rule = self.rules.get("hot_topic")
        if not rule or not rule.enabled:
            return None

        if not self.check_cooldown(rule):
            return None

        conditions = rule.conditions
        min_mentions = conditions.get("min_mentions", 100)

        if topic_mentions >= min_mentions:
            rule.last_triggered = datetime.now()

            alert = self._create_alert(
                rule,
                title="热点话题出现",
                message=f"话题「{topic_name}」在过去{time_window}分钟内被提及{topic_mentions}次",
                data={
                    "topic_name": topic_name,
                    "topic_mentions": topic_mentions,
                    "time_window": time_window
                }
            )

            self._add_to_history(alert)
            self._trigger_callbacks(alert)
            return alert

        return None

    def _add_to_history(self, alert: Alert):
        """添加到预警历史"""
        with self._lock:
            self.alert_history.append(alert)
            if len(self.alert_history) > self.max_history:
                self.alert_history = self.alert_history[-self.max_history:]

    def get_alert_history(self, limit: int = 50, level: str = None, unread_only: bool = False) -> List[Dict]:
        """获取预警历史"""
        with self._lock:
            alerts = self.alert_history.copy()

        if level:
            alerts = [a for a in alerts if a.level.value == level]

        if unread_only:
            alerts = [a for a in alerts if not a.is_read]

        alerts = sorted(alerts, key=lambda x: x.created_at, reverse=True)

        return [a.to_dict() for a in alerts[:limit]]

    def mark_alert_read(self, alert_id: str) -> bool:
        """标记预警已读"""
        with self._lock:
            for alert in self.alert_history:
                if alert.id == alert_id:
                    alert.is_read = True
                    return True
        return False

    def mark_all_read(self) -> int:
        """标记所有预警已读"""
        count = 0
        with self._lock:
            for alert in self.alert_history:
                if not alert.is_read:
                    alert.is_read = True
                    count += 1
        return count

    def get_unread_count(self) -> int:
        """获取未读预警数量"""
        with self._lock:
            return sum(1 for a in self.alert_history if not a.is_read)

    def get_rules(self) -> List[Dict]:
        """获取所有规则"""
        with self._lock:
            return [rule.to_dict() for rule in self.rules.values()]

    def get_stats(self) -> Dict:
        """获取预警统计"""
        with self._lock:
            alerts = self.alert_history

        level_counts = defaultdict(int)
        type_counts = defaultdict(int)

        for alert in alerts:
            level_counts[alert.level.value] += 1
            type_counts[alert.alert_type.value] += 1

        return {
            "total_alerts": len(alerts),
            "unread_count": sum(1 for a in alerts if not a.is_read),
            "level_distribution": dict(level_counts),
            "type_distribution": dict(type_counts),
            "active_rules": sum(1 for r in self.rules.values() if r.enabled)
        }


alert_engine = AlertRuleEngine()
