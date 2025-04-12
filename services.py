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
                    description: str, genre: str, artist_id: int, provenance_entry: str):
    try:
        # Валидация данных
        if not title or not isinstance(title, str):
            raise ValidationError("Название картины обязательно и должно быть строкой.")
        if not isinstance(year_created, int) or year_created <= 0:
            raise ValidationError("Год создания должен быть положительным числом.")
        if not isinstance(artist_id, int) or artist_id <= 0:
            raise ValidationError("ID художника должен быть положительным целым числом.")

        conn = get_connection()
        cursor = conn.cursor()

        # Проверка существования художника
        cursor.execute('SELECT id FROM Artist WHERE id = ?', (artist_id,))
        if not cursor.fetchone():
            raise ValidationError(f"Художник с ID {artist_id} не существует.")

        # Добавление картины
        cursor.execute('''
            INSERT INTO Artwork (title, year_created, technique, dimensions, description, genre, current_location, status, artist_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, year_created, technique, dimensions, description, genre, "Gallery Storage", "Acquired", artist_id))
        artwork_id = cursor.lastrowid

        # Добавление провенанса
        cursor.execute('''
            INSERT INTO Provenance (artwork_id, provenance_entry, entry_date)
            VALUES (?, ?, ?)
        ''', (artwork_id, provenance_entry, date.today()))

        conn.commit()
    except ValidationError as e:
        conn.rollback()
        raise e
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()

# 2. Фиксация состояния перед реставрацией
def record_restoration_state(artwork_id: int, restorer_name: str, condition_before: str):
    """Записывает информацию о начале реставрации"""
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины")
        if not restorer_name:
            raise ValidationError("Имя реставратора обязательно")

        def operation(cursor):
            cursor.execute('''
                INSERT INTO Restoration (artwork_id, restorer_name, start_date, 
                                       condition_before, condition_after)
                VALUES (?, ?, ?, ?, ?)
            ''', (artwork_id, restorer_name, date.today(),
                  condition_before, "Restoration in progress"))
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
    """Обновляет стоимость картины"""
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины")
        if not isinstance(new_price, (int, float)) or new_price < 0:
            raise ValidationError("Цена должна быть положительным числом")

        def operation(cursor):
            cursor.execute('UPDATE Artwork SET price = ? WHERE id = ?',
                           (new_price, artwork_id))
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
def sell_artwork(artwork_id: int, buyer_name: str, price: float):
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины.")
        if not buyer_name:
            raise ValidationError("Имя покупателя обязательно.")
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValidationError("Цена должна быть положительным числом.")

        def operation(cursor):
            cursor.execute('''
                INSERT INTO Sale (artwork_id, buyer_name, sale_date, price)
                VALUES (?, ?, ?, ?)
            ''', (artwork_id, buyer_name, date.today(), price))
            return cursor.lastrowid
        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при продаже картины: {str(e)}")

# 10. Аренда картин
def rent_artwork(artwork_id: int, renter_name: str, start_date: str, end_date: str, rental_fee: float):
    try:
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины.")
        if not renter_name:
            raise ValidationError("Имя арендатора обязательно.")
        if not start_date or not end_date:
            raise ValidationError("Даты начала и окончания аренды обязательны.")
        if not isinstance(rental_fee, (int, float)) or rental_fee <= 0:
            raise ValidationError("Стоимость аренды должна быть положительным числом.")

        def operation(cursor):
            cursor.execute('''
                INSERT INTO Rental (artwork_id, renter_name, start_date, end_date, rental_fee)
                VALUES (?, ?, ?, ?, ?)
            ''', (artwork_id, renter_name, start_date, end_date, rental_fee))
            return cursor.lastrowid
        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при аренде картины: {str(e)}")


# 11. Регистрация посетителей
def register_visitor(name: str, email: str, phone: str):
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

        # Добавление посетителя
        cursor.execute('''
            INSERT INTO Visitor (name, email, phone, registration_date)
            VALUES (?, ?, ?, ?)
        ''', (name, email, phone, date.today()))

        conn.commit()
    except ValidationError as e:
        conn.rollback()
        raise e
    except sqlite3.Error as e:
        conn.rollback()
        raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    finally:
        conn.close()



# 12. Добавление отзыва посетителя
def add_visitor_review(exhibition_id: int, review: str, reviewer_name: str):
    try:
        if not isinstance(exhibition_id, int) or exhibition_id <= 0:
            raise ValidationError("Некорректный ID выставки.")
        if not review:
            raise ValidationError("Текст отзыва обязателен.")
        if not reviewer_name:
            raise ValidationError("Имя автора отзыва обязательно.")

        def operation(cursor):
            cursor.execute('''
                    INSERT INTO Visitor_Review (exhibition_id, review, reviewer_name, review_date)
                    VALUES (?, ?, ?, ?)
                ''', (exhibition_id, review, reviewer_name, date.today()))
            return cursor.lastrowid

        return _execute_db_operation(operation)
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при добавлении отзыва посетителя: {str(e)}")

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
    try:
        if not isinstance(exhibition_id, int) or exhibition_id <= 0:
            raise ValidationError("Некорректный ID выставки.")
        if not isinstance(artwork_id, int) or artwork_id <= 0:
            raise ValidationError("Некорректный ID картины.")

        def operation(cursor):
            cursor.execute('''
                INSERT INTO Exhibition_Artwork (exhibition_id, artwork_id)
                VALUES (?, ?)
            ''', (exhibition_id, artwork_id))
            return cursor.lastrowid

        return _execute_db_operation(operation)
    except sqlite3.IntegrityError:
        raise DatabaseError("Картина уже добавлена на эту выставку.")
    except ArtGalleryError:
        raise
    except Exception as e:
        raise ArtGalleryError(f"Ошибка при добавлении картины на выставку: {str(e)}")

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
            cursor.execute('SELECT * FROM Visitor ORDER BY registration_date DESC')
            return cursor.fetchall()

        return _execute_db_operation(operation)
    except Exception as e:
        raise DatabaseError(f"Ошибка при получении списка посетителей: {str(e)}")