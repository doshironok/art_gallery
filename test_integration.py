import pytest
from datetime import date, timedelta
from services import *
from database import initialize_db, get_connection
import time
import sqlite3


# Фикстуры для тестовых данных
@pytest.fixture(scope="module")
def setup_db():
    """Инициализация временной базы данных."""
    global DATABASE
    DATABASE = ":memory:"
    initialize_db()
    yield
    # Очистка не требуется для in-memory БД


@pytest.fixture
def sample_artist(setup_db):
    """Создает тестового художника и возвращает его ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Artist (name) VALUES (?)', ("Test Artist",))
    artist_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return artist_id

@pytest.fixture
def sample_artwork(setup_db, sample_artist):
    """Создает тестовую картину и возвращает ее ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Artwork (title, year_created, technique, dimensions, 
                           description, genre, current_location, status, artist_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("Sample Artwork", 2020, "Oil", "50x70", "Test", "Portrait",
          "Gallery Storage", "Acquired", sample_artist))
    artwork_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return artwork_id

@pytest.fixture
def sample_exhibition(setup_db):
    """Создает тестовую выставку и возвращает ее ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Exhibition (title, theme, start_date, end_date)
        VALUES (?, ?, ?, ?)
    ''', ("Sample Exhibition", "Modern Art", "2023-01-01", "2023-02-01"))
    exhibition_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return exhibition_id


# Интеграционные тесты
def test_full_artwork_lifecycle(setup_db, sample_artist):
    """Тест полного жизненного цикла картины"""
    # Генерируем уникальные данные для каждого теста
    timestamp = int(time.time())
    unique_email1 = f"one_{timestamp}@test.com"
    unique_email2 = f"two_{timestamp}@test.com"

    # 1. Приобретение картины
    artwork_id = acquire_artwork(
        title=f"Lifecycle Painting {timestamp}",
        year_created=2020,
        technique="Oil on canvas",
        dimensions="80x120",
        description="Impressive artwork",
        genre="Abstract",
        artist_id=sample_artist,
        provenance_entry="Private collection"
    )

    # Проверяем что ID валиден
    assert artwork_id is not None, "Функция acquire_artwork вернула None"
    assert isinstance(artwork_id, int), "ID картины должен быть целым числом"
    assert artwork_id > 0, "ID картины должен быть положительным числом"

    # 2. Добавление документа
    doc_id = add_document(
        artwork_id=artwork_id,
        document_type="Certificate of Authenticity",
        file_path=f"/docs/coa_{timestamp}.pdf"
    )
    assert doc_id is not None and isinstance(doc_id, int) and doc_id > 0

    # 3. Создание выставки
    exhibition_id = create_exhibition(
        title=f"Annual Exhibition {timestamp}",
        theme="Modern Art",
        start_date="2023-03-01",
        end_date="2023-04-15"
    )
    assert isinstance(exhibition_id, int) and exhibition_id > 0

    # 4. Добавление картины на выставку
    add_artwork_to_exhibition(exhibition_id, artwork_id)

    # 5. Обновление статуса
    update_artwork_status(artwork_id, "On Exhibition")

    # 6. Регистрация посетителей с уникальными email
    visitor1 = register_visitor(f"Visitor One {timestamp}", unique_email1, "+111111111")
    visitor2 = register_visitor(f"Visitor Two {timestamp}", unique_email2, "+222222222")
    assert isinstance(visitor1, int) and visitor1 > 0
    assert isinstance(visitor2, int) and visitor2 > 0

    # 7. Добавление отзывов (исправленная версия)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Visitor_Review (exhibition_id, review, reviewer_name, review_date)
        VALUES (?, ?, ?, ?)
    ''', (exhibition_id, "Amazing!", visitor1, date.today()))
    cursor.execute('''
        INSERT INTO Visitor_Review (exhibition_id, review, reviewer_name, review_date)
        VALUES (?, ?, ?, ?)
    ''', (exhibition_id, "Loved it!", visitor2, date.today()))
    conn.commit()
    conn.close()

    # 8. Продажа картины
    sell_artwork(
        artwork_id=artwork_id,
        buyer_name=f"Private Collector {timestamp}",
        price=10000.0
    )

    # Проверка статуса
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM Artwork WHERE id = ?', (artwork_id,))
    assert cursor.fetchone()[0] == "Sold"
    conn.close()


def test_restoration_process(setup_db, sample_artwork):
    """Тест полного цикла реставрации картины"""
    # Очищаем таблицы перед тестом
    conn = get_connection()
    cursor = conn.cursor()
    #cursor.execute('DELETE FROM Restoration_Material')
    #cursor.execute('DELETE FROM Restoration')
    #cursor.execute('DELETE FROM Material')
    conn.commit()
    conn.close()

    # 1. Проверяем начальный статус картины
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM Artwork WHERE id = ?', (sample_artwork,))
    assert cursor.fetchone()[0] == "Acquired"
    conn.close()

    # 2. Начинаем реставрацию
    restoration_id = record_restoration_state(
        artwork_id=sample_artwork,
        restorer_name="Anna Restorer",
        condition_before="Paint peeling",
        cost=100.0
    )
    assert isinstance(restoration_id, int) and restoration_id > 0

    # 3. Создаем уникальные материалы для теста
    materials = [
        {"name": f"Acrylic Paint {restoration_id}", "price": 25.0, "quantity": 2},
        {"name": f"Varnish {restoration_id}", "price": 30.0, "quantity": 1},
        {"name": f"Brush Set {restoration_id}", "price": 15.0, "quantity": 3}
    ]

    # 4. Добавляем материалы и проверяем
    for material in materials:
        # Создаем новый материал
        material_id = add_material(material["name"], material["price"])
        assert isinstance(material_id, int) and material_id > 0

        # Добавляем материал к реставрации
        rm_id = add_restoration_material(restoration_id, material_id, material["quantity"])
        assert isinstance(rm_id, int) and rm_id > 0

        # Проверяем, что материал добавился
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT quantity_used FROM Restoration_Material 
            WHERE restoration_id = ? AND material_id = ?
        ''', (restoration_id, material_id))
        assert cursor.fetchone()[0] == material["quantity"]
        conn.close()

        # Проверяем, что нельзя добавить дубликат
        with pytest.raises(DatabaseError):
            add_restoration_material(restoration_id, material_id, 5)

    # 5. Проверяем общее количество материалов для этой реставрации
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM Restoration_Material WHERE restoration_id = ?', (restoration_id,))
    assert cursor.fetchone()[0] == len(materials)
    conn.close()

    # 6. Завершаем реставрацию
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Restoration SET 
        end_date = ?,
        condition_after = ?
        WHERE id = ?
    ''', (date.today(), "Excellent condition", restoration_id))
    conn.commit()
    conn.close()

    # 7. Обновляем статус картины
    update_artwork_status(sample_artwork, "Restored")

    # 8. Проверяем финальный статус
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM Artwork WHERE id = ?', (sample_artwork,))
    assert cursor.fetchone()[0] == "Restored"
    conn.close()


def test_exhibition_management(setup_db, sample_artwork):
    """Тест управления выставками с обработкой ошибок"""
    # Генерируем уникальное название
    timestamp = int(time.time())

    # 1. Создание выставки
    exhibition_id = create_exhibition(
        title=f"Test Exhibition {timestamp}",
        theme="Modern Art",
        start_date="2023-05-01",
        end_date="2023-05-31"
    )

    # 2. Добавление картины
    add_artwork_to_exhibition(exhibition_id, sample_artwork)

    # 3. Проверка дублирования
    with pytest.raises(DatabaseError):
        add_artwork_to_exhibition(exhibition_id, sample_artwork)

    # 4. Попытка добавить несуществующую картину
    with pytest.raises(DatabaseError):
        add_artwork_to_exhibition(exhibition_id, 99999)

    # 5. Проверка добавления картины
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 1 FROM Exhibition_Artwork 
        WHERE exhibition_id = ? AND artwork_id = ?
    ''', (exhibition_id, sample_artwork))
    assert cursor.fetchone() is not None
    conn.close()


def test_visitor_reviews(setup_db, sample_exhibition):
    """Тест отзывов посетителей с обработкой ошибок"""
    # Генерируем уникальные данные для теста
    timestamp = int(time.time())
    reviewer_name = f"Reviewer {timestamp}"

    # 1. Добавляем отзыв
    review_id = add_visitor_review(
        exhibition_id=sample_exhibition,
        review="Отличная выставка!",
        reviewer_name=reviewer_name
    )
    assert isinstance(review_id, int)

    # 2. Проверяем, что отзыв добавился
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT review, reviewer_name FROM Visitor_Review WHERE id = ?', (review_id,))
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[0] == "Отличная выставка!"
    assert result[1] == reviewer_name

    # 3. Проверяем обработку несуществующей выставки через функцию add_visitor_review
    with pytest.raises(DatabaseError, match="Выставка не найдена"):
        add_visitor_review(
            exhibition_id=99999,
            review="Тестовый отзыв",
            reviewer_name=reviewer_name
        )

    # 4. Проверяем получение списка отзывов
    reviews = get_visitor_reviews()
    assert len(reviews) > 0
    assert any(r[0] == review_id for r in reviews)