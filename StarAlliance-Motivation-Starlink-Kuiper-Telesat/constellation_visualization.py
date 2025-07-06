
import xml.etree.ElementTree as ET
import math
import ephem






def add_coverage_circle(satellite, coverage_radius, color="BLUE"):
    """
    添加覆盖范围的圆形
    :param satellite: 卫星对象
    :param coverage_radius: 覆盖范围半径
    :param color: 圆形颜色
    :return: JavaScript代码字符串
    """
    return "var coverageCircle = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
           + str(math.degrees(satellite.sublong)) + ", " \
           + str(math.degrees(satellite.sublat)) + ", 0), " \
           + "ellipse : {semiMajorAxis : " + str(coverage_radius) + ", semiMinorAxis : " + str(coverage_radius) + ", " \
           + "material : Cesium.Color." + color + ".withAlpha(0.2),}});\n"







# 该函数用来获取卫星对象列表
def get_satellites_list(
        mean_motion,  # 平均运动率，即卫星每天围绕地球转动的次数
        altitude,
        number_of_orbit,
        number_of_satellite_per_orbit,
        inclination,
        phase_shift = True,  # 相邻轨道之间的相位差
        eccentricity = 0.0000001,  # 轨道偏心率
        arg_perigee = 0.0,   # 轨道近地点角
        epoch = "1949-10-01 00:00:00" # 基准时间
        ):
    satellites = [None] * (number_of_orbit * number_of_satellite_per_orbit)
    count = 0
    sat_id = 1
    for orbit in range(0, number_of_orbit):
        raan = orbit * 360 / number_of_orbit
        orbit_wise_shift = 0
        if orbit % 2 == 1:
            if phase_shift:
                orbit_wise_shift = 360 / (number_of_satellite_per_orbit * 2)

        for n_sat in range(0, number_of_satellite_per_orbit):
            mean_anomaly = orbit_wise_shift + (n_sat * 360 / number_of_satellite_per_orbit)

            sat = ephem.EarthSatellite()  # 生成卫星对象
            sat._epoch = epoch  # 设置卫星基准时间
            sat._inc = ephem.degrees(inclination)  # 设置卫星的轨道倾角
            sat._e = eccentricity  # 轨道偏心率
            sat._raan = ephem.degrees(raan)  # 升交点赤经
            sat._ap = arg_perigee  # 轨道近地点角
            sat._M = ephem.degrees(mean_anomaly)  # 卫星在轨道内相对近地点的偏移角度，即轨内偏移
            sat._n = mean_motion  # 平均运动率

            satellites[count] = {
                "satellite": sat,
                "altitude": altitude,
                "orbit": orbit,
                "orbit_satellite_id": n_sat,
                "sat_id":sat_id
            }
            sat_id += 1
            count += 1

    return satellites




# 获取卫星的临近卫星
def get_neighbor_satellite(
        sat1_orb,sat1_rel_id,sat2_orb,sat2_rel_id,satellite,
        number_of_orbit, number_of_satellite_per_orbit):
    neighbor_abs_orb = (sat1_orb + sat2_orb) % number_of_orbit
    neighbor_abs_pos = (sat1_rel_id + sat2_rel_id) % number_of_satellite_per_orbit
    sel_sat_id = -1
    for i in range(0, len(satellite)):
        if (satellite[i]["orbit"] == neighbor_abs_orb and
                satellite[i]["orbit_satellite_id"] == neighbor_abs_pos):
            sel_sat_id = i
            break
    return sel_sat_id





# 获取卫星之间的ISL
def get_ISL(satellite, number_of_orbit, number_of_satellite_per_orbit):
    links = {}
    count = 0
    for i in range(0, len(satellite)):
        sel_sat_id = get_neighbor_satellite(satellite[i]["orbit"],
                                            satellite[i]["orbit_satellite_id"],
                                            0, 1, satellite,
                                            number_of_orbit, number_of_satellite_per_orbit)
        links[count] = {
            "sat1": i,
            "sat2": sel_sat_id,
            "dist": -1.0
        }
        count += 1
    return links


def xml_to_dict(element):
    if len(element) == 0:
        return element.text
    result = {}
    for child in element:
        child_data = xml_to_dict(child)
        if child.tag in result:
            if type(result[child.tag]) is list:
                result[child.tag].append(child_data)
            else:
                result[child.tag] = [result[child.tag], child_data]
        else:
            result[child.tag] = child_data
    return result

