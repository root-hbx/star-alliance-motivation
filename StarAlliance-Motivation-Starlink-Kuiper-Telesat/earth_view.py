import matplotlib.pyplot as plt
import matplotlib
import os

# Set font for academic papers - consistent with reference script
matplotlib.rcParams["font.family"] = "serif"
plt.rcParams["pdf.fonttype"] = 42

# Try importing mapping libraries
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from matplotlib.patches import Circle
    import cartopy.io.img_tiles as cimgt
    CARTOPY_AVAILABLE = True
    print("✓ Cartopy is installed and available")
except ImportError:
    CARTOPY_AVAILABLE = False
    print("✗ Cartopy not installed")

try:
    from mpl_toolkits.basemap import Basemap
    BASEMAP_AVAILABLE = True
    print("✓ Basemap is installed and available")
except ImportError:
    BASEMAP_AVAILABLE = False
    print("✗ Basemap not installed")

if not CARTOPY_AVAILABLE and not BASEMAP_AVAILABLE:
    print("\nWarning: Neither cartopy nor basemap is installed. Please install one or both:")
    print("Install Cartopy: pip install cartopy")
    print("Install Basemap: pip install basemap")
    print("Cartopy is recommended as it is more powerful and better maintained.")

CONSTELLATIONS = {
        'starlink': {'file': './classified_gs/starlink_gs.txt', 'color': "#7fcdbb", 'alpha': 0.5, 'label': 'Starlink'},
        'kuiper':   {'file': './classified_gs/kuiper_gs.txt',   'color': '#FDD835', 'alpha': 0.5, 'label': 'Kuiper'},
        'telesat':  {'file': './classified_gs/telesat_gs.txt',  'color': '#225ea8', 'alpha': 0.5, 'label': 'Telesat'}
    }

def read_satellite_data(file_path):
    """Read satellite data file"""
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
    """Create base earth map - rectangular projection version"""
    fig = plt.figure(figsize=(14, 13))
    # Completely fill the canvas without any margins
    ax = plt.axes(projection=ccrs.PlateCarree(), position=[0.0, 0.0, 1.0, 1.0])
    
    # Set display range: longitude -180 to 180 degrees, latitude -90 to 90 degrees
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
    
    # Add advanced earth features using Natural Earth data
    ax.add_feature(cfeature.LAND, color='#f0f0f0', alpha=0.8)  # Light gray land
    ax.add_feature(cfeature.OCEAN, color='#e6f3ff', alpha=0.8)  # Light blue ocean
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, color='#2c3e50', alpha=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, alpha=0.6, color='#34495e')
    ax.add_feature(cfeature.LAKES, color='#e6f3ff', alpha=0.8)
    ax.add_feature(cfeature.RIVERS, color='#e6f3ff', alpha=0.6, linewidth=0.5)
    
    # Add latitude/longitude grid - no labels, only grid lines
    gl = ax.gridlines(draw_labels=False, dms=False, x_inline=False, y_inline=False,
                     alpha=0.4, linewidth=0.5, color='gray', linestyle='--')
    gl.xlocator = plt.FixedLocator([-180, -120, -60, 0, 60, 120, 180])
    gl.ylocator = plt.FixedLocator([-90, -60, -30, 0, 30, 60, 90])
    
    return fig, ax

def plot_constellation_coverage(ax, constellation_config, constellation_name):
    """Plot single constellation coverage - enhanced version"""
    satellite_data = read_satellite_data(constellation_config['file'])
    if not satellite_data:
        return 0, 700
    
    # Set different coverage radii for different constellation types
    if constellation_name == 'telesat':
        coverage_radius_km = 1000  # Telesat uses 1000km radius
    elif constellation_name == 'kuiper':
        coverage_radius_km = 600
    else:
        coverage_radius_km = 600
    
    # Convert km to degrees (Earth circumference ~40,075km, 360 degrees)
    coverage_radius_deg = coverage_radius_km * 360 / 40075
    
    for lon, lat, alt, tag in satellite_data:
        # Add glow effect coverage circles
        # Outer glow
        circle_glow = Circle((lon, lat), coverage_radius_deg * 1.2, 
                           facecolor=constellation_config['color'], 
                           edgecolor='none',
                           alpha=0.1,
                           transform=ccrs.PlateCarree())
        ax.add_patch(circle_glow)
        
        # Main coverage circle
        circle = Circle((lon, lat), coverage_radius_deg, 
                       facecolor=constellation_config['color'], 
                       edgecolor=constellation_config['color'],
                       alpha=constellation_config['alpha'],
                       linewidth=0.3,
                       transform=ccrs.PlateCarree())
        ax.add_patch(circle)
        
        # Add dashed border for clearer boundaries
        circle_border = Circle((lon, lat), coverage_radius_deg, 
                             facecolor='none', 
                             edgecolor=constellation_config['color'],
                             linewidth=1.5,
                             linestyle='--',
                             alpha=0.8,
                             transform=ccrs.PlateCarree())
        ax.add_patch(circle_border)
    
    return len(satellite_data), coverage_radius_km

