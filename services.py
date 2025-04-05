from datetime import date
from database import get_connection

# 1. Приобретение картины
def acquire_artwork(title: str, year_created: int, technique: str, dimensions: str,
                    description: str, genre: str, artist_id: int, provenance_entry: str):
    conn = get_connection()
    cursor = conn.cursor()

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
    conn.close()

# 2. Фиксация состояния перед реставрацией
def record_restoration_state(artwork_id: int, restorer_name: str, condition_before: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Restoration (artwork_id, restorer_name, start_date, condition_before, condition_after)
        VALUES (?, ?, ?, ?, ?)
    ''', (artwork_id, restorer_name, date.today(), condition_before, "Restoration in progress"))

    conn.commit()
    conn.close()

# 3. Просмотр информации о картинах
def get_artworks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Artwork')
    artworks = cursor.fetchall()

    conn.close()
    return artworks

# 4. Учет стоимости картин
def update_artwork_price(artwork_id: int, new_price: float):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('UPDATE Artwork SET price = ? WHERE id = ?', (new_price, artwork_id))
    conn.commit()
    conn.close()

# 5. Документация о подлинности
def add_document(artwork_id: int, document_type: str, file_path: str):
    conn = get_connection()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()

# 6. Просмотр информации о художниках
def get_artists():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Artist')
    artists = cursor.fetchall()

    conn.close()
    return artists

# 7. Просмотр информации о выставках
def get_exhibitions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Exhibition')
    exhibitions = cursor.fetchall()

    conn.close()
    return exhibitions

# 8. Учет перемещений картин
def record_movement(artwork_id: int, from_location: str, to_location: str, purpose: str, responsible_person: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Movement (artwork_id, from_location, to_location, movement_date, purpose, responsible_person)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (artwork_id, from_location, to_location, date.today(), purpose, responsible_person))

    conn.commit()
    conn.close()

# 9. Продажа картин
def sell_artwork(artwork_id: int, buyer_name: str, price: float):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Sale (artwork_id, buyer_name, sale_date, price)
        VALUES (?, ?, ?, ?)
    ''', (artwork_id, buyer_name, date.today(), price))

    conn.commit()
    conn.close()

# 10. Аренда картин
def rent_artwork(artwork_id: int, renter_name: str, start_date: str, end_date: str, rental_fee: float):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Rental (artwork_id, renter_name, start_date, end_date, rental_fee)
        VALUES (?, ?, ?, ?, ?)
    ''', (artwork_id, renter_name, start_date, end_date, rental_fee))

    conn.commit()
    conn.close()

# 11. Регистрация посетителей
def register_visitor(name: str, email: str, phone: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Visitor (name, email, phone, registration_date)
        VALUES (?, ?, ?, ?)
    ''', (name, email, phone, date.today()))

    conn.commit()
    conn.close()

# 12. Добавление отзыва посетителя
def add_visitor_review(exhibition_id: int, review: str, reviewer_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Visitor_Review (exhibition_id, review, reviewer_name, review_date)
        VALUES (?, ?, ?, ?)
    ''', (exhibition_id, review, reviewer_name, date.today()))

    conn.commit()
    conn.close()

# 13. Добавление отзыва прессы
def add_press_review(exhibition_id: int, review: str, publication_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Press_Review (exhibition_id, review, publication_name, review_date)
        VALUES (?, ?, ?, ?)
    ''', (exhibition_id, review, publication_name, date.today()))

    conn.commit()
    conn.close()

# 14. Добавление материала для реставрации
def add_restoration_material(restoration_id: int, material_id: int, quantity_used: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Restoration_Material (restoration_id, material_id, quantity_used)
        VALUES (?, ?, ?)
    ''', (restoration_id, material_id, quantity_used))

    conn.commit()
    conn.close()

# 15. Добавление материала
def add_material(name: str, unit_price: float):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Material (name, unit_price)
        VALUES (?, ?)
    ''', (name, unit_price))

    conn.commit()
    conn.close()

# 16. Добавление картины на выставку
def add_artwork_to_exhibition(exhibition_id: int, artwork_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Exhibition_Artwork (exhibition_id, artwork_id)
        VALUES (?, ?)
    ''', (exhibition_id, artwork_id))

    conn.commit()
    conn.close()

# 17. Создание выставки
def create_exhibition(title: str, theme: str, start_date: str, end_date: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Exhibition (title, theme, start_date, end_date)
        VALUES (?, ?, ?, ?)
    ''', (title, theme, start_date, end_date))

    conn.commit()
    conn.close()

# 18. Обновление статуса картины
def update_artwork_status(artwork_id: int, new_status: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE Artwork SET status = ? WHERE id = ?
    ''', (new_status, artwork_id))

    conn.commit()
    conn.close()

# 19. Получение списка материалов
def get_materials():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Material')
    materials = cursor.fetchall()

    conn.close()
    return materials

# 20. Получение списка отзывов посетителей
def get_visitor_reviews():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Visitor_Review')
    reviews = cursor.fetchall()

    conn.close()
    return reviews

# 21. Получение списка отзывов прессы
def get_press_reviews():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Press_Review')
    reviews = cursor.fetchall()

    conn.close()
    return reviews