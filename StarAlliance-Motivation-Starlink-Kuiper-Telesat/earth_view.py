import matplotlib.pyplot as plt
import os

# 尝试导入地图库
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.patches import Circle
    import cartopy.io.img_tiles as cimgt
    CARTOPY_AVAILABLE = True
    print("✓ Cartopy 已安装并可用")
except ImportError:
    CARTOPY_AVAILABLE = False
    print("✗ Cartopy 未安装")

try:
    from mpl_toolkits.basemap import Basemap
    BASEMAP_AVAILABLE = True
    print("✓ Basemap 已安装并可用")
except ImportError:
    BASEMAP_AVAILABLE = False
    print("✗ Basemap 未安装")

if not CARTOPY_AVAILABLE and not BASEMAP_AVAILABLE:
    print("\n警告：未安装 cartopy 或 basemap，请安装其中一个或两个都安装：")
    print("安装 Cartopy: pip install cartopy")
    print("安装 Basemap: pip install basemap")
    print("推荐使用 Cartopy，功能更强大且维护更好。")

CONSTELLATIONS = {
        'starlink': {'file': './classified_gs/starlink_gs.txt', 'color': "#7fcdbb", 'alpha': 0.5, 'label': 'Starlink'},
        'kuiper':   {'file': './classified_gs/kuiper_gs.txt',   'color': '#FDD835', 'alpha': 0.5, 'label': 'Kuiper'},
        'telesat':  {'file': './classified_gs/telesat_gs.txt',  'color': '#225ea8', 'alpha': 0.5, 'label': 'Telesat'}
    }

def read_satellite_data(file_path):
    """读取卫星数据文件"""
    satellites = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:
                    lon, lat, alt, tag = float(parts[0]), float(parts[1]), float(parts[2]), int(parts[3])
                    satellites.append((lon, lat, alt, tag))
    return satellites

def create_earth_base_cartopy():
    """创建基础的地球地图 - 矩形投影版本"""
    # 创建图形和地图投影 - 使用PlateCarree投影显示矩形区域
    fig = plt.figure(figsize=(14, 9))
    # 使用subplot参数最大化地图区域，减少空白边距
    # [left, bottom, width, height] - 精确控制地图位置和大小，最大化填充14×9画布
    ax = plt.axes(projection=ccrs.PlateCarree(), position=[0.01, 0.02, 0.98, 0.96])
    
    # 设置显示范围：经度-180到180度，纬度-90到90度
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
    
    # 添加高级地球特征 - 使用Natural Earth数据
    ax.add_feature(cfeature.LAND, color='#f0f0f0', alpha=0.8)  # 浅灰色陆地
    ax.add_feature(cfeature.OCEAN, color='#e6f3ff', alpha=0.8)  # 浅蓝色海洋
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, color='#2c3e50', alpha=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, alpha=0.6, color='#34495e')
    ax.add_feature(cfeature.LAKES, color='#e6f3ff', alpha=0.8)
    ax.add_feature(cfeature.RIVERS, color='#e6f3ff', alpha=0.6, linewidth=0.5)
    
    # 添加经纬网格 - 更精细的网格
    gl = ax.gridlines(draw_labels=True, dms=False, x_inline=False, y_inline=False,
                     alpha=0.4, linewidth=0.5, color='gray', linestyle='--')
    gl.xlabel_style = {'size': 14, 'color': 'black', 'weight': 'bold'}
    gl.ylabel_style = {'size': 14, 'color': 'black', 'weight': 'bold'}
    gl.xlocator = plt.FixedLocator([-180, -120, -60, 0, 60, 120, 180])
    gl.ylocator = plt.FixedLocator([-90, -60, -30, 0, 30, 60, 90])
    
    return fig, ax

