from PySide6 import QtWidgets

import exceptions
from sections.base import Section
from sections.password_input import PasswordInput


class AddSection(Section):
    title = "Add an account"

    def __init__(self, vault, user):
        super().__init__(vault, user)

        self.lineedit_app = QtWidgets.QLineEdit()
        self.lineedit_app.setPlaceholderText("Steam, Gmail, Netflix…")
        self.lineedit_username = QtWidgets.QLineEdit()
        self.lineedit_email = QtWidgets.QLineEdit()
        self.password = PasswordInput()

        # opcionales: escondidos hasta que el usuario los pide
        self.checkbox_extra = QtWidgets.QCheckBox("More fields (type, region, rank)")
        self.lineedit_type = QtWidgets.QLineEdit()
        self.lineedit_region = QtWidgets.QLineEdit()
        self.lineedit_rank = QtWidgets.QLineEdit()
        self.form = QtWidgets.QFormLayout()
        self.form.addRow("App *", self.lineedit_app)
        self.form.addRow("Username *", self.lineedit_username)
        self.form.addRow("Email *", self.lineedit_email)
        self.form.addRow("Password *", self.password)
        self.form.addRow("", self.checkbox_extra)
        self.form.addRow("Type", self.lineedit_type)
        self.form.addRow("Region", self.lineedit_region)
        self.form.addRow("Rank", self.lineedit_rank)
        self.checkbox_extra.toggled.connect(self._toggle_extra)
        self._toggle_extra(False)

        self.button_save = QtWidgets.QPushButton("Save account")
        self.button_save.setObjectName("primaryButton")
        self.button_save.clicked.connect(self.save)

        # Guardar se habilita solo cuando están los 4 obligatorios
        for field in (self.lineedit_app, self.lineedit_username, self.lineedit_email):
            field.textChanged.connect(self._update_save_button)
        self.password.textChanged.connect(self._update_save_button)
        self._update_save_button()

        self.main_layout.addLayout(self.form)
        self.main_layout.addWidget(self.button_save)
        self.main_layout.addWidget(self.label_message)
        self.main_layout.addStretch(1)

    def refresh(self) -> None:
        self.clear_message()

    def _toggle_extra(self, visible: bool) -> None:
        for field in (self.lineedit_type, self.lineedit_region, self.lineedit_rank):
            self.form.setRowVisible(field, visible)

    def _required(self) -> list[str]:
        return [
            self.lineedit_app.text(), self.lineedit_username.text(),
            self.lineedit_email.text(), self.password.text(),
        ]

    def _update_save_button(self, *_) -> None:
        self.button_save.setEnabled(all(value.strip() for value in self._required()))

    def save(self) -> None:
        def optional(field):
            return field.text().strip() or None

        try:
            self.vault.add_account(
                self.user,
                self.lineedit_app.text(),
                self.lineedit_username.text(),
                self.lineedit_email.text(),
                self.password.text(),
                account_type=optional(self.lineedit_type),
                region=optional(self.lineedit_region),
                rank=optional(self.lineedit_rank),
            )
        except exceptions.VaultException as e:
            self.show_error(str(e))
            return

        app = self.lineedit_app.text().strip()
        self._clear_form()
        # primero se avisa (las secciones se refrescan) y después el mensaje,
        # para que el refresh no lo borre
        self.accounts_changed.emit()
        self.show_success(f"'{app}' saved.")

    def _clear_form(self) -> None:
        for field in (self.lineedit_app, self.lineedit_username, self.lineedit_email,
                      self.lineedit_type, self.lineedit_region, self.lineedit_rank):
            field.clear()
        self.password.clear()
        self.checkbox_extra.setChecked(False)
