# プロジェクト TODO リスト

## フェーズ 1: プロジェクトの骨格構築 (スケルトニング)

-   [ ] **1-1. フォルダ構成の作成:** `03_FILE_STRUCTURE.md` に基づき、`app` と `services` フォルダを作成する。
-   [ ] **1-2. 空のPythonファイルの作成:** 設計図に記載されているすべての `.py` ファイルを作成する。
    -   [ ] `main.py`
    -   [ ] `app/__init__.py`
    -   [ ] `app/main_window.py`
    -   [ ] `app/app_logic.py`
    -   [ ] `app/config.py`
    -   [ ] `services/__init__.py`
    -   [ ] `services/video_player.py`
    -   [ ] `services/analysis_service.py`
    -   [ ] `services/preset_service.py`
    -   [ ] `services/settings_service.py`
    -   [ ] `services/export_service.py`
-   [ ] **1-3. クラスの雛形作成:** 作成した各 `.py` ファイルに、対応する空のクラスを定義する。(例: `class MainWindow: ...`)

## フェーズ 2: 機能の分離と移植 (リファクタリング)

-   [ ] **2-1. 設定/定数管理機能の分離:**
    -   [ ] `app/config.py` に、ファイルパスやデフォルト値などの定数を移管する。
    -   [ ] `services/settings_service.py` に、`app_settings.json` の読み書きロジックを実装する。
    -   [ ] `services/preset_service.py` に、`procedure_presets.json` の読み書きロジックを実装する。
-   [ ] **2-2. 動画再生機能の分離:**
    -   [ ] `services/video_player.py` に、VLCの初期化、再生、停止、シークなどのロジックを `VideoPlayerService` クラスとして実装する。
-   [ ] **2-3. UI(View)の分離:**
    -   [ ] `app/main_window.py` に、元の `main.py` からTkinterウィジェットの作成と配置に関するコードをすべて移管する。この時点ではボタンの動作（ロジック）は空にする。
-   [ ] **2-4. エントリーポイントの単純化:**
    -   [ ] `main.py` を書き直し、動画ファイルを選択させ、`AppLogic` と `MainWindow` を起動するだけのシンプルなコードにする。
-   [ ] **2-5. ロジック(Controller)とUIの接続:**
    -   [ ] `app/app_logic.py` を実装し、UIからのイベント（ボタンクリック等）を受け取り、対応するサービスクラスを呼び出す「司令塔」として機能させる。
-   [ ] **2-6. 分析機能の分離:**
    -   [ ] `services/analysis_service.py` に、タイムスタンプ記録 (`Start`, `End`)、Undo、サマリー計算のロジックを移管する。
-   [ ] **2-7. エクスポート機能の分離:**
    -   [ ] `services/export_service.py` に、CSVファイルとグラフ画像の生成・保存ロジックを移管する。

## フェーズ 3: 改善項目の実装

-   [ ] **3-1. ショートカット競合問題の解決:**
    -   [ ] `app/app_logic.py` に、ダイアログ表示中にメインウィンドウのキーボードショートカットを一時的に無効化し、ダイアログが閉じたら元に戻す処理を実装する。
-   [ ] **3-2. 複数動画の連続解析機能の実装:**
    -   [ ] `main.py` のファイル選択ダイアログで、複数ファイルの選択を許可する。
    -   [ ] `services/video_player.py` に、選択された複数ファイルをプレイリストとして管理し、シームレスに連続再生する機能を実装する。
    -   [ ] タイムライン（再生バー）が、全動画の合計時間を正しく反映するように `app_logic.py` と `main_window.py` を修正する。

## フェーズ 4: 最終調整とテスト

-   [ ] **4-1. 動作確認:** すべての機能が意図通りに動作するか、一通りテストする。
-   [ ] **4-2. UIフリーズ問題の確認:** 特にプリセット操作やデータ記録中にUIが固まらないかを確認する。
-   [ ] **4-3. コードのクリーンアップ:** 不要なコメントやコードを削除し、全体の可読性を向上させる。