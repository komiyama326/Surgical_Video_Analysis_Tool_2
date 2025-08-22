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

        # --- タイムライン（再生スライダー） ---
        self.timeline_var = tk.DoubleVar()
        self.timeline = ttk.Scale(
            video_panel,
            from_=0,
            to=1000,
            orient=tk.HORIZONTAL,
            variable=self.timeline_var,
            # command=self.viewmodel.on_timeline_seek # シーク処理は後で実装
        )
        self.timeline.pack(fill=tk.X, pady=5)

        # --- 時間表示ラベル ---
        self.time_display_var = tk.StringVar(value="--:--:-- / --:--:--")
        time_display_label = ttk.Label(
            video_panel,
            textvariable=self.time_display_var,
            anchor=tk.CENTER
        )
        time_display_label.pack(fill=tk.X)

        # --- コントロールパネルのウィジェット ---
        # 上部にファイル操作用のフレームを配置
        file_frame = ttk.Frame(control_panel)
        file_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        self.open_video_button = ttk.Button(
            file_frame,
            text="Open Video File(s)",
            command=self.viewmodel.on_open_video_clicked
        )
        self.open_video_button.pack(expand=True, fill=tk.X)

        # 再生コントロール用のフレーム
        playback_frame = ttk.Frame(control_panel)
        playback_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.play_pause_button = ttk.Button(
            playback_frame,
            text="Play",
            command=self.viewmodel.on_play_pause_clicked
        )
        self.play_pause_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # TODO: ここに早送り・巻き戻し、速度変更ボタンを追加していく


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