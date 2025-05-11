from database import get_connection

def populate():
    conn = get_connection()
    cursor = conn.cursor()

    # Проверка: есть ли уже художники
    cursor.execute("SELECT COUNT(*) FROM Artist")
    if cursor.fetchone()[0] > 0:
        print("Данные уже есть.")
        return

    # Добавим художников
    cursor.execute("INSERT INTO Artist (name, biography, awards, exhibitions_participated) VALUES (?, ?, ?, ?)",
                   ("Винсент Ван Гог", "Голландский постимпрессионист", "—", 5))
    van_gogh_id = cursor.lastrowid

    cursor.execute("INSERT INTO Artist (name, biography, awards, exhibitions_participated) VALUES (?, ?, ?, ?)",
                   ("Пабло Пикассо", "Испанский художник, один из основателей кубизма", "—", 10))
    picasso_id = cursor.lastrowid

    # Добавим картины
    cursor.execute("""INSERT INTO Artwork 
        (title, year_created, technique, dimensions, description, genre, current_location, status, artist_id, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("Звёздная ночь", 1889, "Масло на холсте", "73.7 × 92.1 см", "Ночное небо над Сен-Реми", "Постимпрессионизм", "Музей", "На месте", van_gogh_id, 1000000))

    cursor.execute("""INSERT INTO Artwork 
        (title, year_created, technique, dimensions, description, genre, current_location, status, artist_id, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("Герника", 1937, "Масло на холсте", "349 × 776 см", "Антивоенная картина", "Кубизм", "Музей", "На месте", picasso_id, 2000000))

    # Добавим выставку
    cursor.execute("INSERT INTO Exhibition (title, theme, start_date, end_date) VALUES (?, ?, ?, ?)",
                   ("Шедевры модернизма", "Модернизм", "2024-05-01", "2024-12-31"))
    exhibition_id = cursor.lastrowid

    # Привязка картин к выставке (через Exhibition_Artwork)
    cursor.execute("SELECT id FROM Artwork WHERE title = 'Звёздная ночь'")
    artwork1_id = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM Artwork WHERE title = 'Герника'")
    artwork2_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO Exhibition_Artwork (exhibition_id, artwork_id) VALUES (?, ?)",
                   (exhibition_id, artwork1_id))
    cursor.execute("INSERT INTO Exhibition_Artwork (exhibition_id, artwork_id) VALUES (?, ?)",
                   (exhibition_id, artwork2_id))

    conn.commit()
    conn.close()
    print("База успешно заполнена.")

if __name__ == "__main__":
    populate()
