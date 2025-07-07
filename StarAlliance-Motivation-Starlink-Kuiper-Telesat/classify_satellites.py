import os

def classify_satellites():
    """Read satellite position file and classify by last column"""
    
    # Input file path
    input_file = "SatellitePositions/time_step_3500.txt"
    
    # Ensure output directory exists
    output_dir = "classified_gs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Output file paths
    output_files = {
        1: os.path.join(output_dir, "starlink_gs.txt"),
        2: os.path.join(output_dir, "kuiper_gs.txt"),
        3: os.path.join(output_dir, "telesat_gs.txt")
    }
    
    # Initialize output files (clear content)
    for file_path in output_files.values():
        with open(file_path, 'w') as f:
            pass  # Create empty file
    
    # Statistics counters
    counts = {1: 0, 2: 0, 3: 0}
    
    # Read input file and classify
    try:
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) < 4:
                    print(f"Warning: Line {line_num} format incorrect: {line}")
                    continue
                
                try:
                    # Parse last column (tag)
                    tag = int(parts[-1])
                    
                    if tag in output_files:
                        # Write entire line to corresponding file
                        with open(output_files[tag], 'a') as f:
                            f.write(line + '\n')
                        counts[tag] += 1
                    else:
                        print(f"Warning: Line {line_num} unknown tag: {tag}")
                        
                except ValueError:
                    print(f"Warning: Line {line_num} tag cannot be parsed as integer: {parts[-1]}")
                    
    except FileNotFoundError:
        print(f"Error: Input file not found {input_file}")
        return
    
    # Print statistics
    print("Classification completed! Statistics:")
    print(f"Starlink (tag 1): {counts[1]} satellites")
    print(f"Kuiper (tag 2): {counts[2]} satellites")
    print(f"Telesat (tag 3): {counts[3]} satellites")
    print(f"Total: {sum(counts.values())} satellites")
    
    # Show output files
    print("\nOutput files:")
    for tag, file_path in output_files.items():
        if os.path.exists(file_path):
            constellation_names = {1: "Starlink", 2: "Kuiper", 3: "Telesat"}
            print(f"{constellation_names[tag]}: {file_path}")

if __name__ == "__main__":
    classify_satellites()
