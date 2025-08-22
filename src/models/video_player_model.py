import vlc
import time

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
            
        # TODO: 現時点では最初のファイルのみを再生する。
        #       複数ファイル対応は後のフェーズで実装する。
        media = self.vlc_instance.media_new(file_paths[0])
        self.player.set_media(media)
        
        # ★★★【修正箇所】★★★
        # MediaPlayerオブジェクトではなく、Mediaオブジェクトに対してparseを呼び出す
        media.parse()
        
        self.media_loaded = True
        
        # メディアの長さが取得できるまで少し待つ
        # これにより、UIのタイムラインなどを正しく初期化できる
        time.sleep(0.2) 

        print(f"Media loaded: {file_paths[0]}, Duration: {self.get_length()} ms")

    def set_display_handle(self, handle: int):
        """
        動画を表示するUIコンポーネントのハンドルを設定します。
        設定後、一度再生・停止することで最初のフレームを描画させます。
        
        Args:
            handle: ウィンドウハンドル (Tkinterのwinfo_id()で取得)。
        """
        if not handle or not self.media_loaded:
            return

        self.player.set_hwnd(handle)

        # ★★★【今回の修正の核心部分】★★★
        # 最初のフレームを描画させるための「キックスタート」処理。
        # 再生状態でない場合、一度だけ再生→即時停止を行う。
        # これにより、UIに静止した最初のフレームが表示される。
        if self.player.is_playing() == 0:
            self.player.play()
            # play()の反映には少し時間がかかる場合があるため、ごく短い待機を入れる
            time.sleep(0.1) 
            self.player.pause()

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
            if self.player.is_playing():
                self.player.stop()
            self.player.release()
            self.player = None
            print("VLC Player released.")