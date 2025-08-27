import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.nodes.translation import translator_node

sample_text = """
夏日的黄昏，微风吹拂着窗帘，带来一丝丝晚香玉的甜味。我坐在书桌前，摊开一本旧书，但思绪早已飘到了窗外。天边，火烧云如同被打翻的颜料盒，将整个天空染成绚烂的橘红、深紫和金黄。城市的喧嚣在此刻变得遥远而模糊，只剩下蝉鸣声声，仿佛在诉说着一个古老而漫长的故事。

我抬头望向书架，那本尘封已久的日记本静静地躺在那里。它曾记录着我的青春、梦想和那些早已淡忘的面孔。每一页都像是一扇通往过去的门，门后是阳光明媚的校园、无忧无虑的笑声和那个曾经的自己。我犹豫着，最终还是伸出手，指尖触碰到粗糙的封面，一股冰冷的、熟悉的感觉涌上心头。

记忆的河流开始缓缓流淌，带着我回到了那个炎热的午后。那时，我们坐在梧桐树下，他用指尖在沙地上勾勒着未来的蓝图。他的眼神里充满了光芒，而我只是静静地听着，感受着那份属于年轻人的热烈与憧憬。一切都如此真实，仿佛昨日重现。我闭上眼睛，试图抓住那份温度，但当再次睁开时，眼前只剩下了书桌上微弱的台灯光芒和窗外渐渐黯淡的夜色。
"""
state_input = {"text": sample_text, "language": "Chinese"}
print(translator_node(state_input))
