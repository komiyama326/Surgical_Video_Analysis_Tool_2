import tkinter as tk
from tkinter import ttk
import sys
from ..utils import helpers

class MainWindow(tk.Tk):
    """
    アプリケーションのメインウィンドウ (View)。
    UI要素の作成と配置を担当します。
    """
    def __init__(self, viewmodel):
        """
        MainWindowの初期化
        """
        super().__init__()
        self.viewmodel = viewmodel
        
        self.title("Surgical Video Analysis Tool 2")
        initial_geometry = self.viewmodel.settings_model.get("window_geometry")
        self.geometry(initial_geometry)
        self.protocol("WM_DELETE_WINDOW", self.viewmodel.on_window_closing)

        self._create_widgets()
        
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)

        self.bind_shortcuts()
        self.is_next_session_requested = False

        self.is_slider_dragging = False # タイムラインをドラッグ中かどうかのフラグ

    def set_video_model(self, video_model):
        """VideoPlayerModelへの参照を設定します。"""
        self.video_model = video_model

    # --- イベントハンドラ ---

    def _create_widgets(self):
        """
        UIウィジェットを作成し、ウィンドウに配置します。
        """
        # --- スタイル定義 (デザインガイドラインの適用) ---
        style = ttk.Style(self)
        
        # OSのテーマをベースにする (Windows: "vista", macOS: "aqua", Linux: "clam")
        # これにより、OSネイティブのウィジェット感を維持できる
        style.theme_use('vista' if sys.platform == 'win32' else 'clam')

        # フォント定義
        font_body = ("Segoe UI", 10)
        font_caption = ("Segoe UI", 9)
        font_section_title = ("Segoe UI", 11, "bold") # 少し小さくしてバランス調整

        # カラー定義
        COLOR_BG = "#ECECEC"
        COLOR_TEXT_PRIMARY = "#1D1D1F"
        COLOR_TEXT_SECONDARY = "#6E6E73"
        COLOR_ACCENT = "#007AFF"
        COLOR_ACCENT_TEXT = "#FFFFFF"

        # ウィンドウ全体の背景色
        self.configure(background=COLOR_BG)

        # --- スタイルの設定 ---
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT_PRIMARY, font=font_body)
        style.configure("TButton", font=font_body, padding=(10, 6))
        style.configure("TCheckbutton", background=COLOR_BG, font=font_body)
        
        style.configure("TLabelframe", background=COLOR_BG, borderwidth=1)
        style.configure("TLabelframe.Label", background=COLOR_BG, foreground=COLOR_TEXT_SECONDARY, font=font_section_title)
        
        style.configure("Treeview", rowheight=28, font=font_body, fieldbackground=style.lookup("TFrame", "background"))
        style.configure("Treeview.Heading", font=(font_body[0], font_body[1], "bold")) # 見出しを太字に
        style.map("Treeview", background=[("selected", COLOR_ACCENT)], foreground=[("selected", COLOR_ACCENT_TEXT)])
        
        # 主要アクション用のカスタムスタイル
        style.configure("Accent.TButton", background=COLOR_ACCENT, foreground=COLOR_ACCENT_TEXT)
        style.map("Accent.TButton", background=[("active", "#0056b3")]) # ホバー時の色

        # --- メインレイアウト ---
        main_frame = ttk.Frame(self, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        video_panel = ttk.Frame(paned_window, padding=(0, 0, 12, 0))
        paned_window.add(video_panel, weight=3)
        control_panel = ttk.Frame(paned_window, padding=(12, 0, 0, 0))
        paned_window.add(control_panel, weight=1)

        # --- 動画表示エリア ---
        style.configure("Black.TFrame", background="black")
        self.video_frame = ttk.Frame(video_panel, style="Black.TFrame")
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.timeline_var = tk.DoubleVar()
        self.timeline = ttk.Scale(video_panel, from_=0, to=1000, orient=tk.HORIZONTAL,
                                variable=self.timeline_var)

        def update_timeline_on_event(event):
            """イベントの位置情報から Scale の値を更新し、シークをトリガーする"""
            # スライダーの全長(ピクセル)に対する、クリック位置の割合を計算
            percentage = event.x / event.widget.winfo_width()
            # 割合を scale の値 (0-1000) に変換
            scale_value = percentage * 1000
            # 値が範囲内に収まるように調整
            scale_value = max(0, min(1000, scale_value))
            
            # variable を手動で更新
            self.timeline_var.set(scale_value)
            # ViewModel にシークを依頼
            self.viewmodel.on_timeline_changed(scale_value)

        def on_slider_press(event):
            self.is_slider_dragging = True
            update_timeline_on_event(event)

        def on_slider_drag(event):
            if self.is_slider_dragging:
                update_timeline_on_event(event)

        def on_slider_release(event):
            self.is_slider_dragging = False
            
        # command は使わず、bind のみで全ての操作を管理
        self.timeline.bind("<ButtonPress-1>", on_slider_press)
        self.timeline.bind("<B1-Motion>", on_slider_drag) # ドラッグ中もシーク
        self.timeline.bind("<ButtonRelease-1>", on_slider_release)

        self.timeline.pack(fill=tk.X, pady=(8, 4))

        self.time_display_var = tk.StringVar(value="--:--:-- / --:--:--")
        ttk.Label(video_panel, textvariable=self.time_display_var, anchor=tk.CENTER, font=font_caption).pack(fill=tk.X)


        # --- コントロールパネル ---
        footer_frame = ttk.Frame(control_panel)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(12, 0))
        self.finish_and_next_button = ttk.Button(footer_frame, text="Save & Next", command=self.viewmodel.on_finish_and_next_clicked)
        self.finish_and_next_button.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=4, padx=(0, 4))
        self.finish_button = ttk.Button(footer_frame, text="Save & Finish", command=self.viewmodel.on_finish_and_save_clicked)
        self.finish_button.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=4, padx=(4, 0))
        
        scroll_area_frame = ttk.Frame(control_panel)
        scroll_area_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(scroll_area_frame, highlightthickness=0, background=COLOR_BG)
        scrollbar = ttk.Scrollbar(scroll_area_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")
    
        # --- スクロール可能なフレーム内のウィジェット ---
        file_frame = ttk.Frame(scrollable_frame)
        file_frame.pack(side=tk.TOP, fill=tk.X)
        self.open_video_button = ttk.Button(file_frame, text="Open Video File(s)", command=self.viewmodel.on_open_video_clicked)
        self.open_video_button.pack(expand=True, fill=tk.X, ipady=4)

        main_controls_frame = ttk.Frame(scrollable_frame)
        main_controls_frame.pack(side=tk.TOP, fill=tk.X, pady=(24, 0))

        playback_frame = ttk.LabelFrame(main_controls_frame, text="Playback")
        playback_frame.pack(fill=tk.X)
        skip_backward_btn = ttk.Button(playback_frame, text="<< 10s", command=lambda: self.viewmodel.on_skip_time_clicked(-10000))
        skip_backward_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.play_pause_button = ttk.Button(playback_frame, text="Play (P)", command=self.viewmodel.on_play_pause_clicked)
        self.play_pause_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=8)
        skip_forward_btn = ttk.Button(playback_frame, text="10s >>", command=lambda: self.viewmodel.on_skip_time_clicked(10000))
        skip_forward_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        speed_frame = ttk.LabelFrame(main_controls_frame, text="Playback Speed")
        speed_frame.pack(fill=tk.X, pady=(12, 0))
        self.speed_buttons = {}
        for speed in [0.5, 1.0, 2.0]:
            btn = ttk.Button(speed_frame, text=f"{speed}x", command=lambda s=speed: self.viewmodel.on_set_speed_clicked(s))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
            self.speed_buttons[speed] = btn

        status_frame = ttk.LabelFrame(main_controls_frame, text="Status & Recording")
        status_frame.pack(fill=tk.X, pady=(12, 0))
        self.summary_count_var = tk.StringVar(value="Logged Procedures: 0")
        ttk.Label(status_frame, textvariable=self.summary_count_var).pack(anchor=tk.W, pady=2)
        self.summary_duration_var = tk.StringVar(value="Total Duration: 0.00s")
        ttk.Label(status_frame, textvariable=self.summary_duration_var, font=font_caption).pack(anchor=tk.W, pady=(0, 8))
        self.selected_var = tk.StringVar(value="Selected: ---")
        ttk.Label(status_frame, textvariable=self.selected_var).pack(anchor=tk.W, pady=(8, 0))
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(fill=tk.X, pady=8)
        self.start_button = ttk.Button(button_frame, text="Start (S)", state=tk.DISABLED, command=self.viewmodel.on_start_clicked)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,4))
        self.end_button = ttk.Button(button_frame, text="End (E)", state=tk.DISABLED, command=self.viewmodel.on_end_clicked)
        self.end_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        self.undo_button = ttk.Button(button_frame, text="Undo (U)", state=tk.DISABLED, command=self.viewmodel.on_undo_clicked)
        self.undo_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4,0))
        
        stamp_frame = ttk.LabelFrame(scrollable_frame, text="Procedure Stamps")
        stamp_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(24, 0))
        self.stamp_tree = ttk.Treeview(stamp_frame, columns=("procedure"), show="headings", selectmode="browse")
        self.stamp_tree.heading("procedure", text="Procedure")
        self.stamp_tree.column("procedure", width=250)
        v_scroll = ttk.Scrollbar(stamp_frame, orient=tk.VERTICAL, command=self.stamp_tree.yview)
        self.stamp_tree.configure(yscrollcommand=v_scroll.set)
        self.stamp_tree.bind("<<TreeviewSelect>>", self.viewmodel.on_stamp_select)        
        self.stamp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        settings_frame = ttk.Frame(scrollable_frame)
        settings_frame.pack(side=tk.TOP, fill=tk.X, pady=(24, 0))
        preset_frame = ttk.LabelFrame(settings_frame, text="Preset Manager")
        preset_frame.pack(fill=tk.X)
        self.preset_combo_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_combo_var, state="readonly", font=font_body)
        self.preset_combo.pack(fill=tk.X, pady=4)
        self.preset_combo.bind("<<ComboboxSelected>>", self.viewmodel.on_preset_selected)
        preset_btn_frame = ttk.Frame(preset_frame)
        preset_btn_frame.pack(fill=tk.X, pady=4)
        ttk.Button(preset_btn_frame, text="Add Stamp", command=self.viewmodel.on_add_stamp_clicked).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,4))
        ttk.Button(preset_btn_frame, text="Delete Stamp", command=self.viewmodel.on_delete_stamp_clicked).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        ttk.Button(preset_btn_frame, text="▲ Up", command=lambda: self.viewmodel.on_move_stamp_clicked(-1)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        ttk.Button(preset_btn_frame, text="▼ Down", command=lambda: self.viewmodel.on_move_stamp_clicked(1)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4,0))
        preset_manage_frame = ttk.Frame(preset_frame)
        preset_manage_frame.pack(fill=tk.X, pady=(4,0))
        ttk.Button(preset_manage_frame, text="Save Preset", command=self.viewmodel.on_save_preset_clicked).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,4))
        ttk.Button(preset_manage_frame, text="Save As...", command=self.viewmodel.on_save_preset_as_clicked).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        ttk.Button(preset_manage_frame, text="Rename Preset", command=self.viewmodel.on_rename_preset_clicked).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        ttk.Button(preset_manage_frame, text="Delete Preset", command=self.viewmodel.on_delete_preset_clicked).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4,0))

        options_frame = ttk.LabelFrame(settings_frame, text="Options")
        options_frame.pack(fill=tk.X, pady=(12, 0))
        self.memo_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Enable Memo on 'End'", variable=self.memo_enabled_var,
                        command=self.viewmodel.on_options_changed).pack(anchor=tk.W, pady=4)
        self.graph_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Generate Graph on 'Finish'", variable=self.graph_enabled_var,
                        command=self.viewmodel.on_options_changed).pack(anchor=tk.W, pady=4)

        # マウスホイールでのスクロールを有効化
        def _on_mousewheel(event):
            # Windows/macOS/Linuxでイベントのdelta値が異なるため、それを吸収する
            # event.deltaはWindows, event.numはLinux
            if hasattr(event, 'delta') and event.delta != 0:
                delta = -1 * (event.delta // 120)
            elif hasattr(event, 'num') and event.num in (4, 5):
                delta = 1 if event.num == 5 else -1
            else:
                return # 不明なイベントは無視

            canvas.yview_scroll(delta, "units")

        # ★★★【今回の修正の核心】★★★
        def _on_treeview_scroll_enter(event):
            """Treeviewに入ったら、Canvasのホイールバインドを解除"""
            canvas.unbind("<MouseWheel>")
            for child in scrollable_frame.winfo_children():
                def unbind_recursive(widget):
                    widget.unbind("<MouseWheel>")
                    for sub_child in widget.winfo_children():
                        unbind_recursive(sub_child)
                unbind_recursive(child)

        def _on_treeview_scroll_leave(event):
            """Treeviewから出たら、Canvasのホイールバインドを再設定"""
            canvas.bind("<MouseWheel>", _on_mousewheel)
            for child in scrollable_frame.winfo_children():
                def bind_recursive(widget):
                    widget.bind("<MouseWheel>", _on_mousewheel)
                    for sub_child in widget.winfo_children():
                        bind_recursive(sub_child)
                bind_recursive(child)

        # Treeview自体とその親フレームにEnter/Leaveイベントを設定
        # これにより、Treeviewの領域(スクロールバー含む)で判定
        stamp_frame.bind("<Enter>", _on_treeview_scroll_enter)
        stamp_frame.bind("<Leave>", _on_treeview_scroll_leave)

        # 最初のアプローチに戻り、Canvasエリア全体にバインドを設定
        _on_treeview_scroll_leave(None) # 初期状態でバインドを有効化

    def bind_shortcuts(self):
        """キーボードショートカットを有効化します。"""
        self.bind_all("<p>", lambda event: self.viewmodel.on_play_pause_clicked())
        self.bind_all("<s>", lambda event: self.viewmodel.on_start_clicked())
        self.bind_all("<e>", lambda event: self.viewmodel.on_end_clicked())
        self.bind_all("<u>", lambda event: self.viewmodel.on_undo_clicked())
        self.bind_all("<Left>", lambda e: self.viewmodel.on_skip_time_clicked(-10000))
        self.bind_all("<Right>", lambda e: self.viewmodel.on_skip_time_clicked(10000))
        print("Shortcuts enabled.")

    def unbind_shortcuts(self):
        """キーボードショートカットを無効化します。"""
        self.unbind_all("<p>")
        self.unbind_all("<s>")
        self.unbind_all("<e>")
        self.unbind_all("<u>")
        print("Shortcuts disabled.")

    def get_video_frame_handle(self) -> int:
        return self.video_frame.winfo_id()
    
    def update_preset_combo(self, preset_names: list[str], current_preset: str):
        self.preset_combo['values'] = preset_names
        self.preset_combo_var.set(current_preset)

    def start_main_loop(self):
        self.mainloop()

    def update_stamp_list_and_select(self, stamps: list[str], select_index: int = -1):
        self.stamp_tree.selection_remove(self.stamp_tree.selection())
        for i in self.stamp_tree.get_children():
            self.stamp_tree.delete(i)
        for stamp in stamps:
            self.stamp_tree.insert("", tk.END, values=(stamp,))
        if 0 <= select_index < len(stamps):
            children = self.stamp_tree.get_children()
            item_to_select = children[select_index]
            self.stamp_tree.selection_set(item_to_select)
            self.stamp_tree.focus(item_to_select)
            self.stamp_tree.see(item_to_select)

    def get_selected_stamp_name(self) -> str | None:
        selected_items = self.stamp_tree.selection()
        if not selected_items:
            return None
        return self.stamp_tree.item(selected_items[0], "values")[0]

    def set_selected_stamp_text(self, text: str):
        self.selected_var.set(f"Selected: {text}")