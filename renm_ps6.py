# -*- coding: utf-8 -*-

# ┌──────────────────────────────────────────────────────────
# │ Name     : renm_ps6.py
# │ Library  : PySide6
# │ Function : batch renaming tool for files and directories
# └──────────────────────────────────────────────────────────

import os
import re
import sys
import shutil
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

class RenmWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        icon_path = resource_path("renm_ps6.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("batch renaming tool for files and directories [renm_ps6]")
        self.setFixedSize(780, 600)

        self.current_backup_dir = ""
        self._build_ui()
        self.show_help_message()

    def _build_ui(self) -> None:
        root = QWidget(self)
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        panel = QWidget()
        panel.setObjectName("panel")
        root_layout.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Frame 1
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        layout.addLayout(row1)

        label_width = 110
        self.exec_label = QLabel("Exec directory")
        self.exec_label.setFixedWidth(label_width)
        row1.addWidget(self.exec_label)

        self.exec_dir_entry = QLineEdit()
        self.exec_dir_entry.setReadOnly(True)
        row1.addWidget(self.exec_dir_entry, 1)

        self.select_button = self._make_button("Select")
        self.select_button.setObjectName("subButton")
        self.select_button.clicked.connect(self.select_click)
        row1.addWidget(self.select_button)

        # Frame 2
        row2 = QGridLayout()
        row2.setHorizontalSpacing(8)
        row2.setVerticalSpacing(8)
        layout.addLayout(row2)

        label2 = QLabel("Before word")
        label2.setFixedWidth(label_width)
        row2.addWidget(label2, 0, 0)

        label3 = QLabel("After  word")
        label3.setFixedWidth(label_width)
        row2.addWidget(label3, 1, 0)

        self.before_wd_entry = QLineEdit()
        row2.addWidget(self.before_wd_entry, 0, 1)

        self.after_wd_entry = QLineEdit()
        row2.addWidget(self.after_wd_entry, 1, 1)

        # Frame 3
        row3 = QHBoxLayout()
        row3.setSpacing(8)
        layout.addLayout(row3)
        # 1. 初期状態のテキストに絵文字を付ける
        self.rec_chk = QCheckBox("✅ Recursive processing")
        self.rec_chk.setChecked(True)
        # 2. チェック状態が変わった時に絵文字を切り替える設定
        self.rec_chk.stateChanged.connect(self._update_checkbox_icon)
        # レイアウトへの追加
        row3.addWidget(self.rec_chk)
        row3.addStretch(1)

        # Frame 4
        row4 = QGridLayout()
        row4.setHorizontalSpacing(8)
        row4.setVerticalSpacing(8)
        layout.addLayout(row4, 1)

        msg_label = QLabel("Processing message")
        msg_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        row4.addWidget(msg_label, 0, 0)

        self.msg = QPlainTextEdit()
        self.msg.setReadOnly(True)
        self.msg.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        row4.addWidget(self.msg, 0, 1)

        # Frame 5
        row5 = QHBoxLayout()
        row5.setSpacing(8)
        layout.addLayout(row5)

        self.scan_button = self._make_button("Scan")
        self.scan_button.setObjectName("scanButton")
        self.scan_button.clicked.connect(self.scan_click)
        row5.insertWidget(0, self.scan_button)

        self.move_button = self._make_button("Rename")
        self.move_button.setObjectName("executeButton")
        self.move_button.clicked.connect(self.move_click)
        row5.addWidget(self.move_button)

        self.undo_button = self._make_button("Undo")
        self.undo_button.setObjectName("undoButton")
        self.undo_button.clicked.connect(self.undo_click)
        row5.addWidget(self.undo_button)

        self.clear_button = self._make_button("Clear")
        self.clear_button.setObjectName("subButton")
        self.clear_button.clicked.connect(self.clear_click)
        row5.addWidget(self.clear_button)

        self.help_button = self._make_button("Help")
        self.help_button.setObjectName("subButton")
        self.help_button.clicked.connect(self.help_click)
        row5.addWidget(self.help_button)

        row5.addStretch(1)

        self.exit_button = self._make_button("Exit")
        self.exit_button.setObjectName("exitButton")
        self.exit_button.clicked.connect(self.exit_click)
        row5.addWidget(self.exit_button)

        default_font = QFont()
        default_font.setPointSize(11)
        self.setFont(default_font)

        self.setStyleSheet(
            """
            QWidget {
                background-color: lightblue;
                color: black;
            }
            QWidget#panel {
                border: 1px solid #6f8fa8;
            }
            QLineEdit {
                background: white;
                padding: 4px 6px;
                border: 1px solid #7d9db3;
            }
            QPlainTextEdit {
                background: #333333;
                color: deepskyblue;
                border: 1px solid #7d9db3;
                padding: 6px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 11pt;
            }

            QPushButton {
                min-width: 82px;
                min-height: 28px;
                border: 1px solid #666;
                border-radius: 3px;
                font-weight: 600;
            }
            
            /* Scan（シアン） */
            QPushButton#scanButton {
                color: white;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #CCFFFF,
                    stop:1 #00A6D6
                );
            }
            
            /* Execute（Rename / Delete）（赤） */
            QPushButton#executeButton {
                color: white;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFCCFF,
                    stop:1 #FF0066
                );
            }
            
            /* Undo（黄色） */
            QPushButton#undoButton {
                color: #222;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFCC,
                    stop:1 #FBC02D
                );
            }
            
            /* Exit（黒） */
            QPushButton#exitButton {
                color: white;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #CCCCCC,
                    stop:1 #000000
                );
            }
            
            /* その他（灰色） */
            QPushButton#subButton {
                color: #222;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #CCCCCC,
                    stop:1 #5F5F5F
                );
            }
            
            QPushButton:hover {
                border: 1px solid #333;
            }
            
            QPushButton:pressed {
                padding-top: 1px;
                padding-left: 1px;
            }


            QPushButton:hover {
                border: 1px solid #404040;
            }
            QPushButton:pressed {
                padding-top: 1px;
                padding-left: 1px;
            }
            QCheckBox {
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 0px;  /* 元のチェックボックスを消す */
                border: none;
            }
            QCheckBox {
                spacing: 0px; /* 絵文字と文字の間隔はテキスト内で調整 */
            }

            """
        )

    def _update_checkbox_icon(self, state):
        base_text = "Recursive processing"
        if state == 2: # Qt.CheckState.Checked
            self.rec_chk.setText(f"✅ {base_text}")
        else:
            self.rec_chk.setText(f"🟩{base_text}")

    def _make_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setFocusPolicy(Qt.NoFocus)
        return button

    def append_message(self, text: str) -> None:
        self.msg.moveCursor(QTextCursor.End)
        self.msg.insertPlainText(text)
        self.msg.moveCursor(QTextCursor.End)

    def clear_message(self) -> None:
        self.msg.setPlainText("")

    def show_help_message(self) -> None:
        self.clear_message()
        self.append_message("使用方法は [Help] ボタンで表示されます。")

    def show_error_lines(self, lines: list[str]) -> None:
        self.clear_message()
        for line in lines:
            self.append_message(line + "\n")

    def scan_click(self) -> None:
        self.clear_message()
        selected_dir = self.exec_dir_entry.text().strip()
    
        if not selected_dir:
            self.append_message("'Exec directory' を指定して下さい。\n")
            return
    
        if not os.path.isdir(selected_dir):
            self.append_message("指定されたディレクトリが存在しません。\n")
            return
    
        try:
            entries = sorted(os.listdir(selected_dir))
            for name in entries:
                self.append_message(name + "\n")
        except Exception as exc:
            self.append_message(f"フォルダ内容の取得に失敗しました: {exc}\n")

    def select_click(self) -> None:
        ini_dir = str(Path.home())
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "dir choose",
            ini_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        self.clear_message()

        if not selected_dir:
            self.append_message("フォルダが選択されませんでした。")
            return

        try:
            entries = sorted(os.listdir(selected_dir))
            for name in entries:
                self.append_message(name + "\n")
        except Exception as exc:
            self.append_message(f"フォルダ内容の取得に失敗しました: {exc}\n")

        backup_dir = selected_dir + ".bk"
        try:
            if os.path.isdir(backup_dir):
                shutil.rmtree(backup_dir)
            shutil.copytree(selected_dir, backup_dir)
            self.current_backup_dir = backup_dir
        except Exception as exc:
            self.append_message(f"バックアップ作成に失敗しました: {exc}\n")

        self.exec_dir_entry.setText(selected_dir)

    def clear_click(self) -> None:
        self.exec_dir_entry.clear()
        self.before_wd_entry.clear()
        self.after_wd_entry.clear()
        self.show_help_message()

    def undo_click(self) -> None:
        self.before_wd_entry.clear()
        self.after_wd_entry.clear()
        self.clear_message()

        exec_dir = self.exec_dir_entry.text().strip()
        if not exec_dir:
            self.append_message("'Exec directory' を指定して下さい。\n")
            return

        undo_dir = exec_dir + ".bk"
        if not os.path.isdir(undo_dir):
            self.append_message("バックアップされていないため、リカバリ出来ません。")
            return

        try:
            if os.path.isdir(exec_dir):
                shutil.rmtree(exec_dir)
            os.rename(undo_dir, exec_dir)
            self.append_message("リカバリ完了しました。\n")
            for name in sorted(os.listdir(exec_dir)):
                self.append_message(name + "\n")
        except Exception as exc:
            self.append_message(f"リカバリに失敗しました: {exc}\n")

    def help_click(self) -> None:
        self.clear_message()
        lines = [
            "name : renm",
            "function : batch renaming tool for files and directories",
            "usage :",
            "  Exec directory : 処理対象ディレクトリを指定。",
            "  Before word    : 変換前ファイル[ディレクトリ]名に含まれる文字列を指定。",
            "  After  word    : 変換後ファイル[ディレクトリ]名に含まれる文字列を指定。",
            "  ✅             : 再帰変換を指定。",
        ]
        self.append_message("\n".join(lines))

    def move_click(self) -> None:
        self.clear_message()

        dir_wd = self.exec_dir_entry.text().strip()
        bfr_wd = self.before_wd_entry.text()
        aft_wd = self.after_wd_entry.text()

        errors = []
        if not dir_wd:
            errors.append("'Exec directory' を指定して下さい。")
        if not bfr_wd:
            errors.append("'Before word' を指定して下さい。")
        if aft_wd == "":
            errors.append("'After word' を指定して下さい。")

        if errors:
            self.show_error_lines(errors)
            return

        if not os.path.isdir(dir_wd):
            self.show_error_lines(["指定されたディレクトリが存在しません。"])
            return

        try:
            self.rename_in_directory(Path(dir_wd), bfr_wd, aft_wd, "")
        except re.error as exc:
            self.append_message(f"正規表現エラー: {exc}\n")
        except FileExistsError as exc:
            self.append_message(f"同名ファイル/フォルダが存在するため変更できません: {exc}\n")
        except Exception as exc:
            self.append_message(f"処理中にエラーが発生しました: {exc}\n")

    def rename_in_directory(self, dir_path: Path, before_word: str, after_word: str, indent: str) -> None:
        next_indent = indent + "    "
        self.append_message(f"{indent} => {dir_path}\n\n")

        items = [p for p in dir_path.iterdir() if not p.name.startswith(".")]
        items.sort(key=lambda p: p.name)

        for item in items:
            # ディレクトリは先に中へ入ってから、最後に自分自身をリネーム
            if item.is_dir() and self.rec_chk.isChecked():
                self.rename_in_directory(item, before_word, after_word, next_indent)

            original_path = item
            stem, suffix = os.path.splitext(item.name)

            if suffix:
                new_name = re.sub(before_word, after_word, stem) + suffix
            else:
                new_name = re.sub(before_word, after_word, item.name)

            new_path = item.with_name(new_name)

            self.append_message(f"{next_indent}   {original_path}\n")
            self.append_message(f"{next_indent}-> {new_path}\n\n")

            if original_path == new_path:
                continue

            if new_path.exists():
                raise FileExistsError(str(new_path))

            original_path.rename(new_path)
            item = new_path

        self.append_message(f"{indent} <= {dir_path}\n")

    def exit_click(self) -> None:
        exec_dir = self.exec_dir_entry.text().strip()
        undo_dir = exec_dir + ".bk" if exec_dir else ""
        try:
            if undo_dir and os.path.isdir(undo_dir):
                shutil.rmtree(undo_dir)
        except Exception:
            pass
        QApplication.quit()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.exit_click()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("renm_ps6.ico")))
    window = RenmWindow()
    window.show()
    sys.exit(app.exec())
