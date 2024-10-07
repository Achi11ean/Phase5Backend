from .. import CURSOR, CONN

class Song:
    all = {}

    def __init__(self, title, genre, release_date, artist_id, id=None):
        self.id = id
        self.title = title
        self.genre = genre
        self.release_date = release_date
        self.artist_id = artist_id
    
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if isinstance(title, str) and len(title.strip()) > 0:
            self._title = title
        else:
            raise ValueError("Title must be a non-empty string.")

    @property
    def genre(self):
        return self._genre

    @genre.setter
    def genre(self, genre):
        if isinstance(genre, str) and len(genre.strip()) > 0:
            self._genre = genre
        else:
            raise ValueError("Genre must be a non-empty string.")

    @property
    def release_date(self):
        return self._release_date

    @release_date.setter
    def release_date(self, release_date):
        if isinstance(release_date, str) and len(release_date.strip()) > 0:
            self._release_date = release_date
        else:
            raise ValueError("Release date must be a non-empty string.")


    def __repr__(self):
        return f"<Song {self.id}: {self.title}, Genre: {self.genre}, Release Date: {self.release_date}, Artist ID: {self.artist_id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY,
                title TEXT,
                genre TEXT,
                release_date TEXT,
                artist_id INTEGER,
                FOREIGN KEY (artist_id) REFERENCES artists (id)
            )
        ''')
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute('DROP TABLE IF EXISTS songs')
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO songs (title, genre, release_date, artist_id)
                VALUES (?, ?, ?, ?)
            ''', (self.title, self.genre, self.release_date, self.artist_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            CURSOR.execute('''
                UPDATE songs
                SET title = ?, genre = ?, release_date = ?, artist_id = ?
                WHERE id = ?
            ''', (self.title, self.genre, self.release_date, self.artist_id, self.id))
            CONN.commit()

    @classmethod
    def create(cls, title, genre, release_date, artist_id):
        song = cls(title, genre, release_date, artist_id)
        song.save()
        return song

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute('SELECT * FROM songs').fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, song_id):
        row = CURSOR.execute('SELECT * FROM songs WHERE id = ?', (song_id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def instance_from_db(cls, row):
        song_id = row[0]
        if song_id in cls.all:
            return cls.all[song_id]
        song = cls(id=row[0], title=row[1], genre=row[2], release_date=row[3], artist_id=row[4])
        cls.all[song.id] = song
        return song

    def delete(self):
        if self.id is not None:
            CURSOR.execute('DELETE FROM songs WHERE id = ?', (self.id,))
            CONN.commit()
            del type(self).all[self.id]
            self.id = None