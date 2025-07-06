import math
import os

def LongitudeAndLatitudeToDescartesPoints(satellites):
    result = []
    for sat in satellites:
        R = 6371.0 + sat[2]
        lon_rad = math.radians(sat[0])
        lat_rad = math.radians(sat[1])
        x = R * math.cos(lat_rad) * math.cos(lon_rad)
        y = R * math.cos(lat_rad) * math.sin(lon_rad)
        z = R * math.sin(lat_rad)
        result.append([x, y, z])
    return result

class Sat:
    def __init__(self, x, y, z, SNO):
        self.x = x
        self.y = y
        self.z = z
        self.SNO = SNO

class User:
    def __init__(self, name, x, y, z):
        self.name = name
        self.x = x
        self.y = y
        self.z = z

def process_user(user, satellites_position_by_timeslot, min_elevation_angle, output_dir):
    user_x = user.x
    user_y = user.y
    user_z = user.z
    user_connected_SNO_by_timeslot = []

    for satellites_position in satellites_position_by_timeslot:
        now_connected_SNO = None
        now_connected_satellite_satellite = 1000  # Initialize a large value
        for sat in satellites_position:
            vector1 = [-user_x, -user_y, -user_z]
            vector2 = [sat.x - user_x, sat.y - user_y, sat.z - user_z]
            dot_product = (vector1[0] * vector2[0] +
                           vector1[1] * vector2[1] +
                           vector1[2] * vector2[2])
            magnitude1 = math.sqrt(vector1[0]**2 + vector1[1]**2 + vector1[2]**2)
            magnitude2 = math.sqrt(vector2[0]**2 + vector2[1]**2 + vector2[2]**2)
            cos_angle = dot_product / (magnitude1 * magnitude2)
            angle = math.acos(cos_angle) * (180 / math.pi)

            if angle >= 90 + min_elevation_angle and 180 - angle < now_connected_satellite_satellite:
                now_connected_SNO = sat.SNO
                now_connected_satellite_satellite = 180 - angle
        user_connected_SNO_by_timeslot.append(now_connected_SNO)

    # Write results to a file
    output_path = os.path.join(output_dir, f"{user.name}_connected_SNO.txt")
    with open(output_path, 'w') as f:
        for sno in user_connected_SNO_by_timeslot:
            f.write(f"{sno}\n")