def plot_constellation_coverage(ax, constellation_config, constellation_name):
    """在给定的地图上绘制单个星座的覆盖 - 美化版本"""
    satellite_data = read_satellite_data(constellation_config['file'])
    if not satellite_data:
        return 0, 700
    
    # 根据星座类型设置不同的覆盖半径
    if constellation_name == 'telesat':
        coverage_radius_km = 1000  # Telesat使用1000km半径
    elif constellation_name == 'kuiper':
        coverage_radius_km = 600
    else:
        coverage_radius_km = 600
    
    # 将km转换为度数（地球周长约40,075km，360度）
    coverage_radius_deg = coverage_radius_km * 360 / 40075
    
    for lon, lat, alt, tag in satellite_data:
        # 添加发光效果的覆盖圆圈
        # 外层光晕
        circle_glow = Circle((lon, lat), coverage_radius_deg * 1.2, 
                           facecolor=constellation_config['color'], 
                           edgecolor='none',
                           alpha=0.1,
                           transform=ccrs.PlateCarree())
        ax.add_patch(circle_glow)
        
        # 主覆盖圆圈
        circle = Circle((lon, lat), coverage_radius_deg, 
                       facecolor=constellation_config['color'], 
                       edgecolor=constellation_config['color'],
                       alpha=constellation_config['alpha'],
                       linewidth=0.3,
                       transform=ccrs.PlateCarree())
        ax.add_patch(circle)
        
        # 添加虚线外框 - 使边界更清晰
        circle_border = Circle((lon, lat), coverage_radius_deg, 
                             facecolor='none', 
                             edgecolor=constellation_config['color'],
                             linewidth=1.5,
                             linestyle='--',  # 虚线样式
                             alpha=0.8,
                             transform=ccrs.PlateCarree())
        ax.add_patch(circle_border)
        
        # 添加卫星位置点 - 更亮的点
        # ax.plot(lon, lat, 'o', color=constellation_config['color'], markersize=1.2, 
        #        markeredgecolor='black', markeredgewidth=0.3,
        #        transform=ccrs.PlateCarree(), alpha=0.8)
    
    return len(satellite_data), coverage_radius_km

