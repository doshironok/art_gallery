from PyQt5.QtWidgets import (QWidget, QLabel, QTabWidget, QTextEdit,
                             QComboBox, QSpinBox, QDateEdit, QFormLayout, QLineEdit,
                             QDoubleSpinBox, QMessageBox, QDialog, QVBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QSizePolicy, QHBoxLayout)
from PyQt5.QtCore import QDate
import services

class ArtGalleryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Art Gallery Management")
        self.setGeometry(100, 100, 1000, 800)

        self.tabs = QTabWidget()
        self.init_tabs()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def init_tabs(self):
        self.tabs.addTab(self.create_artwork_tab(), "Картины")
        self.tabs.addTab(self.create_artist_tab(), "Художники")
        self.tabs.addTab(self.create_exhibition_tab(), "Выставки")
        self.tabs.addTab(self.create_sale_tab(), "Продажа")
        self.tabs.addTab(self.create_movement_tab(), "Перемещения")
        self.tabs.addTab(self.create_visitor_tab(), "Посетители")
        self.tabs.addTab(self.create_review_tab(), "Отзывы")
        self.tabs.addTab(self.create_restoration_tab(), "Реставрация")
        self.tabs.addTab(self.create_document_tab(), "Документы")

    def create_artist_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        refresh_button = QPushButton("Показать художников")
        refresh_button.clicked.connect(self.show_artists)

        self.artist_list = QTextEdit()
        self.artist_list.setReadOnly(True)

        layout.addWidget(refresh_button)
        layout.addWidget(self.artist_list)
        widget.setLayout(layout)
        return widget

    def show_artists(self):
        try:
            artists = services.get_artists()
            self.artist_list.clear()
            for artist in artists:
                self.artist_list.append(str(artist))
        except Exception as e:
            self.artist_list.setText(f"Ошибка: {e}")

    def create_artwork_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)  # Главный вертикальный layout

        # Создаем горизонтальный контейнер для кнопок
        button_row = QHBoxLayout()

        # Создаем кнопки с фиксированной высотой
        buttons = [
            QPushButton("Добавить картину"),
            QPushButton("Показать все картины"),
            QPushButton("Обновить статус картины"),
            QPushButton("Обновить стоимость картины")
        ]

        # Настраиваем кнопки
        for btn in buttons:
            btn.setFixedHeight(120)  # Фиксированная высота
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Растягиваем по горизонтали
            button_row.addWidget(btn)

        # Добавляем "распорку" чтобы прижать кнопки к низу
        main_layout.addStretch()
        main_layout.addLayout(button_row)

        # Подключаем сигналы
        buttons[0].clicked.connect(self.open_add_artwork_dialog)
        buttons[1].clicked.connect(self.show_all_artworks_dialog)
        buttons[2].clicked.connect(self.open_update_status_dialog)
        buttons[3].clicked.connect(self.open_update_price_dialog)

        return widget

    def open_add_artwork_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить картину")
        form_layout = QFormLayout()

        title_input = QLineEdit()
        year_input = QSpinBox()
        year_input.setRange(1000, 2100)
        technique_input = QLineEdit()
        height_input = QLineEdit()
        width_input = QLineEdit()
        description_input = QTextEdit()
        genre_input = QLineEdit()
        price_input = QSpinBox()
        price_input.setRange(0, 999999)
        artist_id_input = QSpinBox()
        artist_id_input.setMaximum(100000)
        provenance_input = QTextEdit()

        submit_button = QPushButton("Добавить")
        submit_button.clicked.connect(lambda: self.add_artwork(dialog, title_input, year_input, technique_input,
                                                                height_input, width_input, description_input,
                                                                genre_input, artist_id_input, provenance_input, price_input))

        form_layout.addRow("Название:", title_input)
        form_layout.addRow("Год создания:", year_input)
        form_layout.addRow("Техника:", technique_input)
        form_layout.addRow("Высота (см):", height_input)
        form_layout.addRow("Ширина (см):", width_input)
        form_layout.addRow("Описание:", description_input)
        form_layout.addRow("Жанр:", genre_input)
        form_layout.addRow("Цена:", price_input)
        form_layout.addRow("ID Художника:", artist_id_input)
        form_layout.addRow("Запись провенанса:", provenance_input)
        form_layout.addRow(submit_button)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def add_artwork(self, dialog, title_input, year_input, technique_input,
                    height_input, width_input, description_input,
                    genre_input, artist_id_input, provenance_input, price_input):
        try:
            artwork_id = services.acquire_artwork(
                title=title_input.text(),
                year_created=year_input.value(),
                technique=technique_input.text(),
                dimensions=f"{height_input.text()}x{width_input.text()}",
                description=description_input.toPlainText(),
                genre=genre_input.text(),
                artist_id=artist_id_input.value(),
                provenance_entry=provenance_input.toPlainText(),
                price=price_input.value()
            )
            print(f"Картина добавлена с ID {artwork_id}")
            dialog.accept()
        except Exception as e:
            print(f"Ошибка: {e}")

    def show_all_artworks_dialog(self):
        try:
            artworks = services.get_artworks()

            dialog = QDialog(self)
            dialog.setWindowTitle("Список картин")
            dialog.setGeometry(200, 200, 1000, 400)
            layout = QVBoxLayout()

            table = QTableWidget()
            table.setRowCount(len(artworks))
            table.setColumnCount(len(artworks[0]) if artworks else 0)
            table.setHorizontalHeaderLabels(["ID", "Название", "Год", "Техника", "Размеры", "Описание",
                                             "Жанр", "Локация", "Статус", "ID Художника", "Цена"])

            for row_idx, row_data in enumerate(artworks):
                for col_idx, item in enumerate(row_data):
                    table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

            layout.addWidget(table)
            dialog.setLayout(layout)
            dialog.exec_()

        except Exception as e:
            print(f"Ошибка: {e}")

    def open_update_status_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Обновить статус картины")
        form_layout = QFormLayout()

        artwork_id_input = QLineEdit()
        status_selector = QComboBox()
        status_selector.addItems(["Sold", "Acquired", "Restored"])

        submit_button = QPushButton("Обновить статус")
        submit_button.clicked.connect(lambda: self.update_artwork_status(dialog, artwork_id_input, status_selector))

        form_layout.addRow("ID картины:", artwork_id_input)
        form_layout.addRow("Новый статус:", status_selector)
        form_layout.addRow(submit_button)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def update_artwork_status(self, dialog, artwork_id_input, status_selector):
        try:
            artwork_id = int(artwork_id_input.text())
            new_status = status_selector.currentText()
            services.update_artwork_status(artwork_id, new_status)
            print(f"Статус картины с ID {artwork_id} обновлен на '{new_status}'")
            dialog.accept()
        except Exception as e:
            print(f"Ошибка: {e}")

    def open_update_price_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Обновить стоимость картины")
        form_layout = QFormLayout()

        artwork_id_input = QLineEdit()
        price_input = QDoubleSpinBox()
        price_input.setRange(0, 1_000_000)
        price_input.setDecimals(2)

        submit_button = QPushButton("Обновить стоимость")
        submit_button.clicked.connect(lambda: self.update_artwork_price(dialog, artwork_id_input, price_input))

        form_layout.addRow("ID картины:", artwork_id_input)
        form_layout.addRow("Новая стоимость:", price_input)
        form_layout.addRow(submit_button)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def update_artwork_price(self, dialog, artwork_id_input, price_input):
        try:
            artwork_id = int(artwork_id_input.text())
            new_price = price_input.value()
            services.update_artwork_price(artwork_id, new_price)
            print(f"Цена картины с ID {artwork_id} обновлена на {new_price}")
            dialog.accept()
        except Exception as e:
            print(f"Ошибка: {e}")

    def create_exhibition_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        refresh_button = QPushButton("Показать все выставки")
        refresh_button.clicked.connect(self.show_exhibitions)

        self.exhibition_list = QTextEdit()
        self.exhibition_list.setReadOnly(True)

        create_button = QPushButton("Создать выставку")
        create_button.clicked.connect(self.open_create_exhibition_dialog)

        add_artwork_button = QPushButton("Добавить картину на выставку")
        add_artwork_button.clicked.connect(self.open_add_artwork_to_exhibition_dialog)

        layout.addWidget(refresh_button)
        layout.addWidget(self.exhibition_list)
        layout.addWidget(create_button)
        layout.addWidget(add_artwork_button)

        widget.setLayout(layout)
        return widget

    def show_exhibitions(self):
        try:
            exhibitions = services.get_exhibitions()
            self.exhibition_list.clear()
            for exhibition in exhibitions:
                self.exhibition_list.append(
                    f"ID: {exhibition[0]}, Название: {exhibition[1]}, Тема: {exhibition[2]}, "
                    f"Дата начала: {exhibition[3]}, Дата окончания: {exhibition[4]}"
                )
        except Exception as e:
            self.exhibition_list.setText(f"Ошибка: {e}")

    def open_create_exhibition_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Создать выставку")
        form_layout = QFormLayout()

        title_input = QLineEdit()
        theme_input = QLineEdit()
        start_date_input = QDateEdit()
        start_date_input.setCalendarPopup(True)
        start_date_input.setDate(QDate.currentDate())

        end_date_input = QDateEdit()
        end_date_input.setCalendarPopup(True)
        end_date_input.setDate(QDate.currentDate())

        submit_button = QPushButton("Создать выставку")
        submit_button.clicked.connect(lambda: self.create_exhibition(
            dialog, title_input, theme_input, start_date_input, end_date_input
        ))

        form_layout.addRow("Название:", title_input)
        form_layout.addRow("Тема:", theme_input)
        form_layout.addRow("Дата начала:", start_date_input)
        form_layout.addRow("Дата окончания:", end_date_input)
        form_layout.addRow(submit_button)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def create_exhibition(self, dialog, title_input, theme_input, start_date_input, end_date_input):
        try:
            title = title_input.text()
            theme = theme_input.text()
            start_date = start_date_input.date().toString("yyyy-MM-dd")
            end_date = end_date_input.date().toString("yyyy-MM-dd")

            exhibition_id = services.create_exhibition(title, theme, start_date, end_date)
            print(f"Выставка создана с ID {exhibition_id}")
            dialog.accept()
        except Exception as e:
            print(f"Ошибка: {e}")

    def open_add_artwork_to_exhibition_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить картину на выставку")
        form_layout = QFormLayout()

        exhibition_id_input = QLineEdit()
        artwork_id_input = QLineEdit()

        submit_button = QPushButton("Добавить картину")
        submit_button.clicked.connect(lambda: self.add_artwork_to_exhibition(
            dialog, exhibition_id_input, artwork_id_input
        ))

        form_layout.addRow("ID Выставки:", exhibition_id_input)
        form_layout.addRow("ID Картины:", artwork_id_input)
        form_layout.addRow(submit_button)

        dialog.setLayout(form_layout)
        dialog.exec_()

    def add_artwork_to_exhibition(self, dialog, exhibition_id_input, artwork_id_input):
        try:
            exhibition_id = int(exhibition_id_input.text())
            artwork_id = int(artwork_id_input.text())

            services.add_artwork_to_exhibition(exhibition_id, artwork_id)
            print(f"Картина с ID {artwork_id} добавлена на выставку с ID {exhibition_id}")
            dialog.accept()
        except Exception as e:
            print(f"Ошибка: {e}")

    def create_sale_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)  # Главный вертикальный layout

        # Создаем горизонтальный контейнер для кнопок
        button_row = QHBoxLayout()

        # Создаем кнопки с фиксированной высотой
        rent_button = QPushButton("Оформить аренду картины")
        sell_button = QPushButton("Продать картину")

        # Настраиваем кнопки
        for btn in [rent_button, sell_button]:
            btn.setFixedHeight(120)  # Фиксированная высота
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Растягиваем по горизонтали
            button_row.addWidget(btn)

        # Добавляем "распорку" чтобы прижать кнопки к низу
        main_layout.addStretch()
        main_layout.addLayout(button_row)

        # Подключаем сигналы
        rent_button.clicked.connect(self.open_rent_window)
        sell_button.clicked.connect(self.open_sell_window)

        return widget

    def open_sell_window(self):
        sell_window = QDialog()
        sell_window.setWindowTitle("Продать картину")

        layout = QFormLayout()

        self.sell_artwork_id_input = QLineEdit()
        self.sell_buyer_name_input = QLineEdit()
        self.sell_sale_price_input = QLineEdit()
        self.sell_sale_price_input.setPlaceholderText("Введите цену картины")

        sell_button = QPushButton("Продать картину")
        sell_button.clicked.connect(self.sell_artwork_button_clicked)

        layout.addRow("ID картины:", self.sell_artwork_id_input)
        layout.addRow("Имя покупателя:", self.sell_buyer_name_input)
        layout.addRow("Цена:", self.sell_sale_price_input)
        layout.addRow(sell_button)

        sell_window.setLayout(layout)
        sell_window.exec_()

    def sell_artwork_button_clicked(self):
        artwork_id = int(self.sell_artwork_id_input.text())
        buyer_name = self.sell_buyer_name_input.text()
        sale_price_text = self.sell_sale_price_input.text()

        if not buyer_name or not sale_price_text:
            self.show_error_message("Ошибка", "Все поля должны быть заполнены.")
            return
        try:
            sale_price = float(sale_price_text)
            if sale_price <= 0:
                self.show_error_message("Ошибка", "Цена должна быть больше нуля.")
                return
        except ValueError:
            self.show_error_message("Ошибка", "Введите корректную цену.")
            return

        try:
            services.sell_artwork(artwork_id, buyer_name, sale_price)
            self.show_info_message("Успех", f"Картина с ID {artwork_id} успешно продана.")
        except Exception as e:
            self.show_error_message("Ошибка", str(e))

    def show_error_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def show_info_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def open_rent_window(self):
        rent_window = QDialog()
        rent_window.setWindowTitle("Оформить аренду картины")

        layout = QFormLayout()

        self.rent_artwork_id_input = QLineEdit()
        self.rent_renter_name_input = QLineEdit()
        self.rent_start_date_input = QDateEdit()
        self.rent_start_date_input.setCalendarPopup(True)
        self.rent_start_date_input.setDate(QDate.currentDate())

        self.rent_end_date_input = QDateEdit()
        self.rent_end_date_input.setCalendarPopup(True)
        self.rent_end_date_input.setDate(QDate.currentDate())

        self.rent_fee_input = QLineEdit()
        self.rent_fee_input.setPlaceholderText("Введите стоимость аренды")

        rent_button = QPushButton("Оформить аренду")
        rent_button.clicked.connect(self.rent_artwork_button_clicked)

        layout.addRow("ID картины:", self.rent_artwork_id_input)
        layout.addRow("Имя арендатора:", self.rent_renter_name_input)
        layout.addRow("Дата начала аренды:", self.rent_start_date_input)
        layout.addRow("Дата окончания аренды:", self.rent_end_date_input)
        layout.addRow("Стоимость аренды:", self.rent_fee_input)
        layout.addRow(rent_button)

        rent_window.setLayout(layout)
        rent_window.exec_()

    def rent_artwork_button_clicked(self):
        artwork_id = int(self.rent_artwork_id_input.text())
        renter_name = self.rent_renter_name_input.text()
        start_date = self.rent_start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.rent_end_date_input.date().toString("yyyy-MM-dd")
        rental_fee_text = self.rent_fee_input.text()

        if not renter_name or not start_date or not end_date or not rental_fee_text:
            self.show_error_message("Ошибка", "Все поля должны быть заполнены.")
            return
        try:
            rental_fee = float(rental_fee_text)
            if rental_fee <= 0:
                self.show_error_message("Ошибка", "Стоимость аренды должна быть положительным числом.")
                return
        except ValueError:
            self.show_error_message("Ошибка", "Введите корректную стоимость аренды.")
            return

        try:
            services.rent_artwork(artwork_id, renter_name, start_date, end_date, rental_fee)
            self.show_info_message("Успех", f"Картина с ID {artwork_id} успешно арендована.")
        except Exception as e:
            self.show_error_message("Ошибка", str(e))

    def create_movement_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)  # Главный вертикальный layout

        # Создаем кнопку с настройками
        record_movement_button = QPushButton("Записать перемещение картины")
        record_movement_button.setFixedHeight(120)  # Фиксированная высота
        record_movement_button.setSizePolicy(
            QSizePolicy.Expanding,  # Растягиваем по горизонтали
            QSizePolicy.Fixed  # Фиксированная вертикаль
        )

        # Добавляем распорку и кнопку
        main_layout.addStretch()  # Занимает все свободное пространство сверху
        main_layout.addWidget(record_movement_button)

        # Подключаем сигнал
        record_movement_button.clicked.connect(self.open_movement_window)

        return widget

    def open_movement_window(self):
        movement_window = QDialog()
        movement_window.setWindowTitle("Записать перемещение картины")

        layout = QFormLayout()

        self.movement_artwork_id_input = QLineEdit()
        self.movement_from_location_input = QLineEdit()
        self.movement_to_location_input = QLineEdit()
        self.movement_purpose_input = QLineEdit()
        self.movement_responsible_person_input = QLineEdit()

        record_button = QPushButton("Записать перемещение")
        record_button.clicked.connect(self.record_movement_button_clicked)

        layout.addRow("ID картины:", self.movement_artwork_id_input)
        layout.addRow("Место отправления:", self.movement_from_location_input)
        layout.addRow("Место назначения:", self.movement_to_location_input)
        layout.addRow("Цель перемещения:", self.movement_purpose_input)
        layout.addRow("Ответственное лицо:", self.movement_responsible_person_input)
        layout.addRow(record_button)

        movement_window.setLayout(layout)
        movement_window.exec_()

    def record_movement_button_clicked(self):
        artwork_id = int(self.movement_artwork_id_input.text())
        from_location = self.movement_from_location_input.text()
        to_location = self.movement_to_location_input.text()
        purpose = self.movement_purpose_input.text()
        responsible_person = self.movement_responsible_person_input.text()

        if not from_location or not to_location or not purpose or not responsible_person:
            self.show_error_message("Ошибка", "Все поля должны быть заполнены.")
            return

        try:
            services.record_movement(artwork_id, from_location, to_location, purpose, responsible_person)
            self.show_info_message("Успех", f"Перемещение картины с ID {artwork_id} записано.")
        except Exception as e:
            self.show_error_message("Ошибка", str(e))

    def create_visitor_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)

        button_row = QHBoxLayout()
        buttons = [
            QPushButton("Регистрация посетителя"),
            QPushButton("Показать всех посетителей")
        ]

        for btn in buttons:
            btn.setFixedHeight(120)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button_row.addWidget(btn)

        main_layout.addStretch()
        main_layout.addLayout(button_row)

        buttons[0].clicked.connect(self.open_register_window)
        buttons[1].clicked.connect(self.show_visitors_list)

        return widget

    def create_review_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)

        button_row = QHBoxLayout()
        buttons = [
            QPushButton("Добавить отзыв от посетителя"),
            QPushButton("Добавить отзыв от СМИ"),
            QPushButton("Просмотр отзывов посетителей"),
            QPushButton("Просмотр отзывов СМИ")
        ]

        for btn in buttons:
            btn.setFixedHeight(120)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button_row.addWidget(btn)

        main_layout.addStretch()
        main_layout.addLayout(button_row)

        buttons[0].clicked.connect(self.add_visitor_review)
        buttons[1].clicked.connect(self.add_press_review)
        buttons[2].clicked.connect(self.show_visitor_reviews)
        buttons[3].clicked.connect(self.show_press_reviews)

        return widget

    def create_restoration_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)

        button_row = QHBoxLayout()
        buttons = [
            QPushButton("Начать реставрацию"),
            QPushButton("Добавить материал для реставрации")
        ]

        for btn in buttons:
            btn.setFixedHeight(120)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button_row.addWidget(btn)

        main_layout.addStretch()
        main_layout.addLayout(button_row)

        buttons[0].clicked.connect(self.record_restoration_state)
        buttons[1].clicked.connect(self.add_restoration_material)

        return widget

    def create_document_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout(widget)

        button_row = QHBoxLayout()
        buttons = [
            QPushButton("Добавить документ о подлинности"),
            QPushButton("Добавить новый материал")
        ]

        for btn in buttons:
            btn.setFixedHeight(120)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button_row.addWidget(btn)

        main_layout.addStretch()
        main_layout.addLayout(button_row)

        buttons[0].clicked.connect(self.open_add_document_dialog)
        buttons[1].clicked.connect(self.open_add_material_dialog)

        return widget

    def open_register_window(self):
        register_window = QDialog()
        register_window.setWindowTitle("Регистрация посетителя")

        layout = QFormLayout()

        self.register_name_input = QLineEdit()
        self.register_email_input = QLineEdit()
        self.register_phone_input = QLineEdit()

        register_button = QPushButton("Зарегистрировать")
        register_button.clicked.connect(self.register_visitor_button_clicked)

        layout.addRow("Имя посетителя:", self.register_name_input)
        layout.addRow("Email:", self.register_email_input)
        layout.addRow("Телефон:", self.register_phone_input)
        layout.addRow(register_button)

        register_window.setLayout(layout)
        register_window.exec_()

    def register_visitor_button_clicked(self):
        name = self.register_name_input.text()
        email = self.register_email_input.text()
        phone = self.register_phone_input.text()

        if not name or not email or not phone:
            self.show_error_message("Ошибка", "Все поля должны быть заполнены.")
            return

        try:
            visitor_id = services.register_visitor(name, email, phone)
            self.show_info_message("Успех", f"Посетитель с ID {visitor_id} зарегистрирован.")
        except Exception as e:
            self.show_error_message("Ошибка", str(e))

    def show_visitors_list(self):
        try:
            visitors = services.get_visitors()
            if not visitors:
                self.show_info_message("Информация", "Нет зарегистрированных посетителей.")
                return

            visitors_list_window = QDialog()
            visitors_list_window.setWindowTitle("Список посетителей")
            layout = QVBoxLayout()

            title_label = QLabel("Список всех зарегистрированных посетителей:")
            layout.addWidget(title_label)

            for visitor in visitors:
                visitor_label = QLabel(
                    f"ID: {visitor[0]}, Имя: {visitor[1]}, Email: {visitor[2]}, Телефон: {visitor[3]}")
                layout.addWidget(visitor_label)

            visitors_list_window.setLayout(layout)
            visitors_list_window.exec_()

        except Exception as e:
            self.show_error_message("Ошибка", str(e))

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_info_message(self, title, message):
        QMessageBox.information(self, title, message)

    def add_visitor_review(self):
        review_window = QDialog()
        review_window.setWindowTitle("Добавить отзыв от посетителя")

        layout = QFormLayout()

        self.exhibition_id_input = QLineEdit()
        self.review_text_input = QLineEdit()
        self.reviewer_name_input = QLineEdit()

        add_review_button = QPushButton("Добавить отзыв")
        add_review_button.clicked.connect(self.submit_visitor_review)

        layout.addRow("ID выставки:", self.exhibition_id_input)
        layout.addRow("Текст отзыва:", self.review_text_input)
        layout.addRow("Имя посетителя:", self.reviewer_name_input)
        layout.addRow(add_review_button)

        review_window.setLayout(layout)
        review_window.exec_()

    def add_press_review(self):
        review_window = QDialog()
        review_window.setWindowTitle("Добавить отзыв от СМИ")

        layout = QFormLayout()

        self.exhibition_id_input_press = QLineEdit()
        self.review_text_input_press = QLineEdit()
        self.publication_name_input = QLineEdit()

        add_review_button = QPushButton("Добавить отзыв")
        add_review_button.clicked.connect(self.submit_press_review)

        layout.addRow("ID выставки:", self.exhibition_id_input_press)
        layout.addRow("Текст отзыва:", self.review_text_input_press)
        layout.addRow("Название издания:", self.publication_name_input)
        layout.addRow(add_review_button)

        review_window.setLayout(layout)
        review_window.exec_()

    def submit_visitor_review(self):
        exhibition_id = int(self.exhibition_id_input.text())
        review_text = self.review_text_input.text()
        reviewer_name = self.reviewer_name_input.text()

        if not exhibition_id or not review_text or not reviewer_name:
            print("Ошибка: все поля должны быть заполнены.")
            return

        try:
            review_id = services.add_visitor_review(exhibition_id, review_text, reviewer_name)
            print(f"Отзыв от посетителя добавлен, ID отзыва: {review_id}")
            self.show_success_message("Отзыв успешно добавлен!")
        except Exception as e:
            print(f"Ошибка: {e}")
            self.show_error_message("Не удалось добавить отзыв!")

    def show_success_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Успех")
        msg.exec_()

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Ошибка")
        msg.exec_()

    def submit_press_review(self):
        exhibition_id = int(self.exhibition_id_input_press.text())
        review_text = self.review_text_input_press.text()
        publication_name = self.publication_name_input.text()

        if not exhibition_id or not review_text or not publication_name:
            print("Ошибка: все поля должны быть заполнены.")
            return

        try:
            review_id = services.add_press_review(exhibition_id, review_text, publication_name)
            print(f"Отзыв от СМИ добавлен, ID отзыва: {review_id}")
            self.show_success_message("Отзыв от СМИ успешно добавлен!")
        except Exception as e:
            print(f"Ошибка: {e}")
            self.show_error_message("Не удалось добавить отзыв от СМИ!")

    def show_visitor_reviews(self):
        try:
            reviews = services.get_visitor_reviews()

            review_window = QDialog()
            review_window.setWindowTitle("Отзывы от посетителей")

            layout = QVBoxLayout()
            review_window.setGeometry(200, 200, 1000, 400)

            table = QTableWidget()
            table.setRowCount(len(reviews))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["ID", "Текст отзыва", "Имя посетителя", "Дата"])

            for row, review in enumerate(reviews):
                table.setItem(row, 0, QTableWidgetItem(str(review[0])))
                table.setItem(row, 1, QTableWidgetItem(review[1]))
                table.setItem(row, 2, QTableWidgetItem(review[2]))
                table.setItem(row, 3, QTableWidgetItem(str(review[3])))

            layout.addWidget(table)

            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(review_window.close)
            layout.addWidget(close_button)

            review_window.setLayout(layout)
            review_window.exec_()

        except Exception as e:
            print(f"Ошибка: {e}")

    def show_press_reviews(self):
        try:
            reviews = services.get_press_reviews()

            review_window = QDialog()
            review_window.setWindowTitle("Отзывы от СМИ")

            layout = QVBoxLayout()
            review_window.setGeometry(200, 200, 1000, 400)

            table = QTableWidget()
            table.setRowCount(len(reviews))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["ID", "Текст отзыва", "Название издания", "Дата"])

            for row, review in enumerate(reviews):
                table.setItem(row, 0, QTableWidgetItem(str(review[0])))
                table.setItem(row, 1, QTableWidgetItem(review[1]))
                table.setItem(row, 2, QTableWidgetItem(review[2]))
                table.setItem(row, 3, QTableWidgetItem(str(review[3])))

            layout.addWidget(table)

            close_button = QPushButton("Закрыть")
            close_button.clicked.connect(review_window.close)
            layout.addWidget(close_button)

            review_window.setLayout(layout)
            review_window.exec_()

        except Exception as e:
            print(f"Ошибка: {e}")

    def record_restoration_state(self):
        try:
            restoration_dialog = QDialog(self)
            restoration_dialog.setWindowTitle("Начать реставрацию")
            layout = QFormLayout()

            self.restoration_artwork_id_input = QLineEdit(restoration_dialog)
            self.restoration_artwork_id_input.setPlaceholderText("Введите ID картины для реставрации")

            self.restorer_name_input = QLineEdit(restoration_dialog)
            self.restorer_name_input.setPlaceholderText("Введите имя реставратора")

            self.condition_before_input = QLineEdit(restoration_dialog)
            self.condition_before_input.setPlaceholderText("Введите состояние картины до реставрации")

            self.restore_end_date_input = QDateEdit(restoration_dialog)
            self.restore_end_date_input.setCalendarPopup(True)
            self.restore_end_date_input.setDate(QDate.currentDate())

            self.restore_cost_input = QSpinBox(restoration_dialog)
            self.restore_cost_input.setRange(0, 999999)

            start_button = QPushButton("Начать реставрацию", restoration_dialog)
            start_button.clicked.connect(self.start_restoration)

            layout.addRow("ID картины:", self.restoration_artwork_id_input)
            layout.addRow("Имя реставратора:", self.restorer_name_input)
            layout.addRow("Состояние картины до реставрации:", self.condition_before_input)
            layout.addRow("Дата окончания реставрации", self.restore_end_date_input)
            layout.addRow("Стоимость реставрации:", self.restore_cost_input)
            layout.addRow(start_button)

            restoration_dialog.setLayout(layout)
            restoration_dialog.exec_()

        except Exception as e:
            print(f"Ошибка при открытии диалога реставрации: {e}")
            self.show_error_message("Ошибка при открытии диалога реставрации.")

    def start_restoration(self):
        try:
            artwork_id = int(self.restoration_artwork_id_input.text())
            restorer_name = self.restorer_name_input.text()
            condition_before = self.condition_before_input.text()
            restore_end_date = self.restore_end_date_input.date().toPyDate()
            restore_cost = self.restore_cost_input.value()

            if not artwork_id or not restorer_name or not condition_before or not restore_end_date or not restore_cost:
                print("Ошибка: все поля должны быть заполнены корректно.")
                self.show_error_message("Ошибка: все поля должны быть заполнены корректно.")
                return

            services.record_restoration_state(artwork_id, restorer_name, condition_before, restore_cost, restore_end_date)
            print(f"Реставрация картины с ID {artwork_id} начата.")
            self.show_success_message("Реставрация успешно начата.")

        except ValueError:
            print("Ошибка: введите правильный ID картины.")
            self.show_error_message("Ошибка: введите правильный ID картины.")
        except Exception as e:
            print(f"Ошибка: {e}")
            self.show_error_message("Ошибка при начале реставрации.")

    def add_restoration_material(self):
        material_dialog = QDialog(self)
        material_dialog.setWindowTitle("Добавить материал для реставрации")
        layout = QFormLayout()

        self.restoration_id_input = QLineEdit(material_dialog)
        self.material_id_input = QLineEdit(material_dialog)
        self.material_quantity_input = QSpinBox(material_dialog)
        self.material_quantity_input.setPrefix("Количество: ")

        add_material_button = QPushButton("Добавить материал", material_dialog)
        add_material_button.clicked.connect(self.add_material_to_restoration)

        layout.addRow("ID реставрации:", self.restoration_id_input)
        layout.addRow("ID материала:", self.material_id_input)
        layout.addRow("Количество материала:", self.material_quantity_input)
        layout.addRow(add_material_button)

        material_dialog.setLayout(layout)
        material_dialog.exec_()

    def add_material_to_restoration(self):
        try:
            restoration_id = int(self.restoration_id_input.text())
            material_id = int(self.material_id_input.text())
            quantity_used = self.material_quantity_input.value()

            if restoration_id <= 0 or material_id <= 0 or quantity_used <= 0:
                raise ValueError("Все поля должны быть положительными числами.")

            services.add_restoration_material(restoration_id, material_id, quantity_used)
            print(f"Материал с ID {material_id} для реставрации добавлен в количестве {quantity_used}.")
            self.show_success_message(f"Материал с ID {material_id} добавлен успешно.")
        except ValueError as e:
            print(f"Ошибка: {e}")
            self.show_error_message("Ошибка при добавлении материала.")

    def open_add_document_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить документ о подлинности")
        layout = QFormLayout()

        self.artwork_id_input = QLineEdit(dialog)
        self.document_type_input = QLineEdit(dialog)
        self.file_path_input = QLineEdit(dialog)

        add_document_button = QPushButton("Добавить документ", dialog)
        add_document_button.clicked.connect(self.add_document)

        layout.addRow("ID картины:", self.artwork_id_input)
        layout.addRow("Тип документа:", self.document_type_input)
        layout.addRow("Путь к файлу:", self.file_path_input)
        layout.addRow(add_document_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def add_document(self):
        artwork_id = int(self.artwork_id_input.text())
        document_type = self.document_type_input.text()
        file_path = self.file_path_input.text()

        try:
            services.add_document(artwork_id, document_type, file_path)
            print(f"Документ о подлинности для картины с ID {artwork_id} добавлен")
        except Exception as e:
            print(f"Ошибка: {e}")

    def open_add_material_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить новый материал")
        layout = QFormLayout()

        self.material_name_input = QLineEdit(dialog)
        self.material_price_input = QDoubleSpinBox(dialog)
        self.material_price_input.setPrefix("Цена: ")

        add_material_button = QPushButton("Добавить материал", dialog)
        add_material_button.clicked.connect(self.add_material)

        layout.addRow("Название материала:", self.material_name_input)
        layout.addRow("Цена за единицу:", self.material_price_input)
        layout.addRow(add_material_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def add_material(self):
        name = self.material_name_input.text()
        unit_price = self.material_price_input.value()

        try:
            services.add_material(name, unit_price)
            print(f"Новый материал {name} добавлен")
        except Exception as e:
            print(f"Ошибка: {e}")