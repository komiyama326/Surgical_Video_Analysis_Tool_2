from tkinter import filedialog
from ..utils.helpers import format_time

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
        # 現時点では特に処理はないが、今後ここに初期化コードを追加する
        print("Application initialized by ViewModel.")
        pass

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