def plot_single_constellation_cartopy(constellation_name):
    """绘制单个星座的覆盖图"""
    # 星座配置 - 与合并图使用相同的配色
    constellations = CONSTELLATIONS
    
    if constellation_name not in constellations:
        print(f"错误：未知星座 {constellation_name}")
        return
    
    # 创建基础地图
    fig, ax = create_earth_base_cartopy()
    
    # 绘制单个星座
    config = constellations[constellation_name]
    satellite_count, coverage_radius = plot_constellation_coverage(ax, config, constellation_name)
    
    if satellite_count == 0:
        print(f"警告：{config['label']} 数据文件不存在或为空")
        return
    
    # 添加美化图例 - 放在矩形区域内
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=config['color'], alpha=0.7, label=config['label'], 
                            edgecolor='black', linewidth=1)]
    legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=40, 
                      framealpha=0.9, facecolor='white', edgecolor='black')
    legend.get_frame().set_facecolor('white')
    for text in legend.get_texts():
        text.set_color('black')
        text.set_weight('bold')  # 设置图例文字为粗体
    
    # 设置美化标题 - 调整位置避免与经度刻度重叠
    # plt.suptitle(f'{config["label"]} Global Coverage', 
    #             fontsize=40, fontweight='bold', color='black', y=0.97)
    
    # 设置白色背景
    fig.patch.set_facecolor('white')
    
    # 保存图片
    filename = f'./[Background]-{config["label"]}-Coverage.pdf'
    # 手动调整布局以最大化地图区域 - 与axes position保持一致
    plt.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
    plt.savefig(filename, dpi=300, bbox_inches=None, 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✓ {config['label']} 覆盖图已保存: {filename}")

def plot_all_constellations_cartopy():
    """绘制所有星座的合并覆盖图"""
    # 星座配置
    constellations = CONSTELLATIONS
    
    # 创建基础地图
    fig, ax = create_earth_base_cartopy()
    
    total_satellites = 0
    legend_elements = []
    coverage_info = []
    
    # 绘制所有星座 - 按指定顺序：Telesat(底层) -> Starlink(中层) -> Kuiper(顶层)
    draw_order = ['telesat', 'starlink', 'kuiper']
    
    for constellation_name in draw_order:
        if constellation_name in constellations:
            config = constellations[constellation_name]
            satellite_count, coverage_radius = plot_constellation_coverage(ax, config, constellation_name)
            if satellite_count > 0:
                total_satellites += satellite_count
                coverage_info.append(f"{config['label']}: {satellite_count} sats ({coverage_radius}km)")
                print(f"绘制 {satellite_count} 个 {config['label']} 卫星覆盖区域 (半径: {coverage_radius}km) - {'顶层' if constellation_name=='kuiper' else '中层' if constellation_name=='starlink' else '底层'}")
                # 添加到图例
                from matplotlib.patches import Patch
                legend_elements.append(Patch(facecolor=config['color'], alpha=0.7, label=config['label'],
                                            edgecolor='black', linewidth=1))
    
    # 添加美化图例 - 放在矩形区域内
    if legend_elements:
        legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=40, 
                          framealpha=0.9, facecolor='white', edgecolor='black')
        legend.get_frame().set_facecolor('white')
        for text in legend.get_texts():
            text.set_color('black')
            text.set_weight('bold')  # 设置图例文字为粗体
    
    # 设置美化标题 - 调整位置避免与经度刻度重叠
    # plt.suptitle('Global Satellite Constellation Coverage', 
    #             fontsize=40, fontweight='bold', color='black', y=0.97)
    
    # 设置白色背景
    fig.patch.set_facecolor('white')
    
    # 保存图片
    filename = './[Background]-All-Coverage.pdf'
    # 手动调整布局以最大化地图区域 - 与axes position保持一致
    plt.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
    plt.savefig(filename, dpi=300, bbox_inches=None, 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✓ 所有星座合并覆盖图已保存: {filename}")

def plot_earth_coverage_cartopy():
    """生成所有4张覆盖图"""
    print("开始生成卫星覆盖图...")
    
    # 1. 生成单个星座的图
    print("\n1. 生成 Starlink 覆盖图...")
    plot_single_constellation_cartopy('starlink')
    
    print("\n2. 生成 Kuiper 覆盖图...")
    plot_single_constellation_cartopy('kuiper')
    
    print("\n3. 生成 Telesat 覆盖图...")
    plot_single_constellation_cartopy('telesat')
    
    print("\n4. 生成所有星座合并覆盖图...")
    plot_all_constellations_cartopy()
    
    print("\n✅ 所有4张覆盖图生成完成！")

def plot_earth_coverage_basemap():
    """使用Basemap绘制真实地球覆盖图"""
    plt.figure(figsize=(20, 12))
    
    # 创建Robinson投影的地图
    m = Basemap(projection='robin', lon_0=0, resolution='c')
    
    # 绘制地球特征
    m.drawmapboundary(fill_color='#87CEEB')  # 海洋背景
    m.fillcontinents(color='#8FBC8F', lake_color='#87CEEB')  # 陆地和湖泊
    m.drawcoastlines(linewidth=0.5, color='black')
    m.drawcountries(linewidth=0.3, color='gray')
    
    # 绘制经纬网格
    m.drawparallels(range(-90, 91, 30), labels=[1, 0, 0, 0], fontsize=10, alpha=0.7)
    m.drawmeridians(range(-180, 181, 60), labels=[0, 0, 0, 1], fontsize=10, alpha=0.7)
    
    # 读取所有星座数据
    constellations = CONSTELLATIONS
    
    coverage_radius_km = 600
    coverage_radius_deg = coverage_radius_km * 360 / 40075
    
    total_satellites = 0
    
    for constellation_name, config in constellations.items():
        satellite_data = read_satellite_data(config['file'])
        if not satellite_data:
            continue
            
        total_satellites += len(satellite_data)
        print(f"绘制 {len(satellite_data)} 个 {config['label']} 卫星覆盖区域")
        
        for lon, lat, alt, tag in satellite_data:
            # 将经纬度转换为地图坐标
            x, y = m(lon, lat)
            
            # 添加覆盖圆圈（近似）
            circle = Circle((x, y), coverage_radius_deg * 111320,  # 转换为米
                           facecolor=config['color'], 
                           edgecolor=config['color'],
                           alpha=config['alpha'],
                           linewidth=0.2)
            plt.gca().add_patch(circle)
            
            # 添加虚线外框 - 使边界更清晰
            circle_border = Circle((x, y), coverage_radius_deg * 111320,
                                 facecolor='none',
                                 edgecolor=config['color'],
                                 linewidth=1.2,
                                 linestyle='--',  # 虚线样式
                                 alpha=0.8)
            plt.gca().add_patch(circle_border)
            
            # 添加卫星位置点
            plt.plot(x, y, 'o', color=config['color'], markersize=0.8, 
                    markeredgecolor='black', markeredgewidth=0.1)
    
    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=config['color'], alpha=0.6, label=config['label']) 
                      for config in constellations.values()]
    plt.legend(handles=legend_elements, loc='lower left', fontsize=40, framealpha=0.9)
    
    # plt.title(f'Satellite Constellations Global Coverage\n(Total: {total_satellites} satellites, 600km radius)', 
            #   fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('./satellite_earth_coverage_basemap.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    # plt.show()

