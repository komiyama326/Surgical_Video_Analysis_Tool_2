import sys
import os
import tkinter as tk
from tkinter import filedialog

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import Application

def select_video_files() -> list[str]:
    """
    動画ファイル選択ダイアログを表示し、選択されたファイルのパスリストを返す。
    何も選択されなければ空のリストを返す。
    """
    # メインウィンドウを裏で作成して、ダイアログの親にする
    root = tk.Tk()
    root.withdraw() # ウィンドウは表示しない
    
    file_paths = filedialog.askopenfilenames(
        title="Select Video File(s)",
        filetypes=(("Movie Files", "*.mp4 *.mov *.avi"), ("All files", "*.*"))
    )
    
    root.destroy() # 裏で作ったウィンドウを破棄
    
    return list(file_paths)

def main():
    """
    アプリケーションのメインループ。
    """
    while True:
        video_paths = select_video_files()
        
        # ファイルが選択されなかったら、ループを終了してアプリを閉じる
        if not video_paths:
            break

        app = Application(video_paths) # 選択されたパスを渡して起動
        continue_session = app.run()
        
        if not continue_session:
            break
            
    print("Application has been completely closed.")

if __name__ == "__main__":
    main()