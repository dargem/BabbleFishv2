"""Test fixtures and sample data for translation tests."""

# Sample Chinese text for testing
CHINESE_SAMPLE_TEXT = """
夏日的黄昏，微风吹拂着窗帘，带来一丝丝晚香玉的甜味。我坐在书桌前，摊开一本旧书，但思绪早已飘到了窗外。天边，火烧云如同被打翻的颜料盒，将整个天空染成绚烂的橘红、深紫和金黄。城市的喧嚣在此刻变得遥远而模糊，只剩下蝉鸣声声，仿佛在诉说着一个古老而漫长的故事。

我抬头望向书架，那本尘封已久的日记本静静地躺在那里。它曾记录着我的青春、梦想和那些早已淡忘的面孔。每一页都像是一扇通往过去的门，门后是阳光明媚的校园、无忧无虑的笑声和那个曾经的自己。我犹豫着，最终还是伸出手，指尖触碰到粗糙的封面，一股冰冷的、熟悉的感觉涌上心头。

记忆的河流开始缓缓流淌，带着我回到了那个炎热的午后。那时，我们坐在梧桐树下，他用指尖在沙地上勾勒着未来的蓝图。他的眼神里充满了光芒，而我只是静静地听着，感受着那份属于年轻人的热烈与憧憬。一切都如此真实，仿佛昨日重现。我闭上眼睛，试图抓住那份温度，但当再次睁开时，眼前只剩下了书桌上微弱的台灯光芒和窗外渐渐黯淡的夜色。
"""

ENGLISH_SAMPLE_TEXT = """
In October 1998, Clara Mendoza moved from Seville, Spain, to Brighton, England, to begin her studies at the University of Sussex. She had received a scholarship from the British Council to pursue a degree in History of Art.

Her first professor, Dr. Martin Holloway, introduced her to archival work at the Victoria and Albert Museum in London. There, Clara uncovered letters written in 1872 by Eleanor Whitcombe, a painter who exhibited in the Royal Academy of Arts.
"""

# Sample English translation for testing
ENGLISH_SAMPLE_TRANSLATION = """
As the summer dusk settled, a gentle breeze stirred the curtains, carrying with it the sweet scent of tuberose. I sat at my desk, an old book open before me, but my thoughts had long since drifted out the window. The horizon was ablaze with sunset clouds, like an overturned paint palette, staining the entire sky with brilliant hues of fiery orange, deep violet, and shimmering gold. The city's clamor faded into a distant, hazy hum, leaving only the persistent chirping of cicadas, as if they were recounting an ancient, timeless tale.

My gaze drifted to the bookshelf, where a long-forgotten diary lay nestled. It once held the records of my youth, my dreams, and faces I had since blurred from memory. Each page felt like a doorway to the past, opening onto sun-drenched school grounds, carefree laughter, and the person I used to be. A moment of hesitation, and then my hand reached out. My fingertips brushed against the rough cover, sending a familiar, cool sensation through me.

The river of memory began to flow, carrying me back to a sweltering afternoon. We sat beneath a plane tree, and with his fingertip, he sketched out blueprints for the future in the sand. His eyes shone with an inner light, while I simply listened, absorbing the fervent passion and hopeful aspirations of youth. It all felt so vivid, as if it were yesterday. I closed my eyes, trying to hold onto that warmth, but when I opened them again, only the faint glow of the desk lamp and the deepening twilight outside the window remained.
"""

# Minimal text samples for unit tests
MINIMAL_CHINESE_TEXT = "你好，世界！"
MINIMAL_ENGLISH_TEXT = "Hello, world!"

# Test state objects
TEST_TRANSLATION_STATE = {
    "text": CHINESE_SAMPLE_TEXT,
    "language": "Chinese",
    "translation": ENGLISH_SAMPLE_TRANSLATION,
    "feedback": "The translation captures the poetic nature well.",
    "feedback_rout_loops": 1,
}

# Mock LLM responses for testing
MOCK_STYLE_GUIDE = """
## **1. Genre and Subgenre**
Literary fiction with introspective and nostalgic elements.

## **2. Literary Style and Techniques**
- **Sentence Structure:** Long, flowing sentences with poetic rhythm
- **Pacing:** Slow and reflective
- **Prose Style:** Lyrical and atmospheric
"""

MOCK_FEEDBACK_APPROVED = "approved response accepted - The translation maintains the poetic quality and emotional depth of the original text."

MOCK_FEEDBACK_REJECTED = "The translation lacks the lyrical quality of the original. Please improve the flow and maintain the poetic atmosphere."

ENGLISH_SAMPLE_TEXT_ENTITIES = """
New Avalon, Crystal Spire, Captain Lyra Vey, Lyra Vey, Interstellar Fleet, Codex of Thalos
"""