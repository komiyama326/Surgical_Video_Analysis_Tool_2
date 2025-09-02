import tkinter as tk
from tkinter import ttk

class AddStampDialog(tk.Toplevel):
    def __init__(self, parent, existing_stamps: list[str]):
        super().__init__(parent)
        self.transient(parent) # 親ウィンドウの上に表示
        self.title("Add or Select Stamp")
        self.parent = parent
        self.result = None

        # --- ウィジェットの作成 ---
        main_frame = ttk.Frame(self, padding=12)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 既存スタンプのリストボックス
        list_frame = ttk.LabelFrame(main_frame, text="Select from existing stamps", padding=8)
        list_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 12))

        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, height=10)
        for stamp in existing_stamps:
            self.listbox.insert(tk.END, stamp)
        self.listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 新規入力のエントリー
        entry_frame = ttk.LabelFrame(main_frame, text="Or enter a new name", padding=8)
        entry_frame.pack(fill=tk.X)
        self.entry = ttk.Entry(entry_frame)
        self.entry.pack(expand=True, fill=tk.X)

        # OK/Cancelボタン
        button_frame = ttk.Frame(main_frame, padding=(0, 12, 0, 0))
        button_frame.pack(fill=tk.X)
        
        ok_button = ttk.Button(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

        # --- 初期設定 ---
        self.geometry("350x450")
        self.grab_set() # モーダルにする (このウィンドウ以外操作できなくする)

        # --- ウィンドウ位置を親ウィンドウの中央に調整 ---
        self.update_idletasks() # ウィンドウの正確なサイズを取得するために必要

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        position_x = parent_x + (parent_width // 2) - (dialog_width // 2)
        position_y = parent_y + (parent_height // 2) - (dialog_height // 2)

        self.geometry(f"+{position_x}+{position_y}")

        self.wait_window(self) # このウィンドウが閉じるまで待つ



    def _on_ok(self, event=None):
        # まず新規入力欄を優先
        new_name = self.entry.get().strip()
        if new_name:
            self.result = new_name
        else:
            # 新規入力がなければ、リストの選択を取得
            selected_indices = self.listbox.curselection()
            if selected_indices:
                self.result = self.listbox.get(selected_indices[0])
        
        self.destroy()

    def _on_cancel(self, event=None):
        self.result = None
        self.destroy()