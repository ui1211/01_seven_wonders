# src/data/cards.py
from src.model.card import Card


def create_cards():
    return [
        Card("目星", 90, 14, 0, 0, 4),
        Card("聞き耳", 90, 0, 14, 0, 4),
        Card("図書館", 86, 0, 0, 12, 3),
        Card("追跡", 84, 0, 10, 8, 3),
        Card("回避", 82, 18, 0, 0, 8),
        Card("応急手当", 82, 0, 18, 0, 8),
        Card("言いくるめ", 85, 0, 0, 16, 7),
        Card("こぶし", 78, 22, 0, 0, 11),
        Card("心理学", 80, 14, 10, 0, 8),
        Card("隠れる", 80, 10, 0, 12, 8),
        Card("精神分析", 78, 0, 14, 10, 8),
        Card("組み付き", 74, 24, 0, 0, 12),
        Card("クトゥルフ神話", 62, 30, 0, 0, 16),
        Card("芸術:夢見", 60, 0, 0, 26, 14),
        Card("オカルト", 58, 0, 28, 0, 15),
        Card("狂気のひらめき", 52, 34, 0, 0, 18),
        Card("幸運", 100, 0, 0, 0, -12),
        Card("信用", 92, 0, 0, 0, -16),
        Card("投擲", 70, 20, 0, 0, 6),
        Card("説得", 76, 0, 0, 18, 9),
    ]


def create_reward_cards():
    return [
        Card("救急箱", 100, 0, 0, 0, -18),
        Card("幸運の護符", 95, 0, 0, 0, -12),
        Card("退魔の符", 78, 22, 12, 0, 7),
        Card("古文書の断片", 82, 0, 10, 20, 6),
        Card("証言メモ", 88, 0, 0, 20, 4),
    ]


def create_topic_card(topic_text: str):
    label = str(topic_text).strip() or "話題"
    short = label[:6]
    return Card(f"話題:{short}", 84, 0, 6, 22, 5)
