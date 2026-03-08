# src/data/cards.py
from src.model.card import Card


def create_cards():
    base = [
        # Basic
        Card("速撃", 90, 14, 0, 0, 4),
        Card("火花術", 90, 0, 14, 0, 4),
        Card("読解", 86, 0, 0, 12, 3),
        Card("探り", 84, 0, 10, 8, 3),
        # Stable offense
        Card("強打", 82, 18, 0, 0, 8),
        Card("呪閃", 82, 0, 18, 0, 8),
        Card("対話集中", 85, 0, 0, 16, 7),
        Card("破点", 78, 22, 0, 0, 11),
        # Mixed
        Card("圧迫", 80, 14, 10, 0, 8),
        Card("虚突", 80, 10, 0, 12, 8),
        Card("制御", 78, 0, 14, 10, 8),
        Card("断裂", 74, 24, 0, 0, 12),
        # High risk / high reward
        Card("総力", 62, 30, 0, 0, 16),
        Card("深思", 60, 0, 0, 26, 14),
        Card("曇天術", 58, 0, 28, 0, 15),
        Card("賭け撃ち", 52, 34, 0, 0, 18),
        # Utility
        Card("深呼吸", 100, 0, 0, 0, -12),
        Card("防勢", 92, 0, 0, 0, -16),
        Card("幸運弾", 70, 20, 0, 0, 6),
        Card("対話整流", 76, 0, 0, 18, 9),
    ]

    return base
