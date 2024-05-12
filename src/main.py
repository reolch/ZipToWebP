import os
import shutil
import zipfile
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def validate_folder_path(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Error: Folder '{folder_path}' not found.")

def extract_zip_file(input_zip_file, output_dir):
    try:
        with zipfile.ZipFile(input_zip_file, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        print(f"Zip file '{input_zip_file}' successfully extracted to '{output_dir}'.")
    except FileNotFoundError:
        print(f"Error: Zip file '{input_zip_file}' not found.")
    except zipfile.BadZipFile:
        print(f"Error: '{input_zip_file}' is not a valid zip file.")
    except PermissionError:
        print(f"Error: Permission denied to extract '{input_zip_file}' to '{output_dir}'.")
    except Exception as e:
        print(f"An unexpected error occurred while extracting '{input_zip_file}': {e}")

def convert_image_to_webp(input_image_path, output_image_path):
    try:
        with Image.open(input_image_path) as image:
            image.save(output_image_path, "webp")
    except FileNotFoundError:
        print(f"Error: Input image file not found: {input_image_path}")
    except OSError as e:
        print(f"Error: Unable to open or save image: {e}")

def convert_images_to_webp(temp_dir):
    converted_files = []
    image_files = [os.path.join(root, filename) for root, _, files in os.walk(temp_dir) for filename in files if filename.endswith('.jpeg')]
    total_files = len(image_files)
    with ThreadPoolExecutor() as executor:
        futures = []
        with tqdm(total=total_files, desc="Converting images", unit="file") as pbar:
            for input_image_path in image_files:
                output_image_name = "00001.webp" if os.path.basename(input_image_path) == "cover.jpeg" else os.path.splitext(os.path.basename(input_image_path))[0] + ".webp"
                output_image_path = os.path.join(temp_dir, output_image_name)
                try:
                    future = executor.submit(convert_image_to_webp, input_image_path, output_image_path)
                    futures.append(future)
                except Exception as e:
                    print(f"Error converting {input_image_path}: {e}")
            for future in futures:
                future.result()
                pbar.update(1)
    return converted_files

def create_temp_dir(output_dir):
    temp_dir = os.path.join(output_dir, 'temp_conversion')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def remove_temp_dir(temp_dir):
    shutil.rmtree(temp_dir)

def create_output_folder(output_dir):
    output_folder = os.path.join(os.path.dirname(output_dir), "Output")
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def generate_output_zip_filename(input_zip_file):
    output_zip_filename = "WebP_" + os.path.basename(input_zip_file)
    return output_zip_filename

def add_files_to_zip(converted_files, output_zip_file, temp_dir):
    with zipfile.ZipFile(output_zip_file, 'w') as zipf:
        for converted_file in tqdm(converted_files, desc="Creating output ZIP", unit="file"):
            arcname = os.path.relpath(converted_file, temp_dir)
            zipf.write(converted_file, arcname)

def move_input_zip(input_zip_file, output_dir):
    converted_zip_folder = os.path.join(os.path.dirname(output_dir), "Converted_Zip")
    os.makedirs(converted_zip_folder, exist_ok=True)
    shutil.move(input_zip_file, converted_zip_folder)

def create_webp_zip(input_zip_file, output_dir):
    try:
        temp_dir = create_temp_dir(output_dir)
        extract_zip_file(input_zip_file, temp_dir)
        converted_files = convert_images_to_webp(temp_dir)
        output_folder = create_output_folder(output_dir)
        output_zip_filename = generate_output_zip_filename(input_zip_file)
        output_zip_file = os.path.join(output_folder, output_zip_filename)
        add_files_to_zip(converted_files, output_zip_file, temp_dir)
        remove_temp_dir(temp_dir)
        move_input_zip(input_zip_file, output_dir)
        print("Conversion completed.")
    except Exception as e:
        print(f"An error occurred during conversion: {e}")

def convert_zips_in_folder(folder_path):
    try:
        for root, _, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith('.zip'):
                    input_zip_file = os.path.join(root, filename)
                    create_webp_zip(input_zip_file, root)
    except Exception as e:
        print(f"An error occurred: {e}")

folder_path = input("Enter the folder path: ")
validate_folder_path(folder_path)
convert_zips_in_folder(folder_path)
