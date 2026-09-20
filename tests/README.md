# テスト構成の方針

このプロジェクトの `tests` は、アプリケーションの責務ごとに分けています。

## 基本方針

- 1ファイル = 1責務 or 1機能ごと
- ファイル名は `test_*.py` 形式
- 関数名は `test_` で始める
- 1テストは 1つの確認事項に絞る
- 依存関係は最小化し、テストごとに独立させる

## ディレクトリの役割

- `tests/domain/`: ドメインロジック、エンティティ、バリデーション
- `tests/graph/`: グラフ生成・描画ロジック
- `tests/model/`: モデル層の状態管理・データ変換
- `tests/storages/`: 永続化・リポジトリ処理
- `tests/ui/`: UI コントローラや表示ロジック

## 例: これがよい形

- `tests/domain/test_table_entity.py`
  - `TableEntity` の変換、値設定、検証を確認する
- `tests/storages/test_repository.py`
  - 保存と読み込みの契約を確認する
- `tests/ui/test_performance_tab_controller.py`
  - UI 操作とイベント処理を確認する

## テストの書き方の基本

```python
def test_something():
    # Arrange: 準備
    value = 1

    # Act: 実行
    result = value + 1

    # Assert: 確認
    assert result == 2
```

## 命名のルール

- `test_` で始める
- 何を確認しているかが分かる名前にする
- 例:
  - `test_table_entity_coerces_dict_rows_to_row_model`
  - `test_equipment_row_types`
  - `test_repository_loads_data`

## 追加するときの判断基準

新しいテストを追加するときは、以下のどちらかに属するかを考えます。

- そのロジックはどの層の責務か
- どのエンティティや機能に対する確認なのか

層ごとに分けておくと、どこが壊れたのかがすぐ分かります。
