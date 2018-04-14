class DateTime:
    days_list = ["MWF", "MW", "TR"]
    duration_mapping = {"MWF": 50, "MW": 70, "TR": 70}

    def __init__(self, start_time, days):
        self.start_time = start_time
        self.days = days
        self.duration = DateTime.duration_mapping.get(self.days)

    def __repr__(self):
        return "dt{%d, %s, %d}" % (self.start_time, self.days, self.duration)


class Course:

    def __init__(self, course_id, room_num, date_time, professor):
        self.course_id = course_id
        self.room_num = room_num
        self.date_time = date_time
        self.professor = professor

    def mutate_course_id(self, course_id):
        self.course_id = course_id

    def mutate_room(self, room_num):
        self.room_num = room_num

    def mutate_date_time(self, date_time):
        self.date_time = date_time

    def mutate_professor(self, professor):
        self.professor = professor

    def __repr__(self):
        return "%s, %s, %s %s" % (self.course_id, self.room_num, self.date_time, self.professor)


class Professor:

    professor_id_index = 0

    def __init__(self, name):
        self.professor_id = Professor.get_next_professor_index()
        self.name = name

    @staticmethod
    def get_next_professor_index():
        index = Professor.professor_id_index
        Professor.professor_id_index += 1
        return index

    def __repr__(self):
        return "prof{%d, %s}" % (self.professor_id, self.name)
