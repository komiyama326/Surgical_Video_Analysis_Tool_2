import pandas as pd

class AnalysisDataModel:
    """
    手術分析データを管理するクラス。
    タイムスタンプの記録、削除（Undo）、データのエクスポートを担当します。
    """
    
    def __init__(self):
        """
        AnalysisDataModelの初期化。
        分析データを保存するリストを準備します。
        """
        # 記録されたデータを [手順名, 開始時間, 終了時間, ... ] の形式で格納するリスト
        self._procedure_data = []
        
        # 現在記録中の手順の情報を一時的に保持する変数
        self.current_procedure_name = None
        self.current_start_time = None

    def start_procedure(self, procedure_name: str, start_time: float):
        """
        新しい手順の記録を開始します。
        """
        self.current_procedure_name = procedure_name
        self.current_start_time = start_time
        print(f"Started: {procedure_name} at {start_time:.2f}s") # 動作確認用

    def end_procedure(self, end_time: float, memo: str = ""):
        """
        現在記録中の手順を終了し、データをリストに保存します。
        """
        if self.current_procedure_name is None:
            return

        duration = end_time - self.current_start_time
        record = {
            "手順名": self.current_procedure_name,
            "開始時間(秒)": self.current_start_time,
            "終了時間(秒)": end_time,
            "所要時間(秒)": duration,
            "メモ": memo,
        }
        self._procedure_data.append(record)
        print(f"Ended: {self.current_procedure_name}. Record added.") # 動作確認用
        
        # 一時変数をリセット
        self.current_procedure_name = None
        self.current_start_time = None

    def undo_last_record(self) -> dict | None:
        """
        最後に追加された記録を削除し、その記録を返します。
        """
        if not self._procedure_data:
            return None
        
        return self._procedure_data.pop()

    def get_summary(self) -> tuple[int, float]:
        """
        記録済みの手順数と合計所要時間を返します。
        """
        count = len(self._procedure_data)
        total_duration = sum(item["所要時間(秒)"] for item in self._procedure_data)
        return count, total_duration

    def has_data(self) -> bool:
        """
        記録されたデータが存在するかどうかを返します。
        """
        return bool(self._procedure_data)
        
    import pandas as pd

    def export_to_dataframe(self) -> pd.DataFrame:
        """
        記録されたデータをPandas DataFrameとしてエクスポートします。
        """
        if not self._procedure_data:
            return pd.DataFrame()

        # データ整形処理はViewModelに移動したため、ここでは単純にDataFrameを返す
        df = pd.DataFrame(self._procedure_data)
        return df