import json
import os
from .settings_model import SettingsModel

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

    def __init__(self, settings_model: SettingsModel):
        """
        PresetModelの初期化。
        
        Args:
            settings_model: 設定ファイルのパス情報を取得するために使用。
        """
        self.presets_file_path = self._get_presets_file_path(settings_model)
        self.presets_data = self.load()

    def _get_presets_file_path(self, settings_model: SettingsModel) -> str:
        """
        設定ファイルと同じディレクトリにプリセットファイルを配置します。
        """
        app_data_dir = os.path.dirname(settings_model.settings_file_path)
        return os.path.join(app_data_dir, 'procedure_presets.json')

    def reload(self):
        """ファイルからデータを再読み込みし、メモリ上のデータを上書きする。"""
        self.presets_data = self.load()

    def reload(self):
        """ファイルからデータを再読み込みし、メモリ上のデータを上書きする。"""
        self.presets_data = self.load() # loadはデータを返すだけ

    def load(self) -> dict:
        """
        プリセットファイルからプリセットを読み込みます。
        ファイルが存在しない、または内容が不正な場合はデフォルトプリセットを返します。
        """
        default_data = {
            "presets": {self.DEFAULT_PRESET_NAME: self.DEFAULT_STAMPS},
            "last_used": self.DEFAULT_PRESET_NAME
        }

        try:
            # プリセットファイルが存在しない場合は、まずデフォルトで作成する
            if not os.path.exists(self.presets_file_path):
                self._create_default_preset_file(default_data)
                return default_data

            with open(self.presets_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # データ構造が期待通りか基本的なチェックを行う
            if "presets" not in data or "last_used" not in data:
                raise ValueError("Invalid presets file format")
            
            return data

        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            # ファイルがない、壊れている、形式が違う場合はデフォルトで再作成
            self._create_default_preset_file(default_data)
            return default_data

    def _create_default_preset_file(self, data: dict):
        """
        デフォルトのプリセットデータでファイルを作成します。
        """
        try:
            with open(self.presets_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error creating default preset file: {e}")

    def save(self):
        """
        現在のプリセットデータをファイルに保存します。
        """
        try:
            with open(self.presets_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.presets_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving presets: {e}")

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

    def save_preset(self, name: str, stamps: list[str]):
        """
        指定された名前のプリセットを、指定されたスタンプリストで
        上書きまたは新規作成します。
        """
        self.presets_data["presets"][name] = stamps

    def rename_preset(self, old_name: str, new_name: str) -> bool:
        """
        既存のプリセットの名前を変更します。
        """
        if old_name not in self.presets_data["presets"]:
            return False
        
        # popで既存のものを削除しつつ値を取得し、新しいキーで設定
        self.presets_data["presets"][new_name] = self.presets_data["presets"].pop(old_name)
        return True

    def delete_preset(self, name_to_delete: str) -> bool:
        """
        指定されたプリセットを削除します。
        """
        if name_to_delete not in self.presets_data["presets"]:
            return False
        
        # 最後のプリセットは削除させない (ViewModelで制御)
        if len(self.presets_data["presets"]) <= 1:
            return False

        del self.presets_data["presets"][name_to_delete]
        return True

    def get_all_unique_stamps(self) -> list[str]:
        """
        すべてのプリセットに含まれる、重複のないスタンプ名をソートして返します。
        """
        all_stamps = set()
        for preset_name in self.get_preset_names():
            stamps = self.get_stamps(preset_name)
            all_stamps.update(stamps)
        return sorted(list(all_stamps))

    # TODO: 今後、プリセットの追加、名前変更、削除などのメソッドをここに追加していきます。