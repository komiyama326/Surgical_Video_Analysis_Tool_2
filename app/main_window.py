# app/main_window.py
import tkinter as tk

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Surgical Video Analysis Tool v2")
        self.geometry("1300x850")

        # 今後のウィジェット作成処理をここに追加していく
        label = tk.Label(self, text="UI Window")
        label.pack(pady=20, padx=20)