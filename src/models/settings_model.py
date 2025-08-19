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
        """
        # アプリケーション名を定義
        app_name = "SurgicalVideoAnalysisTool_2"

        if sys.platform == "win32":
            # Windowsの場合: %APPDATA%\AppName
            app_data_dir = os.path.join(os.environ['APPDATA'], app_name)
        else:
            # macOS/Linuxの場合: ~/.config/AppName
            app_data_dir = os.path.join(os.path.expanduser('~'), '.config', app_name)
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(app_data_dir, exist_ok=True)
        
        return os.path.join(app_data_dir, 'app_settings.json')

    def load(self) -> dict:
        """
        設定ファイルから設定を読み込みます。
        ファイルが存在しない、または内容が不正な場合はデフォルト設定を返します。
        """
        try:
            with open(self.settings_file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # デフォルト設定にないキーがあれば追加する
            for key, value in self.DEFAULT_SETTINGS.items():
                settings.setdefault(key, value)
            return settings
            
        except (FileNotFoundError, json.JSONDecodeError):
            # ファイルがないか、JSONとして不正な場合はデフォルトを返す
            return self.DEFAULT_SETTINGS.copy()

    def save(self):
        """
        現在の設定をファイルに保存します。
        """
        try:
            with open(self.settings_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving settings: {e}")

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