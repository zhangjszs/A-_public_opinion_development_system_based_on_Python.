import csv
import os

# --- 配置 ---
# 请确保这个路径与您之前脚本中使用的路径完全一致
csv_file_path = r'spider/navData.csv'
# --- 配置结束 ---

type_count = 0
file_exists = False
has_header = False
has_data = False

print(f"开始检查文件: {csv_file_path}")

# 检查文件是否存在
if os.path.exists(csv_file_path):
    file_exists = True
    print("文件存在，尝试读取...")
    try:
        # 使用 'utf8' 编码打开文件，与您原脚本一致
        with open(csv_file_path, mode='r', encoding='utf8', newline='') as csvfile:
            reader = csv.reader(csvfile)
            try:
                # 尝试读取并跳过表头
                header = next(reader)
                has_header = True
                print(f"已跳过表头: {header}")

                # 遍历剩余的行并计数
                for row in reader:
                    # 确保行不是空的，防止计入空行
                    if row:
                        type_count += 1
                        has_data = True

                if has_data:
                    print(f"\n统计完成：'{os.path.basename(csv_file_path)}' 文件中包含 {type_count} 种类型（数据行）。")
                elif has_header:
                     print(f"\n注意：文件 '{os.path.basename(csv_file_path)}' 只有表头，没有找到有效的数据行（类型）。")
                # 如果连表头都没有（空文件），StopIteration会处理

            except StopIteration:
                # 文件是空的，或者只有一行（被认为是表头但后面没数据了）
                 if has_header:
                     print(f"\n注意：文件 '{os.path.basename(csv_file_path)}' 只有表头，没有数据行。")
                 else:
                     print(f"\n错误：文件 '{os.path.basename(csv_file_path)}' 是空的。")
                 type_count = 0 # 确保计数为0

            except Exception as e:
                print(f"\n读取或处理文件时发生错误: {e}")
                type_count = -1 # 使用-1表示读取出错

    except Exception as e:
        print(f"\n打开文件时发生错误: {e}")
        type_count = -1 # 使用-1表示打开出错

else:
    print(f"错误：在指定路径找不到文件 '{csv_file_path}'。请检查路径是否正确。")
    type_count = -1 # 使用-1表示文件不存在

# 最终总结
print("-" * 20)
if type_count > 0:
    print(f"最终结果：找到 {type_count} 种类型。")
elif type_count == 0 and file_exists and has_header:
     print("最终结果：文件有效但类型数量为 0。")
elif type_count == 0 and file_exists and not has_header:
     print("最终结果：文件为空，类型数量为 0。")
elif type_count == -1:
    print("最终结果：由于发生错误，无法确定类型数量。请检查上面的错误信息。")
print("-" * 20)

# 如果你想在脚本结束后直接获取这个数字，可以取消下面一行的注释
# print(type_count)