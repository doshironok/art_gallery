from datetime import date
from database import get_connection
import sqlite3


class ArtGalleryError(Exception):
    """Базовый класс для ошибок галереи"""
    pass


class DatabaseError(ArtGalleryError):
    """Ошибки работы с базой данных"""
    pass


class ValidationError(ArtGalleryError):
    """Ошибки валидации данных"""
    pass


def _validate_artwork_data(title: str, artist_id: int):
    """Валидация базовых данных о картине"""
    if not title or not isinstance(title, str):
        raise ValidationError("Название картины обязательно и должно быть строкой")
    if not isinstance(artist_id, int) or artist_id <= 0:
        raise ValidationError("ID художника должен быть положительным целым числом")


def _execute_db_operation(operation, *args, **kwargs):
    """Обертка для выполнения операций с БД с обработкой ошибок"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        result = operation(cursor, *args, **kwargs)
        conn.commit()
        return result
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    finally:
        if conn:
            conn.close()


# 1. Приобретение картины
def acquire_artwork(title: str, year_created: int, technique: str, dimensions: str,
                    description: str, genre: str, artist_id: int, provenance_entry: str, price: float) -> int:
    """Добавляет новую картину и возвращает её ID"""
    conn = None
    try:
        _validate_artwork_data(title, artist_id)
        if not isinstance(price, (int, float)) or price < 0:
            raise ValidationError("Цена должна быть положительным числом")

        conn = get_connection()
        cursor = conn.cursor()

        # Проверяем существование художника
        cursor.execute('SELECT 1 FROM Artist WHERE id = ?', (artist_id,))
        if not cursor.fetchone():
            raise DatabaseError(f"Художник с ID {artist_id} не существует")

        # Добавление картины
        cursor.execute('''
            INSERT INTO Artwork (title, year_created, technique, dimensions,
                               description, genre, current_location, status, artist_id, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, year_created, technique, dimensions, description,
              genre, "Gallery Storage", "Acquired", artist_id, price))
        artwork_id = cursor.lastrowid

        # Добавление провенанса
        cursor.execute('''
            INSERT INTO Provenance (artwork_id, provenance_entry, entry_date)
            VALUES (?, ?, ?)
        ''', (artwork_id, provenance_entry, date.today()))

        conn.commit()
        return artwork_id

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Ошибка при добавлении картины: {str(e)}")
    finally:
        if conn:
            conn.close()

# 2. Фиксация состояния перед реставрацией
def record_restoration_state(artwork_id: int, restorer_name: str, condition_before: str, cost: float, end_date=None):
    """Записывает информацию о начале реставрации"""
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины")
        if not restorer_name:
            raise ValidationError("Имя реставратора обязательно")
        if not isinstance(cost, (int, float)) or cost < 0:
            raise ValidationError("Стоимость реставрации должна быть положительным числом")
        if end_date is not None and not isinstance(end_date, date):
            raise ValidationError("Дата окончания должна быть объектом date или None")

        def operation(cursor):
            cursor.execute('''
                INSERT INTO Restoration (artwork_id, restorer_name, start_date, end_date,
                                         cost, condition_before, condition_after)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (artwork_id, restorer_name, date.today(), end_date,
                  cost, condition_before, "Restoration in progress"))
            return cursor.lastrowid

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при записи состояния реставрации: {str(e)}")



# 3. Просмотр информации о картинах
def get_artworks():
    """Возвращает список всех картин"""
    try:
        def operation(cursor):
            cursor.execute('SELECT * FROM Artwork')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка картин: {str(e)}")


# 4. Учет стоимости картин
def update_artwork_price(artwork_id: int, new_price: float):
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины.")
        if not isinstance(new_price, (int, float)) or new_price < 0:
            raise ValidationError("Цена должна быть положительным числом.")

        def operation(cursor):
            # Проверяем существование картины
            cursor.execute('SELECT 1 FROM Artwork WHERE id = ?', (artwork_id,))
            if not cursor.fetchone():
                raise DatabaseError(f"Картина с ID {artwork_id} не существует.")

            # Обновляем стоимость картины
            cursor.execute('''
                UPDATE Artwork SET price = ? WHERE id = ?
            ''', (new_price, artwork_id))
            return cursor.rowcount

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при обновлении цены картины: {str(e)}")


# 5. Документация о подлинности
def add_document(artwork_id: int, document_type: str, file_path: str):
    """Добавляет документ о подлинности картины"""
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины")
        if not document_type:
            raise ValidationError("Тип документа обязателен")

        def operation(cursor):
            # Добавление документа
            cursor.execute('''
                INSERT INTO Document (artwork_id, document_type, issue_date)
                VALUES (?, ?, ?)
            ''', (artwork_id, document_type, date.today()))
            document_id = cursor.lastrowid

            # Добавление файла документа
            cursor.execute('''
                INSERT INTO Document_File (document_id, file_path, upload_date)
                VALUES (?, ?, ?)
            ''', (document_id, file_path, date.today()))
            return document_id

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при добавлении документа: {str(e)}")

# 6. Просмотр информации о художниках
def get_artists():
    try:
        def operation(cursor):
            cursor.execute('SELECT * FROM Artist')
            return cursor.fetchall()
        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка художников: {str(e)}")

# 7. Просмотр информации о выставках
def get_exhibitions():
    try:
        def operation(cursor):
            cursor.execute('SELECT * FROM Exhibition')
            return cursor.fetchall()
        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка выставок: {str(e)}")

# 8. Учет перемещений картин
def record_movement(artwork_id: int, from_location: str, to_location: str, purpose: str, responsible_person: str):
    try:
        # Валидация данных
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("ID картины должен быть положительным целым числом.")
        if not from_location or not isinstance(from_location, str):
            raise ValidationError("Место отправления обязательно и должно быть строкой.")
        if not to_location or not isinstance(to_location, str):
            raise ValidationError("Место назначения обязательно и должно быть строкой.")
        if not purpose or not isinstance(purpose, str):
            raise ValidationError("Цель перемещения обязательна и должна быть строкой.")
        if not responsible_person or not isinstance(responsible_person, str):
            raise ValidationError("Ответственное лицо обязательно и должно быть строкой.")

        conn = get_connection()
        cursor = conn.cursor()

        # Проверка существования картины
        cursor.execute('SELECT id FROM Artwork WHERE id = ?', (artwork_id,))
        if not cursor.fetchone():
            raise ValidationError(f"Картина с ID {artwork_id} не существует.")

        # Добавление перемещения
        cursor.execute('''
            INSERT INTO Movement (artwork_id, from_location, to_location, movement_date, purpose, responsible_person)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (artwork_id, from_location, to_location, date.today(), purpose, responsible_person))

        conn.commit()
    except ValidationError as e:
        conn.rollback()
        raise e
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

# 9. Продажа картин
from datetime import date


def sell_artwork(artwork_id: int, buyer_name: str, sale_price: float):
    try:
        # Валидация входных данных
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины.")
        if not buyer_name:
            raise ValidationError("Имя покупателя обязательно.")
        if not isinstance(sale_price, (int, float)) or sale_price <= 0:
            raise ValidationError("Цена продажи должна быть положительным числом.")

        conn = get_connection()
        cursor = conn.cursor()

        # Проверка существования картины
        cursor.execute('SELECT price FROM Artwork WHERE id = ?', (artwork_id,))
        artwork_price = cursor.fetchone()
        if not artwork_price:
            raise DatabaseError(f"Картина с ID {artwork_id} не существует.")

        '''# Проверка минимальной цены продажи (не менее 80% от текущей стоимости)
        if sale_price < artwork_price[0] * 0.8:
            raise ValidationError("Цена продажи не может быть ниже 80% от стоимости картины.")'''

        # Добавляем запись о продаже
        cursor.execute('''
            INSERT INTO Sale (artwork_id, buyer_name, sale_date, price)
            VALUES (?, ?, ?, ?)
        ''', (artwork_id, buyer_name, date.today(), sale_price))

        # Обновляем статус картины на "Продана"
        cursor.execute('''
            UPDATE Artwork SET status = ? WHERE id = ?
        ''', ("Sold", artwork_id))

        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Ошибка при продаже картины: {str(e)}")
    finally:
        if conn:
            conn.close()

# 10. Аренда картин
def rent_artwork(artwork_id: int, renter_name: str, start_date: str, end_date: str):
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины.")
        if not renter_name:
            raise ValidationError("Имя арендатора обязательно.")
        if not start_date or not end_date:
            raise ValidationError("Даты начала и окончания аренды обязательны.")

        conn = get_connection()
        cursor = conn.cursor()

        # Проверка существования картины
        cursor.execute('SELECT price FROM Artwork WHERE id = ?', (artwork_id,))
        artwork_price = cursor.fetchone()
        if not artwork_price:
            raise DatabaseError(f"Картина с ID {artwork_id} не существует.")

        # Рассчитываем арендную плату (5% от стоимости картины за месяц)
        rental_days = (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days
        if rental_days <= 0:
            raise ValidationError("Дата окончания аренды должна быть позже даты начала.")
        rental_fee = round(artwork_price[0] * 0.05 * (rental_days / 30), 2)

        # Добавляем запись об аренде
        cursor.execute('''
            INSERT INTO Rental (artwork_id, renter_name, start_date, end_date, rental_fee)
            VALUES (?, ?, ?, ?, ?)
        ''', (artwork_id, renter_name, start_date, end_date, rental_fee))

        # Обновляем статус картины на "Арендована"
        cursor.execute('''
            UPDATE Artwork SET status = ? WHERE id = ?
        ''', ("Rented", artwork_id))

        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Ошибка при аренде картины: {str(e)}")
    finally:
        if conn:
            conn.close()

# 11. Регистрация посетителей
def register_visitor(name: str, email: str, phone: str) -> int:
    conn = None
    try:
        # Валидация данных
        if not name or not isinstance(name, str):
            raise ValidationError("Имя посетителя обязательно и должно быть строкой.")
        if not email or "@" not in email:
            raise ValidationError("Email должен содержать символ '@'.")
        if not phone or not isinstance(phone, str):
            raise ValidationError("Телефон обязателен и должен быть строкой.")

        conn = get_connection()
        cursor = conn.cursor()

        # Проверка уникальности email
        cursor.execute('SELECT id FROM Visitor WHERE email = ?', (email,))
        if cursor.fetchone():
            raise ValidationError(f"Посетитель с email {email} уже зарегистрирован.")

        # Регистрация нового посетителя
        cursor.execute('''
            INSERT INTO Visitor (name, email, phone, registration_date)
            VALUES (?, ?, ?, ?)
        ''', (name, email, phone, date.today()))

        visitor_id = cursor.lastrowid
        conn.commit()
        return visitor_id

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Ошибка при регистрации посетителя: {str(e)}")
    finally:
        if conn:
            conn.close()


# 12. Добавление отзыва посетителя
def add_visitor_review(exhibition_id: int, review: str, reviewer_name: str):
    """Добавляет отзыв посетителя с проверками"""
    conn = None
    try:
        # Валидация входных данных
        if not isinstance(exhibition_id, int) or exhibition_id <= 0:
            raise ValidationError("Некорректный ID выставки")
        if not review:
            raise ValidationError("Текст отзыва обязателен")
        if not reviewer_name:
            raise ValidationError("Имя посетителя обязательно")

        conn = get_connection()
        cursor = conn.cursor()

        # Проверяем существование выставки
        cursor.execute('SELECT 1 FROM Exhibition WHERE id = ?', (exhibition_id,))
        if not cursor.fetchone():
            raise DatabaseError("Выставка не найдена")

        # Добавляем отзыв
        cursor.execute('''
            INSERT INTO Visitor_Review (exhibition_id, review, reviewer_name, review_date)
            VALUES (?, ?, ?, ?)
        ''', (exhibition_id, review, reviewer_name, date.today()))

        conn.commit()
        return cursor.lastrowid

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    finally:
        if conn:
            conn.close()

# 13. Добавление отзыва прессы
def add_press_review(exhibition_id: int, review: str, publication_name: str):
    try:
        if not isinstance(exhibition_id, int) or exhibition_id <= 0:
            raise ValidationError("Некорректный ID выставки.")
        if not review:
            raise ValidationError("Текст отзыва обязателен.")
        if not publication_name:
            raise ValidationError("Название издания обязательно.")

        def operation(cursor):
            cursor.execute('''
                INSERT INTO Press_Review (exhibition_id, review, publication_name, review_date)
                VALUES (?, ?, ?, ?)
            ''', (exhibition_id, review, publication_name, date.today()))
            return cursor.lastrowid
        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при добавлении отзыва прессы: {str(e)}")

# 14. Добавление материала для реставрации
def add_restoration_material(restoration_id: int, material_id: int, quantity_used: int):
    try:
        if not isinstance(restoration_id, int) or restoration_id <= 0:
            raise ValidationError("Некорректный ID реставрации.")
        if not isinstance(material_id, int) or material_id <= 0:
            raise ValidationError("Некорректный ID материала.")
        if not isinstance(quantity_used, int) or quantity_used <= 0:
            raise ValidationError("Количество используемого материала должно быть положительным числом.")

        def operation(cursor):
            # Проверяем существование реставрации
            cursor.execute('SELECT 1 FROM Restoration WHERE id = ?', (restoration_id,))
            if not cursor.fetchone():
                raise DatabaseError(f"Реставрация с ID {restoration_id} не существует.")

            # Проверяем существование материала
            cursor.execute('SELECT 1 FROM Material WHERE id = ?', (material_id,))
            if not cursor.fetchone():
                raise DatabaseError(f"Материал с ID {material_id} не существует.")

            # Добавляем материал для реставрации
            cursor.execute('''
                INSERT INTO Restoration_Material (restoration_id, material_id, quantity_used)
                VALUES (?, ?, ?)
            ''', (restoration_id, material_id, quantity_used))
            return cursor.lastrowid

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при добавлении материала для реставрации: {str(e)}")

# 15. Добавление материала
def add_material(name: str, unit_price: float):
    try:
        if not name or not isinstance(name, str):
            raise ValidationError("Название материала обязательно и должно быть строкой.")
        if not isinstance(unit_price, (int, float)) or unit_price <= 0:
            raise ValidationError("Цена за единицу должна быть положительным числом.")

        def operation(cursor):
            cursor.execute('''
                INSERT INTO Material (name, unit_price)
                VALUES (?, ?)
            ''', (name, unit_price))
            return cursor.lastrowid

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при добавлении материала: {str(e)}")

# 16. Добавление картины на выставку
def add_artwork_to_exhibition(exhibition_id: int, artwork_id: int):
    """Добавляет картину на выставку с проверками"""
    try:
        # Проверяем валидность ID
        if not isinstance(exhibition_id, int) or exhibition_id <= 0:
            raise ValidationError("Некорректный ID выставки")
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины")

        def operation(cursor):
            # Проверяем существование выставки
            cursor.execute('SELECT 1 FROM Exhibition WHERE id = ?', (exhibition_id,))
            if not cursor.fetchone():
                raise DatabaseError("Выставка не найдена")

            # Проверяем существование картины
            cursor.execute('SELECT 1 FROM Artwork WHERE id = ?', (artwork_id,))
            if not cursor.fetchone():
                raise DatabaseError("Картина не найдена")

            # Проверяем, не добавлена ли уже картина
            cursor.execute('''
                SELECT 1 FROM Exhibition_Artwork 
                WHERE exhibition_id = ? AND artwork_id = ?
            ''', (exhibition_id, artwork_id))
            if cursor.fetchone():
                raise DatabaseError("Картина уже на выставке")

            # Добавляем картину
            cursor.execute('''
                INSERT INTO Exhibition_Artwork (exhibition_id, artwork_id)
                VALUES (?, ?)
            ''', (exhibition_id, artwork_id))

            return cursor.lastrowid

        return _execute_db_operation(operation)

    except sqlite3.Error as e:
        raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при добавлении картины: {str(e)}")

# 17. Создание выставки
def create_exhibition(title: str, theme: str, start_date: str, end_date: str):
    try:
        if not title or not isinstance(title, str):
            raise ValidationError("Название выставки обязательно и должно быть строкой.")
        if not theme or not isinstance(theme, str):
            raise ValidationError("Тема выставки обязательна и должна быть строкой.")
        if not start_date or not end_date:
            raise ValidationError("Даты начала и окончания выставки обязательны.")
        if start_date > end_date:
            raise ValidationError("Дата окончания выставки должна быть позже даты начала.")

        def operation(cursor):
            cursor.execute('''
                INSERT INTO Exhibition (title, theme, start_date, end_date)
                VALUES (?, ?, ?, ?)
            ''', (title, theme, start_date, end_date))
            return cursor.lastrowid

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при создании выставки: {str(e)}")

# 18. Обновление статуса картины
def update_artwork_status(artwork_id: int, new_status: str):
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины.")
        if not new_status or not isinstance(new_status, str):
            raise ValidationError("Статус обязателен и должен быть строкой.")

        def operation(cursor):
            # Проверяем существование картины
            cursor.execute('SELECT 1 FROM Artwork WHERE id = ?', (artwork_id,))
            if not cursor.fetchone():
                raise DatabaseError(f"Картина с ID {artwork_id} не существует.")

            # Обновляем статус картины
            cursor.execute('''
                UPDATE Artwork SET status = ? WHERE id = ?
            ''', (new_status, artwork_id))
            return cursor.rowcount

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при обновлении статуса картины: {str(e)}")

# 19. Получение списка материалов
def get_materials():
    try:
        def operation(cursor):
            cursor.execute('SELECT * FROM Material')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка материалов: {str(e)}")

# 20. Получение списка отзывов посетителей
def get_visitor_reviews():
    try:
        def operation(cursor):
            cursor.execute('SELECT * FROM Visitor_Review')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка отзывов посетителей: {str(e)}")

# 21. Получение списка отзывов прессы
def get_press_reviews():
    try:
        def operation(cursor):
            cursor.execute('SELECT * FROM Press_Review')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка отзывов прессы: {str(e)}")


# 22. Получение списка всех зарегистрированных посетителей
def get_visitors():
    """Возвращает список всех посетителей"""
    try:
        def operation(cursor):
            cursor.execute('SELECT * FROM Visitor ORDER BY id ASC')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка посетителей: {str(e)}")

# 23. Добавление художника
def add_artist(name: str, biography: str):
    try:
        if not name or not isinstance(name, str):
            raise ValidationError("Имя художника обязательно и должно быть строкой.")
        if not biography or not isinstance(biography, str):
            raise ValidationError("Биография художника обязательна и должна быть строкой.")

        def operation(cursor):
            cursor.execute('''
                INSERT INTO Artist (name, biography)
                VALUES (?, ?)
            ''', (name, biography))
            return cursor.lastrowid

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при добавлении художника: {str(e)}")

# 24. Получение информации о перемещениях
def get_movements():
    try:
        def operation(cursor):
            cursor.execute('SELECT * FROM Movement')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка перемещений: {str(e)}")

# 25. Получение информации о документах картины
def get_documents():
    try:
        def operation(cursor):
            cursor.execute('''
                SELECT d.id, a.title AS artwork_title, d.document_type, d.issue_date, df.file_path
                FROM Document d
                JOIN Artwork a ON d.artwork_id = a.id
                LEFT JOIN Document_File df ON d.id = df.document_id
            ''')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка документов: {str(e)}")

# 26. Получение информации о реставрациях
def get_restorations():
    try:
        def operation(cursor):
            cursor.execute('''
                SELECT r.id, a.title AS artwork_title, r.restorer_name, r.start_date, r.end_date,
                       r.cost, r.condition_before, r.condition_after
                FROM Restoration r
                JOIN Artwork a ON r.artwork_id = a.id
            ''')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка реставраций: {str(e)}")


# 27. Получение информации о продажах
def get_sales():
    try:
        def operation(cursor):
            cursor.execute('''
                SELECT s.id, a.title AS artwork_title, s.buyer_name, s.sale_date, s.price
                FROM Sale s
                JOIN Artwork a ON s.artwork_id = a.id
            ''')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка продаж: {str(e)}")

# 28. Обновление данных художника
def update_artist(artist_id: int, name: str = None, biography: str = None,
                  awards: str = None, exhibitions_participated: int = None):
    try:
        if not isinstance(artist_id, int) or artist_id <= 0:
            raise ValidationError("Некорректный ID художника.")

        updates = []
        params = []

        if name:
            updates.append("name = ?")
            params.append(name)
        if biography:
            updates.append("biography = ?")
            params.append(biography)
        if awards:
            updates.append("awards = ?")
            params.append(awards)
        if exhibitions_participated is not None:
            updates.append("exhibitions_participated = ?")
            params.append(exhibitions_participated)

        if not updates:
            raise ValidationError("Не указаны данные для обновления.")

        query = f"UPDATE Artist SET {', '.join(updates)} WHERE id = ?"
        params.append(artist_id)

        def operation(cursor):
            cursor.execute(query, params)
            return cursor.rowcount

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при обновлении данных о художнике: {str(e)}")

# 29. Удаление художника
def delete_artist(artist_id: int):
    """Удаляет художника по его ID."""
    try:
        if not isinstance(artist_id, int) or artist_id <= 0:
            raise ValidationError("Некорректный ID художника.")

        def operation(cursor):
            # Проверяем, есть ли у художника связанные картины
            cursor.execute('SELECT COUNT(*) FROM Artwork WHERE artist_id = ?', (artist_id,))
            artwork_count = cursor.fetchone()[0]
            if artwork_count > 0:
                raise DatabaseError(f"Невозможно удалить художника с ID {artist_id}, так как у него есть связанные картины.")

            # Удаляем художника
            cursor.execute('DELETE FROM Artist WHERE id = ?', (artist_id,))
            return cursor.rowcount

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при удалении художника: {str(e)}")


# 30. Удаление картины
def delete_artwork(artwork_id: int):
    """Удаляет картину по её ID."""
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины.")

        def operation(cursor):
            # Удаляем связанные записи
            cursor.execute('DELETE FROM Provenance WHERE artwork_id = ?', (artwork_id,))
            cursor.execute('DELETE FROM Movement WHERE artwork_id = ?', (artwork_id,))
            cursor.execute('DELETE FROM Restoration WHERE artwork_id = ?', (artwork_id,))
            cursor.execute('DELETE FROM Sale WHERE artwork_id = ?', (artwork_id,))
            cursor.execute('DELETE FROM Rental WHERE artwork_id = ?', (artwork_id,))
            cursor.execute('DELETE FROM Exhibition_Artwork WHERE artwork_id = ?', (artwork_id,))
            # Удаляем саму картину
            cursor.execute('DELETE FROM Artwork WHERE id = ?', (artwork_id,))
            return cursor.rowcount

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при удалении картины: {str(e)}")
