import os
import shutil
import zipfile
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def convert_image_to_webp(input_image_path, output_image_path):
    try:
        with Image.open(input_image_path) as image:
            image.save(output_image_path, "webp")
    except FileNotFoundError:
        print(f"Error: Input image file not found: {input_image_path}")
    except OSError as e:
        print(f"Error: Unable to open or save image: {e}")

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

def convert_images_to_webp(temp_dir):
    converted_files = []
    
    # 画像ファイルの数を取得
    image_files = [os.path.join(root, filename) for root, _, files in os.walk(temp_dir) for filename in files if filename.endswith('.jpeg')]
    total_files = len(image_files)
    
    with ThreadPoolExecutor() as executor:
        # すべてのFutureオブジェクトを収集するためのリスト
        futures = []
        with tqdm(total=total_files, desc="Converting images", unit="file") as pbar:
            for input_image_path in image_files:
                output_image_name = "00001.webp" if os.path.basename(input_image_path) == "cover.jpeg" else os.path.splitext(os.path.basename(input_image_path))[0] + ".webp"
                output_image_path = os.path.join(temp_dir, output_image_name)
                try:
                    # submitメソッドの戻り値はFutureオブジェクト
                    future = executor.submit(convert_image_to_webp, input_image_path, output_image_path)
                    # Futureオブジェクトをリストに追加
                    futures.append(future)
                except Exception as e:
                    print(f"Error converting {input_image_path}: {e}")
            
            # すべてのFutureオブジェクトの完了を待機し、進捗を更新
            for future in futures:
                future.result()  # 完了を待機
                pbar.update(1)  # 進捗を更新
    
    return converted_files

def create_webp_zip(input_zip_file, output_dir):
    try:
        # 一時ディレクトリを作成
        temp_dir = os.path.join(output_dir, 'temp_conversion')
        os.makedirs(temp_dir, exist_ok=True)

        # Zipファイルを展開して画像をWebP形式に変換
        extract_zip_file(input_zip_file, temp_dir)
        converted_files = convert_images_to_webp(temp_dir)

        # 出力用のフォルダを作成
        output_folder = os.path.join(os.path.dirname(output_dir), "Output")
        os.makedirs(output_folder, exist_ok=True)

        # 出力Zipファイルのパスを生成
        output_zip_filename = "WebP_" + os.path.basename(input_zip_file)
        output_zip_file = os.path.join(output_folder, output_zip_filename)

        # WebP形式に変換した画像をZipファイルに追加
        with zipfile.ZipFile(output_zip_file, 'w') as zipf:
            for converted_file in tqdm(converted_files, desc="Creating output ZIP", unit="file"):
                arcname = os.path.relpath(converted_file, temp_dir)
                zipf.write(converted_file, arcname)

        # 一時ディレクトリを削除
        shutil.rmtree(temp_dir)

        # 入力ZipファイルをConverted_Zipフォルダに移動
        converted_zip_folder = os.path.join(os.path.dirname(output_dir), "Converted_Zip")
        os.makedirs(converted_zip_folder, exist_ok=True)
        shutil.move(input_zip_file, converted_zip_folder)

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
