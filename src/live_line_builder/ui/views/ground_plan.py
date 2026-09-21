from PySide6.QtWidgets import QGridLayout, QLabel, QWidget


class GroundPlanView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image = QLabel(self)
        self.image.setText("何かあるはず")
        layout = QGridLayout()
        layout.addWidget(self.image)
        self.setLayout(layout)
        self.setMinimumSize(200,200)