def read_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return {root.tag: xml_to_dict(root)}





def visualization_constellation_without_ISL(constellation_information, shell_colors, coverage_radius=600000):
    content_string = ""
    for shell_index, shell in enumerate(constellation_information):
        mean_motion_rev_per_day = shell[0]
        altitude = shell[1]
        number_of_orbit = shell[2]
        number_of_satellite_per_orbit = shell[3]
        inclination = shell[4]
        base_id = shell[5]

        # 获取当前 shell 的颜色
        satellite_color = shell_colors[shell_index % len(shell_colors)]

        satellites = get_satellites_list(mean_motion_rev_per_day, altitude, number_of_orbit,
                                         number_of_satellite_per_orbit, inclination)

        for j in range(len(satellites)):
            satellites[j]["satellite"].compute("1949-10-01 00:00:00")
            content_string += "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                              + str(math.degrees(satellites[j]["satellite"].sublong)) + ", " \
                              + str(math.degrees(satellites[j]["satellite"].sublat)) + ", " + str(
                satellites[j]["altitude"] * 1000) + "), " \
                              + "ellipsoid : {radii : new Cesium.Cartesian3(30000.0, 30000.0, 30000.0), " \
                              + "material : Cesium.Color." + satellite_color + ".withAlpha(1),}});\n"
            # 调用封装的覆盖范围函数
            content_string += add_coverage_circle(satellites[j]["satellite"], coverage_radius, satellite_color)
    return content_string



def visualization_constellation_with_ISL(constellation_information):
    content_string = ""
    count = 0
    for shell in constellation_information:
        mean_motion_rev_per_day = shell[0]
        altitude = shell[1]
        number_of_orbit = shell[2]
        number_of_satellite_per_orbit = shell[3]
        inclination = shell[4]
        base_id = shell[5]

        satellites = get_satellites_list(mean_motion_rev_per_day, altitude, number_of_orbit
                                         , number_of_satellite_per_orbit, inclination)



        sat_id=1
        flag=1
        for j in range(len(satellites)):
            satellites[j]["satellite"].compute("1949-10-01 00:00:00")
            if flag==1:
                content_string += (
                    "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                    + str(math.degrees(satellites[j]["satellite"].sublong)) + ", " \
                    + str(math.degrees(satellites[j]["satellite"].sublat)) + ", "
                    + str(satellites[j]["altitude"] * 1000) + "), " \
                    + "ellipsoid : {radii : new Cesium.Cartesian3(30000.0, 30000.0, 30000.0), " \
                    + "material : Cesium.Color.BLACK.withAlpha(1),}});\n")
                flag += 1
            elif flag==2:
                content_string += (
                        "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                        + str(math.degrees(satellites[j]["satellite"].sublong)) + ", " \
                        + str(math.degrees(satellites[j]["satellite"].sublat)) + ", "
                        + str(satellites[j]["altitude"] * 1000) + "), " \
                        + "ellipsoid : {radii : new Cesium.Cartesian3(30000.0, 30000.0, 30000.0), " \
                        + "material : Cesium.Color.BLACK.withAlpha(0),}});\n")
                flag += 1
            elif flag == 3:
                content_string += (
                        "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                        + str(math.degrees(satellites[j]["satellite"].sublong)) + ", " \
                        + str(math.degrees(satellites[j]["satellite"].sublat)) + ", "
                        + str(satellites[j]["altitude"] * 1000) + "), " \
                        + "ellipsoid : {radii : new Cesium.Cartesian3(30000.0, 30000.0, 30000.0), " \
                        + "material : Cesium.Color.BLACK.withAlpha(0),}});\n")
                flag = 1



            sat_id += 1

        orbit_links = get_ISL(satellites, number_of_orbit, number_of_satellite_per_orbit)
        # Starlink color = ['AQUA', 'BLUE', 'MEDIUMAQUAMARINE', 'RED','YELLOW']
        # Kuiper color = ['MEDIUMVIOLETRED','ORANGE','YELLOW','LIGHTCORAL']
        # Telesat color = ['GREEN', 'DEEPSKYBLUE', 'LAWNGREEN', 'MEDIUMSEAGREEN']
        color = ['MEDIUMVIOLETRED','ORANGERED','RED','PALEVIOLETRED']

        for key in orbit_links:
            sat1 = orbit_links[key]["sat1"]
            sat2 = orbit_links[key]["sat2"]
            content_string += (
                    "viewer.entities.add({name : '', polyline: { positions: Cesium.Cartesian3.fromDegreesArrayHeights([" \
                    + str(math.degrees(satellites[sat1]["satellite"].sublong)) + "," \
                    + str(math.degrees(satellites[sat1]["satellite"].sublat)) + "," \
                    + str(satellites[sat1]["altitude"] * 1000) + "," \
                    + str(math.degrees(satellites[sat2]["satellite"].sublong)) + "," \
                    + str(math.degrees(satellites[sat2]["satellite"].sublat)) + "," \
                    + str(satellites[sat2]["altitude"] * 1000) + "]), " \
                    + "width: 2, arcType: Cesium.ArcType.NONE, " \
                    + "material: new Cesium.PolylineOutlineMaterialProperty({ " \
                    + "color: Cesium.Color." + color[count]
                    + ".withAlpha(0.4), outlineWidth: 0, outlineColor: Cesium.Color.BLACK})}});")
        count += 1
    return content_string


