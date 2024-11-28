import random
from typing import List, Dict

class CourseClass:
    def __init__(self, id, name, department, max_students, duration, requires_lab, teacher, campus, room_id=None):
        self.id = id
        self.name = name
        self.department = department
        self.max_students = max_students
        self.duration = duration
        self.requires_lab = requires_lab
        self.teacher = teacher
        self.room_id = room_id  
        self.campus = campus


class Room:
    def __init__(self, id: int, name: str, seats: int, 
                 is_lab: bool, campus: str):
        self.id = id
        self.name = name
        self.seats = seats
        self.is_lab = is_lab
        self.campus = campus


class Schedule:
    def __init__(self):
        self.classes: Dict[CourseClass, int] = {}  # Mapping of courses to slots
        self.slots: List[List[CourseClass]] = []   # List of slots with scheduled classes
        self.score: float = 0

    def add_class_to_slot(self, course_class: CourseClass, slot: int):
        # Check if course is already scheduled
        if course_class in self.classes:
            raise ValueError("Course already scheduled.")

        # Expand slots list if needed
        while len(self.slots) <= slot:
            self.slots.append([])

        # Check for scheduling conflicts
        if any(other == course_class for other in self.slots[slot]):
            raise ValueError("Slot conflict detected.")

        # Add class to slot
        self.slots[slot].append(course_class)
        self.classes[course_class] = slot

    def calculate_score(self, rooms: List[Room]):
        self.score = 0
        department_slots: Dict[str, List[int]] = {}

        for course, slot in list(self.classes.items()):
            try:
                room = rooms[slot % len(rooms)]

                # Room capacity and lab constraints
                if room.seats < course.duration or (course.requires_lab and not room.is_lab):
                    continue

                # Department slot constraint
                if course.department in department_slots:
                    if slot in department_slots[course.department]:
                        continue
                    department_slots[course.department].append(slot)
                else:
                    department_slots[course.department] = [slot]

                # Increment score for valid scheduling
                self.score += 1

            except ValueError:
                # Remove invalid class scheduling
                del self.classes[course]
                if course in self.slots[slot]:
                    self.slots[slot].remove(course)

        return self.score


def initialize_population(population_size: int, courses: List[CourseClass], 
                          rooms: List[Room], total_slots: int) -> List[Schedule]:
    population = []
    for _ in range(population_size):
        schedule = Schedule()
        for course in courses:
            for _ in range(total_slots):  # Multiple attempts to schedule
                random_slot = random.randint(0, total_slots - 1)
                try:
                    schedule.add_class_to_slot(course, random_slot)
                    break  # Successfully scheduled
                except ValueError:
                    continue
        population.append(schedule)
    return population


def crossover(parent1: Schedule, parent2: Schedule, 
              rooms: List[Room]) -> Schedule:
    child = Schedule()
    courses = list(parent1.classes.keys())
    
    # Create crossover mask
    crossover_mask = [random.random() < 0.5 for _ in range(len(courses))]
    
    for i, course in enumerate(courses):
        try:
            # Choose slot from either parent based on crossover mask
            slot = (parent1.classes[course] if crossover_mask[i] 
                    else parent2.classes[course])
            child.add_class_to_slot(course, slot)
        except ValueError:
            continue
    
    return child


def mutate(schedule: Schedule, rooms: List[Room], 
           total_slots: int, mutation_chance: float = 0.1):
    for course in list(schedule.classes.keys()):
        if random.random() < mutation_chance:
            # Remove from current slot
            current_slot = schedule.classes[course]
            schedule.slots[current_slot].remove(course)
            del schedule.classes[course]
            
            # Try to reschedule
            for _ in range(total_slots):
                new_slot = random.randint(0, total_slots - 1)
                try:
                    schedule.add_class_to_slot(course, new_slot)
                    break
                except ValueError:
                    continue


def select_parent(population: List[Schedule]) -> Schedule:
    tournament_size = 3
    tournament = random.sample(population, tournament_size)
    return max(tournament, key=lambda sched: sched.score)


def genetic_algorithm(courses: List[CourseClass], rooms: List[Room], 
                      total_slots: int, generations: int = 100, 
                      population_size: int = 50) -> Schedule:
    population = initialize_population(population_size, courses, rooms, total_slots)

    best_overall_schedule = None
    best_overall_score = float('-inf')

    for _ in range(generations):
        # Calculate scores for current population
        for schedule in population:
            schedule.calculate_score(rooms)

        # Find best schedule in current generation
        current_best = max(population, key=lambda sched: sched.score)
        
        # Track overall best schedule
        if current_best.score > best_overall_score:
            best_overall_schedule = current_best
            best_overall_score = current_best.score

        # Check for perfect scheduling
        if current_best.score == len(courses):
            return current_best

        # Create new population
        new_population = []
        while len(new_population) < population_size:
            parent1 = select_parent(population)
            parent2 = select_parent(population)
            
            # Create child through crossover
            child = crossover(parent1, parent2, rooms)
            
            # Mutate child
            mutate(child, rooms, total_slots)
            
            # Recalculate score
            child.calculate_score(rooms)
            
            new_population.append(child)

        # Update population
        population = new_population

    return best_overall_schedule or max(population, key=lambda sched: sched.score)