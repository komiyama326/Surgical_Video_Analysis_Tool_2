# app/config.py
"""アプリケーション全体で使用する定数や設定値を定義するファイル"""

import os
import sys

# --- Path Settings ---
def get_app_data_path(filename=""):
    """
    ユーザーのAppData/Roamingフォルダ内にアプリケーション用のフォルダを作成し、
    指定されたファイルへのフルパスを返す。
    """
    if sys.platform == "win32":
        app_data_dir = os.path.join(os.environ['APPDATA'], 'SurgicalVideoAnalysisTool_v2')
    else: # macOS, Linux
        app_data_dir = os.path.join(os.path.expanduser('~'), '.config', 'SurgicalVideoAnalysisTool_v2')
    
    os.makedirs(app_data_dir, exist_ok=True)
    return os.path.join(app_data_dir, filename)

PRESETS_FILE = get_app_data_path('procedure_presets.json')
SETTINGS_FILE = get_app_data_path('app_settings.json')
RESULTS_DIR = get_app_data_path('AnalysisResults')


# --- Default Settings ---
DEFAULT_PRESET_NAME = "Default"
DEFAULT_STAMPS = [
    "角膜切開", 
    "前嚢切開 (CCC)", 
    "ハイドロダイセクション", 
    "水晶体超音波乳化吸引術 (PEA)", 
    "皮質吸引 (I/A)", 
    "眼内レンズ挿入 (IOL挿入)"
]
DEFAULT_SETTINGS = {
    "window_geometry": "1300x850+50+50", 
    "memo_enabled": False, 
    "graph_enabled": False
}