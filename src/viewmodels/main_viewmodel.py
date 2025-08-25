import os
from datetime import datetime
from ..utils import helpers
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
            self.view.update_stamp_list(self.current_stamps)

        print(f"Loaded preset '{self.current_preset_name}' with {len(self.current_stamps)} stamps.")

        # プリセット選択コンボボックスも更新する
        if self.view:
            preset_names = self.preset_model.get_preset_names()
            self.view.update_preset_combo(preset_names, self.current_preset_name)

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
        「再生/一時停止」ボタンがクリックされたときの処理。
        """
        self.video_model.play_pause()
        self.update_ui_regularly() # UI更新タイマーを開始/停止

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

        # 現在の再生時間を取得して、AnalysisDataModelに記録終了を指示
        end_time = self.video_model.get_time() / 1000.0
        # TODO: メモ機能は後で実装
        self.analysis_model.end_procedure(end_time, memo="")
        
        self.is_recording = False
        
        # --- UIの状態を更新 ---
        # Endボタンを無効化
        self.view.end_button.config(state=tk.DISABLED)
        
        # リストの選択を再び可能にする
        self.view.stamp_tree.config(selectmode="browse")
        
        # 選択状態を再評価して、Startボタンの状態を決定
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
                self.view.update_stamp_list(self.current_stamps)
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
            
    def _update_ui(self):
        """
        UIを一度更新するための内部メソッド。
        """
        if not self.view or not self.video_model.media_loaded:
            return

        # ボタンのテキストを更新
        play_pause_text = "Pause" if self.video_model.is_playing() else "Play"
        self.view.play_pause_button.config(text=play_pause_text)

        # 時間表示を更新
        current_time_sec = self.video_model.get_time() / 1000.0
        total_time_sec = self.video_model.get_length() / 1000.0
        
        # format_timeヘルパー関数を使用
        time_str = f"{format_time(current_time_sec)} / {format_time(total_time_sec)}"
        self.view.time_display_var.set(time_str)

        # タイムラインスライダーを更新 (0除算を回避)
        if total_time_sec > 0:
            position = (current_time_sec / total_time_sec) * 1000
            self.view.timeline_var.set(position)

        # 次の更新をスケジュール (再生中のみ)
        if self.video_model.is_playing():
            self._update_timer = self.view.after(100, self._update_ui)

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
                self.view.update_stamp_list(self.current_stamps)
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

        # 1. 保存先ディレクトリを決定 (SettingsModelが知っているパスを利用)
        output_dir = os.path.join(
            os.path.dirname(self.settings_model.settings_file_path),
            'AnalysisResults'
        )
        os.makedirs(output_dir, exist_ok=True)

        # 2. ファイル名を決定 (元のコードのロジックを踏襲)
        #    TODO: 複数動画対応時にファイル名をどうするか検討が必要
        date_prefix = datetime.now().strftime('%Y%m%d%H%M')
        sequence_number = 1
        while True:
            # TODO: ここで使用するビデオファイル名は、動画選択時に保持しておく必要がある
            video_basename = "analysis_result" 
            output_filename = f"{video_basename}_{date_prefix}_{sequence_number:02d}.csv"
            output_csv_path = os.path.join(output_dir, output_filename)
            if not os.path.exists(output_csv_path):
                break
            sequence_number += 1

        # 3. DataFrameを取得し、CSVとして保存
        df = self.analysis_model.export_to_dataframe()
        
        # 移行時間を計算
        df['移行時間(秒)'] = df['開始時間(秒)'] - df['終了時間(秒)'].shift(1)
        # 列の順番を整理
        df = df[["手順名", "開始時間(秒)", "終了時間(秒)", "所要時間(秒)", "移行時間(秒)", "メモ"]]

        try:
            df.to_csv(output_csv_path, index=False, encoding='utf-8-sig', float_format='%.2f')
            print(f"CSV saved to {output_csv_path}")

            # 4. グラフを生成して保存
            # TODO: グラフ生成の有効/無効を設定で切り替えられるようにする
            font_prop = helpers.get_japanese_font()
            graph_path = helpers.create_and_save_graph(df, output_csv_path, font_prop)

            # 5. 結果表示ダイアログ (今回はメッセージボックスで代用)
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