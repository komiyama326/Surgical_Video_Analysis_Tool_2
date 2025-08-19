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
        
        # Viewへの参照を保持するための変数 (後で設定される)
        self.view = None
        
        print("MainViewModel initialized.")

    def set_view(self, view):
        """
        Viewへの参照を設定します。
        """
        self.view = view

    # --- Viewからのイベントハンドラ ---
    # TODO: ここに、UI上のボタンが押されたときなどに呼び出されるメソッドを
    #       多数実装していきます。
    # 例: def on_play_pause_clicked(self): ...
    # 例: def on_start_button_clicked(self): ...

    # --- アプリケーションのライフサイクル ---
    def on_window_closing(self):
        """
        アプリケーション終了時の処理を行います。
        """
        # TODO: 設定の保存、VLCリソースの解放などを行います。
        print("Window is closing. Cleaning up...")
        self.video_model.release_player()
        self.settings_model.save()
        self.preset_model.save()