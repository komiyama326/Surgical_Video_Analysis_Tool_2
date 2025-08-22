from tkinter import filedialog

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