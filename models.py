"""
Модуль содержит модели данных для информационной системы картинной галереи.
Каждый класс представляет собой сущность предметной области с соответствующими атрибутами.
"""

from datetime import date

class Artwork:
    def __init__(self, id=None, title=None, year_created=None, technique=None, dimensions=None,
                 description=None, genre=None, current_location=None, status=None, artist_id=None):
        self.id = id
        self.title = title
        self.year_created = year_created
        self.technique = technique
        self.dimensions = dimensions
        self.description = description
        self.genre = genre
        self.current_location = current_location
        self.status = status
        self.artist_id = artist_id

class Artist:
    def __init__(self, id=None, name=None, biography=None, awards=None, exhibitions_participated=None):
        self.id = id
        self.name = name
        self.biography = biography
        self.awards = awards
        self.exhibitions_participated = exhibitions_participated

class Movement:
    def __init__(self, id=None, artwork_id=None, from_location=None, to_location=None,
                 movement_date=None, purpose=None, responsible_person=None):
        self.id = id
        self.artwork_id = artwork_id
        self.from_location = from_location
        self.to_location = to_location
        self.movement_date = movement_date
        self.purpose = purpose
        self.responsible_person = responsible_person

class Visitor:
    def __init__(self, id=None, name=None, email=None, phone=None, registration_date=None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.registration_date = registration_date or date.today()

class Exhibition:
    def __init__(self, id=None, title=None, theme=None, start_date=None, end_date=None):
        self.id = id
        self.title = title
        self.theme = theme
        self.start_date = start_date
        self.end_date = end_date

class Provenance:
    def __init__(self, id=None, artwork_id=None, provenance_entry=None, entry_date=None):
        self.id = id
        self.artwork_id = artwork_id
        self.provenance_entry = provenance_entry
        self.entry_date = entry_date or date.today()

class Restoration:
    def __init__(self, id=None, artwork_id=None, restorer_name=None, start_date=None, end_date=None,
                 cost=None, condition_before=None, condition_after=None):
        self.id = id
        self.artwork_id = artwork_id
        self.restorer_name = restorer_name
        self.start_date = start_date or date.today()
        self.end_date = end_date
        self.cost = cost
        self.condition_before = condition_before
        self.condition_after = condition_after

class Document:
    def __init__(self, id=None, artwork_id=None, document_type=None, issue_date=None):
        self.id = id
        self.artwork_id = artwork_id
        self.document_type = document_type
        self.issue_date = issue_date or date.today()

class Material:
    def __init__(self, id=None, name=None, unit_price=None):
        self.id = id
        self.name = name
        self.unit_price = unit_price

class Sale:
    def __init__(self, id=None, artwork_id=None, buyer_name=None, sale_date=None, price=None):
        self.id = id
        self.artwork_id = artwork_id
        self.buyer_name = buyer_name
        self.sale_date = sale_date or date.today()
        self.price = price

class Rental:
    def __init__(self, id=None, artwork_id=None, renter_name=None, start_date=None, end_date=None, rental_fee=None):
        self.id = id
        self.artwork_id = artwork_id
        self.renter_name = renter_name
        self.start_date = start_date
        self.end_date = end_date
        self.rental_fee = rental_fee

class VisitorReview:
    def __init__(self, id=None, exhibition_id=None, review=None, reviewer_name=None, review_date=None):
        self.id = id
        self.exhibition_id = exhibition_id
        self.review = review
        self.reviewer_name = reviewer_name
        self.review_date = review_date or date.today()

class PressReview:
    def __init__(self, id=None, exhibition_id=None, review=None, publication_name=None, review_date=None):
        self.id = id
        self.exhibition_id = exhibition_id
        self.review = review
        self.publication_name = publication_name
        self.review_date = review_date or date.today()