def plot_single_constellation_cartopy(constellation_name):
    """Plot single constellation coverage map"""
    constellations = CONSTELLATIONS
    
    if constellation_name not in constellations:
        print(f"Error: Unknown constellation {constellation_name}")
        return
    
    fig, ax = create_earth_base_cartopy()
    
    config = constellations[constellation_name]
    satellite_count, coverage_radius = plot_constellation_coverage(ax, config, constellation_name)
    
    if satellite_count == 0:
        print(f"Warning: {config['label']} data file does not exist or is empty")
        return
    
    # Add enhanced legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=config['color'], alpha=0.7, label=config['label'], 
                            edgecolor='black', linewidth=1)]
    legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=40, 
                      framealpha=0.9, facecolor='white', edgecolor='black')
    legend.get_frame().set_facecolor('white')
    for text in legend.get_texts():
        text.set_color('black')
        text.set_weight('demibold')
        text.set_fontfamily('serif')
    
    fig.patch.set_facecolor('white')
    
    filename = f'./[Background]-{config["label"]}-Coverage.pdf'
    plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0,
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✓ {config['label']} coverage map saved: {filename}")

def plot_all_constellations_cartopy():
    """Plot combined coverage map for all constellations"""
    constellations = CONSTELLATIONS
    
    fig, ax = create_earth_base_cartopy()
    
    total_satellites = 0
    legend_elements = []
    coverage_info = []
    
    # Draw all constellations in specified order: Telesat(bottom) -> Starlink(middle) -> Kuiper(top)
    draw_order = ['telesat', 'starlink', 'kuiper']
    
    for constellation_name in draw_order:
        if constellation_name in constellations:
            config = constellations[constellation_name]
            satellite_count, coverage_radius = plot_constellation_coverage(ax, config, constellation_name)
            if satellite_count > 0:
                total_satellites += satellite_count
                coverage_info.append(f"{config['label']}: {satellite_count} sats ({coverage_radius}km)")
                layer_desc = 'top' if constellation_name=='kuiper' else 'middle' if constellation_name=='starlink' else 'bottom'
                print(f"Drawing {satellite_count} {config['label']} satellite coverage areas (radius: {coverage_radius}km) - {layer_desc} layer")
                from matplotlib.patches import Patch
                legend_elements.append(Patch(facecolor=config['color'], alpha=0.7, label=config['label'],
                                            edgecolor='black', linewidth=1))
    
    if legend_elements:
        legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=40, 
                          framealpha=0.9, facecolor='white', edgecolor='black')
        legend.get_frame().set_facecolor('white')
        for text in legend.get_texts():
            text.set_color('black')
            text.set_weight('demibold')
            text.set_fontfamily('serif')
    
    fig.patch.set_facecolor('white')
    
    filename = './[Background]-All-Coverage.pdf'
    plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0,
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✓ Combined constellation coverage map saved: {filename}")

def plot_earth_coverage_cartopy():
    """Generate all 4 coverage maps"""
    print("Starting satellite coverage map generation...")
    
    print("\n1. Generating Starlink coverage map...")
    plot_single_constellation_cartopy('starlink')
    
    print("\n2. Generating Kuiper coverage map...")
    plot_single_constellation_cartopy('kuiper')
    
    print("\n3. Generating Telesat coverage map...")
    plot_single_constellation_cartopy('telesat')
    
    print("\n4. Generating combined constellation coverage map...")
    plot_all_constellations_cartopy()
    
    print("\n✅ All 4 coverage maps generated successfully!")

