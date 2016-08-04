from app import db

locations = db.Table('locations',
    db.Column('location_id', db.Integer, db.ForeignKey('location.id')),
    db.Column('vacancy_id', db.Integer, db.ForeignKey('vacancy.id'))
)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=False)  # collation='utf8', convert_unicode=True
    company = db.Column(db.String(), unique=False)
    url = db.Column(db.String(), unique=False)
    description = db.Column(db.String(), unique=False)
    locations = db.relationship('Location', secondary=locations, backref=db.backref('vacancies', lazy='dynamic'))

    def __init__(self, title, company, url, description):
        self.title = title
        self.company = company
        self.url = url
        self.description = description

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
        }

    # def __repr__(self):
    #     return '<Vacancy %r in %r>' % (self.title, self.company)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place = db.Column(db.String(), unique=False)   # collation='utf8', convert_unicode=True

    def __repr__(self):
        return '<Location %r>' % self.place

