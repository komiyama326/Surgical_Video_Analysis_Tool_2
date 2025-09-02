# 04_UI_DESIGN_GUIDELINES.md

## Surgical Video Analysis Tool 2 - UIデザインガイドライン

このガイドラインは、アプリケーションのUIに一貫性、明瞭性、そしてプロフェッショナルな品質を与えることを目的とします。Tkinter/ttkの技術的制約を考慮し、実装コストを抑えつつ最大の効果を得られるルールを定義します。

### 1. 配色システム (Color System)

OSのテーマ（ライト/ダーク）に馴染みつつ、視認性とコントラストを確保するカラーパレット。

- **背景 (Backgrounds)**
  - `Window Background`: `#ECECEC` (Windows標準に近いライトグレー)
  - `Control Panel Background`: `#F5F5F7` (Apple風のわずかに明るいグレー)
  - `Video Area Background`: `#000000` (Black)

- **テキスト (Text)**
  - `Primary Text`: `#1D1D1F` (ほぼ黒に近い、可読性の高いグレー)
  - `Secondary Text`: `#6E6E73` (LabelFrameのタイトルなど)
  - `Disabled Text`: `#AEAEB2` (無効状態の文字)
  - `Accent Text / Link`: `#007AFF` (Apple System Blue)

- **UIコントロール (Controls)**
  - `Button Accent Background`: `#007AFF` (主要なアクションボタン用)
  - `Button Accent Text`: `#FFFFFF` (White)
  - `Error / Destructive`: `#FF3B30` (Apple System Red - 削除ボタンなど)

### 2. 余白システム (Spacing System)

アプリケーション全体のレイアウトの「呼吸」を整えるためのルール。**8px**を基本単位とする。

- **`4px` (x-small):**
  - アイコンとテキストの間など、密接に関連する要素間。
- **`8px` (small):**
  - 同じグループ内のウィジェット間の標準的な間隔。（例: `pady=8`）
- **`12px` (medium):**
  - 異なるが関連のあるグループ間の間隔。
- **`16px` (large):**
  - `LabelFrame`の内部 `padding` など、明確なセクションの内側の余白。
- **`24px` (x-large):**
  - `Preset Manager`と`Procedure Stamps`のような、大きなセクション間の外側余白。

#### 実装ルール:

- `pack()` を使用する際は `padx` と `pady` で余白を厳密に管理する。
- 関連するウィジェットは `ttk.Frame` にまとめ、そのFrameに対して余白を設定することで、一貫性を保つ。

### 3. タイポグラフィ (Typography)

情報の階層を明確にし、可読性を向上させる。OS標準フォントを基本とし、サイズとウェイトで差をつける。

- **フォントファミリー:**
  - **Windows:** `"Segoe UI"`
  - **macOS:** `".SF NS Text"` (システムフォント)
  - **Linux:** `"DejaVu Sans"` (一般的なフォールバック)

- **サイズとウェイト:**
  - **`16pt Bold` (Title):**
    - 用途: (未使用) アプリケーションのタイトルなど（将来用）
  - **`12pt Bold` (Section Title):**
    - 用途: `LabelFrame` のタイトルテキスト
  - **`10pt Normal` (Body / Standard):**
    - 用途: ボタンのテキスト、ラベル、リストの項目など、UIの基本フォント。
  - **`9pt Normal` (Caption):**
    - 用途: 補足的な情報、ステータスバーのテキストなど。

#### 実装ルール:

- `ttk.Style` を用いて、ウィジェットの種類ごとにフォント設定を共通化する。
  - 例: `style.configure("TButton", font=("Segoe UI", 10))`

### 4. UIコントロールのスタイル (Control Styles)

- **角丸 (Border Radius) と 影 (Shadow):**
  - **ルール:** OSネイティブのスタイルに従う。Tkinterでのカスタム実装は行わない。
  - **理由:** 実装コストが非常に高く、OSとの統一感を損なう可能性があるため。`ttk` の標準スタイルが、各OSで最も自然な見た目を提供する。

- **ボタン (Buttons):**
  - **標準ボタン:** OSネイティブのスタイル。
  - **主要アクションボタン (例: "Finish & Save"):**
    - 背景色: `Accent Blue (#007AFF)`
    - 文字色: `White (#FFFFFF)`
    - `ttk.Style` で特別なスタイル (`Accent.TButton`) を定義して適用する。

- **リスト表示 (Treeview):**
  - **選択行のハイライト:** `Accent Blue (#007AFF)` を基本とするが、OSネイティブの選択色を優先する。
  - **行の高さ:** 標準より少し広げ、タッチ操作や視認性を向上させる (例: `rowheight=28`)。

---