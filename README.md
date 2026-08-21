# 概要
ローカルで動かせる学生等を対象とした音響回線表作成アプリ。
Excelで音響回線表(仕込み図)作ると開発環境と運用環境が混ざるという欠点があるためストレスがたまるし、引継ぎが難しい。
そうであれば自作アプリを作ってしまおうという寸法である。

# 詳細(拙速だが作り途中)
[パッケージの分類方針](https://github.com/Anzu324/Live-Line-Builder/blob/main/docs/design-strategy/role-of-packages.md)

## 使っているライブラリ等

- UV (Pythonのバージョンやライブラリをプロジェクト単位で管理する)
- Pyside6 (UIを作成する)
- Pydantic(バリデーションとシリアライズ)

詳しくは[pyproject.toml](https://github.com/Anzu324/Live-Line-Builder/blob/main/pyproject.toml)を参照しよう。