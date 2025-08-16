# 3. ファイル・フォルダ構成 (File & Folder Structure)

`02_ARCHITECTURE.md`で定義したアーキテクチャに基づき、プロジェクトのファイルとフォルダを以下のように構成する。

Surgical_Video_Analysis_Tool_2/
│
├── .vscode/ # VS Codeの設定ファイル (自動生成される場合)
│
├── .svat_docs/ # プロジェクトドキュメント
│ ├── 01_DESIGN_PHILOSOPHY.md
│ ├── 02_ARCHITECTURE.md
│ └── 03_FILE_STRUCTURE.md
│
├── main.py # アプリケーション起動スクリプト (エントリーポイント)
│
├── app/ # UIとアプリケーションロジック
│ ├── init.py
│ ├── main_window.py # MainWindowクラス (View)
│ ├── app_logic.py # AppLogicクラス (Controller)
│ └── config.py # 定数、設定値
│
└── services/ # ビジネスロジック
├── init.py
├── video_player.py # VideoPlayerServiceクラス
├── analysis_service.py # AnalysisServiceクラス
├── preset_service.py # PresetServiceクラス
├── settings_service.py # SettingsServiceクラス
└── export_service.py # ExportServiceクラス


## 各ファイルの役割

-   **`main.py`**: アプリケーションを起動する。
-   **`app/main_window.py`**: `tkinter` を使ったGUIの見た目と配置を定義する。
-   **`app/app_logic.py`**: `main_window.py` からの操作を受け取り、`services` を呼び出す。
-   **`app/config.py`**: 設定ファイル名やデフォルト値などの定数を置く。
-   **`services/*.py`**: 動画再生、データ記録、ファイル保存など、それぞれの専門的な処理を担当するクラスを定義する。