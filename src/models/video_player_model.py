import vlc

class VideoPlayerModel:
    """
    VLCプレイヤーを管理し、動画再生のロジックを担当するクラス。
    """
    
    def __init__(self):
        """
        VideoPlayerModelの初期化。
        VLCインスタンスとプレイヤーを作成します。
        """
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        
        self.media_loaded = False

    def set_video_files(self, file_paths: list[str]):
        """
        再生する動画ファイルのリストを設定します。
        
        Args:
            file_paths: 動画ファイルのパスのリスト。
        """
        if not file_paths:
            self.media_loaded = False
            return
            
        # TODO: 複数の動画ファイルを連続再生するための MediaList と MediaListPlayer を
        #       ここで作成・設定するロジックを実装します。
        #       単一ファイルの場合は、元のコードと同様に Media を作成します。
        
        # とりあえず単一ファイルの場合の雛形
        media = self.vlc_instance.media_new(file_paths[0])
        self.player.set_media(media)
        self.media_loaded = True
        print(f"Media loaded: {file_paths}") # 動作確認用

    def set_display_handle(self, handle: int):
        """
        動画を表示するUIコンポーネントのハンドルを設定します。
        
        Args:
            handle: ウィンドウハンドル (Tkinterのwinfo_id()で取得)。
        """
        if handle:
            self.player.set_hwnd(handle)

    def play_pause(self):
        """
        動画の再生と一時停止を切り替えます。
        """
        if not self.media_loaded: return
        
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def set_time(self, time_ms: int):
        """
        再生位置を指定された時間（ミリ秒）に設定（シーク）します。
        """
        if self.player.is_seekable():
            self.player.set_time(time_ms)
    
    def set_rate(self, rate: float):
        """
        再生速度を設定します。
        """
        self.player.set_rate(rate)

    def get_time(self) -> int:
        """
        現在の再生時間をミリ秒単位で取得します。
        """
        return self.player.get_time()

    def get_length(self) -> int:
        """
        動画の総再生時間をミリ秒単位で取得します。
        """
        return self.player.get_length()
        
    def is_playing(self) -> bool:
        """
        現在再生中かどうかを返します。
        """
        return self.player.is_playing()

    def release_player(self):
        """
        プレイヤーリソースを解放します。
        """
        if self.player:
            self.player.stop()
            self.player.release()
            self.player = None