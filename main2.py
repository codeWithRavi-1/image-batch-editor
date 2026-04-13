import os
from PIL import Image, ImageDraw, ImageFont

# Select source folder
source_folder = input("Enter source folder path (with images): ").strip()
if not os.path.isdir(source_folder):
    print("Invalid source folder. Exiting.")
    exit()

# Select destination folder
destination_folder = input("Enter destination folder path (for edited images): ").strip()
if not os.path.isdir(destination_folder):
    print("Invalid destination folder. Exiting.")
    exit()

# Ask user for resize dimensions
try:
    width = int(input("Enter target width (e.g., 1280): "))
    height = int(input("Enter target height (e.g., 1280): "))
    target_size = (width, height)
except:
    print("Invalid size. Using default 1280x1280.")
    target_size = (1280, 1280)

# Maintain aspect ratio?
maintain_aspect = input("Maintain aspect ratio? (yes/no): ").strip().lower().startswith('y')

# Ask user which operations to apply
operations = {
    "grayscale": False,
    "rotate": False,
    "watermark": False,
    "convert_format": False,
    "crop": False
}

operation_choices = input(
    "Enter comma-separated operations to apply (grayscale, rotate, watermark, convert_format, crop): "
)
if operation_choices:
    selected_ops = [op.strip().lower() for op in operation_choices.split(',')]
    for op in selected_ops:
        if op in operations:
            operations[op] = True

# Additional inputs
angle = 0
watermark_text = ""
target_format = ""
crop_x = crop_y = crop_width = crop_height = 0

if operations["rotate"]:
    angle = float(input("Enter rotation angle (e.g., 90): "))

if operations["watermark"]:
    watermark_text = input("Enter watermark text (e.g., Sample): ")

if operations["convert_format"]:
    target_format = input("Enter target format (jpg, png, bmp): ").strip().upper()
    if target_format not in ['JPG', 'PNG', 'BMP']:
        print("Invalid format. Using PNG.")
        target_format = 'PNG'

if operations["crop"]:
    crop_x = int(input("Enter crop start X: "))
    crop_y = int(input("Enter crop start Y: "))
    crop_width = int(input("Enter crop width: "))
    crop_height = int(input("Enter crop height: "))

# Supported extensions
supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

backup_images = []

for filename in os.listdir(source_folder):
    if filename.lower().endswith(supported_extensions) and '_edited' not in filename:
        source_path = os.path.join(source_folder, filename)

        name, ext = os.path.splitext(filename)
        save_ext = f".{target_format.lower()}" if operations["convert_format"] else ext
        new_filename = f"{name}_edited{save_ext}"
        destination_path = os.path.join(destination_folder, new_filename)

        try:
            with Image.open(source_path) as img:
                original_format = img.format
                original_img = img.copy()

                # Resize
                if maintain_aspect:
                    img.thumbnail(target_size, Image.Resampling.LANCZOS)
                else:
                    img = img.resize(target_size, Image.Resampling.LANCZOS)

                if operations["grayscale"]:
                    img = img.convert("L")

                if operations["rotate"]:
                    img = img.rotate(angle, expand=True)

                if operations["watermark"]:
                    draw = ImageDraw.Draw(img)
                    font = ImageFont.load_default()
                    text_width, text_height = draw.textsize(watermark_text, font)
                    x = img.width - text_width - 10
                    y = img.height - text_height - 10
                    draw.text((x, y), watermark_text, fill="white", font=font)

                if operations["crop"]:
                    right = crop_x + crop_width
                    bottom = crop_y + crop_height
                    img = img.crop((crop_x, crop_y, right, bottom))

                save_format = target_format if operations["convert_format"] else original_format
                if save_format == 'JPG':
                    save_format = 'JPEG'

                img.save(destination_path, format=save_format)
                print(f"Saved: {new_filename} ({img.size})")

                backup_images.append((original_img.copy(), f"{name}_reversed{ext}"))

        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Ask to reverse
undo = input("Undo changes for all images? (yes/no): ").strip().lower().startswith('y')
if undo:
    for img, rev_name in backup_images:
        rev_path = os.path.join(destination_folder, rev_name)
        img.save(rev_path)
        print(f"Reversed: {rev_name}")
