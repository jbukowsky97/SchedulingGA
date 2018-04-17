class DateTime:
    days_dict = {1: {"T": 50, "R": 50}, 3: {"MWF": 50, "MW": 75, "TR": 75}, 4: {"T": 110, "R": 110}}
    # duration_mapping = {"MWF": 50, "MW": 70, "TR": 70, "T": 50}

    def __init__(self, start_time, days, credits):
        self.start_time = start_time
        self.days = days
        self.duration = DateTime.days_dict[credits][days]

    @staticmethod
    def get_day_list(credits):
        return list(DateTime.days_dict[credits].keys())

    @staticmethod
    def get_duration(credits, days):
        return DateTime.days_dict[credits][days]

    def __repr__(self):
        return "dt{%d, %s, %d}" % (self.start_time, self.days, self.duration)


class Course:

    def __init__(self, course_id, credits, room_num, date_time, professor):
        self.course_id = course_id
        self.credits = credits
        self.room_num = room_num
        self.date_time = date_time
        self.professor = professor

    def mutate_course(self, course):
        self.course_id = course[0]
        self.credits = course[1]

    def mutate_room(self, room_num):
        self.room_num = room_num

    def mutate_date_time(self, date_time):
        self.date_time = date_time

    def mutate_professor(self, professor):
        self.professor = professor

    def __repr__(self):
        return "%s, %s, %s, %s %s" % (self.course_id, self.credits, self.room_num, self.date_time, self.professor)


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
