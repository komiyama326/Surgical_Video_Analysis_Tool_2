# 00_TODO_LIST.md

## Surgical Video Analysis Tool 2 - 開発タスクリスト

### フェーズ 1: 設計と計画 (完了)
- [x] `01_DESIGN_PHILOSOPHY.md` の作成
- [x] `02_ARCHITECTURE.md` の作成
- [x] `03_FILE_STRUCTURE.md` の作成
- [x] `00_TODO_LIST.md` の作成

### フェーズ 2: 環境構築
- [ ] Gitリポジトリの初期化 (`git init`)
- [ ] `.gitignore` ファイルの作成
- [ ] 仮想環境の構築 (`.venv`) とアクティベート
- [ ] 依存ライブラリのインストール (`python-vlc`, `pandas`, `matplotlib`)
- [ ] 設計ドキュメントの初回コミット

### フェーズ 3: 実装 (スケルトニング)
- [ ] `03_FILE_STRUCTURE.md` に基づくディレクトリと空ファイルの作成
- [ ] 各ファイルにクラスや関数の雛形（スケルトンコード）を記述
- [ ] スケルトンコードのコミット

### フェーズ 4: 実装 (コア機能)
- [ ] **Model**: `SettingsModel` - 設定の読み込み/保存機能の実装
- [ ] **Model**: `PresetModel` - プリセットの読み込み/保存機能の実装
- [ ] **View**: `MainWindow` - Tkinterウィンドウの基本レイアウト実装
- [ ] **ViewModel**: `MainViewModel` - アプリケーション起動時の初期化処理（設定とプリセットの読み込み）
- [ ] **エントリーポイント**: `main.py` と `src/app.py` を実装し、空のウィンドウが表示されることを確認
- [ ] **Model**: `VideoPlayerModel` - 動画の読み込みと表示機能の実装
- [ ] **View/ViewModel**: 動画を開くダイアログの実装
- [ ] **View/ViewModel**: 再生コントロール（再生/一時停止、シーク、速度変更）の実装
- [ ] **View/ViewModel**: タイムラインと時間表示の更新機能の実装

### フェーズ 5: 実装 (分析機能)
- [ ] **View/ViewModel**: プリセットリストの表示と選択機能の実装
- [ ] **Model**: `AnalysisDataModel` - 分析データ（タイムスタンプ）の管理機能
- [ ] **View/ViewModel**: "Start", "End", "Undo" ボタンのロジック実装
- [ ] **View/ViewModel**: ライブサマリー（記録数、合計時間）の表示更新機能
- [ ] **改善要件**: 入力ダイアログ中のショートカットキー無効化機能の実装

### フェーズ 6: 実装 (プリセット管理機能)
- [ ] **View/ViewModel**: プリセットの追加/削除/名前変更機能の実装
- [ ] **View/ViewModel**: 未保存の変更がある場合に `*` を表示する機能の実装

### フェーズ 7: 実装 (ファイル出力機能)
- [ ] **ViewModel**: 分析結果をCSVファイルとして保存する機能の実装
- [ ] **ViewModel**: グラフを生成してPNGファイルとして保存する機能の実装
- [ ] **View**: 結果表示ダイアログの実装

### フェーズ 8: 実装 (複数動画対応)
- [ ] **Model**: `VideoPlayerModel` を複数の動画ファイルを扱えるように拡張
- [ ] **View/ViewModel**: 複数動画選択ダイアログと、動画リストの管理UIを実装
- [ ] **ViewModel**: 動画間のシームレスな再生移行処理を実装

### フェーズ 9: 最終調整とテスト
- [ ] 全機能の動作確認とデバッグ
- [ ] コードのリファクタリングとクリーンアップ
- [ ] `requirements.txt` の生成
- [ ] (オプション) PyInstallerによる実行可能ファイル（.exe）化の検討