if __name__ == "__main__":
    """
    # Load satellite positions
    satellites_position_by_timeslot = []
    satellite_files = [f for f in os.listdir('SatellitePositions') if f.endswith('.txt')]
    for file in satellite_files:
        file_path = os.path.join('SatellitePositions', file)
        with open(file_path, 'r') as f:
            lines = f.readlines()
            satellites = []
            for line in lines:
                parts = line.strip().split(' ')
                satellite_xyz = LongitudeAndLatitudeToDescartesPoints([[float(parts[0]), float(parts[1]), float(parts[2])]])[0]
                satellites.append(Sat(satellite_xyz[0], satellite_xyz[1], satellite_xyz[2], int(parts[3])))
            satellites_position_by_timeslot.append(satellites)

    # Load user locations
    users = []
    with open('user_locations.txt', 'r') as f:
        for line in f:
            user_location_data = line.strip()
            user_coordinates = user_location_data.split(' ')
            user_name = user_coordinates[0]
            user_longitude = float(user_coordinates[1])
            user_latitude = float(user_coordinates[2])
            user_xyz = LongitudeAndLatitudeToDescartesPoints([[user_longitude, user_latitude, 0]])[0]
            users.append(User(user_name, user_xyz[0], user_xyz[1], user_xyz[2]))

    # Minimum elevation angle
    min_elevation_angle = 25  # degrees

    # Output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Create processes for each user
    processes = []
    cpu_cores = cpu_count()  # Get the number of CPU cores
    for i in range(cpu_cores):
        for user in users:
            p = Process(target=process_user, args=(user, satellites_position_by_timeslot, min_elevation_angle, output_dir))
            processes.append(p)
            p.start()

    # Wait for all processes to finish
    for p in processes:
        p.join()
    """


    # 上面将每个用户在每个时间片的SNO计算出来了，现在统计每个用户的切换次数
    user_switch_count = {}
    output_dir = "output"
    user_files = [f for f in os.listdir(output_dir) if f.endswith('_connected_SNO.txt')]
    for user_file in user_files:
        user_name = user_file.split('_')[0] + "_" + user_file.split('_')[1]
        with open(os.path.join(output_dir, user_file), 'r') as f:
            sno_list = f.readlines()
            sno_list = [sno.strip() for sno in sno_list]
            switch_count = 0
            last_sno = None
            for sno in sno_list:
                if sno != last_sno:
                    switch_count += 1
                    last_sno = sno
            user_switch_count[user_name] = switch_count

    # 按照用户名的前两个字符进行分类，因为前两个字符表示用户所属的大洲。key是大洲名称，value是一个list，表示该大洲所有用户的切换次数
    continent_switch_count = {}
    for user_name, switch_count in user_switch_count.items():
        continent = user_name[:2]  # 前两个字符表示大洲
        if continent not in continent_switch_count:
            continent_switch_count[continent] = []
        continent_switch_count[continent].append(switch_count/24)

    # 输出每个大洲的list
    for continent, switch_counts in continent_switch_count.items():
        print(f"Continent: {continent}, Switch Counts: {switch_counts}")

    # 画图：将每个大洲的切换次数画成小提琴图，x轴表示大洲名称，y轴表示切换次数
    import matplotlib.pyplot as plt
    import matplotlib
    
    # 设置字体为学术论文标准
    matplotlib.rcParams["font.family"] = "serif"
    plt.rcParams["pdf.fonttype"] = 42
    
    # 准备数据
    continent_names = list(continent_switch_count.keys())
    continent_data = list(continent_switch_count.values())
    
    # 创建图形 - 调整为与参考脚本一致的比例 (12, 8->7)
    plt.figure(figsize=(12, 7))
    ax1 = plt.gca()
    
    # 创建小提琴图，使用更宽的宽度以在每个隔间中占据更多空间
    parts = ax1.violinplot(continent_data, positions=range(len(continent_names)), 
                          widths=0.3, showmeans=True, showmedians=True)
    
    # 定义与附图类似的颜色方案
    # colors = ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377']
    # colors = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948']
    # colors = ['#E69F00', '#56B4E9', '#009E73', '#0072B2', '#D55E00', '#CC79A7']
    # colors = ['#8C564B', '#7F7F7F', '#9467BD', '#17BECF', '#BCBD22', '#E377C2']
    # colors = ['#B2182B', '#1B7837', '#2166AC', '#D95F02', '#84542B', '#69408A']
    colors = ["#d80007ff", '#0e8e0e', '#0000ff', '#D95F02', '#84542B', '#69408A']
    
    # 设置小提琴图的颜色和透明度
    for i, pc in enumerate(parts['bodies']):
        color = colors[i % len(colors)]
        pc.set_facecolor(color)
        pc.set_alpha(0.95)
        pc.set_edgecolor('black')
        pc.set_linewidth(2.0)  # 加粗边框线以增强视觉效果
    
    # 设置其他部分的颜色 - 使用黑色以保持专业外观
    parts['cmeans'].set_color('black')
    parts['cmeans'].set_linewidth(2.0)
    parts['cmedians'].set_color('black')
    parts['cmedians'].set_linewidth(2.0)
    parts['cbars'].set_color('black')
    parts['cbars'].set_linewidth(1.5)
    parts['cmins'].set_color('black')
    parts['cmins'].set_linewidth(1.5)
    parts['cmaxes'].set_color('black')
    parts['cmaxes'].set_linewidth(1.5)
    
    # 创建大洲简写到全称的映射
    continent_mapping = {
        'AF': 'AF',
        'AS': 'AS',
        'AU': 'AU',
        'EU': 'EU',
        'NA': 'NA',
        'SA': 'SA'
    }
    
    # 将简写转换为全称
    continent_full_names = [continent_mapping.get(name, name) for name in continent_names]
    
    # 设置坐标轴
    ax1.set_xticks(range(len(continent_names)))
    ax1.set_xticklabels(continent_full_names)
    ax1.set_xlim(-0.5, len(continent_names) - 0.5)
    
    # 计算Y轴范围，设置上限为70
    all_values = [val for sublist in continent_data for val in sublist]
    y_min = min(all_values)
    ax1.set_ylim(y_min * 0.9, 70)
    
    # 设置标签和字体 - 增大字号以提高可读性
    plt.ylabel("Inter-Handoff", fontsize=40, fontweight="demibold")
    # plt.ylabel("Inter-Handoff", fontsize=40)
    
    # 调整刻度字体大小和字体族 - 增大刻度标签字号
    ax1.tick_params(axis="x", labelsize=40)
    ax1.tick_params(axis="y", labelsize=35)
    
    # 设置刻度标签的字体为serif并加粗
    for label in ax1.get_xticklabels():
        label.set_fontfamily('serif')
        label.set_fontweight('demibold')
    
    for label in ax1.get_yticklabels():
        label.set_fontfamily('serif')
        label.set_fontweight('demibold')
    
    # 添加竖直分隔线，在每个大洲之间
    for i in range(1, len(continent_names)):
        ax1.axvline(x=i-0.5, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    
    # 调整布局并保存
    plt.tight_layout()
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    plt.savefig("./[Background]-Inter-Handover-Counts.pdf", bbox_inches="tight", dpi=300)







