import tkinter as tk
from tkinter import simpledialog, messagebox
import os
from datetime import datetime
from ..utils import helpers
import pandas as pd
from ..utils.helpers import format_time
from tkinter import filedialog

class MainViewModel:
    """
    メインウィンドウのViewModel。
    Viewからのユーザー操作を処理し、Modelと連携してアプリケーションの状態を管理します。
    """
    def __init__(self, settings_model, preset_model, analysis_model, video_model):
        self.settings_model = settings_model
        self.preset_model = preset_model
        self.analysis_model = analysis_model
        self.video_model = video_model
        self.view = None
        
        print("MainViewModel initialized.")

        self._update_timer = None
        self.current_preset_name = None
        self.selected_stamp = None
        self.is_recording = False
        self.is_preset_modified = False

    def set_view(self, view):
        self.view = view

    def on_window_closing(self):
        if self.is_preset_modified:
            if not messagebox.askyesno("Unsaved Changes", "Preset has unsaved changes. Exit without saving?"):
                return
        
        print("Window is closing. Starting cleanup...")
        if self.view:
            self.settings_model.set("window_geometry", self.view.geometry())
        
        self.settings_model.save()
        self.video_model.release_player()
        
        print("Cleanup finished. Exiting.")
        if self.view:
            self.view.destroy()

    def initialize_app(self):
        self.current_preset_name = self.preset_model.presets_data.get("last_used")
        stamps = self.preset_model.get_stamps(self.current_preset_name)
        
        if self.view:
            self.view.update_stamp_list_and_select(stamps)
            preset_names = self.preset_model.get_preset_names()
            self.view.update_preset_combo(preset_names, self.current_preset_name)
            self.view.speed_buttons[1.0].config(state=tk.DISABLED)
            memo_enabled = self.settings_model.get("memo_enabled", False)
            self.view.memo_enabled_var.set(memo_enabled)
            graph_enabled = self.settings_model.get("graph_enabled", True)
            self.view.graph_enabled_var.set(graph_enabled)
        print(f"Loaded preset '{self.current_preset_name}' with {len(stamps)} stamps.")

    def _mark_preset_as_modified(self):
        if self.is_preset_modified: return
        self.is_preset_modified = True
        display_name = f"{self.current_preset_name} *"
        self.view.update_preset_combo(self.preset_model.get_preset_names(), display_name)

    # --- プリセットのスタンプ変更 (メモリ上のModelデータを直接変更) ---
    
    def on_add_stamp_clicked(self):
        self.view.unbind_shortcuts()
        new_stamp_name = simpledialog.askstring("Add Stamp", "Enter new stamp name:", parent=self.view)
        self.view.bind_shortcuts()
        if not new_stamp_name: return
        
        stamps = self.preset_model.get_stamps(self.current_preset_name)
        if new_stamp_name in stamps:
            messagebox.showwarning("Add Failed", f"'{new_stamp_name}' already exists.", parent=self.view)
        else:
            stamps.append(new_stamp_name)
            self.view.update_stamp_list_and_select(stamps, -1)
            self._mark_preset_as_modified()

    def on_delete_stamp_clicked(self):
        if not self.selected_stamp:
            messagebox.showinfo("Delete Stamp", "Please select a stamp to delete.", parent=self.view)
            return
        if messagebox.askyesno("Confirm Deletion", f"Delete '{self.selected_stamp}'?"):
            stamps = self.preset_model.get_stamps(self.current_preset_name)
            stamps.remove(self.selected_stamp)
            self.view.update_stamp_list_and_select(stamps)
            self._mark_preset_as_modified()

    def on_move_stamp_clicked(self, direction: int):
        if not self.selected_stamp: return
        stamps = self.preset_model.get_stamps(self.current_preset_name)
        current_index = stamps.index(self.selected_stamp)
        new_index = current_index + direction
        if 0 <= new_index < len(stamps):
            stamp = stamps.pop(current_index)
            stamps.insert(new_index, stamp)
            self.view.update_stamp_list_and_select(stamps, new_index)
            self._mark_preset_as_modified()

    # --- プリセット自体の管理 (ファイルI/Oを伴う) ---

    def on_preset_selected(self, event=None):
        if not self.view: return
        new_preset_name = self.view.preset_combo_var.get().replace(" *", "")
        if new_preset_name == self.current_preset_name: return

        if self.is_preset_modified:
            if not messagebox.askyesno("Unsaved Changes", "Discard changes and switch preset?"):
                display_name = f"{self.current_preset_name} *"
                self.view.preset_combo_var.set(display_name)
                return
        
        self.preset_model.reload()
        
        self.is_preset_modified = False
        self.current_preset_name = new_preset_name
        self.preset_model.presets_data["last_used"] = new_preset_name
        
        stamps = self.preset_model.get_stamps(self.current_preset_name)
        self.view.update_preset_combo(self.preset_model.get_preset_names(), self.current_preset_name)
        self.view.update_stamp_list_and_select(stamps)
        print(f"Switched to preset: {new_preset_name}")

    def on_save_preset_clicked(self):
        if not self.is_preset_modified:
            messagebox.showinfo("Save Preset", "No changes to save.", parent=self.view)
            return
        
        self.preset_model.save()
        self.is_preset_modified = False
        self.view.update_preset_combo(self.preset_model.get_preset_names(), self.current_preset_name)
        messagebox.showinfo("Success", f"Preset '{self.current_preset_name}' saved.", parent=self.view)

    def on_save_preset_as_clicked(self):
        self.view.unbind_shortcuts()
        new_name = simpledialog.askstring("Save Preset As", "Enter new preset name:", parent=self.view)
        self.view.bind_shortcuts()
        if not new_name: return

        if new_name in self.preset_model.get_preset_names():
            if not messagebox.askyesno("Confirm Overwrite", f"Preset '{new_name}' already exists. Overwrite?"):
                return

        stamps_to_save = self.preset_model.get_stamps(self.current_preset_name)[:] # コピーを渡す
        self.preset_model.save_preset(new_name, stamps_to_save)
        self.preset_model.presets_data["last_used"] = new_name
        self.preset_model.save()
        
        self.is_preset_modified = False
        self.current_preset_name = new_name
        stamps = self.preset_model.get_stamps(new_name)
        preset_names = self.preset_model.get_preset_names()
        self.view.update_preset_combo(preset_names, new_name)
        self.view.update_stamp_list_and_select(stamps)
        messagebox.showinfo("Success", f"Preset saved as '{new_name}'.", parent=self.view)

    def on_rename_preset_clicked(self):
        if self.is_preset_modified:
            messagebox.showwarning("Unsaved Changes", "Please save or discard current changes before renaming.", parent=self.view)
            return
        old_name = self.current_preset_name
        self.view.unbind_shortcuts()
        new_name = simpledialog.askstring("Rename Preset", f"Rename '{old_name}' to:", initialvalue=old_name, parent=self.view)
        self.view.bind_shortcuts()
        if not new_name or new_name == old_name: return
        if new_name in self.preset_model.get_preset_names():
            messagebox.showerror("Error", "Name already exists.", parent=self.view)
            return

        self.preset_model.rename_preset(old_name, new_name)
        self.preset_model.presets_data["last_used"] = new_name
        self.preset_model.save()
        
        self.is_preset_modified = False
        self.current_preset_name = new_name
        preset_names = self.preset_model.get_preset_names()
        self.view.update_preset_combo(preset_names, new_name)
        messagebox.showinfo("Success", f"Preset renamed to '{new_name}'.", parent=self.view)

    def on_delete_preset_clicked(self):
        if len(self.preset_model.get_preset_names()) <= 1:
            messagebox.showwarning("Cannot Delete", "Cannot delete the last preset.", parent=self.view)
            return
        if self.is_preset_modified:
            messagebox.showwarning("Unsaved Changes", "Please save or discard current changes before deleting.", parent=self.view)
            return
        name_to_delete = self.current_preset_name
        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{name_to_delete}'?"):
            return

        self.preset_model.delete_preset(name_to_delete)
        new_current_preset = self.preset_model.get_preset_names()[0]
        self.preset_model.presets_data["last_used"] = new_current_preset
        self.preset_model.save()
        
        self.is_preset_modified = False
        self.current_preset_name = new_current_preset
        stamps = self.preset_model.get_stamps(new_current_preset)
        preset_names = self.preset_model.get_preset_names()
        self.view.update_preset_combo(preset_names, self.current_preset_name)
        self.view.update_stamp_list_and_select(stamps)
        messagebox.showinfo("Success", f"Preset '{name_to_delete}' deleted.", parent=self.view)

    # --- 以下、再生・記録関連のメソッド (変更なし) ---
    
    def on_open_video_clicked(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Video File(s)",
            filetypes=(("Movie Files", "*.mp4 *.mov *.avi"), ("All files", "*.*"))
        )
        if not file_paths: return
        self.video_model.set_video_files(list(file_paths))
        if self.view:
            handle = self.view.get_video_frame_handle()
            self.video_model.set_display_handle(handle)
        print(f"Video files selected: {file_paths}")
        self.update_ui_regularly()

    def on_play_pause_clicked(self):
        self.video_model.play_pause()
        self.update_ui_regularly()

    def on_skip_time_clicked(self, time_ms: int):
        current_time = self.video_model.get_time()
        new_time = current_time + time_ms
        if new_time < 0: new_time = 0
        self.video_model.set_time(new_time)

    def on_set_speed_clicked(self, rate: float):
        self.video_model.set_rate(rate)
        for speed, button in self.view.speed_buttons.items():
            button.config(state=(tk.DISABLED if speed == rate else tk.NORMAL))
        print(f"Playback speed set to {rate}x")

    def on_stamp_select(self, event=None):
        if not self.view: return
        selected_name = self.view.get_selected_stamp_name()
        self.selected_stamp = selected_name
        if selected_name:
            self.view.set_selected_stamp_text(selected_name)
            if not self.is_recording:
                self.view.start_button.config(state=tk.NORMAL)
        else:
            self.view.set_selected_stamp_text("---")
            self.view.start_button.config(state=tk.DISABLED)

    def on_start_clicked(self):
        if not self.selected_stamp or self.is_recording: return
        self.is_recording = True
        start_time = self.video_model.get_time() / 1000.0
        self.analysis_model.start_procedure(self.selected_stamp, start_time)
        self.view.start_button.config(state=tk.DISABLED)
        self.view.end_button.config(state=tk.NORMAL)
        self.view.stamp_tree.config(selectmode="none")
        print(f"Recording started for: {self.selected_stamp}")

    def on_end_clicked(self):
        if not self.is_recording: return
        memo_text = ""
        if self.settings_model.get("memo_enabled"):
            self.view.unbind_shortcuts()
            memo_text = simpledialog.askstring("Memo", f"Enter a memo for '{self.selected_stamp}':", parent=self.view) or ""
            self.view.bind_shortcuts()
        end_time = self.video_model.get_time() / 1000.0
        self.analysis_model.end_procedure(end_time, memo=memo_text)
        self.is_recording = False
        self.view.end_button.config(state=tk.DISABLED)
        self.view.stamp_tree.config(selectmode="browse")
        
        stamps = self.preset_model.get_stamps(self.current_preset_name)
        current_index = -1
        if self.selected_stamp and self.selected_stamp in stamps:
            current_index = stamps.index(self.selected_stamp)
        if 0 <= current_index < len(stamps) - 1:
            next_index = current_index + 1
            self.view.update_stamp_list_and_select(stamps, next_index)
            self.on_stamp_select()
        else:
            self.view.stamp_tree.selection_remove(self.view.stamp_tree.selection())
            self.on_stamp_select()
        self._update_summary()
        self._update_undo_button_state()
        print("Recording ended.")

    def on_undo_clicked(self):
        undone_record = self.analysis_model.undo_last_record()
        if undone_record:
            print(f"Undone: {undone_record.get('手順名')}")
            self._update_summary()
        self._update_undo_button_state()

    def on_finish_and_save_clicked(self):
        if not self.analysis_model.has_data():
            messagebox.showinfo("No Data", "No data has been recorded to save.", parent=self.view)
            return
        output_dir = os.path.join(os.path.dirname(self.settings_model.settings_file_path),'AnalysisResults')
        os.makedirs(output_dir, exist_ok=True)
        video_files = self.video_model.video_files
        base_name = os.path.splitext(os.path.basename(video_files[0]))[0] if video_files else "analysis_result"
        date_prefix = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_csv_path = os.path.join(output_dir, f"{base_name}_{date_prefix}.csv")
        df = self.analysis_model.export_to_dataframe()
        df['移行時間(秒)'] = df['開始時間(秒)'] - df['終了時間(秒)'].shift(1)
        df = df[["手順名", "開始時間(秒)", "終了時間(秒)", "所要時間(秒)", "移行時間(秒)", "メモ"]]
        total_duration = df['所要時間(秒)'].sum()
        total_transition = df['移行時間(秒)'].sum()
        sum_row = pd.DataFrame([{'手順名': '合計', '所要時間(秒)': total_duration, '移行時間(秒)': total_transition}])
        df_with_total = pd.concat([df, sum_row], ignore_index=True)
        try:
            df_with_total.to_csv(output_csv_path, index=False, encoding='utf-8-sig', float_format='%.2f')
            print(f"CSV saved to {output_csv_path}")
            graph_path = None
            if self.settings_model.get("graph_enabled"):
                font_prop = helpers.get_japanese_font()
                graph_path = helpers.create_and_save_graph(df, output_csv_path, font_prop)
            messagebox.showinfo("Save Successful", f"Results saved successfully!\n\nCSV: {output_csv_path}" + (f"\nGraph: {graph_path}" if graph_path else ""))
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save results.\nError: {e}")

    def on_timeline_changed(self, scale_value: str):
        total_duration_ms = self.video_model.get_length()
        if total_duration_ms <= 0: return
        target_time_ms = int((float(scale_value) / 1000.0) * total_duration_ms)
        self.video_model.set_time(target_time_ms)

    def on_options_changed(self):
        if not self.view: return
        self.settings_model.set("memo_enabled", self.view.memo_enabled_var.get())
        self.settings_model.set("graph_enabled", self.view.graph_enabled_var.get())
        self.settings_model.save()
        print("Settings updated.")

    def update_ui_regularly(self):
        if self._update_timer: self.view.after_cancel(self._update_timer)
        self._ui_update_loop()

    def _ui_update_loop(self):
        if not self.view or not self.video_model.media_loaded: return
        is_playing = self.video_model.is_playing()
        self.view.play_pause_button.config(text=("Pause" if is_playing else "Play"))
        current_time_sec = self.video_model.get_time() / 1000.0
        total_time_sec = self.video_model.get_length() / 1000.0
        self.view.time_display_var.set(f"{format_time(current_time_sec)} / {format_time(total_time_sec)}")
        if total_time_sec > 0:
            self.view.timeline_var.set((current_time_sec / total_time_sec) * 1000)
        self._update_timer = self.view.after(50, self._ui_update_loop)

    def _update_summary(self):
        if not self.view: return
        count, total_duration = self.analysis_model.get_summary()
        self.view.summary_count_var.set(f"Logged Procedures: {count}")
        self.view.summary_duration_var.set(f"Total Duration: {total_duration:.2f}s")

    def _update_undo_button_state(self):
        if not self.view: return
        self.view.undo_button.config(state=(tk.NORMAL if self.analysis_model.has_data() else tk.DISABLED))

    def on_finish_and_next_clicked(self):
        """
        「Finish & Next Video」ボタンがクリックされたときの処理。
        """
        # データを保存する (データがない場合は何もしない)
        if self.analysis_model.has_data():
            self.on_finish_and_save_clicked()
        
        # Viewに次のセッションを要求するフラグを立てさせる
        if self.view:
            self.view.is_next_session_requested = True
        
        # 現在のウィンドウを閉じる
        self.on_window_closing()

    def load_videos(self, file_paths: list[str]):
        """
        指定された動画ファイルを読み込んで表示する。
        """
        if not file_paths: return
            
        self.video_model.set_video_files(file_paths)
        
        if self.view:
            handle = self.view.get_video_frame_handle()
            self.video_model.set_display_handle(handle)

        print(f"Initial video files loaded: {file_paths}")
        self.update_ui_regularly()

        