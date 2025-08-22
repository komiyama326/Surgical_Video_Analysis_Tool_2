import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

def format_time(seconds: float) -> str:
    """
    秒数を "HH:MM:SS" 形式の文字列に変換します。

    Args:
        seconds: 変換する秒数。

    Returns:
        フォーマットされた時間文字列。
    """
    if seconds is None or seconds < 0:
        return "00:00:00"
    
    # divmodを使って、商と余りを同時に計算します。
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    
    # f-stringを使って文字列をフォーマットします。
    return f"{hours:02d}:{mins:02d}:{secs:02d}"

def get_japanese_font() -> FontProperties | None:
    """
    環境に応じた日本語フォントのパスを取得します。
    見つからない場合は None を返します。
    """
    if sys.platform == "win32":
        font_path = os.path.join(os.environ['SystemRoot'], 'Fonts', 'meiryo.ttc')
        if os.path.exists(font_path):
            return FontProperties(fname=font_path)
    # TODO: macOSやLinux向けのフォントパスも追加可能
    return None

def create_and_save_graph(df, output_path: str, font_prop: FontProperties | None) -> str | None:
    """
    DataFrameからグラフを生成し、指定されたパスに画像として保存します。
    成功した場合はグラフ画像のパスを、失敗した場合は None を返します。
    """
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(12, 7))
        
        bar_width = 0.4
        index = np.arange(len(df['手順名']))
        
        bar1 = ax.bar(index - bar_width/2, df['所要時間(秒)'], bar_width, label='所要時間', color='royalblue')
        bar2 = ax.bar(index + bar_width/2, df['移行時間(秒)'].fillna(0), bar_width, label='移行時間', color='skyblue')
        
        ax.set_ylabel('時間 (秒)', fontsize=12, fontproperties=font_prop)
        ax.set_title('各手技の所要時間と移行時間', fontsize=16, pad=20, fontproperties=font_prop)
        ax.set_xticks(index)
        ax.set_xticklabels(df['手順名'], rotation=30, ha='right', fontsize=11, fontproperties=font_prop)
        ax.legend(prop=font_prop)
        ax.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)

        plt.tight_layout(pad=1.5)
        
        graph_path = output_path.replace('.csv', '.png')
        plt.savefig(graph_path, dpi=150)
        plt.close(fig)
        
        print(f"Graph saved to {graph_path}")
        return graph_path
    except Exception as e:
        print(f"Failed to create or save graph: {e}")
        return None

# TODO: 今後、他のヘルパー関数（例: グラフ生成関数）もここに追加する可能性があります。