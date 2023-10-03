# OR-Toolsと比較してベンチマーキングする

## 事前準備

- requirements.txtのモジュールをインストール
    ```
    pip install -r requirements.txt
    ```

- CARGのVRPソルバをリポジトリの直下にコピー
    - CNSsolver_20221031_v2209a_EnglishVerの`vrp_classical`をコピーしてくる

## 使い方

- データディレクトリを準備
    - 適当なところに作成

- ベンチマークデータを取得
    - 取得先: https://www.sintef.no/projectweb/top/vrptw/100-customers/
    - `インスタンス名.txt`をデータディレクトリに保存

- ベンチマーキングを実行
    - `benchmarking`に移動
    - コード実行
        - `compare_ortools.ipynb`の場合
            - 特定のインスタンスをインタラクティブに実行
            - `DATA_DIR_PATH`にデータディレクトリを指定
            - `INSTANCE_NAME`にインスタンスを指定
        - `compare_ortools.py`の場合
            - 複数のインスタンスをバッチ処理
            - `DATA_DIR_PATH`にデータディレクトリを指定
            - `INSTANCE_NAMES`に対象インスタンス群をリスト形式で指定
    - 出力データ
        - `インスタンス名.png`: インスタンスの配置画像
        - `インスタンス名_result_ソルバ名.csv`: ソルバのベンチマーキング結果
            - TOTALCOST: 総距離
            - TOTAL_NUMBER_OF VEHICLES: 使用車両数
            - ELAPSED_TIME: 計算時間
                - CONSTRUCTION_TIME: 初期解生成時間※CARGソルバのみ
                - IMPROVEMENT_TIME: 近傍探索時間※CARGソルバのみ
        - `インスタンス名_route_ソルバ名.png`: ソルバの最適ルート画像
            - html画像でインタラクティブに見たい場合は`compare_ortools.ipynb`上で確認
        