# ISL参数是一个布尔变量，用来控制是否可视化ISL
def constellation_visualization(constellation_name , xml_file_path ,output_file_path,
                                head_html_file , tail_html_file ,ISL = False, satellite_color = "BLACK", coverage_radius = 600000):


    # 读取星座配置信息
    constellation_configuration_information = read_xml_file(xml_file_path)
    # 卫星层数量
    number_of_shells = int(constellation_configuration_information['constellation']['number_of_shells'])

    constellation_information = []
    for count in range(1, number_of_shells + 1, 1):
        altitude = int(constellation_configuration_information['constellation']['shell' + str(count)]['altitude'])
        orbit_cycle = int(constellation_configuration_information['constellation']['shell' + str(count)]['orbit_cycle'])
        inclination = float(
            constellation_configuration_information['constellation']['shell' + str(count)]['inclination'])
        number_of_orbit = int(
            constellation_configuration_information['constellation']['shell' + str(count)]['number_of_orbit'])
        number_of_satellite_per_orbit = int(
            constellation_configuration_information['constellation']['shell' + str(count)]
            ['number_of_satellite_per_orbit'])

        # 平均运动率，即卫星每天围绕地球转动的次数，计算方法是用卫星轨道周期的秒数除以一天总共的秒数（24*60*60=86400）
        mean_motion_rev_per_day = 1.0 * 86400 / orbit_cycle

        constellation_information.append(
            [mean_motion_rev_per_day, altitude, number_of_orbit, number_of_satellite_per_orbit,
             inclination])

    # 向每一层信息中添加base_id信息，即每一层第一颗卫星的编号
    for index in range(len(constellation_information)):
        if index == 0:
            constellation_information[index].append(0)
        else:
            constellation_information[index].append(constellation_information[index - 1][5] +
                                                    constellation_information[index - 1][2] *
                                                    constellation_information[index - 1][3])


    if ISL:
        # 可视化星座中的卫星和ISL
        visualization_content = visualization_constellation_with_ISL(constellation_information)
        writer_html = open(output_file_path + constellation_name + "_with_ISL.html", 'w')
        with open(head_html_file, 'r') as fi:
            writer_html.write(fi.read())
        writer_html.write(visualization_content)
        with open(tail_html_file, 'r') as fb:
            writer_html.write(fb.read())
        writer_html.close()
    else:
        # 只可视化星座中的卫星，不可视化ISL
        shell_colors = ["RED", "BLUE", "GREEN", "YELLOW"]
        visualization_content = visualization_constellation_without_ISL(constellation_information, shell_colors,
                                                                        coverage_radius)
        writer_html = open(output_file_path + constellation_name + "_without_ISL.html", 'w')
        with open(head_html_file, 'r') as fi:
            writer_html.write(fi.read())
        writer_html.write(visualization_content)
        with open(tail_html_file, 'r') as fb:
            writer_html.write(fb.read())
        writer_html.close()


