import os

def classify_satellites():
    """读取卫星位置文件并按照最后一列进行分类"""
    
    # 输入文件路径
    input_file = "SatellitePositions/time_step_3500.txt"
    
    # 确保输出目录存在
    output_dir = "classified_gs"
    os.makedirs(output_dir, exist_ok=True)
    
    # 输出文件路径
    output_files = {
        1: os.path.join(output_dir, "starlink_gs.txt"),
        2: os.path.join(output_dir, "oneweb_gs.txt"),
        3: os.path.join(output_dir, "telesat_gs.txt")
    }
    
    # 初始化输出文件（清空内容）
    for file_path in output_files.values():
        with open(file_path, 'w') as f:
            pass  # 创建空文件
    
    # 统计计数器
    counts = {1: 0, 2: 0, 3: 0}
    
    # 读取输入文件并分类
    try:
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) < 4:
                    print(f"警告：第{line_num}行格式不正确: {line}")
                    continue
                
                try:
                    # 解析最后一列（标签）
                    tag = int(parts[-1])
                    
                    if tag in output_files:
                        # 将整行写入对应的文件
                        with open(output_files[tag], 'a') as f:
                            f.write(line + '\n')
                        counts[tag] += 1
                    else:
                        print(f"警告：第{line_num}行标签未知: {tag}")
                        
                except ValueError:
                    print(f"警告：第{line_num}行标签无法解析为整数: {parts[-1]}")
                    
    except FileNotFoundError:
        print(f"错误：找不到输入文件 {input_file}")
        return
    
    # 打印统计结果
    print("分类完成！统计结果：")
    print(f"Starlink (标签1): {counts[1]} 个卫星")
    print(f"OneWeb (标签2): {counts[2]} 个卫星")
    print(f"Telesat (标签3): {counts[3]} 个卫星")
    print(f"总计: {sum(counts.values())} 个卫星")
    
    # 显示输出文件
    print("\n输出文件：")
    for tag, file_path in output_files.items():
        if os.path.exists(file_path):
            constellation_names = {1: "Starlink", 2: "OneWeb", 3: "Telesat"}
            print(f"{constellation_names[tag]}: {file_path}")

if __name__ == "__main__":
    classify_satellites()
