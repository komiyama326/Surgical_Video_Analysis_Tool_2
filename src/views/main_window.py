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

    def set_video_model(self, video_model):
        """VideoPlayerModelへの参照を設定します。"""
        self.video_model = video_model

    # --- イベントハンドラ ---

    def _create_widgets(self):
        """
        UIウィジェットを作成し、ウィンドウに配置します。
        """
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        video_panel = ttk.Frame(main_frame)
        video_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        ttk.Separator(main_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y)
        control_panel = ttk.Frame(main_frame, width=350)
        control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        control_panel.pack_propagate(False)

        style = ttk.Style(self)
        style.configure("Black.TFrame", background="black")
        self.video_frame = ttk.Frame(video_panel, style="Black.TFrame")
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.timeline_var = tk.DoubleVar()
        self.timeline = ttk.Scale(video_panel, from_=0, to=1000, orient=tk.HORIZONTAL,
                                  variable=self.timeline_var, command=self.viewmodel.on_timeline_changed)
        self.timeline.pack(fill=tk.X, pady=5)

        self.time_display_var = tk.StringVar(value="--:--:-- / --:--:--")
        ttk.Label(video_panel, textvariable=self.time_display_var, anchor=tk.CENTER).pack(fill=tk.X)

        file_frame = ttk.Frame(control_panel)
        file_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        self.open_video_button = ttk.Button(file_frame, text="Open Video File(s)", command=self.viewmodel.on_open_video_clicked)
        self.open_video_button.pack(expand=True, fill=tk.X)

        playback_frame = ttk.Frame(control_panel)
        playback_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        skip_backward_btn = ttk.Button(playback_frame, text="<< 10s", command=lambda: self.viewmodel.on_skip_time_clicked(-10000))
        skip_backward_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        # 修正後
        self.play_pause_button = ttk.Button(
            playback_frame,
            text="Play",
            command=self.viewmodel.on_play_pause_clicked
        )
        self.play_pause_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        skip_forward_btn = ttk.Button(playback_frame, text="10s >>", command=lambda: self.viewmodel.on_skip_time_clicked(10000))
        skip_forward_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        speed_frame = ttk.LabelFrame(control_panel, text="Playback Speed", padding=5)
        speed_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.speed_buttons = {}
        for speed in [0.5, 1.0, 2.0]:
            btn = ttk.Button(speed_frame, text=f"{speed}x", command=lambda s=speed: self.viewmodel.on_set_speed_clicked(s))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.speed_buttons[speed] = btn

        options_frame = ttk.LabelFrame(control_panel, text="Options", padding=5)
        options_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.memo_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Enable Memo on 'End'", variable=self.memo_enabled_var,
                        command=self.viewmodel.on_options_changed).pack(anchor=tk.W)
        self.graph_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Generate Graph on 'Finish'", variable=self.graph_enabled_var,
                        command=self.viewmodel.on_options_changed).pack(anchor=tk.W)

        preset_frame = ttk.LabelFrame(control_panel, text="Preset Manager", padding=5)
        preset_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        self.preset_combo_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_combo_var, state="readonly")
        self.preset_combo.pack(fill=tk.X, pady=(0, 5))
        self.preset_combo.bind("<<ComboboxSelected>>", self.viewmodel.on_preset_selected)

        preset_btn_frame = ttk.Frame(preset_frame)
        preset_btn_frame.pack(fill=tk.X)
        ttk.Button(preset_btn_frame, text="Add Stamp", command=self.viewmodel.on_add_stamp_clicked).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(preset_btn_frame, text="Delete Stamp", command=self.viewmodel.on_delete_stamp_clicked).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(preset_btn_frame, text="▲ Up", command=lambda: self.viewmodel.on_move_stamp_clicked(-1)).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(preset_btn_frame, text="▼ Down", command=lambda: self.viewmodel.on_move_stamp_clicked(1)).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # プリセット自体を管理するボタン用のフレーム
        preset_manage_frame = ttk.Frame(preset_frame)
        preset_manage_frame.pack(fill=tk.X, pady=(5, 0))

        save_btn = ttk.Button(
            preset_manage_frame, text="Save Preset",
            command=self.viewmodel.on_save_preset_clicked
        )
        save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        save_as_btn = ttk.Button(
            preset_manage_frame, text="Save As...",
            command=self.viewmodel.on_save_preset_as_clicked
        )
        save_as_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        rename_btn = ttk.Button(
            preset_manage_frame, text="Rename Preset",
            command=self.viewmodel.on_rename_preset_clicked
        )
        rename_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        delete_btn = ttk.Button(
            preset_manage_frame, text="Delete Preset",
            command=self.viewmodel.on_delete_preset_clicked
        )
        delete_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        stamp_frame = ttk.LabelFrame(control_panel, text="Procedure Stamps", padding=5)
        stamp_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)
        self.stamp_tree = ttk.Treeview(stamp_frame, columns=("procedure"), show="headings", selectmode="browse")
        self.stamp_tree.heading("procedure", text="手順名")
        self.stamp_tree.column("procedure", width=250)
        v_scroll = ttk.Scrollbar(stamp_frame, orient=tk.VERTICAL, command=self.stamp_tree.yview)
        self.stamp_tree.configure(yscrollcommand=v_scroll.set)
        self.stamp_tree.bind("<<TreeviewSelect>>", self.viewmodel.on_stamp_select)        
        self.stamp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        status_frame = ttk.LabelFrame(control_panel, text="Status & Recording", padding=5)
        status_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))
        self.summary_count_var = tk.StringVar(value="Logged Procedures: 0")
        ttk.Label(status_frame, textvariable=self.summary_count_var).pack(anchor=tk.W)
        self.summary_duration_var = tk.StringVar(value="Total Duration: 0.00s")
        ttk.Label(status_frame, textvariable=self.summary_duration_var).pack(anchor=tk.W, pady=(0, 5))
        self.selected_var = tk.StringVar(value="Selected: ---")
        ttk.Label(status_frame, textvariable=self.selected_var).pack(anchor=tk.W, pady=(5, 0))
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(fill=tk.X, pady=5)
        self.start_button = ttk.Button(button_frame, text="Start (S)", state=tk.DISABLED, command=self.viewmodel.on_start_clicked)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.end_button = ttk.Button(button_frame, text="End (E)", state=tk.DISABLED, command=self.viewmodel.on_end_clicked)
        self.end_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.undo_button = ttk.Button(button_frame, text="Undo (U)", state=tk.DISABLED, command=self.viewmodel.on_undo_clicked)
        self.undo_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        finish_frame = ttk.Frame(control_panel)
        finish_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        ttk.Button(finish_frame, text="Finish & Save Results", command=self.viewmodel.on_finish_and_save_clicked).pack(expand=True, fill=tk.X)

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