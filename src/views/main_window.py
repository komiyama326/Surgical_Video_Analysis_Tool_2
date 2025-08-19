import tkinter as tk
from tkinter import ttk

class MainWindow(tk.Tk):
    """
    アプリケーションのメインウィンドウ (View)。
    UI要素の作成と配置を担当します。
    """
    def __init__(self, viewmodel):
        """
        MainWindowの初期化。

        Args:
            viewmodel: このViewに対応するViewModel。
        """
        super().__init__()
        self.viewmodel = viewmodel
        
        # ウィンドウの基本設定
        self.title("Surgical Video Analysis Tool 2")
        # TODO: ウィンドウサイズはSettingsModelから取得して設定する
        self.geometry("1200x800") 
        
        # ウィンドウが閉じられるときのイベントをViewModelに通知
        self.protocol("WM_DELETE_WINDOW", self.viewmodel.on_window_closing)

        # TODO: ここに、動画表示フレーム、ボタン、リストなどの
        #       UIウィジェットを作成し、配置するコードを記述します。
        self._create_widgets()
        
        print("MainWindow (View) initialized.")

    def _create_widgets(self):
        """
        UIウィジェットを作成し、ウィンドウに配置します。
        """
        # --- レイアウトの作成 ---
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # TODO: ここに詳細なウィジェットを作成していく
        label = ttk.Label(main_frame, text="UI Skeleton - Widgets will be placed here.")
        label.pack(pady=20, padx=20)

    def start_main_loop(self):
        """
        Tkinterのメインイベントループを開始します。
        """
        self.mainloop()