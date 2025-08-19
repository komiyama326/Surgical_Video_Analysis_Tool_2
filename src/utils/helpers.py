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

# TODO: 今後、他のヘルパー関数（例: グラフ生成関数）もここに追加する可能性があります。