def interactive_plot_selection():
    """交互式选择绘图方式"""
    print("\n=== 卫星覆盖图绘制选项 ===")
    print("1. 仅使用 Cartopy 绘制")
    print("2. 仅使用 Basemap 绘制")
    print("3. 使用所有可用库绘制")
    print("4. 自动选择最佳库")
    
    available_libs = []
    if CARTOPY_AVAILABLE:
        available_libs.append("cartopy")
    if BASEMAP_AVAILABLE:
        available_libs.append("basemap")
    
    if not available_libs:
        print("错误：未安装任何地图库！")
        return False
    
    print(f"\n当前可用的库: {', '.join(available_libs)}")
    
    while True:
        try:
            choice = input("\n请选择 (1-4): ").strip()
            if choice == "1":
                if CARTOPY_AVAILABLE:
                    print("\n使用Cartopy绘制...")
                    plot_earth_coverage_cartopy()
                    print("Cartopy版本绘制完成！")
                else:
                    print("Cartopy 未安装！")
                break
            elif choice == "2":
                if BASEMAP_AVAILABLE:
                    print("\n使用Basemap绘制...")
                    plot_earth_coverage_basemap()
                    print("Basemap版本绘制完成！")
                else:
                    print("Basemap 未安装！")
                break
            elif choice == "3":
                print("\n使用所有可用库绘制...")
                count = 0
                if CARTOPY_AVAILABLE:
                    print("绘制Cartopy版本...")
                    plot_earth_coverage_cartopy()
                    count += 1
                if BASEMAP_AVAILABLE:
                    print("绘制Basemap版本...")
                    plot_earth_coverage_basemap()
                    count += 1
                print(f"完成！共绘制了 {count} 个版本")
                break
            elif choice == "4":
                # 自动选择：优先使用Cartopy
                if CARTOPY_AVAILABLE:
                    print("\n自动选择：使用Cartopy绘制...")
                    plot_earth_coverage_cartopy()
                    print("Cartopy版本绘制完成！")
                elif BASEMAP_AVAILABLE:
                    print("\n自动选择：使用Basemap绘制...")
                    plot_earth_coverage_basemap()
                    print("Basemap版本绘制完成！")
                break
            else:
                print("无效选择，请输入1-4之间的数字")
        except KeyboardInterrupt:
            print("\n用户取消操作")
            return False
    
    return True

# 如果直接运行脚本，可以使用交互模式

if __name__ == "__main__":
    # 确保分类的GS文件存在
    if not os.path.exists('./classified_gs/'):
        print("classified_gs目录不存在，请先运行分类脚本：python classify_satellites.py")
        exit(1)
    
    print("=== 高级卫星覆盖图生成工具 ===")
    print("将生成4张高质量PDF图片：")
    print("1. [Background]-Starlink-Coverage.pdf - Starlink单独覆盖图 (600km)")
    print("2. [Background]-Kuiper-Coverage.pdf - Kuiper单独覆盖图 (600km)") 
    print("3. [Background]-Telesat-Coverage.pdf - Telesat单独覆盖图 (1000km)")
    print("4. [Background]-All-Coverage.pdf - 三星座合并覆盖图")
    
    # 检查可用的绘图库并绘制地图
    if CARTOPY_AVAILABLE:
        print("\n使用Cartopy绘制高级地球背景地图...")
        plot_earth_coverage_cartopy()
        print("\n🎉 所有高质量PDF图片生成完成！")
        print("\n生成的文件:")
        print("├── [Background]-Starlink-Coverage.pdf (600km覆盖)")
        print("├── [Background]-Kuiper-Coverage.pdf (600km覆盖)")
        print("├── [Background]-Telesat-Coverage.pdf (1000km覆盖)")
        print("└── [Background]-All-Coverage.pdf (多星座合并)")
    else:
        print("错误：需要安装cartopy库才能绘制真实地球背景")
        print("请运行以下命令：")
        print("pip install cartopy")
        print("或者")
        print("conda install -c conda-forge cartopy")
        exit(1)
