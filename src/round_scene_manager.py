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
            "かすかな灯りが壁を照らしている。",
            "天井から水滴が落ちる音が響く。",
            "重たい扉が軋みながら揺れている。",
            "足音がやけに大きく反響した。",
            "どこからともなく視線を感じる。",
            "古びた紋様が床に刻まれている。",
            "冷え切った石壁に触れた。",
            "遠くで風が唸り声のように鳴る。",
            "空気が淀み、息苦しさを覚える。",
            "灯りが一瞬だけ揺らめいた。",
            "足元で砂がわずかに崩れた。",
            "奥から低い振動が伝わってくる。",
            "壁の隙間から微かな光が漏れている。",
            "鼓動だけがやけに大きく聞こえる。",
        ]

        self.current_intro = ""

    def start_round_intro(self):
        self.current_intro = random.choice(self.intro_pool)
        return self.current_intro

    def get_current_intro(self):
        return self.current_intro
