import random
import math
from cat.plugins.NaturalComputingPlugIn.ga_mutation import Mutation
from cat.plugins.NaturalComputingPlugIn.ga_fitness import FitnessCalculator

class SimulatedAnnealing:
    def __init__(self, tasks, students, fitness_calculator=None):
        self.tasks = tasks
        self.students = students
        self.fitness_calculator = fitness_calculator if fitness_calculator else FitnessCalculator(tasks, students)
        self.mutation = Mutation(tasks, students)
        
    def _try_reassignment(self, solution, temperature):
        """Try reassigning a random task to a different student."""
        new_solution = solution.copy()
        if not new_solution:
            return new_solution
            
        # Select random task
        task_idx = random.randint(0, len(new_solution) - 1)
        task_id, _, start_time = new_solution[task_idx]
        
        # Try assigning to different student
        new_student = self.mutation.get_suitable_student(task_id)  # Use intelligent student selection
        new_solution[task_idx] = (task_id, new_student, start_time)
        
        return new_solution
    
    def _try_time_adjustment(self, solution, temperature):
        """Try adjusting the start time of a random task."""
        new_solution = solution.copy()
        if not new_solution:
            return new_solution
            
        # Select random task
        task_idx = random.randint(0, len(new_solution) - 1)
        task_id, student_id, start_time = new_solution[task_idx]
        
        # Convert start_time to float
        start_time = float(start_time)
        
        # Temperature-based adjustment
        temp_ratio = temperature / self.initial_temp
        task_duration = float(self.tasks[task_id]['estimated_time'])
        max_adjustment = task_duration * temp_ratio * 0.5  # More conservative adjustment
        adjustment = random.uniform(-max_adjustment, max_adjustment)
        new_start_time = max(0, start_time + adjustment)
        
        new_solution[task_idx] = (task_id, student_id, str(new_start_time))
        return new_solution
    
    def _try_task_swap(self, solution, temperature):
        """Try swapping two tasks between different students."""
        new_solution = solution.copy()
        if len(new_solution) < 2:
            return new_solution
            
        # Select two random tasks
        pos1, pos2 = random.sample(range(len(new_solution)), 2)
        task1, student1, time1 = new_solution[pos1]
        task2, student2, time2 = new_solution[pos2]
        
        # Swap students
        new_solution[pos1] = (task1, student2, time1)
        new_solution[pos2] = (task2, student1, time2)
        
        return new_solution
    
    def _get_neighbor(self, solution, temperature):
        """Generate a neighbor solution using focused local changes."""
        temp_ratio = temperature / self.initial_temp
        
        # Choose operation based on temperature
        if temp_ratio > 0.7:
            # High temperature: try all operations
            ops = ['reassign', 'time', 'swap']
            weights = [0.4, 0.4, 0.2]
        elif temp_ratio > 0.3:
            # Medium temperature: focus on reassignment and time
            ops = ['reassign', 'time', 'swap']
            weights = [0.5, 0.4, 0.1]
        else:
            # Low temperature: mostly small time adjustments
            ops = ['reassign', 'time', 'swap']
            weights = [0.3, 0.6, 0.1]
            
        operation = random.choices(ops, weights=weights)[0]
        
        if operation == 'reassign':
            return self._try_reassignment(solution, temperature)
        elif operation == 'time':
            return self._try_time_adjustment(solution, temperature)
        else:
            return self._try_task_swap(solution, temperature)
    
    def _acceptance_probability(self, old_cost, new_cost, temperature):
        """Calculate probability of accepting worse solution."""
        if new_cost < old_cost:  # Better solution, always accept
            return 1.0
        
        # Calculate relative improvement
        delta = new_cost - old_cost
        relative_delta = delta / old_cost
        
        # More selective about accepting worse solutions
        temp_ratio = temperature / self.initial_temp
        
        # Exponential decay with scaled delta
        return math.exp(-relative_delta / (temp_ratio * 0.1))  # More selective acceptance

    def improve_solution(self, initial_solution, max_iterations=100, 
                        initial_temp=1000.0, cooling_rate=0.95, min_temp=0.1):
        """
        Improve a solution using simulated annealing
        
        Args:
            initial_solution: Starting solution
            max_iterations: Maximum number of iterations
            initial_temp: Starting temperature
            cooling_rate: Rate at which temperature decreases
            min_temp: Minimum temperature before stopping
            
        Returns:
            tuple: (best_solution, best_fitness)
        """
        self.initial_temp = initial_temp  # Store for normalized calculations
        
        current_solution = initial_solution.copy()
        current_fitness = self.fitness_calculator.calculate_fitness(current_solution)
        
        best_solution = current_solution.copy()
        best_fitness = current_fitness
        
        temperature = initial_temp
        temperature_history = [temperature]
        no_improve = 0
        accepted_worse = 0
        total_tries = 0
        neighbor_history = []
        
        # print("\nStarting Simulated Annealing...")
        # print(f"Initial fitness: {current_fitness:.2f}")
        # print(f"Initial temperature: {temperature:.2f}")
        
        for iteration in range(max_iterations):
            # Stop if temperature is too low
            if temperature < min_temp:
                # print(f"Stopping: Temperature {temperature:.2f} below minimum {min_temp}")
                break
            
            # Generate multiple neighbors and pick the best one
            num_neighbors = 3  # Try multiple neighbors each iteration
            best_neighbor = None
            best_neighbor_fitness = float('inf')
            
            for _ in range(num_neighbors):
                neighbor = self._get_neighbor(current_solution, temperature)
                neighbor_fitness = self.fitness_calculator.calculate_fitness(neighbor)
                neighbor_history.append(neighbor_fitness)

                
                if neighbor_fitness < best_neighbor_fitness:
                    best_neighbor = neighbor
                    best_neighbor_fitness = neighbor_fitness
            
            total_tries += 1
            
            # Use the best neighbor for acceptance decision
            if self._acceptance_probability(current_fitness, best_neighbor_fitness, temperature) > random.random():
                if best_neighbor_fitness > current_fitness:
                    accepted_worse += 1
                current_solution = best_neighbor
                current_fitness = best_neighbor_fitness
                
                # Update best if we found a better solution
                if current_fitness < best_fitness:
                    best_solution = current_solution.copy()
                    best_fitness = current_fitness
                    no_improve = 0
                    # print(f"New best fitness: {best_fitness:.2f}")
                else:
                    no_improve += 1
            else:
                no_improve += 1
            
            # Cool down temperature
            temperature *= cooling_rate
            temperature_history.append(temperature)
            
            # Early stopping if no improvement for a while
            if no_improve >= 50:  # Reduced from 100 to be more aggressive about stopping
                # print("Early stopping: No improvement for 50 iterations")
                break
        
        # print(f"\nSimulated Annealing complete after {iteration + 1} iterations")
        # print(f"Final temperature: {temperature:.2f}")
        # print(f"Temperature history: {temperature_history}")
        # print(f"Best fitness found: {best_fitness:.2f}")
        # print(f"Neighbor fitness history: {neighbor_history}")
        # print(f"Accepted {accepted_worse} worse solutions out of {total_tries} attempts ({(accepted_worse/total_tries)*100:.1f}%)")
        
        return best_solution, best_fitness
