import os
from datetime import datetime
from ..utils import helpers
import pandas as pd
from tkinter import filedialog
from ..utils.helpers import format_time
import tkinter as tk
from tkinter import simpledialog, messagebox

class MainViewModel:
    """
    メインウィンドウのViewModel。
    Viewからのユーザー操作を処理し、Modelと連携してアプリケーションの状態を管理します。
    """
    def __init__(self, settings_model, preset_model, analysis_model, video_model):
        """
        MainViewModelの初期化。

        Args:
            settings_model: 設定管理モデル。
            preset_model: プリセット管理モデル。
            analysis_model: 分析データ管理モデル。
            video_model: 動画プレイヤー管理モデル。
        """
        # 各Modelへの参照を保持
        self.settings_model = settings_model
        self.preset_model = preset_model
        self.analysis_model = analysis_model
        self.video_model = video_model
        
        # Viewへの参照を保持するための変数 (Applicationクラスによって設定される)
        self.view = None
        
        print("MainViewModel initialized.")

        # UIの定期更新を行うタイマーID
        self._update_timer = None

        # 現在のプリセット情報を保持する
        self.current_preset_name = None
        self.current_stamps = []

        # 現在選択中の手順名を保持する
        self.selected_stamp = None

        # 現在記録中かどうかを示すフラグ
        self.is_recording = False

    def set_view(self, view):
        """
        Viewへの参照を設定します。
        これによりViewModelからViewのメソッドを呼び出せるようになります。
        """
        self.view = view

    def on_window_closing(self):
        """
        アプリケーション終了時の処理を行います。
        """
        print("Window is closing. Starting cleanup...")
        
        # 現在のウィンドウサイズを取得してSettingsModelに保存
        if self.view:
            current_geometry = self.view.geometry()
            self.settings_model.set("window_geometry", current_geometry)
        
        # 各Modelにデータの保存とリソースの解放を指示
        self.settings_model.save()
        self.preset_model.save()
        self.video_model.release_player()
        
        print("Cleanup finished. Exiting.")
        
        # ウィンドウを破棄してアプリケーションを終了
        if self.view:
            self.view.destroy()

    # --- アプリケーション起動時の処理 ---
    def initialize_app(self):
        """
        アプリケーション起動時に必要な初期化処理を行います。
        """
        # Modelから最後に使用したプリセット名を取得
        last_used_preset = self.preset_model.presets_data.get("last_used")
        
        if last_used_preset:
            self.current_preset_name = last_used_preset
            # Modelからプリセットの手順リストを取得
            self.current_stamps = self.preset_model.get_stamps(last_used_preset)
            
        # Viewに手順リストの表示更新を指示
        if self.view:
            self.view.update_stamp_list_and_select(self.current_stamps)

        print(f"Loaded preset '{self.current_preset_name}' with {len(self.current_stamps)} stamps.")

        # プリセット選択コンボボックスも更新する
        if self.view:
            preset_names = self.preset_model.get_preset_names()
            self.view.update_preset_combo(preset_names, self.current_preset_name)

        # 1.0xボタンをデフォルトで無効化しておく
        if self.view:
            self.view.speed_buttons[1.0].config(state=tk.DISABLED)

        # オプションのチェックボックスを初期化
        if self.view:
            memo_enabled = self.settings_model.get("memo_enabled", False)
            self.view.memo_enabled_var.set(memo_enabled)
            
            graph_enabled = self.settings_model.get("graph_enabled", True)
            self.view.graph_enabled_var.set(graph_enabled)

    # --- Viewからのイベントハンドラ ---

    def on_open_video_clicked(self):
        """
        「動画を開く」ボタンがクリックされたときの処理。
        ファイル選択ダイアログを表示し、選択されたファイルをVideoPlayerModelに渡す。
        """
        # ファイル選択ダイアログを開く
        # askopenfilenames を使うことで、複数のファイルを同時に選択できる
        file_paths = filedialog.askopenfilenames(
            title="Select Video File(s)",
            filetypes=(("Movie Files", "*.mp4 *.mov *.avi"), ("All files", "*.*"))
        )
        
        # ファイルが選択されなかった場合は何もしない
        if not file_paths:
            return
            
        # VideoPlayerModelにファイルのパスリストを渡す
        self.video_model.set_video_files(list(file_paths))
        
        # 動画の描画先をVideoPlayerModelに伝える
        # この処理は動画ファイルがセットされた後に行う必要がある
        if self.view:
            handle = self.view.get_video_frame_handle()
            self.video_model.set_display_handle(handle)

        print(f"Video files selected: {file_paths}")

        self.update_ui_regularly() # UIの初期状態を更新

    def on_play_pause_clicked(self):
        """
        「再生/一時停止」ボタンまたはPキーが押されたときの処理。
        """
        self.video_model.play_pause()
        # UI更新ループは独立して動き続けるため、ここでは何もしない

    def on_stamp_select(self, event=None):
        """
        手順リストの項目が選択されたときに呼び出されます。
        """
        if not self.view:
            return

        # Viewから選択された項目名を取得
        selected_name = self.view.get_selected_stamp_name()
        self.selected_stamp = selected_name
        
        if selected_name:
            # Viewのラベルを更新
            self.view.set_selected_stamp_text(selected_name)
            # 記録中でない場合のみStartボタンを有効化
            if not self.is_recording:
                self.view.start_button.config(state=tk.NORMAL)
        else:
            # 何も選択されていない状態に戻す
            self.view.set_selected_stamp_text("---")
            self.view.start_button.config(state=tk.DISABLED)

        print(f"Stamp selected: {selected_name}")

    def on_start_clicked(self):
        """
        「Start」ボタンがクリックされたときの処理。
        """
        if not self.selected_stamp or self.is_recording:
            return
            
        self.is_recording = True
        
        # 現在の再生時間を取得して、AnalysisDataModelに記録開始を指示
        start_time = self.video_model.get_time() / 1000.0
        self.analysis_model.start_procedure(self.selected_stamp, start_time)
        
        # --- UIの状態を更新 ---
        # Startボタンを無効化し、Endボタンを有効化
        self.view.start_button.config(state=tk.DISABLED)
        self.view.end_button.config(state=tk.NORMAL)
        
        # 記録中はリストの選択を変更できないようにする
        self.view.stamp_tree.config(selectmode="none")

        print(f"Recording started for: {self.selected_stamp}")

    def on_end_clicked(self):
        """
        「End」ボタンがクリックされたときの処理。
        """
        if not self.is_recording:
            return

        memo_text = ""
        # メモ機能が有効な場合のみダイアログを表示
        if self.settings_model.get("memo_enabled"):
            self.view.unbind_shortcuts()
            memo_text = simpledialog.askstring(
                "Memo",
                f"Enter a memo for '{self.selected_stamp}':",
                parent=self.view
            ) or ""
            self.view.bind_shortcuts()

        # 現在の再生時間を取得して、AnalysisDataModelに記録終了を指示
        end_time = self.video_model.get_time() / 1000.0
        self.analysis_model.end_procedure(end_time, memo=memo_text)
        
        self.is_recording = False
        
        # --- UIの状態を更新 ---
        self.view.end_button.config(state=tk.DISABLED)
        self.view.stamp_tree.config(selectmode="browse")
        
        # ★★★ ここから下のブロックを追加・修正 ★★★

        # 現在選択されている項目のインデックスを取得
        current_index = -1
        if self.selected_stamp and self.selected_stamp in self.current_stamps:
            current_index = self.current_stamps.index(self.selected_stamp)

        # 次の項目があれば、それを選択状態にする
        if 0 <= current_index < len(self.current_stamps) - 1:
            next_index = current_index + 1
            self.view.update_stamp_list_and_select(self.current_stamps, next_index)
            # ViewModelの状態も更新
            self.on_stamp_select()
        else:
            # 次の項目がない場合は、選択を解除
            self.view.stamp_tree.selection_remove(self.view.stamp_tree.selection())
            self.on_stamp_select()
        
        self._update_summary()
        self._update_undo_button_state()
        
        print("Recording ended.")

    def on_add_stamp_clicked(self):
        """
        「Add Stamp」ボタンがクリックされたときの処理。
        """
        if not self.view:
            return

        # ショートカットを一時的に無効化
        self.view.unbind_shortcuts()
        
        # 入力ダイアログを表示して、新しいスタンプ名を取得
        new_stamp_name = simpledialog.askstring(
            "Add Stamp", "Enter new stamp name:", parent=self.view
        )
        
        # ショートカットを再有効化
        self.view.bind_shortcuts()

        if new_stamp_name:
            # Modelにスタンプの追加を依頼
            success = self.preset_model.add_stamp(self.current_preset_name, new_stamp_name)
            
            if success:
                # Modelの内部データが変更されたので、ViewModelのデータも更新
                self.current_stamps = self.preset_model.get_stamps(self.current_preset_name)
                # Viewのリスト表示を更新
                # 最後の項目が追加されたインデックス (-1はリストの末尾を指す) を渡す
                self.view.update_stamp_list_and_select(self.current_stamps, -1)
                print(f"Stamp '{new_stamp_name}' added to preset '{self.current_preset_name}'.")
                # TODO: プリセットが変更されたことを示すマーカー(*)をUIに表示
            else:
                messagebox.showwarning(
                    "Add Stamp Failed",
                    f"The stamp '{new_stamp_name}' already exists in this preset.",
                    parent=self.view
                )

    def on_undo_clicked(self):
        """
        「Undo」ボタンがクリックされたときの処理。
        """
        # Modelに最後の記録の削除を依頼
        undone_record = self.analysis_model.undo_last_record()
        
        if undone_record:
            print(f"Undone: {undone_record.get('手順名')}")
            # サマリー表示を更新
            self._update_summary()
        
        # Undoボタンの状態を更新
        self._update_undo_button_state()

    def _update_summary(self):
        """
        ライブサマリー表示を更新します。
        """
        if not self.view:
            return
            
        # Modelからサマリー情報を取得
        count, total_duration = self.analysis_model.get_summary()
        
        # Viewのラベルを更新
        self.view.summary_count_var.set(f"Logged Procedures: {count}")
        self.view.summary_duration_var.set(f"Total Duration: {total_duration:.2f}s")

    def update_ui_regularly(self):
        """
        UI要素（タイムライン、時間表示など）を定期的に更新します。
        """
        # 既存のタイマーがあればキャンセル
        if self._update_timer:
            self.view.after_cancel(self._update_timer)
            self._update_timer = None

        # 動画が再生中の場合のみ、新しいタイマーを開始する
        if self.video_model.is_playing():
            self._update_ui() # 最初の更新を即時実行
        else:
            # 停止した場合は、ボタンのテキストなどを最終状態に更新
            self._update_ui()
            
    def update_ui_regularly(self):
        """
        UI定期更新を開始するためのトリガー。
        一度だけ呼び出され、ループを開始させる。
        """
        # 既存のタイマーがあればキャンセル（念のため）
        if self._update_timer:
            self.view.after_cancel(self._update_timer)
        
        # UI更新ループを開始
        self._ui_update_loop()

    def _ui_update_loop(self):
        """
        UIを定期的に更新し続けるためのループ。
        このループは動画がロードされてからアプリ終了まで停止しない。
        """
        if not self.view or not self.video_model.media_loaded:
            # 動画がロードされていないなど、更新すべきでない状況なら停止
            return

        # --- 実際のUI更新処理 ---
        is_playing = self.video_model.is_playing()
        
        # ボタンのテキストを更新
        play_pause_text = "Pause" if is_playing else "Play"
        self.view.play_pause_button.config(text=play_pause_text)

        # 時間表示を更新
        current_time_sec = self.video_model.get_time() / 1000.0
        total_time_sec = self.video_model.get_length() / 1000.0
        time_str = f"{format_time(current_time_sec)} / {format_time(total_time_sec)}"
        self.view.time_display_var.set(time_str)

        # タイムラインスライダーを更新 (0除算を回避)
        if total_time_sec > 0:
            position = (current_time_sec / total_time_sec) * 1000
            # TODO: ユーザーがスライダーをドラッグ中は更新を止める配慮が必要
            self.view.timeline_var.set(position)
        
        # 次の更新を50ms後にスケジュールする
        self._update_timer = self.view.after(50, self._ui_update_loop)

    def _update_undo_button_state(self):
        """
        Undoボタンの状態を、記録データがあるかどうかに基づいて更新します。
        """
        if not self.view:
            return
            
        # Modelにデータがあるか問い合わせる
        if self.analysis_model.has_data():
            self.view.undo_button.config(state=tk.NORMAL)
        else:
            self.view.undo_button.config(state=tk.DISABLED)

    def on_delete_stamp_clicked(self):
        """
        「Delete Stamp」ボタンがクリックされたときの処理。
        """
        if not self.view or not self.selected_stamp:
            messagebox.showinfo(
                "Delete Stamp",
                "Please select a stamp from the list to delete.",
                parent=self.view
            )
            return

        # 確認ダイアログを表示
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the stamp '{self.selected_stamp}'?",
            parent=self.view
        )

        if confirm:
            # Modelにスタンプの削除を依頼
            success = self.preset_model.delete_stamp(self.current_preset_name, self.selected_stamp)
            
            if success:
                # Modelの内部データが変更されたので、ViewModelのデータも更新
                self.current_stamps = self.preset_model.get_stamps(self.current_preset_name)
                # Viewのリスト表示を更新
                self.view.update_stamp_list_and_select(self.current_stamps)
                print(f"Stamp '{self.selected_stamp}' deleted from preset '{self.current_preset_name}'.")
                # TODO: プリセットが変更されたことを示すマーカー(*)をUIに表示
            else:
                # 基本的にこのエラーは発生しないはずだが、念のため
                messagebox.showerror(
                    "Delete Stamp Failed",
                    f"Could not find the stamp '{self.selected_stamp}' to delete.",
                    parent=self.view
                )

    def on_finish_and_save_clicked(self):
        """
        「Finish & Save」ボタンがクリックされたときの処理。
        分析結果をファイルに保存する。
        """
        if not self.analysis_model.has_data():
            messagebox.showinfo(
                "No Data", "No data has been recorded to save.", parent=self.view
            )
            return

        # 1. 保存先ディレクトリを決定
        output_dir = os.path.join(
            os.path.dirname(self.settings_model.settings_file_path),
            'AnalysisResults'
        )
        os.makedirs(output_dir, exist_ok=True)

        # 2. ファイル名を決定
        # 最初の動画ファイル名(拡張子なし)をベースにする
        video_files = self.video_model.video_files
        if video_files:
            base_name = os.path.splitext(os.path.basename(video_files[0]))[0]
        else:
            base_name = "analysis_result"

        date_prefix = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{base_name}_{date_prefix}.csv"
        output_csv_path = os.path.join(output_dir, output_filename)

        # 3. DataFrameを取得し、整形
        df = self.analysis_model.export_to_dataframe()
        df['移行時間(秒)'] = df['開始時間(秒)'] - df['終了時間(秒)'].shift(1)
        df = df[["手順名", "開始時間(秒)", "終了時間(秒)", "所要時間(秒)", "移行時間(秒)", "メモ"]]

        # 4. 合計行を追加
        total_duration = df['所要時間(秒)'].sum()
        total_transition = df['移行時間(秒)'].sum()
        sum_row = pd.DataFrame([{
            '手順名': '合計', 
            '所要時間(秒)': total_duration, 
            '移行時間(秒)': total_transition
        }])
        df_with_total = pd.concat([df, sum_row], ignore_index=True)

        try:
            # 5. CSVとして保存
            df_with_total.to_csv(output_csv_path, index=False, encoding='utf-8-sig', float_format='%.2f')
            print(f"CSV saved to {output_csv_path}")

            # 6. グラフを生成して保存 (オプションが有効な場合のみ)
            graph_path = None
            if self.settings_model.get("graph_enabled"):
                font_prop = helpers.get_japanese_font()
                # グラフには合計行を含まない元のdfを使用
                graph_path = helpers.create_and_save_graph(df, output_csv_path, font_prop)

            # 7. 結果表示
            messagebox.showinfo(
                "Save Successful",
                f"Results saved successfully!\n\nCSV: {output_csv_path}"
                + (f"\nGraph: {graph_path}" if graph_path else "")
            )

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save results.\nError: {e}")
            print(f"Error during save: {e}")

    def on_timeline_changed(self, scale_value: str):
        """
        タイムラインスライダーがユーザーによって操作されたときに呼び出されます。
        
        Args:
            scale_value: スライダーの現在値 (0.0 から 1000.0 の文字列)。
        """
        # Modelに動画の総長さを問い合わせる
        total_duration_ms = self.video_model.get_length()
        if total_duration_ms <= 0:
            return

        # スライダーの値 (0-1000) を、動画の総時間内のミリ秒に変換
        target_time_ms = int((float(scale_value) / 1000.0) * total_duration_ms)
        
        # Modelにシークを指示
        self.video_model.set_time(target_time_ms)

    def on_move_stamp_clicked(self, direction: int):
        """
        「▲ Up」「▼ Down」ボタンがクリックされたときの処理。
        """
        if not self.view or not self.selected_stamp:
            return

        # Modelにスタンプの移動を依頼
        new_index = self.preset_model.move_stamp(
            self.current_preset_name, self.selected_stamp, direction
        )

        if new_index is not None:
            # Modelのデータが変更されたので、ViewModelのデータも更新
            self.current_stamps = self.preset_model.get_stamps(self.current_preset_name)
            # Viewのリスト表示を更新し、移動した項目を選択状態にする
            self.view.update_stamp_list_and_select(self.current_stamps, new_index)
            print(f"Stamp '{self.selected_stamp}' moved.")
            # TODO: プリセットが変更されたことを示すマーカー(*)をUIに表示

    def on_preset_selected(self, event=None):
        """
        プリセット選択コンボボックスの値が変更されたときの処理。
        """
        if not self.view: return

        new_preset_name = self.view.preset_combo_var.get()
        if new_preset_name == self.current_preset_name:
            return

        # TODO: 未保存の変更がある場合は確認ダイアログを出す

        self.current_preset_name = new_preset_name
        self.current_stamps = self.preset_model.get_stamps(new_preset_name)
        
        # ★★★【バグ修正の核心部分】★★★
        # スタンプリストの表示を新しいプリセットの内容に更新する命令が抜けていた
        self.view.update_stamp_list_and_select(self.current_stamps)
        
        # 最後に使用したプリセットとして記憶
        self.preset_model.presets_data["last_used"] = new_preset_name
        self.preset_model.save()
        
        print(f"Switched to preset: {new_preset_name}")

    def on_save_preset_as_clicked(self):
        """
        「Save As...」ボタンがクリックされたときの処理。
        """
        self.view.unbind_shortcuts()
        new_name = simpledialog.askstring(
            "Save Preset As", "Enter new preset name:", parent=self.view
        )
        self.view.bind_shortcuts()

        if not new_name:
            return

        if new_name in self.preset_model.get_preset_names():
            messagebox.showerror("Error", f"Preset name '{new_name}' already exists.", parent=self.view)
            return
            
        # Modelに保存を依頼
        self.preset_model.save_preset_as(new_name, self.current_stamps)
        self.preset_model.presets_data["last_used"] = new_name
        self.preset_model.save()
        
        # UIを更新
        self.current_preset_name = new_name
        preset_names = self.preset_model.get_preset_names()
        self.view.update_preset_combo(preset_names, new_name)
        messagebox.showinfo("Success", f"Preset '{new_name}' saved.", parent=self.view)

    def on_rename_preset_clicked(self):
        """
        「Rename」ボタンがクリックされたときの処理。
        """
        old_name = self.current_preset_name
        self.view.unbind_shortcuts()
        new_name = simpledialog.askstring(
            "Rename Preset", f"Rename '{old_name}' to:", initialvalue=old_name, parent=self.view
        )
        self.view.bind_shortcuts()
        
        if not new_name or new_name == old_name:
            return
            
        if new_name in self.preset_model.get_preset_names():
            messagebox.showerror("Error", f"Preset name '{new_name}' already exists.", parent=self.view)
            return

        # Modelに名前変更を依頼
        self.preset_model.rename_preset(old_name, new_name)
        self.preset_model.presets_data["last_used"] = new_name
        self.preset_model.save()
        
        # UIを更新
        self.current_preset_name = new_name
        preset_names = self.preset_model.get_preset_names()
        self.view.update_preset_combo(preset_names, new_name)
        messagebox.showinfo("Success", f"Preset renamed to '{new_name}'.", parent=self.view)

    def on_delete_preset_clicked(self):
        """
        「Delete Preset」ボタンがクリックされたときの処理。
        """
        if len(self.preset_model.get_preset_names()) <= 1:
            messagebox.showwarning("Cannot Delete", "Cannot delete the last preset.", parent=self.view)
            return

        name_to_delete = self.current_preset_name
        confirm = messagebox.askyesno(
            "Confirm Deletion", f"Are you sure you want to delete the preset '{name_to_delete}'?"
        )
        if not confirm:
            return

        # Modelに削除を依頼
        self.preset_model.delete_preset(name_to_delete)
        
        # 新しいカレントプリセットを選択 (通常はリストの先頭)
        new_current_preset = self.preset_model.get_preset_names()[0]
        self.preset_model.presets_data["last_used"] = new_current_preset
        self.preset_model.save()

        # ★★★【バグ修正の核心部分】★★★
        # UIを能動的に更新する
        # 1. ViewModelの状態を新しいプリセットに更新
        self.current_preset_name = new_current_preset
        self.current_stamps = self.preset_model.get_stamps(new_current_preset)
        
        # 2. Viewのコンボボックスとスタンプリストを両方更新
        preset_names = self.preset_model.get_preset_names()
        self.view.update_preset_combo(preset_names, self.current_preset_name)
        self.view.update_stamp_list_and_select(self.current_stamps)
        
        messagebox.showinfo("Success", f"Preset '{name_to_delete}' deleted.", parent=self.view)

    def on_skip_time_clicked(self, time_ms: int):
        """
        「10s >>」「<< 10s」ボタンまたは左右キーが押されたときの処理。
        """
        current_time = self.video_model.get_time()
        new_time = current_time + time_ms
        
        # ★★★【今回の修正】★★★
        # new_timeが0未満になった場合は、0に補正する
        if new_time < 0:
            new_time = 0
            
        self.video_model.set_time(new_time)

    def on_set_speed_clicked(self, rate: float):
        """
        再生速度変更ボタンがクリックされたときの処理。
        """
        self.video_model.set_rate(rate)
        # UIのボタン状態を更新
        for speed, button in self.view.speed_buttons.items():
            if speed == rate:
                button.config(state=tk.DISABLED)
            else:
                button.config(state=tk.NORMAL)
        print(f"Playback speed set to {rate}x")

    def on_options_changed(self):
        """
        オプションのチェックボックスが変更されたときの処理。
        設定をSettingsModelに保存する。
        """
        if not self.view: return
        
        self.settings_model.set("memo_enabled", self.view.memo_enabled_var.get())
        self.settings_model.set("graph_enabled", self.view.graph_enabled_var.get())
        
        # アプリ終了時だけでなく、変更の都度保存する
        self.settings_model.save()
        print("Settings updated.")
