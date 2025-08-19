import json
import os
import sys

class PresetModel:
    """
    手順名プリセットを管理するクラス。
    プリセットファイルの読み込み、保存、編集を担当します。
    """
    DEFAULT_PRESET_NAME = "Default"
    DEFAULT_STAMPS = [
        "角膜切開", "前嚢切開 (CCC)", "ハイドロダイセクション",
        "水晶体超音波乳化吸引術 (PEA)", "皮質吸引 (I/A)", "眼内レンズ挿入 (IOL挿入)"
    ]

    def __init__(self, settings_model):
        """
        PresetModelの初期化。
        
        Args:
            settings_model: 設定ファイルのパス情報を取得するために使用。
        """
        # AppData/ConfigフォルダのパスはSettingsModelが知っているので、それを利用します。
        self.presets_file_path = self._get_presets_file_path(settings_model)
        self.presets_data = self.load()

    def _get_presets_file_path(self, settings_model) -> str:
        """
        設定ファイルと同じディレクトリにプリセットファイルを配置します。
        """
        app_data_dir = os.path.dirname(settings_model.settings_file_path)
        return os.path.join(app_data_dir, 'procedure_presets.json')

    def load(self) -> dict:
        """
        プリセットファイルからプリセットを読み込みます。
        ファイルが存在しない、または内容が不正な場合はデフォルトプリセットを返します。
        """
        # TODO: JSONファイルからの読み込みと、データ形式の検証、
        #       デフォルトデータでの初期化処理を実装します。
        print("Loading presets...") # 動作確認用
        default_data = {
            "presets": {self.DEFAULT_PRESET_NAME: self.DEFAULT_STAMPS},
            "last_used": self.DEFAULT_PRESET_NAME
        }
        return default_data

    def save(self):
        """
        現在のプリセットデータをファイルに保存します。
        """
        # TODO: JSONファイルへの書き込み処理を実装します。
        print(f"Saving presets to {self.presets_file_path}") # 動作確認用
        pass

    def get_preset_names(self) -> list:
        """
        すべてのプリセット名のリストを返します。
        """
        return list(self.presets_data.get("presets", {}).keys())

    def get_stamps(self, preset_name: str) -> list:
        """
        指定されたプリセット名に登録されている手順（スタンプ）のリストを返します。
        """
        return self.presets_data.get("presets", {}).get(preset_name, [])

    # TODO: 今後、プリセットの追加、名前変更、削除などのメソッドをここに追加していきます。