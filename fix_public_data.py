import os

file_path = r'd:\coding\Pycharm\基于python微博舆情分析可视化系统\src\utils\getPublicData.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
imported = False
for i, line in enumerate(lines):
    new_lines.append(line)
    if '"""获取词频统计数据"""' in line and not imported:
        new_lines.append('    import os\n')
        imported = True

# Convert back to string to handle duplicate main block
content = "".join(new_lines)

# Remove duplicate main block at the end (keep only the first one if multiple exist, or just ensure only one exists)
# The file has two identical blocks at the end.
expected_block = """if __name__ == '__main__':
    print(getAllCiPingTotal())
"""

# Count occurrences
if content.count(expected_block.strip()) > 1:
    print("Found duplicate main blocks, removing one...")
    # Keep everything up to the last occurrence
    # Actually, simplistic approach: find the last occurrence and remove it
    last_idx = content.rfind("if __name__ == '__main__':")
    if last_idx > 0:
        # Check if it's indeed a duplicate (i.e., there's another one before)
        first_idx = content.find("if __name__ == '__main__':")
        if first_idx != last_idx:
            content = content[:last_idx]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully fixed getPublicData.py")
