from PIL import Image, ImageOps
from rembg import remove
import io

def remove_background(input_path):
    """Remove the background from an image and return an image with a transparent background."""
    # Process the image to remove background
    input_image = Image.open(input_path)
    output_image = remove(input_image)
        
    # Ensure the image mode is RGBA to support transparency
    if output_image.mode != 'RGBA':
        output_image = output_image.convert('RGBA')
    
    return output_image

def create_passport_photo_sheet(input_image_path, dpi=300, border_size=2, spacing=20):
    # Remove the background and get an image with a transparent background
    passport_photo = remove_background(input_image_path)
    
    # Resize the image to passport size (1.2x1.5 inches) and rotate 90 degrees
    passport_width = int(1.2 * dpi)  # 1.2 inches at given DPI
    passport_height = int(1.5 * dpi)  # 1.5 inches at given DPI
    passport_photo = passport_photo.resize((passport_width, passport_height), Image.LANCZOS).rotate(90, expand=True)
    
    # Add a black border
    passport_photo = ImageOps.expand(passport_photo, border=border_size, fill='black')

    # Create a white background image
    passport_width_with_border = passport_photo.width
    passport_height_with_border = passport_photo.height
    white_background = Image.new("RGBA", (passport_width_with_border, passport_height_with_border), "white")
    
    # Paste passport photo onto the white background
    white_background.paste(passport_photo, (0, 0), passport_photo)

    # Create a 4x6 inch canvas
    sheet_width = int(4 * dpi)  # 4 inches at given DPI
    sheet_height = int(6 * dpi)  # 6 inches at given DPI
    sheet = Image.new("RGBA", (sheet_width, sheet_height), "white")

    # Number of photos horizontally and vertically
    photos_per_row = 2
    photos_per_column = 4

    # Calculate total width and height required for all photos with spacing
    total_width = photos_per_row * passport_width_with_border + (photos_per_row - 1) * spacing
    total_height = photos_per_column * passport_height_with_border + (photos_per_column - 1) * spacing

    # Calculate starting position to center photos on the canvas
    x_start = (sheet_width - total_width) // 2
    y_start = (sheet_height - total_height) // 2

    # Calculate positions for the 8 passport photos on the 4x6 sheet with spacing
    positions = []
    for row in range(photos_per_column):
        for col in range(photos_per_row):
            x_pos = x_start + col * (passport_width_with_border + spacing)
            y_pos = y_start + row * (passport_height_with_border + spacing)
            positions.append((x_pos, y_pos))
    
    # Paste the passport photo onto the 4x6 sheet at the calculated positions
    for position in positions:
        sheet.paste(white_background, position, white_background)


    img_io = io.BytesIO()
    sheet.save(img_io, format='PNG')
    img_io.seek(0)

    return img_io

# Example usage
# create_passport_photo_sheet("file.jpeg", "passport_sheet.png")
