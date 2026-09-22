"""
PySide6のウインドウのテーマに関するコードや定義があります。
PySide6のテーマ用としてqdarkthemeを読み込み、追加のQSSを記述して連結します。
UI側はsetObjectName("An UI Widget")などを用いてデザインの使用を宣言します。
QSSは当ては余るものがあればそのWidgetに適用されます。
"""

import qdarktheme

# 【✨ここで後付け設定】丸ボタンに適用したいテーマカラーのCSSを追記する
# qdarkthemeの変数（--md-sys-color-primary など）を利用すれば、テーマと完璧にシンクロします
# カラーパレットの定義
PALETTE = {
    "primary": {"normal": "#3b82f6", "hover": "#2563eb"},
    "success": {"normal": "#10b981", "hover": "#059669"},
    "danger": {"normal": "#ef4444", "hover": "#dc2626"},
    "warning": {"normal": "#f59e0b", "hover": "#d97706"},
    "info": {"normal": "#06b6d4", "hover": "#0891b2"},
    "neutral": {"normal": "#4b5563", "hover": "#374151"},
    "transparent": {"normal": "rgba(50, 81, 114, 0.3)", "hover": "#355785"},
}

# 自作の追加QSSがまとめられた定数。
# パレット辞書からQSSを組み立て
CUSTOM_QSS = f"""
QPushButton#overlayAddButton {{
    color: #999999;
    font-size: 18px;
    font-weight: bold;
    border: none;
    border-radius: 15px;
    background-color: {PALETTE["transparent"]["normal"]};
}}
QPushButton#overlayAddButton:hover {{
    font-size: 21px;
    color: #ffffff;
    background-color: {PALETTE["transparent"]["hover"]};
}}

"""


def setup_theme() -> None:
    qdarktheme.setup_theme(theme="dark", additional_qss=CUSTOM_QSS)
