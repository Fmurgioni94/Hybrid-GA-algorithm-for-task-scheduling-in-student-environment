import random
from copy import deepcopy

class LocalSearch:
    def __init__(self, tasks, students, fitness_calculator):
        self.tasks = tasks
        self.students = students
        self.fitness_calculator = fitness_calculator
        
    def improve_solution(self, solution, max_iterations=100, max_no_improve=20):
        """Apply local search to improve the solution."""
        best_solution = deepcopy(solution)
        best_fitness = self.fitness_calculator.calculate_fitness(best_solution)
        current_solution = deepcopy(solution)
        no_improve_counter = 0
        
        for iteration in range(max_iterations):
            # Try different neighborhood moves
            improved = False
            
            # 1. Try reassigning tasks to different students
            new_solution = self._try_reassignment(current_solution)
            new_fitness = self.fitness_calculator.calculate_fitness(new_solution)
            if new_fitness < best_fitness:
                best_solution = deepcopy(new_solution)
                best_fitness = new_fitness
                current_solution = deepcopy(new_solution)
                improved = True
            
            # 2. Try adjusting task times
            new_solution = self._try_time_adjustment(current_solution)
            new_fitness = self.fitness_calculator.calculate_fitness(new_solution)
            if new_fitness < best_fitness:
                best_solution = deepcopy(new_solution)
                best_fitness = new_fitness
                current_solution = deepcopy(new_solution)
                improved = True
            
            # 3. Try swapping tasks between students
            new_solution = self._try_task_swap(current_solution)
            new_fitness = self.fitness_calculator.calculate_fitness(new_solution)
            if new_fitness < best_fitness:
                best_solution = deepcopy(new_solution)
                best_fitness = new_fitness
                current_solution = deepcopy(new_solution)
                improved = True
            
            if not improved:
                no_improve_counter += 1
            else:
                no_improve_counter = 0
                
            if no_improve_counter >= max_no_improve:
                break
                
        return best_solution, best_fitness
    
    def _try_reassignment(self, solution):
        """Try reassigning a random task to a different student."""
        new_solution = deepcopy(solution)
        if not new_solution:
            return new_solution
            
        # Select random task
        task_idx = random.randint(0, len(new_solution) - 1)
        task_id, _, start_time = new_solution[task_idx]
        
        # Try assigning to different student
        new_student = random.choice(list(self.students.keys()))
        new_solution[task_idx] = (task_id, new_student, start_time)
        
        return new_solution
    
    def _try_time_adjustment(self, solution):
        """Try adjusting the start time of a random task."""
        new_solution = deepcopy(solution)
        if not new_solution:
            return new_solution
            
        # Select random task
        task_idx = random.randint(0, len(new_solution) - 1)
        task_id, student_id, start_time = new_solution[task_idx]
        
        # Convert start_time to float
        start_time = float(start_time)
        
        # Adjust start time slightly
        max_adjustment = float(self.tasks[task_id]['estimated_time']) / 2
        adjustment = random.uniform(-max_adjustment, max_adjustment)
        new_start_time = max(0, start_time + adjustment)
        
        new_solution[task_idx] = (task_id, student_id, new_start_time)
        return new_solution
    
    def _try_task_swap(self, solution):
        """Try swapping two tasks between different students."""
        new_solution = deepcopy(solution)
        if len(new_solution) < 2:
            return new_solution
            
        # Select two random tasks
        idx1, idx2 = random.sample(range(len(new_solution)), 2)
        task1_id, student1_id, start1 = new_solution[idx1]
        task2_id, student2_id, start2 = new_solution[idx2]
        
        # Swap students
        new_solution[idx1] = (task1_id, student2_id, start1)
        new_solution[idx2] = (task2_id, student1_id, start2)
        
        return new_solution