def filter_orbits_to_ensure_coverage(constellation_information, coverage_radius, keep_ratios):
    """
    根据每个 shell 的保留比例删除连续的轨道，确保所有 shell 能完全覆盖地球表面
    :param constellation_information: 星座信息
    :param coverage_radius: 每颗卫星的覆盖半径
    :param keep_ratios: 每个 shell 的保留比例列表（长度需与 shell 数量一致）
    :return: 修改后的星座信息
    """
    filtered_constellation_information = []

    for shell_index, shell in enumerate(constellation_information):
        mean_motion_rev_per_day = shell[0]
        altitude = shell[1]
        number_of_orbit = shell[2]
        number_of_satellite_per_orbit = shell[3]
        inclination = shell[4]
        base_id = shell[5]

        # 获取当前 shell 的保留比例
        keep_ratio = keep_ratios[shell_index]

        # 计算需要保留的轨道数量
        keep_orbit_count = int(number_of_orbit * keep_ratio)

        # 保留前 keep_orbit_count 个连续轨道
        remaining_orbits = list(range(keep_orbit_count))

        # 更新 shell 信息
        filtered_constellation_information.append([
            mean_motion_rev_per_day, altitude, len(remaining_orbits), number_of_satellite_per_orbit, inclination, base_id
        ])

    return filtered_constellation_information



def should_keep_orbit(satellites, orbit, coverage_radius, number_of_orbit, number_of_satellite_per_orbit):
    """
    检查是否需要保留该轨道
    :param satellites: 卫星列表
    :param orbit: 当前轨道编号
    :param coverage_radius: 覆盖半径
    :param number_of_orbit: 轨道总数
    :param number_of_satellite_per_orbit: 每轨道卫星数量
    :return: 是否保留该轨道
    """
    # 简单逻辑：保留轨道的条件（可以根据覆盖范围计算更复杂的逻辑）
    return orbit % 2 == 0  # 示例：保留偶数轨道



import math

def print_satellite_positions(filtered_constellation_information):
    """
    打印每一层 shell 中被保留的卫星的经纬度和高度信息
    :param filtered_constellation_information: 过滤后的星座信息
    """
    for shell_index, shell in enumerate(filtered_constellation_information):
        mean_motion_rev_per_day = shell[0]
        altitude = shell[1]
        number_of_orbit = shell[2]
        number_of_satellite_per_orbit = shell[3]
        inclination = shell[4]
        base_id = shell[5]

        print(f"Shell {shell_index + 1}:")
        for orbit_index in range(number_of_orbit):
            for satellite_index in range(number_of_satellite_per_orbit):
                # 计算卫星的经纬度
                longitude = (360.0 / number_of_satellite_per_orbit) * satellite_index
                latitude = inclination * math.sin(math.radians((360.0 / number_of_orbit) * orbit_index))
                height = altitude

                print(f"  Satellite {base_id + orbit_index * number_of_satellite_per_orbit + satellite_index}: "
                      f"Longitude: {longitude:.2f}, Latitude: {latitude:.2f}, Height: {height:.2f} m")





import datetime
import os
import math

