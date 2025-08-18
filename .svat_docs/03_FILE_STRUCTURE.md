# 03_FILE_STRUCTURE.md

## プロジェクトファイル構造

プロジェクトは、責務の分離と管理のしやすさを目的として、以下のディレクトリ構造を採用する。

Surgical_Video_Analysis_Tool_2/
│
├── .venv/ # Python仮想環境 (Git管理外)
│
├── .gitignore # Gitの追跡対象外ファイルを指定
│
├── main.py # アプリケーションのエントリーポイント（起動用スクリプト）
│
├── requirements.txt # プロジェクトの依存ライブラリリスト
│
└── src/ # ソースコードディレクトリ
│
├── init.py # このディレクトリをPythonパッケージとして認識させるためのファイル
│
├── app.py # アプリケーションのメインクラスと組み立て処理
│
├── models/
│ ├── init.py
│ ├── video_player_model.py
│ ├── analysis_data_model.py
│ ├── preset_model.py
│ └── settings_model.py
│
├── viewmodels/
│ ├── init.py
│ └── main_viewmodel.py
│
├── views/
│ ├── init.py
│ └── main_window.py
│
└── utils/
├── init.py
└── helpers.py # フォーマット関数などの汎用ヘルパー関数


### 各ファイルの役割

-   **`main.py`**:
    -   アプリケーションを起動する唯一の目的を持つ。
    -   `src.app` からメインアプリケーションクラスをインポートし、インスタンス化して実行する。

-   **`src/app.py`**:
    -   `MainWindow` (View), `MainViewModel`, 各`Model`をインスタンス化し、それらを結合してアプリケーションを構築する。
    -   アプリケーションのライフサイクル（開始と終了）を管理する。

-   **`src/models/`**:
    -   `video_player_model.py`: VLCプレイヤーの制御。
    -   `analysis_data_model.py`: 分析データの管理。
    -   `preset_model.py`: プリセットデータの管理。
    -   `settings_model.py`: 設定データの管理。

-   **`src/viewmodels/`**:
    -   `main_viewmodel.py`: UIからのイベントを処理し、ModelとViewの間のデータフローを管理する。

-   **`src/views/`**:
    -   `main_window.py`: Tkinterを使ったメインウィンドウとUIコンポーネントの定義。

-   **`src/utils/`**:
    -   `helpers.py`: `format_time` のような、プロジェクト全体で再利用可能な関数を配置する。