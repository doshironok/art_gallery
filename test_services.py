import pytest
from datetime import date
from services import *
from database import initialize_db, get_connection

@pytest.fixture(scope="function")
def setup_db():
    """Фикстура для инициализации и очистки тестовой БД."""
    global database
    database = ":memory:"  # Используем временную базу данных в памяти
    initialize_db()  # Инициализация таблиц

    yield

    # Очистка всех таблиц после теста
    conn = get_connection()
    cursor = conn.cursor()
    tables = [
        "Artwork", "Artist", "Visitor", "Exhibition",
        "Provenance", "Restoration", "Document", "Material",
        "Sale", "Rental", "Visitor_Review", "Press_Review",
        "Movement", "Exhibition_Artwork"
    ]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()

@pytest.fixture
def sample_artist(setup_db):
    """Фикстура для тестового художника."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Artist (name) VALUES ("Test Artist")')
    artist_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return artist_id

@pytest.fixture
def sample_artwork(sample_artist):
    """Фикстура для тестовой картины."""
    acquire_artwork(
        title="Sample Artwork",
        year_created=2020,
        technique="Oil",
        dimensions="50x70",
        description="Test",
        genre="Portrait",
        artist_id=sample_artist,
        provenance_entry="Test provenance"
    )
    artworks = get_artworks()
    return artworks[0][0]  # Возвращаем ID картины

@pytest.fixture
def sample_exhibition():
    """Фикстура для тестовой выставки."""
    create_exhibition(
        title="Sample Exhibition",
        theme="Modern Art",
        start_date="2023-01-01",
        end_date="2023-02-01"
    )
    exhibitions = get_exhibitions()
    return exhibitions[0][0]  # Возвращаем ID выставки

@pytest.fixture
def sample_visitor():
    """Фикстура для тестового посетителя."""
    register_visitor(
        name="Test Visitor",
        email="visitor@test.com",
        phone="+1234567890"
    )
    visitors = get_visitors()
    return visitors[0][0]  # Возвращаем ID посетителя

# Тесты
def test_get_visitors(setup_db, sample_visitor):
    """Тест получения списка посетителей."""
    visitors = get_visitors()
    assert len(visitors) == 1
    assert visitors[0][1] == "Test Visitor"

def test_acquire_artwork(setup_db, sample_artist):
    """Тест добавления новой картины."""
    acquire_artwork(
        title="Test Artwork",
        year_created=2023,
        technique="Oil on canvas",
        dimensions="50x70 cm",
        description="Test description",
        genre="Landscape",
        artist_id=sample_artist,
        provenance_entry="Test provenance"
    )
    artworks = get_artworks()
    assert len(artworks) == 1
    assert artworks[0][1] == "Test Artwork"

def test_register_visitor(setup_db):
    """Тест регистрации посетителя."""
    register_visitor(
        name="Test Visitor",
        email="visitor@test.com",
        phone="+1234567890"
    )
    visitors = get_visitors()
    assert len(visitors) == 1
    assert visitors[0][1] == "Test Visitor"

def test_create_exhibition(setup_db):
    """Тест создания выставки."""
    create_exhibition(
        title="Test Exhibition",
        theme="Modern Art",
        start_date="2023-01-01",
        end_date="2023-02-01"
    )
    exhibitions = get_exhibitions()
    assert len(exhibitions) == 1
    assert exhibitions[0][1] == "Test Exhibition"

def test_record_movement(setup_db, sample_artwork):
    """Тест записи перемещения картины."""
    record_movement(
        artwork_id=sample_artwork,
        from_location="Storage A",
        to_location="Exhibition Hall 1",
        purpose="Exhibition",
        responsible_person="John Doe"
    )
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Movement WHERE artwork_id = ?', (sample_artwork,))
    movement = cursor.fetchone()
    conn.close()
    assert movement[2] == "Storage A"
    assert movement[3] == "Exhibition Hall 1"

def test_artwork_status_transitions(setup_db, sample_artwork):
    """Тест изменения статусов картины."""
    update_artwork_status(sample_artwork, "On Exhibition")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM Artwork WHERE id = ?', (sample_artwork,))
    status = cursor.fetchone()[0]
    conn.close()
    assert status == "On Exhibition"

def test_add_artwork_to_exhibition(setup_db, sample_artwork, sample_exhibition):
    """Тест добавления картины на выставку."""
    add_artwork_to_exhibition(sample_exhibition, sample_artwork)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM Exhibition_Artwork 
        WHERE exhibition_id = ? AND artwork_id = ?
    ''', (sample_exhibition, sample_artwork))
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 1

def test_invalid_artist_id(setup_db):
    """Тест обработки несуществующего artist_id."""
    with pytest.raises(Exception):
        acquire_artwork(
            title="Invalid Artist",
            year_created=2023,
            technique="Test",
            dimensions="10x10",
            description="Test",
            genre="Test",
            artist_id=999,  # Несуществующий ID
            provenance_entry="Test"
        )

def test_empty_artwork_title(setup_db, sample_artist):
    """Тест добавления картины без названия."""
    with pytest.raises(Exception):
        acquire_artwork(
            title="",  # Пустое название
            year_created=2023,
            technique="Test",
            dimensions="10x10",
            description="Test",
            genre="Test",
            artist_id=sample_artist,
            provenance_entry="Test"
        )

def test_duplicate_visitor_email(setup_db):
    """Тест регистрации посетителя с существующим email."""
    email = "duplicate@test.com"
    register_visitor("First Visitor", email, "+111111111")
    with pytest.raises(Exception):
        register_visitor("Second Visitor", email, "+222222222")

def test_past_exhibition_date(setup_db):
    """Тест создания выставки с датой окончания в прошлом."""
    with pytest.raises(Exception):
        create_exhibition(
            title="Past Exhibition",
            theme="Test",
            start_date="2020-01-01",
            end_date="2019-12-31"  # Дата окончания раньше начала
        )

def test_nonexistent_artwork_movement(setup_db):
    """Тест перемещения несуществующей картины."""
    with pytest.raises(Exception):
        record_movement(
            artwork_id=999,  # Несуществующий ID
            from_location="Storage",
            to_location="Hall",
            purpose="Test",
            responsible_person="Test"
        )