if __name__ == '__main__':
    constellation_name = "Starlink_Kuiper_Telesat"
    xml_file_path = "../config/XML_constellation/" + constellation_name + ".xml"
    output_file_path = "./CesiumAPP/"
    head_html_file = "./html_head_tail/head.html"
    tail_html_file = "./html_head_tail/tail.html"
    txt_output_path = "./SatellitePositions/"  # 保存卫星位置信息的目录

    # 创建保存卫星位置信息的目录
    if not os.path.exists(txt_output_path):
        os.makedirs(txt_output_path)

    # 读取星座配置信息
    constellation_configuration_information = read_xml_file(xml_file_path)
    number_of_shells = int(constellation_configuration_information['constellation']['number_of_shells'])

    # 构造星座信息时添加 base_id
    constellation_information = []
    base_id = 0  # 初始化 base_id
    for count in range(1, number_of_shells + 1):
        altitude = int(constellation_configuration_information['constellation']['shell' + str(count)]['altitude'])
        orbit_cycle = int(constellation_configuration_information['constellation']['shell' + str(count)]['orbit_cycle'])
        inclination = float(
            constellation_configuration_information['constellation']['shell' + str(count)]['inclination'])
        number_of_orbit = int(
            constellation_configuration_information['constellation']['shell' + str(count)]['number_of_orbit'])
        number_of_satellite_per_orbit = int(
            constellation_configuration_information['constellation']['shell' + str(count)][
                'number_of_satellite_per_orbit'])

        mean_motion_rev_per_day = 1.0 * 86400 / orbit_cycle

        # 添加 base_id 信息
        constellation_information.append([
            mean_motion_rev_per_day, altitude, number_of_orbit, number_of_satellite_per_orbit, inclination, base_id
        ])

        # 更新 base_id 为下一层的起始编号
        base_id += number_of_orbit * number_of_satellite_per_orbit

    # 过滤轨道以确保覆盖地球表面
    coverage_radius_list = [600000, 600000, 1000000]  # 每个 shell 的覆盖半径
    keep_ratios = [0.25, 0.25, 0.25]  # 每个 shell 的保留比例
    filtered_constellation_information = filter_orbits_to_ensure_coverage(constellation_information, coverage_radius_list,
                                                                          keep_ratios)

    # 时间片设置
    start_time = datetime.datetime(1949, 10, 1, 0, 0, 0)
    time_step = datetime.timedelta(seconds=15)  # 每个时间片间隔15秒
    num_time_steps = 24 * 60 * 60 // 15  # 总共计算24小时内的时间片
    selected_time_step_index = 1000  # 选取第1000个时间片进行可视化

    # 可视化每层 shell 并保存 HTML 文件
    shell_colors = ["RED", "GREEN", "YELLOW"]
    all_shells_visualization_content = ""
    for shell_index, shell in enumerate(filtered_constellation_information):
        mean_motion_rev_per_day = shell[0]
        altitude = shell[1]
        number_of_orbit = shell[2]
        number_of_satellite_per_orbit = shell[3]
        inclination = shell[4]
        base_id = shell[5]

        # 获取当前 shell 的颜色
        satellite_color = shell_colors[shell_index % len(shell_colors)]

        satellites = get_satellites_list(mean_motion_rev_per_day, altitude, number_of_orbit,
                                         number_of_satellite_per_orbit, inclination)

        visualization_content = ""
        print(f"Shell {shell_index + 1} Satellite Positions:")

        # 计算多个时间片的卫星位置
        for time_step_index in range(num_time_steps):
            current_time = start_time + time_step * time_step_index
            txt_file_path = os.path.join(txt_output_path, f"time_step_{time_step_index + 1}.txt")
            with open(txt_file_path, 'a') as txt_file:
                for j in range(len(satellites)):
                    satellites[j]["satellite"].compute(current_time.strftime("%Y-%m-%d %H:%M:%S"))
                    longitude = math.degrees(satellites[j]["satellite"].sublong)
                    latitude = math.degrees(satellites[j]["satellite"].sublat)
                    height_km = satellites[j]["altitude"]
                    txt_file.write(f"{longitude:.2f} {latitude:.2f} {height_km:.2f} {shell_index + 1}\n")

                    # 仅生成选定时间片的可视化信息
                    if time_step_index == selected_time_step_index:
                        visualization_content += "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                                                  + str(longitude) + ", " + str(latitude) + ", " + str(
                            height_km * 1000) + "), " \
                                                  + "ellipsoid : {radii : new Cesium.Cartesian3(30000.0, 30000.0, 30000.0), " \
                                                  + "material : Cesium.Color." + satellite_color + ".withAlpha(1),}});\n"
                        visualization_content += add_coverage_circle(satellites[j]["satellite"], coverage_radius_list[shell_index], satellite_color)

        # 保存每层 shell 的 HTML 文件
        writer_html = open(output_file_path + f"shell_{shell_index + 1}_filtered.html", 'w')
        with open(head_html_file, 'r') as fi:
            writer_html.write(fi.read())
        writer_html.write(visualization_content)
        with open(tail_html_file, 'r') as fb:
            writer_html.write(fb.read())
        writer_html.close()

        # 合并所有 shell 的可视化内容
        all_shells_visualization_content += visualization_content

    # 保存所有 shell 合并的 HTML 文件
    writer_html = open(output_file_path + "all_shells_filtered.html", 'w')
    with open(head_html_file, 'r') as fi:
        writer_html.write(fi.read())
    writer_html.write(all_shells_visualization_content)
    with open(tail_html_file, 'r') as fb:
        writer_html.write(fb.read())
    writer_html.close()