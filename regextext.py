import re

text = """
<index 5>
He placed the card upon the desk and once again closed his eyes, silently reciting in his heart a prayer:
</index 5>
<index 4>
He placed the card upon the desk and once again closed his eyes, silently reciting in his heart a prayer:
</index 6>
<index 7>
He placed the card upon the desk and once again closed his eyes, silently reciting in his heart a prayer:
</index 7>
"""

# Capture index numbers + text
pattern = r"<index (\d+)>\s*(.*?)\s*</index \1>"
matches = re.findall(pattern, text, re.DOTALL)

print(matches)

for idx, content in matches:
    print(f"Index {idx}: {content.strip()}")
