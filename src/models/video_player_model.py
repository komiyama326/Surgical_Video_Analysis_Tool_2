import vlc
import time
import os

class VideoPlayerModel:
    """
    VLCプレイヤーを管理し、動画再生のロジックを担当するクラス。
    複数動画の連続再生に対応。
    """
    
    def __init__(self):
        """
        VideoPlayerModelの初期化。
        VLCインスタンスとMediaListPlayerを作成します。
        """
        self.vlc_instance = vlc.Instance()
        
        # MediaListPlayerを作成
        self.list_player = self.vlc_instance.media_list_player_new()
        
        # MediaListPlayerから内部のMediaPlayerインスタンスを取得
        self.player = self.list_player.get_media_player()
        
        self.media_loaded = False
        self.video_files = []

        # 各動画の長さ(ms)と、その動画までの合計時間(ms)をキャッシュする
        self._media_durations = []
        self._cumulative_durations = []
        self._total_duration = 0

    def set_video_files(self, file_paths: list[str]):
        """
        再生する動画ファイルのリストを設定します。
        
        Args:
            file_paths: 動画ファイルのパスのリスト。
        """
        if not file_paths:
            self.media_loaded = False
            return
        
        self.video_files = file_paths
        
        # キャッシュをリセット
        self._media_durations = []
        self._cumulative_durations = [0]
        self._total_duration = 0

        media_list = self.vlc_instance.media_list_new()
        
        for path in file_paths:
            media = self.vlc_instance.media_new(path)
            media_list.add_media(media)
            
            # 各動画の長さを取得してキャッシュする
            # この処理は時間がかかる可能性があるため、本来は非同期処理が望ましい
            media.parse()
            time.sleep(0.05) # パースを待つ
            duration = media.get_duration()
            if duration > 0:
                self._media_durations.append(duration)
                self._total_duration += duration
                self._cumulative_durations.append(self._total_duration)

        self.list_player.set_media_list(media_list)
        self.media_loaded = True
        
        print(f"Media list loaded. Total duration: {self._total_duration / 1000.0:.2f}s")

    def get_current_video_path(self) -> str | None:
        """現在再生中の動画ファイルのパスを返します。"""
        if not self.media_loaded:
            return None
        
        media = self.player.get_media()
        if not media:
            return None
        
        return media.get_mrl()

    def set_display_handle(self, handle: int):
        """
        動画を表示するUIコンポーネントのハンドルを設定します。
        設定後、一度再生・停止することで最初のフレームを描画させます。
        """
        if not handle or not self.media_loaded:
            return

        self.player.set_hwnd(handle)

        # ★★★【今回の修正の核心】★★★
        # 最初のフレームを描画させ、かつ確実に一時停止状態にする
        self.list_player.play()
        
        # play()の反映を少し待つ
        time.sleep(0.1) 
        
        # 再生中であれば、pause()を呼び出す
        if self.list_player.is_playing():
            self.list_player.pause()

    def play_pause(self):
        """動画の再生と一時停止を切り替えます。"""
        if not self.media_loaded: return
        
        # MediaListPlayerのplay/pauseメソッドを呼び出す
        self.list_player.pause()

    def set_time(self, time_ms: int):
        """
        プレイリスト全体の指定された総経過時間（ミリ秒）に再生位置を設定します。
        """
        if not self.media_loaded or time_ms < 0 or time_ms > self._total_duration:
            return
            
        # ★★★【修正の核心】★★★
        # シーク操作の前に、現在の再生状態を記憶しておく
        was_playing = self.list_player.is_playing()

        # 1. どの動画を再生すべきか (target_index) を特定
        target_index = -1
        for i, cumulative_time in enumerate(self._cumulative_durations):
            if time_ms < cumulative_time:
                target_index = i - 1
                break
        
        if target_index == -1: return

        # 2. その動画内での再生時間 (time_in_media) を計算
        time_offset = self._cumulative_durations[target_index]
        time_in_media = time_ms - time_offset

        # 3. MediaListPlayerで目的の動画に切り替え、シークを実行
        self.list_player.play_item_at_index(target_index)
        
        time.sleep(0.1) 
        
        self.player.set_time(time_in_media)

        # 4. 記憶しておいた再生状態に戻す
        if was_playing:
            # 再生中だった場合は、再生を再開
            self.list_player.play()
        else:
            # 一時停止中だった場合は、一時停止を維持
            self.list_player.pause()

    def set_rate(self, rate: float):
        """再生速度を設定します。"""
        self.player.set_rate(rate)

    def get_time(self) -> int:
        """
        プレイリスト全体の現在の総再生時間をミリ秒単位で取得します。
        """
        if not self.media_loaded:
            return 0

        # 現在再生中のメディアがリストの何番目かを取得
        current_media = self.player.get_media()
        if not current_media:
            return 0
        
        try:
            # Mediaオブジェクトから直接インデックスを取得するのは難しいため、
            # MRL (パス) を比較してインデックスを特定する
            current_path = current_media.get_mrl()
            current_index = -1
            for i, path in enumerate(self.video_files):
                # vlc.Media.new()で生成されるMRLは 'file:///C:/...' のようになるため、それを考慮
                if os.path.basename(path) in current_path: # ファイル名で比較
                    current_index = i
                    break
            
            if current_index == -1: return 0

            # 前の動画までの合計時間 + 現在の動画での経過時間
            time_offset = self._cumulative_durations[current_index]
            current_media_time = self.player.get_time()
            return time_offset + current_media_time
        except Exception:
            # まだメディア情報が取得できていない場合など
            return 0

    def get_length(self) -> int:
        """
        プレイリスト全体の総再生時間をミリ秒単位で取得します。
        """
        return self._total_duration
        
    def is_playing(self) -> bool:
        """現在再生中かどうかを返します。"""
        return self.list_player.is_playing()

    def release_player(self):
        """プレイヤーリソースを解放します。"""
        if self.list_player:
            if self.list_player.is_playing():
                self.list_player.stop()
            self.list_player.release()
            self.list_player = None
            self.player = None # 内部のplayer参照もクリア
            print("VLC List Player released.")