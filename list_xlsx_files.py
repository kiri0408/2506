import os
import sys

def list_xlsx_files(folder_path):
    """
    指定フォルダ以下のすべての .xlsx ファイルのパスをリストアップする。
    """
    xlsx_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.xlsx') and '報告書' in file:
                full_path = os.path.join(root, file)
                xlsx_files.append(full_path)
    return xlsx_files

def main(folder=None):
    # 引数でフォルダパスを受け取る。指定なければカレントディレクトリを使う。
    if folder is None:
        folder = os.getcwd()
    files = list_xlsx_files(folder)
    for f in files:
        print(f)

if __name__ == "__main__":
    main()
