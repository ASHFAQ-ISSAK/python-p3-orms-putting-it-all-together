import sqlite3

CONN = sqlite3.connect("lib/dogs.db")
CURSOR = CONN.cursor()


class Dog:
    def __init__(self, name, breed):
        self.id = None
        self.name = name
        self.breed = breed

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS dogs (
                id INTEGER PRIMARY KEY,
                name TEXT,
                breed TEXT
            )
        """
        CURSOR.execute(sql)

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS dogs")

    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO dogs (name, breed)
                VALUES (?, ?)
            """
            CURSOR.execute(sql, (self.name, self.breed))
            CONN.commit()
            self.id = CURSOR.lastrowid
        else:
            self.update()

    def update(self):
        sql = """
            UPDATE dogs
            SET name=?, breed=?
            WHERE id=?
        """
        CURSOR.execute(sql, (self.name, self.breed, self.id))
        CONN.commit()

    @classmethod
    def create(cls, name, breed):
        dog = Dog(name, breed)
        dog.save()
        return dog

    @classmethod
    def new_from_db(cls, row):
        dog = Dog(row[1], row[2])
        dog.id = row[0]
        return dog

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM dogs"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        dogs = [Dog.new_from_db(row) for row in rows]
        return dogs

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM dogs WHERE name=?"
        CURSOR.execute(sql, (name,))
        row = CURSOR.fetchone()
        if row is not None:
            return Dog.new_from_db(row)
        return None

    @classmethod
    def find_by_id(cls, id_):
        sql = "SELECT * FROM dogs WHERE id=?"
        CURSOR.execute(sql, (id_,))
        row = CURSOR.fetchone()
        if row is not None:
            return Dog.new_from_db(row)
        return None

    @classmethod
    def find_or_create_by(cls, name, breed):
        dog = Dog.find_by_name(name)
        if dog is not None:
            return dog
        return Dog.create(name, breed)


class TestDog:
    def test_has_name_and_breed_attributes(self):
        dog = Dog(name="joey", breed="cocker spaniel")
        assert dog.name == "joey" and dog.breed == "cocker spaniel"

    def test_creates_table(self):
        CURSOR.execute("DROP TABLE IF EXISTS dogs")
        Dog.create_table()
        CURSOR.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='dogs'"
        )
        result = CURSOR.fetchone()
        assert result is not None

    def test_drops_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS dogs
                (id INTEGER PRIMARY KEY,
                name TEXT,
                breed TEXT)
        """
        CURSOR.execute(sql)
        Dog.drop_table()
        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """
        result = CURSOR.execute(sql_table_names).fetchall()
        assert len(result) == 0

    def test_saves_dog(self):
        Dog.drop_table()
        Dog.create_table()
        joey = Dog("joey", "cocker spaniel")
        joey.save()
        sql = """
            SELECT * FROM dogs
            WHERE name='joey'
            LIMIT 1
        """
        result = CURSOR.execute(sql).fetchone()
        assert result == (1, "joey", "cocker spaniel")

    def test_creates_dog(self):
        Dog.drop_table()
        Dog.create_table()
        joey = Dog.create("joey", "cocker spaniel")
        assert (joey.id, joey.name, joey.breed) == (1, "joey", "cocker spaniel")

    def test_new_from_db(self):
        Dog.drop_table()
        Dog.create_table()
        sql = """
            INSERT INTO dogs (name, breed)
            VALUES ('joey', 'cocker spaniel')
        """
        CURSOR.execute(sql)
        sql = """
            SELECT * FROM dogs
            WHERE name='joey'
            LIMIT 1
        """
        row = CURSOR.execute(sql).fetchone()
        joey = Dog.new_from_db(row)
        assert (joey.id, joey.name, joey.breed) == (1, "joey", "cocker spaniel")

    def test_get_all(self):
        Dog.drop_table()
        Dog.create_table()
        Dog.create("joey", "cocker spaniel")
        Dog.create("fanny", "cockapoo")
        dogs = Dog.get_all()
        assert (dogs[0].id, dogs[0].name, dogs[0].breed) == (
            1,
            "joey",
            "cocker spaniel",
        ) and (dogs[1].id, dogs[1].name, dogs[1].breed) == (2, "fanny", "cockapoo")

    def test_finds_by_name(self):
        Dog.drop_table()
        Dog.create_table()
        Dog.create("joey", "cocker spaniel")
        joey = Dog.find_by_name("joey")
        assert (joey.id, joey.name, joey.breed) == (1, "joey", "cocker spaniel")

    def test_finds_by_id(self):
        Dog.drop_table()
        Dog.create_table()
        Dog.create("joey", "cocker spaniel")
        joey = Dog.find_by_id(1)
        assert (joey.id, joey.name, joey.breed) == (1, "joey", "cocker spaniel")

    def test_finds_or_creates_by_name_and_breed(self):
        Dog.drop_table()
        Dog.create_table()
        Dog.create("joey", "cocker spaniel")
        joey = Dog.find_or_create_by("joey", "cocker spaniel")
        assert (joey.id, joey.name, joey.breed) == (1, "joey", "cocker spaniel")

    def test_finds_or_creates_by_name_and_breed_when_not_exists(self):
        Dog.drop_table()
        Dog.create_table()
        joey = Dog.find_or_create_by("joey", "cocker spaniel")
        assert (joey.id, joey.name, joey.breed) == (1, "joey", "cocker spaniel")

    def test_saves_with_id(self):
        Dog.drop_table()
        Dog.create_table()
        joey = Dog("joey", "cocker spaniel")
        joey.save()
        assert (joey.id, joey.name, joey.breed) == (1, "joey", "cocker spaniel")

    def test_updates_record(self):
        Dog.drop_table()
        Dog.create_table()
        joey = Dog.create("joey", "cocker spaniel")
        joey.name = "joseph"
        joey.update()
        assert Dog.find_by_id(1).name == "joseph" and Dog.find_by_name("joey") is None
