"""In-memory stand-ins for the repositories.

Each fake has the same method names the services call, but stores rows in a dict
instead of the database. They hold no business logic, so a unit test only
exercises the service under test.
"""

from app.models.user import User


class _Store:
    def __init__(self):
        self.rows = {}
        self._next_id = 1

    def save(self, obj):
        if obj.id is None:
            obj.id = self._next_id
            self._next_id += 1
        self.rows[obj.id] = obj
        return obj

    def get_by_id(self, obj_id):
        return self.rows.get(obj_id)


class FakeCompanyRepo(_Store):
    def get_by_user_id(self, user_id):
        return next((c for c in self.rows.values() if c.user_id == user_id), None)


class FakeInternshipRepo(_Store):
    def __init__(self):
        super().__init__()
        self.eligible = []  # what find_matching returns: [(internship, company)]

    def get_by_company(self, company_id):
        return [i for i in self.rows.values() if i.company_id == company_id]

    def find_matching(self, **filters):
        return self.eligible


class FakeMatchRepo(_Store):
    def __init__(self):
        super().__init__()
        self.counts = {}  # {internship_id: number of matches}

    def count_for_internship(self, internship_id):
        return self.counts.get(internship_id, 0)

    def counts_for_internships(self, internship_ids):
        return {i: self.counts[i] for i in internship_ids if i in self.counts}

    def create_match(self, match, application, internship):
        self.counts[internship.id] = self.counts.get(internship.id, 0) + 1
        return self.save(match)


class FakeStudentRepo(_Store):
    def get_by_user_id(self, user_id):
        return next((s for s in self.rows.values() if s.user_id == user_id), None)

    def get_by_student_number(self, student_number):
        return next((s for s in self.rows.values() if s.student_id == student_number), None)


class FakeApplicationRepo(_Store):
    def get_by_student(self, student_pk):
        return next((a for a in self.rows.values() if a.student_id == student_pk), None)


class FakeUserRepo(_Store):
    def get_by_username(self, username):
        return next((u for u in self.rows.values() if u.username == username), None)

    def get_by_email(self, email):
        return next((u for u in self.rows.values() if u.email == email), None)

    def create(self, user_data):
        return self.save(User.model_validate(user_data))

    def delete_user(self, user_id):
        self.rows.pop(user_id, None)
