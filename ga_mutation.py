import random
import numpy as np

class Mutation:
    def __init__(self, tasks, students):
        self.tasks = tasks
        self.students = students
        self.mutation_types = ['reassign', 'adjust_time', 'swap_tasks', 'shift_schedule']
        self.mutation_weights = [0.4, 0.3, 0.2, 0.1]  # Initial weights for mutation types

    def get_suitable_student(self, task_id):
        """Find a suitable student based on task requirements"""
        task = self.tasks[task_id]
        required_skills = task['skill_requirements']
        
        suitable_students = []
        for student_id, student in self.students.items():
            if all(skill in student['skills'] for skill in required_skills):
                suitable_students.append(student_id)
        
        return random.choice(suitable_students) if suitable_students else random.choice(list(self.students.keys()))

    def mutate(self, solution, generation=0, max_generations=100, temperature_ratio=1.0):
        """Enhanced mutation with multiple strategies and temperature-based control"""
        if not solution:
            return None
        
        mutated = list(solution)
        
        # Use temperature ratio to control mutation intensity
        # High temperature = more mutations and more diverse changes
        # Low temperature = fewer mutations and more conservative changes
        num_mutations = max(1, int(len(solution) * 0.1 * temperature_ratio))
        
        for _ in range(num_mutations):
            # Adjust weights based on both generation progress and temperature
            progress = generation / max_generations
            if temperature_ratio > 0.7:  # High temp: more experimental
                self.mutation_weights = [0.4, 0.3, 0.2, 0.1]  # Favor reassignment
            elif temperature_ratio > 0.3:  # Mid temp: balanced
                self.mutation_weights = [0.5, 0.3, 0.1, 0.1]  # More conservative
            else:  # Low temp: very conservative
                self.mutation_weights = [0.6, 0.3, 0.1, 0.0]  # No schedule shifts at low temp

            mutation_type = random.choices(self.mutation_types, weights=self.mutation_weights)[0]
            
            if mutation_type == 'reassign':
                # Intelligent task reassignment
                pos = random.randint(0, len(mutated) - 1)
                task_id, _, start_time = mutated[pos]
                new_student = self.get_suitable_student(task_id)
                mutated[pos] = (task_id, new_student, start_time)
                
            elif mutation_type == 'adjust_time':
                # Smart time adjustment based on task duration and temperature
                pos = random.randint(0, len(mutated) - 1)
                task_id, student_id, start_time = mutated[pos]
                task_duration = float(self.tasks[task_id]['estimated_time'])
                # More conservative time adjustments
                max_adjustment = task_duration * temperature_ratio * 0.5
                adjustment = random.uniform(-max_adjustment, max_adjustment)
                new_start = str(max(0, float(start_time) + adjustment))
                mutated[pos] = (task_id, student_id, new_start)
                
            elif mutation_type == 'swap_tasks':
                # Swap two tasks between students
                if len(mutated) >= 2:
                    pos1, pos2 = random.sample(range(len(mutated)), 2)
                    task1, student1, time1 = mutated[pos1]
                    task2, student2, time2 = mutated[pos2]
                    mutated[pos1] = (task1, student2, time1)
                    mutated[pos2] = (task2, student1, time2)
                    
            else:  # shift_schedule
                # Shift a sequence of tasks, length based on temperature
                if len(mutated) >= 2:
                    start_pos = random.randint(0, len(mutated) - 2)
                    # Shorter sequences
                    max_length = max(1, int(2 * temperature_ratio))
                    length = random.randint(1, min(max_length, len(mutated) - start_pos))
                    # Smaller shifts
                    max_shift = 2 * temperature_ratio
                    shift = random.uniform(-max_shift, max_shift)
                    
                    for i in range(start_pos, start_pos + length):
                        task_id, student_id, start_time = mutated[i]
                        new_start = str(max(0, float(start_time) + shift))
                        mutated[i] = (task_id, student_id, new_start)
        
        return mutated
