import os
import shutil
import zipfile
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def convert_image_to_webp(input_image_path, output_image_path):
    with Image.open(input_image_path) as image:
        image.save(output_image_path, "webp")

def extract_zip(input_zip_file, temp_dir):
    try:
        with zipfile.ZipFile(input_zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    except Exception as e:
        print(f"Error extracting zip file {input_zip_file}: {e}")

# def convert_images_to_webp(temp_dir):
#     converted_files = []
#     total_files = len([filename for _, _, files in os.walk(temp_dir) for filename in files if filename.endswith('.jpeg')])
#     with ThreadPoolExecutor() as executor:
#         for root, _, files in os.walk(temp_dir):
#             for filename in tqdm(files, desc="Converting images", unit="file", total=total_files):
#                 if filename.endswith('.jpeg'):
#                     input_image_path = os.path.join(root, filename)
#                     output_image_name = "00001.webp" if filename == "cover.jpeg" else os.path.splitext(filename)[0] + ".webp"
#                     output_image_path = os.path.join(temp_dir, output_image_name)
#                     try:
#                         executor.submit(convert_image_to_webp, input_image_path, output_image_path)
#                         converted_files.append(output_image_path)
#                     except Exception as e:
#                         print(f"Error converting {input_image_path}: {e}")
#     return converted_files

def convert_images_to_webp(temp_dir):
    converted_files = []
    
    # 画像ファイルの数を取得
    image_files = [os.path.join(root, filename) for root, _, files in os.walk(temp_dir) for filename in files if filename.endswith('.jpeg')]
    total_files = len(image_files)
    
    with ThreadPoolExecutor() as executor:
        for input_image_path in tqdm(image_files, desc="Converting images", unit="file", total=total_files):
            output_image_name = "00001.webp" if os.path.basename(input_image_path) == "cover.jpeg" else os.path.splitext(os.path.basename(input_image_path))[0] + ".webp"
            output_image_path = os.path.join(temp_dir, output_image_name)
            try:
                executor.submit(convert_image_to_webp, input_image_path, output_image_path)
                converted_files.append(output_image_path)
            except Exception as e:
                print(f"Error converting {input_image_path}: {e}")
    
    return converted_files

def create_webp_zip(input_zip_file, output_dir):
    temp_dir = os.path.join(output_dir, 'temp_conversion')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        extract_zip(input_zip_file, temp_dir)
        converted_files = convert_images_to_webp(temp_dir)

        output_folder = os.path.join(os.path.dirname(output_dir), "Output")
        os.makedirs(output_folder, exist_ok=True)
        output_zip_filename = "WebP_" + os.path.basename(input_zip_file)
        output_zip_file = os.path.join(output_folder, output_zip_filename)

        with zipfile.ZipFile(output_zip_file, 'w') as zipf:
            for converted_file in tqdm(converted_files, desc="Creating output ZIP", unit="file"):
                arcname = os.path.relpath(converted_file, temp_dir)
                zipf.write(converted_file, arcname)

        shutil.rmtree(temp_dir)

        converted_zip_folder = os.path.join(os.path.dirname(output_dir), "Converted_Zip")
        os.makedirs(converted_zip_folder, exist_ok=True)
        shutil.move(input_zip_file, converted_zip_folder)
        # shutil.move(output_zip_file, output_folder)

        print("Conversion completed.")
    except Exception as e:
        print(f"An error occurred during conversion: {e}")

def convert_zips_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.zip'):
                input_zip_file = os.path.join(root, filename)
                create_webp_zip(input_zip_file, root)

folder_path = input("Enter the folder path: ")
convert_zips_in_folder(folder_path)
