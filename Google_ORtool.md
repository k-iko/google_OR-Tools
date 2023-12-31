# Google OR-Tools
## 概要
OR-Tools は組み合わせ最適化向けのオープンソース ソフトウェアです。これは、非常に広範な可能性のあるソリューションの中から問題に対する最適なソリューションを見つけるものです。
## 特徴
- 簡単なモデル構築： Python言語を使用して、線形および非線形の最適化問題、混合整数問題、二次制約問題をモデル化できます。
- 多機能ソルバーインターフェース：COIN-ORオープンソースソルバ、商用ソルバなど様々なソルバへのインターフェースがあります。
- 可視化：最適化プロセス中の制約条件や目的関数の変化をグラフ化して可視化できます。
- 柔軟性のあるAPI：Pythonの独自機能を利用して柔軟にモデルを操作することができます。
## 活用領域
OR-Tools で解決できる問題の例を次に示します。
- 車両のルーティング: 特定の制約（「このトラックは 20,000 ポンド以下にする必要があります」または「すべての配達は 2 時間の時間枠内で行う必要があります」。
- スケジューリング: 複雑なタスクセットに対する最適なスケジュールを見つけます。固定されたマシンセット、またはその他のリソースよりも先に実行しなければならないタスクもあります。
- ビンパッキング: 最大容量の固定数のビンに、さまざまなサイズのオブジェクトをできるだけ多くパッキングします。
多くの場合、このような問題には可能性のある解決策が膨大な数にのぼります。パソコンにとってその解決策は多すぎます。これに対処するために、OR-Tools は最先端のアルゴリズムを使用して検索セットを絞り込み、最適な（または最適な）ソリューションを見つけます。
## 使用するアルゴリズム
 Google OR-Toolsは、最適化問題を解決するための一連のツールを提供します。以下は、OR-Toolsを活用した最適化のプログラムの例です。

1. Linear Programming (LP) Solver: LP solverは、線形計画問題を解決するために使用されます。この問題は、目的関数を最小化（または最大化）する変数xの値を求めるものです。OR-ToolsのLP solverは、Simplex法やInterior Point Methodsなどの手法を使用して、効率的かつ正確に解を得ることができます。
2. Integer Programming (IP) Solver: IP solverは、整数計画問題を解決するために使用されます。この問題は、目的関数を最小化（または最大化）する整数変数xの値を求めるものです。OR-ToolsのIP solverは、Branch & Bound法やCutting Plane Methodsなどの手法を使用して、効率的かつ正確に解を得ることができます。
3. Nonlinear Programming (NLP) Solver: NLP solverは、非線形計画問題を解決するために使用されます。この問題は、目的関数を最小化（または最大化）する非線形変数xの値を求めるものです。OR-ToolsのNLP solverは、Newton Raphson法やQuasi-Newton法などの手法を使用して、効率的かつ正確に解を得ることができます。
4. Dynamic Programming (DP): DPは、動的計画法を使用して、最適化問題を解決するために使用されます。この方法では、各状態における最適な解を保存し、次の状態への移行時にそれを参照することで、高速かつ正確に解を得ることができます。OR-ToolsのDPは、費用最小化問題や配置問題などの問題を解決するためによく使用されます。
5. Genetic Algorithm (GA): GAは、進化計算法を使用して、最適化問題を解決するために使用されます。この方法では、初期解を生成し、それを反復的に改良して、最適解を見つけ出すことができます。OR-ToolsのGAは、複雑な最適化問題を解決するためによく使用されます。
6. Ant Colony Optimization (ACO): ACOは、コロニー最適化法を使用して、最適化問題を解決するために使用されます。この方法では、蚂蚁群が食事源を捜索するように、解空間内の点を探索して、最適解を見つけ出すことができます。OR-ToolsのACOは、複雑な最適化問題を解決するためによく使用されます。
7. Particle Swarm Optimization (PSO): PSOは、パーティクル群最適化法を使用して、最適化問題を解決するために使用されます。この方法では、パーティクル群が解空間内を移動して、最適解を見つけ出すことができます。OR-ToolsのPSOは、複雑な最適化問題を解決するためによく使用されます。
8. Simulated Annealing (SA): SAは、模擬降温法を使用して、最適化問題を解決するために使用されます。この方法では、初期解を生成し、それを反復的に改良して、最適解を見つけ出すことができます。OR-ToolsのSAは、複雑な最適化問題を解決するためによく使用されます。
9. Bee Colony Optimization (BCO): BCOは、蜂の集団最適化法を使用して、最適化問題を解決するために使用されます。この方法では、蜂の集団が食事源を捜索するように、解空間内の点を探索して、最適解を見つけ出すことができます。OR-ToolsのBCOは、複雑な最適化問題を解決するためによく使用されます。
10. Firefly Algorithm (FA): FAは、火蟲最適化法を使用して、最適化問題を解決するために使用されます。この方法では、火蟲が光を放つことで、他の火蟲に向かって移動することで、最適解を見つけ出すことができます。OR-ToolsのFAは、複雑な最適化問題を解決するためによく使用されます。
以上のように、OR-Toolsは、幅広い最適化問題を解決するために使用される多くの技術を提供しています。ユーザーは、自身の問題に合った最適化手法を選択することができます。
## 実行環境
## データ準備
## 使い方
## 終わりに
## 参考にしたサイト
[Google OR-Tools](https://developers.google.com/optimization/introduction?hl=ja)<br>
[OR-Toolsによる配送計画最適化](https://qiita.com/_jinta/items/3494dff06bee9d85f1e5)