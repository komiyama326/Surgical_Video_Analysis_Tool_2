# --- Model層のインポート ---
from .models.settings_model import SettingsModel
from .models.preset_model import PresetModel
from .models.analysis_data_model import AnalysisDataModel
from .models.video_player_model import VideoPlayerModel

# --- ViewModel層のインポート ---
from .viewmodels.main_viewmodel import MainViewModel

# --- View層のインポート ---
from .views.main_window import MainWindow

class Application:
    """
    アプリケーション全体を管理するクラスです。
    MVVMの各コンポーネントを初期化し、結合します。
    """
    def __init__(self):
        """
        アプリケーションの初期化を行います。
        MVVMの各コンポーネントをインスタンス化し、接続します。
        """
        # 1. Model層のインスタンス化
        #    依存関係のないものから順に作成する
        settings_model = SettingsModel()
        #    PresetModelはSettingsModelに依存している
        preset_model = PresetModel(settings_model)
        analysis_model = AnalysisDataModel()
        video_model = VideoPlayerModel()

        # 2. ViewModel層のインスタンス化
        #    ViewModelはすべてのModelにアクセスできる必要がある
        self.viewmodel = MainViewModel(
            settings_model=settings_model,
            preset_model=preset_model,
            analysis_model=analysis_model,
            video_model=video_model
        )

        # 3. View層のインスタンス化
        #    ViewはViewModelと対話する
        self.view = MainWindow(self.viewmodel)

        # 4. ViewModelとViewを相互に接続
        #    ViewModelがViewを操作できるように、Viewへの参照を渡す
        self.viewmodel.set_view(self.view)

        self.view.set_video_model(video_model)
        
        print("Application components assembled.")

    def run(self):
        """
        アプリケーションのメインループを開始します。
        """
        # ViewModelにアプリケーションの初期化を指示
        self.viewmodel.initialize_app()
        
        # Viewにメインループの開始を指示
        self.view.start_main_loop()