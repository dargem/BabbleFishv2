import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.nodes.editing import fluency_editor_node

sample_translation = """
As the summer dusk settled, a gentle breeze stirred the curtains, carrying with it the sweet scent of tuberose. I sat at my desk, an old book open before me, but my thoughts had long since drifted out the window. The horizon was ablaze with sunset clouds, like an overturned paint palette, staining the entire sky with brilliant hues of fiery orange, deep violet, and shimmering gold. The city's clamor faded into a distant, hazy hum, leaving only the persistent chirping of cicadas, as if they were recounting an ancient, timeless tale.

My gaze drifted to the bookshelf, where a long-forgotten diary lay nestled. It once held the records of my youth, my dreams, and faces I had since blurred from memory. Each page felt like a doorway to the past, opening onto sun-drenched school grounds, carefree laughter, and the person I used to be. A moment of hesitation, and then my hand reached out. My fingertips brushed against the rough cover, sending a familiar, cool sensation through me.

The river of memory began to flow, carrying me back to a sweltering afternoon. We sat beneath a plane tree, and with his fingertip, he sketched out blueprints for the future in the sand. His eyes shone with an inner light, while I simply listened, absorbing the fervent passion and hopeful aspirations of youth. It all felt so vivid, as if it were yesterday. I closed my eyes, trying to hold onto that warmth, but when I opened them again, only the faint glow of the desk lamp and the deepening twilight outside the window remained.
"""

if __name__ == "__main__":
    state_input = {"translation": sample_translation}
    fluency_adjusted_translation = fluency_editor_node(state_input)[
        "fluent_translation"
    ]

    split_fluency_adjusted = fluency_adjusted_translation.split("\n\n")
    keyed_fluency_adjusted = {
        edit_index: text for edit_index, text in enumerate(split_fluency_adjusted)
    }

    split_sample = sample_translation.split("\n\n")
    keyed_sample = {edit_index: text for edit_index, text in enumerate(split_sample)}

    for key in keyed_sample:
        if keyed_sample[key] != keyed_fluency_adjusted[key]:
            print(f"original: {keyed_sample[key]}")
            print("\n")
            print(f"altered: {keyed_fluency_adjusted[key]}")
            print("\n")

    print(f"""
    Original: 
    {sample_translation}

    Fluent: 
    {fluency_adjusted_translation}
    """)
