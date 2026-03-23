#!/usr/bin/env python3
"""
Create iPhone mockup composite images
Places app screenshots inside the iPhone mockup frame
"""

from PIL import Image
import os

# Configuration
mockup_path = "iphone-mockup.png"
apps = ["planner", "coffee", "pantry", "mantras", "outflows"]

# Load the mockup
mockup = Image.open(mockup_path)
mockup_width, mockup_height = mockup.size

# iPhone screen area (you may need to adjust these coordinates based on your mockup)
# These are approximate values - adjust based on your specific mockup
screen_left = int(mockup_width * 0.12)  # 12% from left
screen_top = int(mockup_height * 0.08)  # 8% from top  
screen_right = int(mockup_width * 0.88)  # 88% from left (76% width)
screen_bottom = int(mockup_height * 0.92)  # 92% from top (84% height)

screen_width = screen_right - screen_left
screen_height = screen_bottom - screen_top

print(f"Mockup size: {mockup_width}x{mockup_height}")
print(f"Screen area: {screen_width}x{screen_height}")
print(f"Screen position: ({screen_left},{screen_top}) to ({screen_right},{screen_bottom})")

for app in apps:
    input_file = f"{app}.png"
    output_file = f"{app}-mockup.png"
    
    if not os.path.exists(input_file):
        print(f"⚠️  Skipping {app} - file not found")
        continue
    
    # Load app screenshot
    screenshot = Image.open(input_file)
    
    # Resize screenshot to fit screen area while maintaining aspect ratio
    screenshot_ratio = screenshot.width / screenshot.height
    screen_ratio = screen_width / screen_height
    
    if screenshot_ratio > screen_ratio:
        # Screenshot is wider - fit to width
        new_width = screen_width
        new_height = int(screen_width / screenshot_ratio)
    else:
        # Screenshot is taller - fit to height
        new_height = screen_height
        new_width = int(screen_height * screenshot_ratio)
    
    screenshot_resized = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a copy of the mockup for this composite
    composite = mockup.copy()
    
    # Center the screenshot in the screen area
    paste_x = screen_left + (screen_width - new_width) // 2
    paste_y = screen_top + (screen_height - new_height) // 2
    
    # Paste screenshot onto mockup
    if screenshot_resized.mode == 'RGBA':
        composite.paste(screenshot_resized, (paste_x, paste_y), screenshot_resized)
    else:
        composite.paste(screenshot_resized, (paste_x, paste_y))
    
    # Save the composite
    composite.save(output_file, 'PNG')
    print(f"✅ Created {output_file}")

print("\n✨ All mockups created successfully!")
