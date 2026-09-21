## 概要と目的

本ドキュメントは、音響配線パッチングシステムにおけるドメイン層の再設計および2次元ビュー描画エンジンの実装方針をまとめたものである。人間（開発者）とAI（実装アシスタント）の双方が設計の背景（Why）・構造（What）・タスク手順（How）を誤解なく理解し、段階的に実装を進められるようにタスク別にセクション化している。

---

## 全体設計の基本原則 (Architecture Principles)

1. **ユビキタス言語の徹底**: 画面UIの表記とコードのクラス名を完全一致させる（`EquipmentDefinition` など）。
2. **Pure Python ドメインエンティティ**: ドメイン層（`domain/`）の Entity / Value Object は Pydantic や PySide6 等に依存せず、標準の `@dataclass` で定義する。Pydantic は Storage/Repository 層に閉じる。
3. **2段階射影アーキテクチャ (2-Stage Projection)**:
* グラフ（多次元） ➜ 探索アルゴリズム ➜ **`SignalPath`（1本の回線経路中間表現）** ➜ 各ビュー（2次元テーブル）へ射影。


4. **Soft Limit（柔軟な警告）**: 数量超過や軽微な不一致は操作をブロックせず、警告（Warning）状態としてUIに通知する。

---

## タスク別実装方針

### Task 1: ドメインエンティティの Pure Python 化と命名統一

* **目的**: 既存の `EquipmentEntity` / `Master` 等の命名を整理し、サードパーティ依存のない純粋なドメインエンティティを再構築する。
* **意図**: DDDの観点から「定義（Definition）」と「現場での実体（Instance）」を対比させ、可読性と移植性を向上させる。

#### 実装仕様

* **ファイル配置**: `domain/entities/`
* **主要クラス**:
* `EquipmentDefinition`: 機材のひな形・構造定義（型番、ポート構成、内部接続、持ち込み上限数）。
* `EquipmentInstance`: 現場グラフ上に配置された1台ごとの実体（参照定義ID、現場用ラベル、ポート個別状態）。


* **注意事項**: Pydanticの `BaseModel` ではなく、標準の `@dataclass` を使用すること。

```python
# domain/entities/equipment_definition.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class EquipmentDefinition:
    id: str
    vendor: str
    model_name: str
    ports: list[PortDefinition]
    internal_links: list["InternalLink"]
    max_quantity: Optional[int] = None  # 持ち込み上限数
```

---

### Task 2: 機材内部接続 (`InternalLink`) と数量監視 (`max_quantity`) の実装

* **目的**: DIのスルーアウトやミキサー内部ルーティングをモデル化し、集約（`AudioPatchSystem`）での数量監視を可能にする。
* **意図**: シグナルフローを中断させることなく追跡可能にし、持ち込み数オーバーを自動検知して現場トラブルを防ぐ。

#### 実装仕様

1. **内部接続 (`InternalLink`)**:
* `InternalLinkType`: `PASSTHROUGH`（DIのThru等）、`INTERNAL_ROUTE`（卓内部割り当て等）
* `EquipmentDefinition` に `internal_links: list[InternalLink]` を保持させる。


2. **数量監視 (Soft Limit Monitoring)**:
* `AudioPatchSystem` に配置数の動的カウントメソッド `get_instance_count(definition_id: str) -> int` を実装。
* 追加時に `max_quantity` を超過していても例外で弾かず、`QuantityWarning` を返す仕様とする。



---

### Task 3: コネクタ接続評価と変換アダプターフラグの実装

* **目的**: コネクタ形状・性別の判定ロジックを整理し、XLR ↔ BTS などの変換ケーブル使用フラグ（`is_adapted`）を保持する。
* **意図**: 実用に影響しない複雑な仕様（ケーブル本数管理やレベル差チェック）を削ぎ落とし、現場で頻出する「規格違いの変換噛ませ」のみをシンプルに管理する。

#### 実装仕様

* **ファイル配置**: `domain/services/connection_validator.py`
* **データ構造**:
* `ConnectorType`: `XLR_3PIN`, `BTS_21`, `TRS_1_4`, `TS_1_4`, `ETHERCON`, `SPEAKON_4P`
* `ConnectorGender`: `MALE`, `FEMALE`, `GENDERLESS`
* `ConnectionResult`: `is_connectable: bool`, `is_adapted: bool`, `reason: str`


* **判定ルール**:
* コネクタ型と性別が完全一致 ➜ 直結（`is_adapted=False`）
* 変換可能ペア（`ADAPTABLE_PAIRS`: XLR ↔ BTS, XLR ↔ TRS 等） ➜ 変換接続（`is_adapted=True`）



---

### Task 4: グラフ探索による `SignalPath` 生成エンジンの構築

* **目的**: 複雑なノード・エッジ・内部リンク構造から、起点（音源/マイク）〜終点（卓/スピーカー）までの直線的な回線リストを抽出する。
* **意図**: 2次元テーブル（ビュー）を描画するための共通中間表現 `SignalPath` を生成し、UI層とグラフ探索ロジックを完全分離する。

#### 実装仕様

* **中間データ表現 (`SignalPath`)**:
```python
@dataclass
class PathSegment:
    instance_id: str
    instance_name: str
    port_id: str
    port_name: str
    equipment_category: str


@dataclass
class SignalPath:
    path_id: str
    source_name: str  # 音源/楽器名 (例: "Dr.Kick", "Fa-07")
    source_instance_id: str  # 音源の機材ID
    mic_or_di: Optional[str]  # 使用マイク/DI名
    segments: list[PathSegment]  # 経路上の通過ノード順序リスト
    is_pa_send: bool = True  # メインPA送りか、モニター等か
```


* **探索処理 (`AudioPatchSystem.generate_signal_paths()`)**:
* 深さ優先探索（DFS）等を用い、起点ポートから `InternalLink` および外部 `PatchConnection` を順に辿って `SignalPath` のリストを吐き出す。



---

### Task 5: 3つのビューへの射影と割り込みソート (Interleaving) の実装

* **目的**: 抽出された `list[SignalPath]` を元に、3種類の2次元表示テーブルを生成する。
* **意図**: 舞台仕込みスタッフおよびPAオペレーター双方にとって見やすい画面出力を実現する。



#### 3つのビューと射影ルール

1. **機材グループビュー (仕込み図用)**:


* 対象機材（例: ミキサー `MG24` やマルチ）の全ポート（1〜N）を固定行とし、各ポートを通る `SignalPath` から音源名や経由マルチを補填（空きポートは空行表示）。


2. **ノード追跡ビュー (全回線一覧)**:
* `SignalPath` 単位で、起点から終点までの通過ノードを左から右へ列方向に展開。


3. **舞台側全体ビュー (割り込みソート / Interleaving)**:


* **基本軸**: アンカーとなるマルチのチャンネル順 (Ch 1, Ch 2, Ch 3...)。
* **割り込みロジック**: 同一音源（例: キーボード `Fa-07`）から発する回線群（メインPA送り、モニター送り）をグループ化し、メインPA送りの直後にモニター回線を「割り込み行（サブ行）」として並べ替えて描画する。



---

ドキュメントの構成や各タスクの記載内容について、「ここをもっとこう書いておきたい」「追加したい補足」などがあれば自由に調整してご活用ください！