import sys
import os
import tkinter as tk
from tkinter import filedialog

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import Application

def select_video_files() -> list[str]:
    """
    動画ファイル選択ダイアログを画面の中央に表示し、
    選択されたファイルのパスリストを返す。
    """
    root = tk.Tk()
    # まずウィンドウ自体を画面中央に移動させる準備
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # ウィンドウを非表示にする
    root.withdraw()

    # transient()でダイアログを親ウィンドウの上に表示する設定
    # これにより、ダイアログが親ウィンドウの中央に表示されやすくなる
    root.transient()
    
    file_paths = filedialog.askopenfilenames(
        parent=root, # 親ウィンドウを明示的に指定
        title="Select Video File(s)",
        filetypes=(("Movie Files", "*.mp4 *.mov *.avi"), ("All files", "*.*"))
    )
    
    # 念のためgrab_release()を呼んでおく
    root.grab_release()
    root.destroy()
    
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