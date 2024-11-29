import random
from typing import List, Dict

# Khai báo lớp CourseClass, Room và Schedule
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
        self.classes: Dict[CourseClass, int] = {}  # Ánh xạ các khóa học vào các slot
        self.slots: List[List[CourseClass]] = []   # Danh sách các slot với các lớp đã được xếp lịch
        self.score: float = 0

    def add_class_to_slot(self, course_class: CourseClass, slot: int, rooms: List[Room]):
        # Kiểm tra xem khóa học đã được xếp lịch chưa
        if course_class in self.classes:
            raise ValueError("Khóa học đã được xếp lịch.")

        # Mở rộng danh sách slot nếu cần
        while len(self.slots) <= slot:
            self.slots.append([])

        # Kiểm tra xung đột lịch
        if any(other == course_class for other in self.slots[slot]):
            raise ValueError("Phát hiện xung đột slot.")

        # Gán phòng dựa trên các ràng buộc
        for room in rooms:
            if (room.seats >= course_class.max_students and 
                (not course_class.requires_lab or room.is_lab) and 
                room.campus == course_class.campus):
                course_class.room_id = room.id
                break
        else:
            raise ValueError("Không tìm thấy phòng phù hợp.")

        # Thêm lớp vào slot
        self.slots[slot].append(course_class)
        self.classes[course_class] = slot

    def calculate_score(self, rooms: List[Room]):
        self.score = 0
        department_slots: Dict[str, List[int]] = {}

        for course, slot in list(self.classes.items()):
            try:
                room = rooms[slot % len(rooms)]

                # Ràng buộc về sức chứa phòng và phòng thí nghiệm
                if room.seats < course.max_students or (course.requires_lab and not room.is_lab):
                    continue

                # Ràng buộc về slot của khoa
                if course.department in department_slots:
                    if slot in department_slots[course.department]:
                        continue
                    department_slots[course.department].append(slot)
                else:
                    department_slots[course.department] = [slot]

                # Gán phòng cho khóa học
                course.room_id = room.id

                # Tăng điểm cho việc xếp lịch hợp lệ
                self.score += 1

            except ValueError:
                # Xóa lịch xếp lớp không hợp lệ
                del self.classes[course]
                if course in self.slots[slot]:
                    self.slots[slot].remove(course)

        return self.score


def initialize_population(population_size: int, courses: List[CourseClass], rooms: List[Room], total_slots: int) -> List[Schedule]:
    population = []
    for _ in range(population_size):
        schedule = Schedule()
        for course in courses:
            for _ in range(total_slots):
                random_slot = random.randint(0, total_slots - 1)
                try:
                    schedule.add_class_to_slot(course, random_slot, rooms)
                    break  # Đã xếp lịch thành công
                except ValueError:
                    continue
        population.append(schedule)
    return population


def crossover(parent1: Schedule, parent2: Schedule, rooms: List[Room]) -> Schedule:
    child = Schedule()
    courses = list(parent1.classes.keys())
    
    # Tạo mặt nạ crossover
    crossover_mask = [random.random() < 0.5 for _ in range(len(courses))]
    
    for i, course in enumerate(courses):
        try:
            # Chọn slot từ một trong hai cha mẹ dựa trên mặt nạ crossover
            slot = (parent1.classes[course] if crossover_mask[i] 
                    else parent2.classes[course])
            child.add_class_to_slot(course, slot, rooms)
        except ValueError:
            continue
    
    return child


def mutate(schedule: Schedule, rooms: List[Room], total_slots: int, mutation_chance: float = 0.1):
    for course in list(schedule.classes.keys()):
        if random.random() < mutation_chance:
            # Xóa khỏi slot hiện tại
            current_slot = schedule.classes[course]
            schedule.slots[current_slot].remove(course)
            del schedule.classes[course]
            
            # Thử xếp lại lịch
            for _ in range(total_slots):
                random_slot = random.randint(0, total_slots - 1)
                try:
                    schedule.add_class_to_slot(course, random_slot, rooms)
                    break  # Đã xếp lại lịch thành công
                except ValueError:
                    continue


def select_parent(population: List[Schedule]) -> Schedule:
    tournament_size = 3
    tournament = random.sample(population, tournament_size)
    return max(tournament, key=lambda sched: sched.score)


def genetic_algorithm(courses: List[CourseClass], rooms: List[Room], 
                      total_slots: int, generations: int = 100, 
                      population_size: int = 50, crossover_rate: float = 0.7, 
                      mutation_rate: float = 0.1) -> Schedule:
    population = initialize_population(population_size, courses, rooms, total_slots)

    best_overall_schedule = None
    best_overall_score = float('-inf')

    for _ in range(generations):
        # Tính điểm cho dân số hiện tại
        for schedule in population:
            schedule.calculate_score(rooms)

        # Tìm lịch tốt nhất trong thế hệ hiện tại
        current_best = max(population, key=lambda sched: sched.score)
        
        # Theo dõi lịch tốt nhất tổng thể
        if current_best.score > best_overall_score:
            best_overall_schedule = current_best
            best_overall_score = current_best.score

        # Kiểm tra lịch hoàn hảo
        if current_best.score == len(courses):
            return current_best

        # Tạo dân số mới
        new_population = []
        while len(new_population) < population_size:
            parent1 = select_parent(population)
            parent2 = select_parent(population)
            
            # Tạo con thông qua crossover
            if random.random() < crossover_rate:
                child = crossover(parent1, parent2, rooms)
            else:
                child = parent1 if parent1.score > parent2.score else parent2
            
            # Đột biến con
            mutate(child, rooms, total_slots, mutation_rate)
            
            # Tính lại điểm
            child.calculate_score(rooms)
            
            new_population.append(child)

        # Cập nhật dân số
        population = new_population

    return best_overall_schedule or max(population, key=lambda sched: sched.score)