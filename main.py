import sys
import os

# プロジェクトのルートディレクトリをPythonのパスに追加します。
# これにより、`src` フォルダ内のモジュール（例: app.py）を正しく見つけられるようになります。
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import Application

def main():
    """
    アプリケーションを起動するためのメイン関数です。
    """
    # Applicationクラスのインスタンスを作成し、実行します。
    app = Application()
    app.run()

if __name__ == "__main__":
    # このスクリプトが直接実行された場合にのみ、main()関数を呼び出します。
    main()