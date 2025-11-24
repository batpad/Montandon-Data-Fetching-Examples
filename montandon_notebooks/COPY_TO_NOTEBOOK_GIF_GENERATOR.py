# ============================================================================
# ADD THIS CODE TO YOUR NOTEBOOK 
# ============================================================================
# This creates a new cell with a function to generate a GIF animation
# Copy and paste this entire block into a new code cell in your notebook

# First, make sure you have the required libraries installed:
# !pip install imageio matplotlib pillow

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import imageio
import numpy as np
from pathlib import Path

def create_cyclone_gif(
    cyclone_event, 
    hazard_items,
    output_filename='beryl_cyclone_animation.gif',
    fps=2,
    dpi=100
):
    """
    Create an animated GIF of the cyclone track that can be used in presentations.
    
    Parameters:
    -----------
    cyclone_event : pystac.Item
        The main cyclone event item
    hazard_items : List[pystac.Item]
        List of hazard point items sorted by datetime
    output_filename : str
        Name of the output GIF file (will be saved in the notebook directory)
    fps : int
        Frames per second for the GIF (default: 2)
    dpi : int
        Resolution of the GIF (default: 100 - higher = better quality but larger file)
        
    Returns:
    --------
    str : Path to the saved GIF file
    """
    if not cyclone_event or not hazard_items:
        print("❌ No cyclone or hazard data provided")
        return None
    
    print(f"📊 Creating GIF animation with {len(hazard_items)} frames...")
    
    # Get the directory where the notebook is located
    output_path = Path.cwd() / output_filename
    
    # Extract coordinates and wind speeds
    coords = []
    wind_speeds = []
    datetimes = []
    
    for item in hazard_items:
        geom_coords = item.geometry.get("coordinates")
        if isinstance(geom_coords[0], list):
            geom_coords = geom_coords[-1]
        
        coords.append([geom_coords[0], geom_coords[1]])  # [lon, lat]
        
        # Get wind speed using helper function
        hazard_detail = get_monty_hazard_detail(item)
        wind_speed = hazard_detail.get('severity_value', 0) if hazard_detail else 0
        wind_speeds.append(wind_speed)
        datetimes.append(item.datetime)
    
    # Convert to numpy arrays
    lons = np.array([c[0] for c in coords])
    lats = np.array([c[1] for c in coords])
    
    # Create frames
    frames = []
    
    for i in range(len(coords)):
        # Create figure for this frame
        fig, ax = plt.subplots(figsize=(12, 8), dpi=dpi)
        
        # Set map bounds with padding
        lon_padding = (lons.max() - lons.min()) * 0.1
        lat_padding = (lats.max() - lats.min()) * 0.1
        ax.set_xlim(lons.min() - lon_padding, lons.max() + lon_padding)
        ax.set_ylim(lats.min() - lat_padding, lats.max() + lat_padding)
        
        ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
        
        # Get cyclone name from event
        cyclone_name = cyclone_event.properties.get('title', cyclone_event.id)
        ax.set_title(f'{cyclone_name}', fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Plot the complete track in light gray for context
        ax.plot(lons, lats, color='lightgray', linewidth=1, alpha=0.5, zorder=1)
        
        # Plot the track up to current point
        for j in range(i + 1):
            color = get_wind_speed_color(wind_speeds[j])
            
            if j > 0:
                # Draw line segment
                ax.plot([lons[j-1], lons[j]], [lats[j-1], lats[j]], 
                       color=color, linewidth=3, alpha=0.8, zorder=2)
            
            # Draw point
            marker_size = 150 if j == i else 80  # Current point is larger
            ax.scatter(lons[j], lats[j], c=color, s=marker_size, 
                      edgecolors='black', linewidths=1.5, zorder=5, alpha=0.9)
        
        # Add current position marker
        ax.scatter(lons[i], lats[i], marker='*', s=400, c='white', 
                  edgecolors='black', linewidths=2, zorder=6)
        
        # Add timestamp and wind speed
        timestamp_text = datetimes[i].strftime('%Y-%m-%d %H:%M UTC')
        wind_text = f'Wind Speed: {wind_speeds[i]} knots'
        info_text = f'{timestamp_text}\n{wind_text}\nFrame {i+1}/{len(coords)}'
        
        ax.text(0.02, 0.98, info_text, 
               transform=ax.transAxes, fontsize=11,
               verticalalignment='top', fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, 
                        edgecolor='black', linewidth=1.5))
        
        # Add legend
        legend_elements = [
            mpatches.Patch(color='darkred', label='Cat 5 (≥137 kn)'),
            mpatches.Patch(color='red', label='Cat 4 (113-136 kn)'),
            mpatches.Patch(color='orange', label='Cat 3 (96-112 kn)'),
            mpatches.Patch(color='yellow', label='Cat 2 (83-95 kn)'),
            mpatches.Patch(color='green', label='Cat 1 (64-82 kn)'),
            mpatches.Patch(color='blue', label='Trop. Storm (34-63 kn)'),
            mpatches.Patch(color='lightblue', label='Trop. Dep. (<34 kn)'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=9,
                 framealpha=0.9, edgecolor='black')
        
        # Save frame to buffer
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(image)
        
        plt.close(fig)
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Generated {i + 1}/{len(coords)} frames...")
    
    # Save as GIF
    print(f"💾 Saving GIF to {output_filename}...")
    imageio.mimsave(output_path, frames, fps=fps, loop=0)
    
    # Get file size
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    
    print(f"✅ GIF saved successfully!")
    print(f"   📁 Location: {output_path}")
    print(f"   📊 Frames: {len(frames)}")
    print(f"   🎬 FPS: {fps}")
    print(f"   💾 Size: {file_size_mb:.2f} MB")
    
    return str(output_path)

# ============================================================================
# USAGE EXAMPLE - Add this in a new cell after you have cyclone_event and hazards
# ============================================================================

# Create the GIF (this will save to the same folder as the notebook)
# gif_path = create_cyclone_gif(
#     cyclone_event, 
#     hazards,
#     output_filename='beryl_cyclone_track.gif',
#     fps=3,  # 3 frames per second - adjust for speed
#     dpi=100  # Resolution - higher = better quality but larger file
# )

# Display the saved path
# print(f"\n🎉 Your GIF is ready at: {gif_path}")
# print("You can now use this in your presentations!")
