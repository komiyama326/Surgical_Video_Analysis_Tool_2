# main.py
import tkinter as tk

def main():
    """アプリケーションを起動するエントリーポイント"""
    root = tk.Tk()
    root.withdraw() # ファイル選択ダイアログの背後に表示される不要なウィンドウを隠す
    # 今後の処理をここに追加していく
    print("Application started.") # 動作確認用

if __name__ == "__main__":
    main()