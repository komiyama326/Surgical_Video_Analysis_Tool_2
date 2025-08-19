import json
import os
import sys

class SettingsModel:
    """
    アプリケーションの設定を管理するクラス。
    設定ファイルの読み込み、保存、デフォルト設定の提供を担当します。
    """
    DEFAULT_SETTINGS = {
        "window_geometry": "1300x850+50+50",
        "memo_enabled": False,
        "graph_enabled": False,
    }

    def __init__(self):
        """
        SettingsModelの初期化。
        設定ファイルのパスを決定し、設定を読み込みます。
        """
        self.settings_file_path = self._get_settings_file_path()
        self.settings = self.load()

    def _get_settings_file_path(self) -> str:
        """
        プラットフォームに応じて適切な設定ファイルのパスを生成します。
        元のコードの get_app_data_path に相当します。
        """
        # TODO: AppData や .config フォルダ内に専用ディレクトリを作成し、
        #       その中に 'app_settings.json' のパスを返す処理を実装します。
        if sys.platform == "win32":
            app_data_dir = os.path.join(os.environ['APPDATA'], 'SurgicalVideoAnalysisTool_2')
        else:
            app_data_dir = os.path.join(os.path.expanduser('~'), '.config', 'SurgicalVideoAnalysisTool_2')
        
        os.makedirs(app_data_dir, exist_ok=True)
        return os.path.join(app_data_dir, 'app_settings.json')

    def load(self) -> dict:
        """
        設定ファイルから設定を読み込みます。
        ファイルが存在しない、または内容が不正な場合はデフォルト設定を返します。
        """
        # TODO: JSONファイルからの読み込みと、デフォルト値での補完処理を実装します。
        print("Loading settings...") # 動作確認用
        return self.DEFAULT_SETTINGS.copy()

    def save(self):
        """
        現在の設定をファイルに保存します。
        """
        # TODO: JSONファイルへの書き込み処理を実装します。
        print(f"Saving settings to {self.settings_file_path}") # 動作確認用
        pass

    def get(self, key: str, default=None):
        """
        指定されたキーの設定値を取得します。
        """
        return self.settings.get(key, default)

    def set(self, key: str, value):
        """
        指定されたキーの設定値を更新します。
        """
        self.settings[key] = value