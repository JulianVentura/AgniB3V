import subprocess
import os


def convert_to_xlsx(file):
    command = [
        "libreoffice",
        "--headless",
        "--convert-to",
        "xlsx",
        "--outdir",
        os.path.dirname(file),
        file,
    ]
    # Run the command
    try:
        subprocess.run(command, check=True)
        print("Conversion successful!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")


def convert_all_files():
    all_files = []
    for root, dirs, files in os.walk("./Pruebas estudiantes"):
        for file in files:
            # The 'os.path.join()' function is used to create the full path of each file
            file_path = os.path.join(root, file)
            if os.path.splitext(file_path)[1] == ".xls":
                all_files.append(file_path)

    i = 0
    for file in all_files:
        convert_to_xlsx(file)
        print(i / len(all_files) * 100, "%")
        i += 1


convert_all_files()
