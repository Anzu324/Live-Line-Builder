# ドメインモデル仕様書

## 1. ドメイン層の設計原則
- **外部依存の排除**: ドメイン層の Entity / Value Object は Pydantic や PySide6 等のサードパーティライブラリに依存させず、標準の `@dataclass` または純粋な Python クラスで実装する。
- **永続化層との分離**: Pydantic スキーマは Storage / Infrastructure 層（JSON シリアライズ等）に閉じ込め、データ復元時にドメイン Entity へ変換する。

## 2. 主要エンティティ定義

### 機材定義 (EquipmentDefinition)
```python
@dataclass
class EquipmentDefinition:
    id: str
    vendor: str
    model_name: str
    ports: list[PortDefinition]
    internal_links: list[InternalLink]
    max_quantity: Optional[int] = None  # 持ち込み/確保上限数
```

### 機材インスタンス (EquipmentInstance)

```python
@dataclass
class EquipmentInstance:
    id: str
    definition_id: str
    label: str  # 例: "A.Gtr DI", "Stagebox Prompt L"
    port_states: dict[str, PortState]
```

### 内部リンク (InternalLink)

```python
class InternalLinkType(str, Enum):
    PASSTHROUGH = "passthrough"  # スルーアウト・パラレル（DI Thru等）
    INTERNAL_ROUTE = "internal_route"  # ミキサー内部ルーティング等


@dataclass
class InternalLink:
    from_port_id: str
    to_port_id: str
    link_type: InternalLinkType
```

## 3. 数量監視ロジック (Quantity Monitoring)

* 集約である `AudioPatchSystem` が `EquipmentInstance` の配置数を動的に集計する。
* 配置数が `EquipmentDefinition.max_quantity` を超過した場合でも操作はブロックせず、警告オブジェクト（Soft Limit Warning）を発行して UI 上で視覚的にアピールする。

## 4. 接続判定ロジック (Connection Validation)

* コネクタ型（`ConnectorType`）および性別（`ConnectorGender`）に基づき、`evaluate_connection()` ドメインサービスが適合性を判定する。
* 変換可能ペア（`ADAPTABLE_PAIRS`: 例 XLR ↔ BTS, XLR ↔ TRS）に該当する場合、`ConnectionResult(is_connectable=True, is_adapted=True)` を返し、接続情報に変換フラグを保持する。



### 3. `docs/architecture.md`（全体アーキテクチャ・射影設計）

UIとドメインの分離、および2段階変換アルゴリズムの仕様です。

# システムアーキテクチャ・射影仕様書

## 1. レイヤー構造とデータフロー

```

[UI Layer (PySide6)]
▲
│ (Qt Signal / TableModel)
[Application Layer / Controllers]
│ (SignalPath の生成・射影要求)
▼
[Domain Layer] (AudioPatchSystem / Graph Search)
▲
│ (Entity の復元・保存)
[Storage Layer] (Repository / Pydantic JSON Schema)

```

## 2. 2段階射影アーキテクチャ (2-Stage Projection)
グラフ構造（DAG）から2次元テーブルを生成するため、中間表現 `SignalPath` を経由する2段階変換を採用する。

1. **グラフ探索 ➔ SignalPath 生成**:
   `AudioPatchSystem` のグラフ（ノード・エッジ・InternalLink）を探索アルゴリズムで走査し、起点（音源）から終点（卓/スピーカー）までの順序付き通過リスト `SignalPath` を一括生成する。
2. **SignalPath ➔ View Projection**:
   生成された `list[SignalPath]` を各ビューの要求に合わせてソート・フィルタリングしてテーブル描画用データに変換する。

## 3. ビュー別の変換仕様

### (A) 機材グループビュー (仕込み図用)
- **基準軸**: 特定機材（ミキサー、マルチ等）の固定ポート順（1〜N）。
- **ロジック**: 対象機材の各ポートに対応する `SignalPath` を検索し、上流の音源名・経由ポート・マイク/DI名・手動メモを埋める。パッチのないポートは空行として描画。

### (B) ノード追跡ビュー (全経路リスト)
- **基準軸**: 回線（`SignalPath`）単位。
- **ロジック**: 起点から終点までの全通過ノードを左から右へ列方向に展開。

### (C) 舞台側全体ビュー (割り込みソート / Interleaving)
- **基準軸**: アンカーとなる舞台側マルチボックスのチャンネル順。
- **割り込みロジック (Interleaving)**:
  1. 全経路をアンカーマルチのCh番号順に一時整列。
  2. 同一の音源機材（`source_instance_id`）に属する回線群（メインPA送り、モニター送り等）をグループ化。
  3. 代表回線（PA送り）の直後の行に関連回線（モニター等）を「割り込み行」として挿入・再配列する。
