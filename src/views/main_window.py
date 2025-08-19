import tkinter as tk
from tkinter import ttk
import sys

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
        
        # --- ウィンドウの基本設定 ---
        self.title("Surgical Video Analysis Tool 2")
        
        # ViewModel経由でSettingsModelからウィンドウサイズを取得して設定
        initial_geometry = self.viewmodel.settings_model.get("window_geometry")
        self.geometry(initial_geometry)
        
        # ウィンドウが閉じられるときのイベントをViewModelのメソッドに紐付け
        self.protocol("WM_DELETE_WINDOW", self.viewmodel.on_window_closing)

        # --- ウィジェットの作成と配置 ---
        self._create_widgets()
        
        # --- exe化で背面に行く問題への対策 ---
        # 元のコードにあった処理を踏襲し、ウィンドウを一度最前面に表示させる
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)


    def _create_widgets(self):
        """
        UIウィジェットを作成し、ウィンドウに配置します。
        """
        # --- メインレイアウトのフレームを作成 ---
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左側: 動画表示エリア
        video_panel = ttk.Frame(main_frame)
        video_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 垂直セパレーター
        ttk.Separator(main_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y)

        # 右側: コントロールパネルエリア
        control_panel = ttk.Frame(main_frame, width=350)
        control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        control_panel.pack_propagate(False) # 幅を350pxに固定

        # --- 動画表示エリアのウィジェット ---
        # 黒い背景のフレームを動画表示領域として作成
        style = ttk.Style(self)
        style.configure("Black.TFrame", background="black")
        self.video_frame = ttk.Frame(video_panel, style="Black.TFrame")
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- コントロールパネルのウィジェット（仮） ---
        label = ttk.Label(control_panel, text="Control Panel Skeleton")
        label.pack(pady=20, padx=20)


    def get_video_frame_handle(self) -> int:
        """
        動画表示用フレームのウィンドウハンドルを返します。
        VLCが描画対象を特定するために使用します。
        """
        # WindowsとLinux/macOSでVLCへのハンドル渡し方が異なるため、
        # winfo_id() でプラットフォーム共通のIDを取得する
        return self.video_frame.winfo_id()

    def start_main_loop(self):
        """
        Tkinterのメインイベントループを開始します。
        """
        self.mainloop()