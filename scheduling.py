import sys
import pprint

import copy
import random
from objects import *

courses = ["162-01", "162-02", "163-01", "163-02", "263-01", "263-02", "343-01", "343-02", "350-1", "350-2", "351-01",
           "351-02", "353-01", "353-02", "357-01", "451-01", "452-01", "452-02", "457-01", "457-02", "678-01"]

rooms = ["0", "1", "2", "3", "4", "5"]

DAYS_OF_WEEK = "MTWRF"

GENOMES_SIZE = 5000

MIN_START_TIME = 8
MAX_START_TIME = 16

NUM_COURSES = len(courses)
NUM_ROOMS = len(rooms)
TIME_SLICES = MAX_START_TIME - MIN_START_TIME + 2

COURSE_INC = 5
ROOM_INC = 1

TOP_PERCENT = .05
PERCENT_UN_MUTATED = .01

random.seed()

pp = pprint.PrettyPrinter(indent=2)


def fitness(gene):
    score = COURSE_INC * NUM_COURSES + ROOM_INC * 2 * NUM_COURSES + 1
    course_count = {}
    for course_id in courses:
        course_count[course_id] = 0
    room_count = {}
    for room in rooms:
        room_count[room] = {}
        for day in DAYS_OF_WEEK:
            room_count[room][day] = []
            for i in range(MIN_START_TIME, MAX_START_TIME + 2, 1):
                room_count[room][day].append(0)
    for course in gene:
        course_count[course.course_id] += 1
        for time_slice in range(course.date_time.start_time - MIN_START_TIME,
                                course.date_time.start_time + course.date_time.duration // 60 + 1 - MIN_START_TIME):
            for day in course.date_time.days:
                room_count[course.room_num][day][time_slice] += 1
    # pp.pprint(gene)
    # pp.pprint(room_count)
    # sys.exit(0)
    for count in course_count.values():
        if count == 1:
            score += COURSE_INC
        else:
            score -= COURSE_INC
    for days in room_count.values():
        for day in days.values():
            for count in day:
                if count != 0 and count != 1:
                    score -= ROOM_INC
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
                    new_course_id = random.choice(courses)
                    genomes[scores[i][0]][c].mutate_course_id(new_course_id)
                elif mutation_choice == 1:
                    new_room = random.choice(rooms)
                    genomes[scores[i][0]][c].mutate_room(new_room)
                elif mutation_choice == 2:
                    start_time = random.randint(MIN_START_TIME, MAX_START_TIME)
                    day_structure = random.choice(DateTime.days_list)
                    date_time = DateTime(start_time, day_structure)
                    genomes[scores[i][0]][c].mutate_date_time(date_time)
    print("mutation complete")


def main():
    genomes = []

    for gene in range(GENOMES_SIZE):
        genomes.append([])
        for i in range(len(courses)):
            course_id = random.choice(courses)
            room = random.choice(rooms)
            start_time = random.randint(MIN_START_TIME, MAX_START_TIME)
            day_structure = random.choice(DateTime.days_list)
            date_time = DateTime(start_time, day_structure)
            genomes[gene].append(Course(course_id, room, date_time))
    #########################################
    for i in range(0, 50):
        scores = []
        for gene in range(GENOMES_SIZE):
            scores.append((gene, fitness(genomes[gene])))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        print(scores[:10])
        print(scores[-10:])
        print("\n")
        genomes = selection(genomes, scores)
        ####################
        scores = []
        for gene in range(GENOMES_SIZE):
            scores.append((gene, fitness(genomes[gene])))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        print(scores[:10])
        print(scores[-10:])
        print("\n")
        ####################
        #pp.pprint(genomes[scores[0][0]])
        mutation(genomes, scores)
        #pp.pprint(genomes[scores[0][0]])
        ####################
    pp.pprint(genomes[scores[0][0]])
    print("\n")
    room_count = {}
    for room in rooms:
        room_count[room] = {}
        for day in DAYS_OF_WEEK:
            room_count[room][day] = []
            for i in range(MIN_START_TIME, MAX_START_TIME + 2, 1):
                room_count[room][day].append(0)
    for course in genomes[scores[0][0]]:
        for time_slice in range(course.date_time.start_time - MIN_START_TIME,
                                course.date_time.start_time + course.date_time.duration // 60 + 1 - MIN_START_TIME):
            for day in course.date_time.days:
                room_count[course.room_num][day][time_slice] += 1
    pp.pprint(room_count)


if __name__ == "__main__":
    main()