def plot_earth_coverage_basemap():
    """Draw earth coverage map using Basemap"""
    plt.figure(figsize=(20, 12))
    
    m = Basemap(projection='robin', lon_0=0, resolution='c')
    
    m.drawmapboundary(fill_color='#87CEEB')
    m.fillcontinents(color='#8FBC8F', lake_color='#87CEEB')
    m.drawcoastlines(linewidth=0.5, color='black')
    m.drawcountries(linewidth=0.3, color='gray')
    
    m.drawparallels(range(-90, 91, 30), labels=[1, 0, 0, 0], fontsize=10, alpha=0.7)
    m.drawmeridians(range(-180, 181, 60), labels=[0, 0, 0, 1], fontsize=10, alpha=0.7)
    
    constellations = CONSTELLATIONS
    
    coverage_radius_km = 600
    coverage_radius_deg = coverage_radius_km * 360 / 40075
    
    total_satellites = 0
    
    for constellation_name, config in constellations.items():
        satellite_data = read_satellite_data(config['file'])
        if not satellite_data:
            continue
            
        total_satellites += len(satellite_data)
        print(f"Drawing {len(satellite_data)} {config['label']} satellite coverage areas")
        
        for lon, lat, alt, tag in satellite_data:
            x, y = m(lon, lat)
            
            circle = Circle((x, y), coverage_radius_deg * 111320,
                           facecolor=config['color'], 
                           edgecolor=config['color'],
                           alpha=config['alpha'],
                           linewidth=0.2)
            plt.gca().add_patch(circle)
            
            circle_border = Circle((x, y), coverage_radius_deg * 111320,
                                 facecolor='none',
                                 edgecolor=config['color'],
                                 linewidth=1.2,
                                 linestyle='--',
                                 alpha=0.8)
            plt.gca().add_patch(circle_border)
            
            plt.plot(x, y, 'o', color=config['color'], markersize=0.8, 
                    markeredgecolor='black', markeredgewidth=0.1)
    
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=config['color'], alpha=0.6, label=config['label']) 
                      for config in constellations.values()]
    plt.legend(handles=legend_elements, loc='lower left', fontsize=40, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig('./satellite_earth_coverage_basemap.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')

def interactive_plot_selection():
    """Interactive plotting option selection"""
    print("\n=== Satellite Coverage Map Plotting Options ===")
    print("1. Plot using Cartopy only")
    print("2. Plot using Basemap only")
    print("3. Plot using all available libraries")
    print("4. Auto-select best library")
    
    available_libs = []
    if CARTOPY_AVAILABLE:
        available_libs.append("cartopy")
    if BASEMAP_AVAILABLE:
        available_libs.append("basemap")
    
    if not available_libs:
        print("Error: No mapping library installed!")
        return False
    
    print(f"\nCurrently available libraries: {', '.join(available_libs)}")
    
    while True:
        try:
            choice = input("\nPlease choose (1-4): ").strip()
            if choice == "1":
                if CARTOPY_AVAILABLE:
                    print("\nUsing Cartopy for plotting...")
                    plot_earth_coverage_cartopy()
                    print("Cartopy version plotting completed!")
                else:
                    print("Cartopy not installed!")
                break
            elif choice == "2":
                if BASEMAP_AVAILABLE:
                    print("\nUsing Basemap for plotting...")
                    plot_earth_coverage_basemap()
                    print("Basemap version plotting completed!")
                else:
                    print("Basemap not installed!")
                break
            elif choice == "3":
                print("\nUsing all available libraries for plotting...")
                count = 0
                if CARTOPY_AVAILABLE:
                    print("Plotting Cartopy version...")
                    plot_earth_coverage_cartopy()
                    count += 1
                if BASEMAP_AVAILABLE:
                    print("Plotting Basemap version...")
                    plot_earth_coverage_basemap()
                    count += 1
                print(f"Completed! Generated {count} versions")
                break
            elif choice == "4":
                if CARTOPY_AVAILABLE:
                    print("\nAuto-selected: Using Cartopy for plotting...")
                    plot_earth_coverage_cartopy()
                    print("Cartopy version plotting completed!")
                elif BASEMAP_AVAILABLE:
                    print("\nAuto-selected: Using Basemap for plotting...")
                    plot_earth_coverage_basemap()
                    print("Basemap version plotting completed!")
                break
            else:
                print("Invalid choice, please enter a number between 1-4")
        except KeyboardInterrupt:
            print("\nUser cancelled operation")
            return False
    
    return True

if __name__ == "__main__":
    if not os.path.exists('./classified_gs/'):
        print("classified_gs directory does not exist, please run classification script first: python classify_satellites.py")
        exit(1)
    
    print("=== Advanced Satellite Coverage Map Generation Tool ===")
    print("Will generate 4 high-quality PDF images:")
    print("1. [Background]-Starlink-Coverage.pdf - Starlink individual coverage map (600km)")
    print("2. [Background]-Kuiper-Coverage.pdf - Kuiper individual coverage map (600km)") 
    print("3. [Background]-Telesat-Coverage.pdf - Telesat individual coverage map (1000km)")
    print("4. [Background]-All-Coverage.pdf - Combined three-constellation coverage map")
    
    if CARTOPY_AVAILABLE:
        print("\nUsing Cartopy to draw advanced earth background maps...")
        plot_earth_coverage_cartopy()
        print("\n🎉 All high-quality PDF images generated successfully!")
        print("\nGenerated files:")
        print("├── [Background]-Starlink-Coverage.pdf (600km coverage)")
        print("├── [Background]-Kuiper-Coverage.pdf (600km coverage)")
        print("├── [Background]-Telesat-Coverage.pdf (1000km coverage)")
        print("└── [Background]-All-Coverage.pdf (multi-constellation combined)")
    else:
        print("Error: Cartopy library is required to draw real earth backgrounds")
        print("Please run the following command:")
        print("pip install cartopy")
        print("or")
        print("conda install -c conda-forge cartopy")
        exit(1)
