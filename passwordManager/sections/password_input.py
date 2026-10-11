from PySide6 import QtCore, QtWidgets

import core
from sections.base import set_state


class PasswordInput(QtWidgets.QWidget):
    """Campo de contraseña con botón para mostrarla, generador 🎲 con slider
    y medidor de reglas en vivo. Lo usan Add y Change.

    Las reglas son informativas: add_account no las exige, porque las reglas de
    la contraseña de Steam las pone Steam, no esta app.
    """

    textChanged = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        self.lineedit = QtWidgets.QLineEdit()
        self.lineedit.setPlaceholderText("Password")
        self.lineedit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineedit.textChanged.connect(self._update_rules)
        self.lineedit.textChanged.connect(self.textChanged)

        self.button_show = QtWidgets.QPushButton("Show")
        self.button_show.setObjectName("smallButton")
        self.button_show.setCheckable(True)
        self.button_show.toggled.connect(self._toggle_visible)

        self.button_generate = QtWidgets.QPushButton("🎲 Generate")
        self.button_generate.setObjectName("smallButton")
        self.button_generate.clicked.connect(self._generate)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(core.MINIMUM_LENGTH, core.MAXIMUM_LENGTH)
        self.slider.setValue(16)
        self.label_length = QtWidgets.QLabel()
        self.label_length.setMinimumWidth(80)
        self.slider.valueChanged.connect(self._update_length)
        self._update_length(self.slider.value())

        row_field = QtWidgets.QHBoxLayout()
        row_field.addWidget(self.lineedit, 1)
        row_field.addWidget(self.button_show)

        row_generator = QtWidgets.QHBoxLayout()
        row_generator.addWidget(self.button_generate)
        row_generator.addWidget(self.slider, 1)
        row_generator.addWidget(self.label_length)

        # un label por regla, con los textos que define core (no escritos a mano)
        self.rule_labels = {}
        rules_box = QtWidgets.QGridLayout()
        rules_box.setHorizontalSpacing(16)
        for i, rule in enumerate(core.validate_password("")):
            label = QtWidgets.QLabel(rule)
            set_state(label, "muted", rule)
            self.rule_labels[rule] = label
            rules_box.addWidget(label, i // 2, i % 2)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(row_field)
        layout.addLayout(row_generator)
        layout.addLayout(rules_box)

    def text(self) -> str:
        return self.lineedit.text()

    def clear(self) -> None:
        self.lineedit.clear()
        self.button_show.setChecked(False)

    def _toggle_visible(self, visible: bool) -> None:
        mode = QtWidgets.QLineEdit.Normal if visible else QtWidgets.QLineEdit.Password
        self.lineedit.setEchoMode(mode)
        self.button_show.setText("Hide" if visible else "Show")

    def _update_length(self, value: int) -> None:
        self.label_length.setText(f"{value} chars")

    def _generate(self) -> None:
        self.lineedit.setText(core.generate_password(self.slider.value()))
        self.button_show.setChecked(True)

    def _update_rules(self, password: str) -> None:
        if not password:
            for rule, label in self.rule_labels.items():
                set_state(label, "muted", rule)
            return
        for rule, passed in core.validate_password(password).items():
            set_state(self.rule_labels[rule], "success" if passed else "error", rule)
