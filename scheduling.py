import sys
import signal
import pprint

import copy
import random
from objects import *

sig_int = False

courses = None
with open("courses.txt") as f:
    courses = []
    for line in f.read().splitlines():
        entries = line.split(" ")
        courses.append((entries[0], int(entries[1])))


professors = None
with open("professors.txt") as f:
    professors = [Professor(name) for name in f.read().splitlines()]

rooms = None
with open("rooms.txt") as f:
    rooms = [room for room in f.read().splitlines()]

DAYS_OF_WEEK = "MTWRF"

GENOMES_SIZE = 1000

MIN_START_TIME = 8
MAX_START_TIME = 16

NUM_COURSES = len(courses)
NUM_ROOMS = len(rooms)

HOUR = 60
TIME_SLICE = 60
TIME_SLICES = MAX_START_TIME - MIN_START_TIME + 2

COURSE_INC = 50
ROOM_INC = 10
PROFESSOR_INC = 30

TOP_PERCENT = .05
PERCENT_UN_MUTATED = .01

random.seed()

pp = pprint.PrettyPrinter(indent=2)


def fitness(gene):
    score = COURSE_INC * NUM_COURSES + 4 * (NUM_COURSES - 1) * ROOM_INC + 4 * (NUM_COURSES - 1) * PROFESSOR_INC + 1
    course_count = {}
    for course in courses:
        course_count[course[0]] = 0
    room_count = {}
    for room in rooms:
        room_count[room] = {}
        for day in DAYS_OF_WEEK:
            room_count[room][day] = []
            for i in range(TIME_SLICES):
                room_count[room][day].append(0)
    # check professor overlap
    professors_schedule = {}
    for day in DAYS_OF_WEEK:
        professors_schedule[day] = []
        for i in range(TIME_SLICES):
            professors_schedule[day].append({})
    for course in gene:
        course_count[course.course_id] += 1
        for time_slice in range(course.date_time.start_time - MIN_START_TIME,
                                course.date_time.start_time + course.date_time.duration // 60 + 1 - MIN_START_TIME):
            for day in course.date_time.days:
                room_count[course.room_num][day][time_slice] += 1
                if course.professor.name not in professors_schedule[day][time_slice]:
                    professors_schedule[day][time_slice][course.professor.name] = 1
                else:
                    professors_schedule[day][time_slice][course.professor.name] += 1
    for count in course_count.values():
        if count == 1:
            score += COURSE_INC
        else:
            score -= COURSE_INC
    for days in room_count.values():
        for day in days.values():
            for count in day:
                if count > 1:
                    score -= (count - 1) * ROOM_INC
    for day in DAYS_OF_WEEK:
        for i in range(TIME_SLICES):
            for count in professors_schedule[day][i].values():
                if count > 1:
                    score -= (count - 1) * PROFESSOR_INC
    if score <= 0:
        print("score of %d not allowed, exiting..." % score)
        sys.exit(-1)
    return score


def selection(genomes, scores):
    children = []
    # select top 10% to be part of children
    children.extend([genomes[i[0]] for i in scores[:(int(GENOMES_SIZE * TOP_PERCENT))]])

    scores_sum = sum([i[1] for i in scores])
    proportional_selection = []
    index = 0
    for i in scores:
        proportional_selection.append(range(index, index + i[1]))
        index = index + i[1]

    for i in range(0, GENOMES_SIZE - int(GENOMES_SIZE * TOP_PERCENT)):
        selection1 = random.randint(0, scores_sum - 1)
        selection2 = random.randint(0, scores_sum - 1)

        parent1 = None
        parent2 = None

        for k in range(len(proportional_selection)):
            if selection1 in proportional_selection[k]:
                parent1 = genomes[scores[k][0]]
            if selection2 in proportional_selection[k]:
                parent2 = genomes[scores[k][0]]
            if parent1 is not None and parent2 is not None:
                break

        point1 = random.randint(1, NUM_COURSES - 2)
        point2 = random.randint(point1, NUM_COURSES - 1)

        children.append(copy.deepcopy(parent1[:point1] + parent2[point1:point2] + parent1[point2:]))
    print("selection complete")
    return children


def mutation(genomes, scores):
    for i in range(int(GENOMES_SIZE * PERCENT_UN_MUTATED), GENOMES_SIZE):
        for c in range(NUM_COURSES):
            if random.randint(1, NUM_COURSES) == 1:
                mutation_choice = random.randint(0, 2)
                if mutation_choice == 0:
                    new_course = random.choice(courses)
                    if genomes[scores[i][0]][c].credits != new_course[1]:
                        # credits are different, need to generate new times
                        start_time = random.randint(MIN_START_TIME, MAX_START_TIME)
                        day_structure = random.choice(DateTime.get_day_list(new_course[1]))
                        date_time = DateTime(start_time, day_structure, new_course[1])
                        genomes[scores[i][0]][c].mutate_date_time(date_time)
                    genomes[scores[i][0]][c].mutate_course(new_course)
                elif mutation_choice == 1:
                    new_room = random.choice(rooms)
                    genomes[scores[i][0]][c].mutate_room(new_room)
                elif mutation_choice == 2:
                    start_time = random.randint(MIN_START_TIME, MAX_START_TIME)
                    day_structure = random.choice(DateTime.get_day_list(genomes[scores[i][0]][c].credits))
                    date_time = DateTime(start_time, day_structure, genomes[scores[i][0]][c].credits)
                    genomes[scores[i][0]][c].mutate_date_time(date_time)
    print("mutation complete")


def score_genomes(genomes):
    scores = []
    for gene in range(GENOMES_SIZE):
        scores.append((gene, fitness(genomes[gene])))
    return sorted(scores, key=lambda x: x[1], reverse=True)


def print_rooms(gene):
    room_count = {}
    for room in rooms:
        room_count[room] = {}
        for day in DAYS_OF_WEEK:
            room_count[room][day] = []
            for i in range(MIN_START_TIME, MAX_START_TIME + 2, 1):
                room_count[room][day].append(0)
    for course in gene:
        for time_slice in range(course.date_time.start_time - MIN_START_TIME,
                                course.date_time.start_time + course.date_time.duration // 60 + 1 - MIN_START_TIME):
            for day in course.date_time.days:
                room_count[course.room_num][day][time_slice] += 1
    pp.pprint(room_count)


def print_professors(gene):
    professors_schedule = {}
    for day in DAYS_OF_WEEK:
        professors_schedule[day] = []
        for i in range(TIME_SLICES):
            professors_schedule[day].append({})
    for course in gene:
        for time_slice in range(course.date_time.start_time - MIN_START_TIME,
                                course.date_time.start_time + course.date_time.duration // 60 + 1 - MIN_START_TIME):
            for day in course.date_time.days:
                if course.professor.name not in professors_schedule[day][time_slice]:
                    professors_schedule[day][time_slice][course.professor.name] = 1
                else:
                    professors_schedule[day][time_slice][course.professor.name] += 1
    pp.pprint(professors_schedule)


def signal_handler(signal, frame):
    global sig_int
    sig_int = True


def main():
    print("Max Score:\t%d" % (COURSE_INC * NUM_COURSES + 4 * (NUM_COURSES - 1) * ROOM_INC + 4 * (NUM_COURSES - 1) *
                              PROFESSOR_INC + 1 + NUM_COURSES * COURSE_INC))

    genomes = []

    for gene in range(GENOMES_SIZE):
        genomes.append([])
        for i in range(len(courses)):
            course = random.choice(courses)
            room = random.choice(rooms)
            start_time = random.randint(MIN_START_TIME, MAX_START_TIME)
            day_structure = random.choice(DateTime.get_day_list(course[1]))
            date_time = DateTime(start_time, day_structure, course[1])
            professor = random.choice(professors)
            genomes[gene].append(Course(course[0], course[1], room, date_time, professor))
    #########################################

    signal.signal(signal.SIGINT, signal_handler)

    scores = score_genomes(genomes)
    print("Starting Scores:")
    print(scores[:10])
    print(scores[-10:])
    print("\n")

    for i in range(0, 1000):
        if sig_int:
            break
        print("Generation %d:" % i)
        scores = score_genomes(genomes)
        genomes = selection(genomes, scores)
        ####################
        scores = score_genomes(genomes)
        mutation(genomes, scores)
        ####################
        print(scores[:10])
        print(scores[-10:])
        print("\n")
    scores = score_genomes(genomes)
    pp.pprint(genomes[scores[0][0]])
    print("\n")
    print_rooms(genomes[scores[0][0]])
    print("\n\"")
    print_professors(genomes[scores[0][0]])


if __name__ == "__main__":
    main()
