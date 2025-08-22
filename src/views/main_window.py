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

        # ショートカットキーをバインド
        self.bind_shortcuts()


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

        # プリセット管理用のフレーム
        preset_frame = ttk.LabelFrame(control_panel, text="Preset Manager", padding=5)
        preset_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        # 現在のプリセット名を表示・選択するためのコンボボックス
        self.preset_combo_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_combo_var,
            state="readonly"
        )
        # self.preset_combo.bind("<<ComboboxSelected>>", self.viewmodel.on_preset_selected) # 後で実装
        self.preset_combo.pack(fill=tk.X, pady=(0, 5))

        # プリセット管理ボタン用のフレーム
        preset_btn_frame = ttk.Frame(preset_frame)
        preset_btn_frame.pack(fill=tk.X)

        add_stamp_btn = ttk.Button(
            preset_btn_frame, text="Add Stamp",
            command=self.viewmodel.on_add_stamp_clicked
        )
        add_stamp_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        delete_stamp_btn = ttk.Button(
            preset_btn_frame, text="Delete Stamp",
            command=self.viewmodel.on_delete_stamp_clicked
        )
        delete_stamp_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 手順スタンプリスト用のフレーム
        stamp_frame = ttk.LabelFrame(control_panel, text="Procedure Stamps", padding=5)
        stamp_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)

        # Treeviewウィジェットを作成 (リスト表示用)
        self.stamp_tree = ttk.Treeview(
            stamp_frame,
            columns=("procedure"),
            show="headings",
            selectmode="browse"
        )
        self.stamp_tree.heading("procedure", text="手順名")
        self.stamp_tree.column("procedure", width=250)
        
        # 縦スクロールバーを作成
        v_scroll = ttk.Scrollbar(
            stamp_frame,
            orient=tk.VERTICAL,
            command=self.stamp_tree.yview
        )
        self.stamp_tree.configure(yscrollcommand=v_scroll.set)
        self.stamp_tree.bind("<<TreeviewSelect>>", self.viewmodel.on_stamp_select)        
        
        # Treeviewとスクロールバーを配置
        self.stamp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ステータス表示と記録ボタン用のフレーム
        status_frame = ttk.LabelFrame(control_panel, text="Status & Recording", padding=5)
        status_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))

        # ライブサマリー
        self.summary_count_var = tk.StringVar(value="Logged Procedures: 0")
        summary_count_label = ttk.Label(status_frame, textvariable=self.summary_count_var)
        summary_count_label.pack(anchor=tk.W)

        self.summary_duration_var = tk.StringVar(value="Total Duration: 0.00s")
        summary_duration_label = ttk.Label(status_frame, textvariable=self.summary_duration_var)
        summary_duration_label.pack(anchor=tk.W, pady=(0, 5))

        # 選択中アイテムの表示ラベル
        self.selected_var = tk.StringVar(value="Selected: ---")
        selected_label = ttk.Label(status_frame, textvariable=self.selected_var)
        selected_label.pack(anchor=tk.W, pady=(5, 0))

        # ボタン用のフレーム
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(fill=tk.X, pady=5)

        # 記録ボタン
        self.start_button = ttk.Button(
            button_frame, text="Start (S)",
            state=tk.DISABLED,
            command=self.viewmodel.on_start_clicked
        )
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.end_button = ttk.Button(
            button_frame, text="End (E)",
            state=tk.DISABLED,
            command=self.viewmodel.on_end_clicked
        )
        self.end_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.undo_button = ttk.Button(
            button_frame, text="Undo (U)",
            state=tk.DISABLED,
            command=self.viewmodel.on_undo_clicked
        )
        self.undo_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 終了・保存ボタン用のフレーム
        finish_frame = ttk.Frame(control_panel)
        finish_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        finish_button = ttk.Button(
            finish_frame,
            text="Finish & Save Results",
            command=self.viewmodel.on_finish_and_save_clicked
        )
        finish_button.pack(expand=True, fill=tk.X)

    def get_video_frame_handle(self) -> int:
        """
        動画表示用フレームのウィンドウハンドルを返します。
        VLCが描画対象を特定するために使用します。
        """
        # WindowsとLinux/macOSでVLCへのハンドル渡し方が異なるため、
        # winfo_id() でプラットフォーム共通のIDを取得する
        return self.video_frame.winfo_id()
    
    def bind_shortcuts(self):
        """
        キーボードショートカットを有効化します。
        """
        # .bind_all() を使うことで、どのウィジェットがフォーカスされていても反応する
        self.bind_all("<s>", lambda event: self.viewmodel.on_start_clicked())
        self.bind_all("<e>", lambda event: self.viewmodel.on_end_clicked())
        self.bind_all("<u>", lambda event: self.viewmodel.on_undo_clicked())
        print("Shortcuts enabled.")

    def unbind_shortcuts(self):
        """
        キーボードショートカットを無効化します。
        """
        self.unbind_all("<s>")
        self.unbind_all("<e>")
        self.unbind_all("<u>")
        print("Shortcuts disabled.")

    def update_preset_combo(self, preset_names: list[str], current_preset: str):
        """
        プリセット選択コンボボックスの内容を更新します。
        """
        self.preset_combo['values'] = preset_names
        self.preset_combo_var.set(current_preset)

    def start_main_loop(self):
        """
        Tkinterのメインイベントループを開始します。
        """
        self.mainloop()

    def update_stamp_list(self, stamps: list[str]):
        """
        手順スタンプのリスト表示を更新します。
        
        Args:
            stamps: 表示する手順名のリスト。
        """
        # 既存の項目をすべて削除
        for i in self.stamp_tree.get_children():
            self.stamp_tree.delete(i)
            
        # 新しいリストの項目を挿入
        for stamp in stamps:
            self.stamp_tree.insert("", tk.END, values=(stamp,))

    def get_selected_stamp_name(self) -> str | None:
        """
        Treeviewで現在選択されている項目の名前を返します。
        選択されていない場合は None を返します。
        """
        selected_items = self.stamp_tree.selection()
        if not selected_items:
            return None
        
        selected_item = selected_items[0]
        name = self.stamp_tree.item(selected_item, "values")[0]
        return name

    def set_selected_stamp_text(self, text: str):
        """
        選択中アイテム表示ラベルのテキストを更新します。
        """
        self.selected_var.set(f"Selected: {text}")