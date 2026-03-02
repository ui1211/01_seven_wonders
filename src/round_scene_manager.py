# src/scene/round_scene_manager.py
import random


class RoundSceneManager:
    def __init__(self):
        self.intro_pool = [
            "薄暗い廊下に足を踏み入れた。",
            "冷たい空気が肌を刺す。",
            "遠くで何かが軋む音がした。",
            "足元に不気味な影が伸びる。",
            "異様な気配が漂っている。",
            "静寂が支配している。",
        ]

        self.current_intro = ""

    def start_round_intro(self):
        self.current_intro = random.choice(self.intro_pool)
        return self.current_intro

    def get_current_intro(self):
        return self.current_intro
