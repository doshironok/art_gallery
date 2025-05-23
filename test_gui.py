# tests/test_gui.py
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QTabWidget, QDialog, QLineEdit, QMessageBox, QTextEdit, QSpinBox
from gui import ArtGalleryApp
from unittest.mock import patch


@pytest.fixture
def app(qtbot):
    test_app = ArtGalleryApp()
    qtbot.addWidget(test_app)
    return test_app


def print_test_header(test_name):
    print(f"\n\033[1;34m=== {test_name} ===\033[0m")


def print_result(success, message):
    color = "\033[1;32m" if success else "\033[1;31m"
    status = "[OK]" if success else "[FAIL]"
    print(f"{color}{status}\033[0m {message}")


def test_main_window_init(app):
    """Проверка инициализации главного окна"""
    print_test_header("Инициализация главного окна")
    try:
        assert app.windowTitle() == "Art Gallery Management", "Неверный заголовок окна"
        print_result(True, "Заголовок окна корректен")

        assert isinstance(app.tabs, QTabWidget), "Не найден виджет вкладок"
        print_result(True, "Виджет вкладок инициализирован")

        assert app.tabs.count() == 9, f"Найдено {app.tabs.count()} вкладок вместо 9"
        print_result(True, "Количество вкладок соответствует")

        expected_tabs = ["Картины", "Художники", "Выставки", "Продажа",
                         "Перемещения", "Посетители", "Отзывы", "Реставрация", "Документы"]
        for i, title in enumerate(expected_tabs):
            assert app.tabs.tabText(i) == title, f"Вкладка '{app.tabs.tabText(i)}' не соответствует ожидаемой"
        print_result(True, "Названия вкладок корректны")

    except AssertionError as e:
        print_result(False, str(e))
        raise


def test_artwork_tab_buttons(app):
    """Проверка кнопок вкладки 'Картины'"""
    print_test_header("Проверка кнопок вкладки 'Картины'")
    try:
        artwork_tab = app.tabs.widget(0)
        buttons = artwork_tab.findChildren(QPushButton)

        assert len(buttons) == 4, f"Найдено {len(buttons)} кнопок вместо 4"
        print_result(True, "Количество кнопок соответствует")

        expected_buttons = [
            "Добавить картину",
            "Показать все картины",
            "Обновить статус картины",
            "Обновить стоимость картины"
        ]
        for btn in buttons:
            assert btn.text() in expected_buttons, f"Неожиданная кнопка: {btn.text()}"
        print_result(True, "Все кнопки соответствуют ожидаемым")

    except AssertionError as e:
        print_result(False, str(e))
        raise

def test_show_artists(app, qtbot):
    """Тест отображения списка художников"""
    print_test_header("Тест отображения художников")
    try:
        artists_tab = app.tabs.widget(1)
        refresh_btn = artists_tab.findChild(QPushButton)
        text_edit = artists_tab.findChild(QTextEdit)

        test_data = [(1, "Van Gogh", "France"), (2, "Picasso", "Spain")]
        with patch('services.get_artists', return_value=test_data):
            qtbot.mouseClick(refresh_btn, Qt.LeftButton)

            content = text_edit.toPlainText()
            assert "Van Gogh" in content, "Данные Van Gogh не найдены"
            assert "Picasso" in content, "Данные Picasso не найдены"
            print_result(True, "Данные художников отображены корректно")

    except AssertionError as e:
        print_result(False, str(e))
        raise
