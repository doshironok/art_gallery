import sqlite3
#from datetime import date

# Создание и подключение к базе данных SQLite
DATABASE = "art_gallery.db"

def get_connection():
    """Создает соединение с включенным lastrowid"""
    conn = sqlite3.connect(DATABASE)
    # Убедимся что lastrowid будет работать
    conn.isolation_level = None  # Автокоммит отключен
    return conn

def initialize_db():
    """Инициализация таблиц в базе данных."""
    conn = get_connection()
    cursor = conn.cursor()

    # Artwork
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Artwork (
                id INTEGER PRIMARY KEY,
                title TEXT,
                year_created INTEGER,
                technique TEXT,
                dimensions TEXT,
                description TEXT,
                genre TEXT,
                current_location TEXT,
                status TEXT,
                artist_id INTEGER,
                price REAL
            )
        ''')



    # Artist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Artist (
            id INTEGER PRIMARY KEY,
            name TEXT,
            biography TEXT,
            awards TEXT,
            exhibitions_participated INTEGER
        )
    ''')

    # Movement
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Movement (
            id INTEGER PRIMARY KEY,
            artwork_id INTEGER,
            from_location TEXT,
            to_location TEXT,
            movement_date DATE,
            purpose TEXT,
            responsible_person TEXT
        )
    ''')

    # Visitor
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Visitor (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            registration_date DATE
        )
    ''')

    # Exhibition_Artwork
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Exhibition_Artwork (
            exhibition_id INTEGER,
            artwork_id INTEGER,
            PRIMARY KEY (exhibition_id, artwork_id)
        )
    ''')

    # Provenance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Provenance (
            id INTEGER PRIMARY KEY,
            artwork_id INTEGER,
            provenance_entry TEXT,
            entry_date DATE
        )
    ''')

    # Restoration
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Restoration (
            id INTEGER PRIMARY KEY,
            artwork_id INTEGER,
            restorer_name TEXT,
            start_date DATE,
            end_date DATE,
            cost REAL,
            condition_before TEXT,
            condition_after TEXT
        )
    ''')

    # Restoration_Material
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Restoration_Material (
            restoration_id INTEGER,
            material_id INTEGER,
            quantity_used INTEGER,
            PRIMARY KEY (restoration_id, material_id)
        )
    ''')

    # Exhibition
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Exhibition (
            id INTEGER PRIMARY KEY,
            title TEXT,
            theme TEXT,
            start_date DATE,
            end_date DATE
        )
    ''')

    # Visitor_Review
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Visitor_Review (
            id INTEGER PRIMARY KEY,
            exhibition_id INTEGER,
            review TEXT,
            reviewer_name TEXT,
            review_date DATE
        )
    ''')

    # Press_Review
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Press_Review (
            id INTEGER PRIMARY KEY,
            exhibition_id INTEGER,
            review TEXT,
            publication_name TEXT,
            review_date DATE
        )
    ''')

    # Document
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Document (
            id INTEGER PRIMARY KEY,
            artwork_id INTEGER,
            document_type TEXT,
            issue_date DATE
        )
    ''')

    # Document_File
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Document_File (
            id INTEGER PRIMARY KEY,
            document_id INTEGER,
            file_path TEXT,
            upload_date DATE
        )
    ''')

    # Sale
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sale (
            id INTEGER PRIMARY KEY,
            artwork_id INTEGER,
            buyer_name TEXT,
            sale_date DATE,
            price REAL
        )
    ''')

    # Rental
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Rental (
            id INTEGER PRIMARY KEY,
            artwork_id INTEGER,
            renter_name TEXT,
            start_date DATE,
            end_date DATE,
            rental_fee REAL
        )
    ''')

    # Material
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Material (
            id INTEGER PRIMARY KEY,
            name TEXT,
            unit_price REAL
        )
    ''')

    conn.commit()
    conn.close()