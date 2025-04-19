import random
import os
import json
from cat.plugins.NaturalComputingPlugIn.ga_initialization import PopulationInitializer, InitializationStrategy
from cat.plugins.NaturalComputingPlugIn.ga_fitness import FitnessCalculator
from cat.plugins.NaturalComputingPlugIn.ga_selection import Selection
from cat.plugins.NaturalComputingPlugIn.ga_crossover import Crossover
from cat.plugins.NaturalComputingPlugIn.ga_mutation import Mutation
from cat.plugins.NaturalComputingPlugIn.ga_local_search import LocalSearch
from cat.plugins.NaturalComputingPlugIn.ga_simulated_annealing import SimulatedAnnealing
import multiprocessing as mp
from cat.mad_hatter.decorators import tool
from cat.log import log
import boto3

class GeneticAlgorithm:
    def __init__(self, tasks, students, population_size=50, generations=100,
                mutation_rate=0.1, crossover_rate=0.8,
                init_strategy=InitializationStrategy.RANDOM,
                crossover_strategy='single_point',
                use_simulated_annealing=False):
        # Initialize parameters
        self.tasks = tasks
        self.students = students
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.crossover_strategy = crossover_strategy
        self.use_simulated_annealing = use_simulated_annealing
        
        # Initialize metrics tracking
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.best_solution = None
        self.best_solution_fitness = float('inf')
        
        # Fitness cache
        self._fitness_cache = {}
        
        # Current population for island model
        self.current_population = []
        
        # Initialize GA components
        self.initializer = PopulationInitializer(tasks, students, init_strategy)
        self.fitness_calculator = FitnessCalculator(tasks, students)
        self.selection = Selection(self)
        self.crossover = Crossover(tasks, self.initializer)
        self.mutation = Mutation(tasks, students)
        self.local_search = LocalSearch(tasks, students, self.fitness_calculator)
        self.simulated_annealing = SimulatedAnnealing(tasks, students, self.fitness_calculator)

    def get_fitness(self, solution):
        """Get fitness with caching"""
        solution_tuple = tuple(tuple(x) for x in solution)
        
        if solution_tuple not in self._fitness_cache:
            self._fitness_cache[solution_tuple] = self.fitness_calculator.calculate_fitness(solution)
        
        return self._fitness_cache[solution_tuple]

    def clear_fitness_cache(self):
        """Clear the fitness cache"""
        self._fitness_cache = {}

    def initialize_population(self):
        """Initialize population for island model"""
        self.current_population = self.initializer.create_population(self.population_size)
        return self.current_population

    def evolve_generation(self, generation):
        """Evolve population for one generation"""
        if not self.current_population:
            self.initialize_population()
        
        # Calculate fitness for all solutions
        generation_fitness = []
        for solution in self.current_population:
            fitness = self.get_fitness(solution)
            generation_fitness.append(fitness)
            
            if fitness < self.best_solution_fitness:
                self.best_solution = solution
                self.best_solution_fitness = fitness
        
        # Track metrics
        self.best_fitness_history.append(min(generation_fitness))
        self.avg_fitness_history.append(sum(generation_fitness) / len(generation_fitness))
        
        # Evolve population
        self.current_population = self.evolve_population(self.current_population, generation)

    def evolve_population(self, population, generation):
        """Evolve the population through selection, crossover, and mutation"""
        new_population = []
        
        # Keep track of best solution in this generation
        generation_best = None
        generation_best_fitness = float('inf')
        
        while len(new_population) < self.population_size:
            # Select parents
            parent1 = self.selection.tournament_select(population)
            parent2 = self.selection.tournament_select(population)
            
            # Apply crossover
            if random.random() < self.crossover_rate:
                offspring1, offspring2 = self.crossover.crossover(parent1, parent2)
                
                # Apply local search to offspring with some probability
                if random.random() < 0.4:  # 40% chance to apply local search
                    offspring1, _ = self.local_search.improve_solution(offspring1, max_iterations=20, max_no_improve=5)
                    offspring2, _ = self.local_search.improve_solution(offspring2, max_iterations=20, max_no_improve=5)
            else:
                offspring1, offspring2 = parent1.copy(), parent2.copy()
            
            # Apply mutation
            if random.random() < self.mutation_rate:
                offspring1 = self.mutation.mutate(offspring1)
            if random.random() < self.mutation_rate:
                offspring2 = self.mutation.mutate(offspring2)
            
            # Add to new population
            new_population.append(offspring1)
            if len(new_population) < self.population_size:
                new_population.append(offspring2)
            
            # Update generation best
            for offspring in [offspring1, offspring2]:
                fitness = self.get_fitness(offspring)
                if fitness < generation_best_fitness:
                    generation_best = offspring
                    generation_best_fitness = fitness

        # Apply Simulated Annealing to generation's best solution
        if self.use_simulated_annealing and generation_best is not None:
            sa_solution, sa_fitness = self.simulated_annealing.improve_solution(
                generation_best,
                max_iterations=50,  # Shorter run to avoid degrading good solutions
                initial_temp=100.0,  # Lower initial temperature
                cooling_rate=0.90,   # Faster cooling
                min_temp=0.1
            )
            
            if sa_fitness < generation_best_fitness:
                # Replace worst solution in population with SA improved solution
                worst_idx = max(range(len(new_population)), 
                              key=lambda i: self.get_fitness(new_population[i]))
                new_population[worst_idx] = sa_solution
        
        return new_population

    def run(self, cat):
        """Run the genetic algorithm"""
        
        population = self.initializer.create_population(self.population_size)
        
        
        for generation in range(self.generations):            
            # Calculate fitness for all solutions
            cat.send_notification(f"Running iteration {generation+1}/{self.generations}")
            generation_fitness = []
            for solution in population:
                fitness = self.get_fitness(solution)
                generation_fitness.append(fitness)
                
                if fitness < self.best_solution_fitness:
                    self.best_solution = solution
                    self.best_solution_fitness = fitness
            
            # Track metrics
            self.best_fitness_history.append(min(generation_fitness))
            self.avg_fitness_history.append(sum(generation_fitness) / len(generation_fitness))
            
            # Evolve population
            population = self.evolve_population(population, generation)
        
        print("\n=== Genetic Algorithm Complete ===")
        print(f"Final best fitness: {self.best_solution_fitness}")
        
        
        return self.best_solution, self.best_solution_fitness

def load_data(filename):
    """Load tasks and students data from JSON file"""
    # Get the absolute path to the plugin directory
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(plugin_dir, filename)
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('tasks', {}), data.get('students', {})
    except FileNotFoundError:
        log.error(f"Error loading data from {filename}: File not found at {file_path}")
        return None, None
    except json.JSONDecodeError as e:
        log.error(f"Error parsing {filename}: Invalid JSON format - {str(e)}")
        return None, None
    except Exception as e:
        log.error(f"Error loading data from {filename}: {str(e)}")
        return None, None

def validate_schedule(tasks, students, solution):
    """Validate if a schedule is feasible"""
    # Create timeline for each student
    student_timelines = {s: [] for s in students.keys()}
    task_start_times = {}
    
    # First pass: calculate start times respecting dependencies
    for task_id, student_id, start_time in solution:
        task = tasks[task_id]
        start_time = float(start_time)
        
        # Check dependencies
        for dep in task['dependencies']:
            if dep not in task_start_times:
                return False
            dep_end_time = task_start_times[dep] + float(tasks[dep]['estimated_time'])
            start_time = max(start_time, dep_end_time)
        
        # Find first available slot for student
        student_busy_times = student_timelines[student_id]
        for busy_start, busy_end in student_busy_times:
            if start_time < busy_end:
                if start_time + float(task['estimated_time']) <= busy_start:
                    break
                start_time = busy_end
        
        # Update timelines
        task_start_times[task_id] = start_time
        student_timelines[student_id].append((start_time, start_time + float(task['estimated_time'])))
        student_timelines[student_id].sort()
    
    # Check for overlaps
    for student_id, timeline in student_timelines.items():
        for i in range(len(timeline) - 1):
            if timeline[i][1] > timeline[i + 1][0]:
                return False
    
    return True

def print_schedule(tasks, students, solution):
    """Print the optimized schedule with overlap checking"""
    print("\nOptimized Schedule:")
    print("-" * 80 + "\n")
    
    # Calculate start times and check feasibility
    student_timelines = {s: [] for s in students.keys()}
    task_start_times = {}
    
    # First pass: calculate start times respecting dependencies
    for task_id, student_id, start_time in solution:
        task = tasks[task_id]
        start_time = float(start_time)
        
        # Check dependencies
        for dep in task['dependencies']:
            if dep in task_start_times:
                dep_end_time = task_start_times[dep] + float(tasks[dep]['estimated_time'])
                start_time = max(start_time, dep_end_time)
        
        # Find first available slot for student
        student_busy_times = student_timelines[student_id]
        for busy_start, busy_end in student_busy_times:
            if start_time < busy_end:
                if start_time + float(task['estimated_time']) <= busy_start:
                    break
                start_time = busy_end
        
        task_start_times[task_id] = start_time
        student_timelines[student_id].append((start_time, start_time + float(task['estimated_time'])))
        student_timelines[student_id].sort()
        
        # Print task details
        student = students[student_id]
        print(f"Task: {task['name']}")
        print(f"Assigned to: Student {student_id}")
        print(f"Start Time: {start_time:.2f}")
        print(f"End Time: {start_time + float(task['estimated_time']):.2f}")
        print(f"Duration: {task['estimated_time']}")
        print(f"Required Skills: {task['skill_requirements']}")
        print(f"Dependencies: {task['dependencies']}")
        print(f"Student Skills: {student['skills']}\n")
    
    # Print timeline for each student
    print("\nStudent Timelines:")
    print("-" * 80)
    for student_id, timeline in student_timelines.items():
        print(f"\nStudent {student_id}:")
        for start, end in timeline:
            task_id = next(t_id for t_id, s_id, _ in solution 
                         if s_id == student_id and abs(task_start_times[t_id] - start) < 0.01)
            print(f"  {start:.2f} - {end:.2f}: {tasks[task_id]['name']}")
            
        # Check for overlaps
        for i in range(len(timeline) - 1):
            if timeline[i][1] > timeline[i + 1][0]:
                print(f"  WARNING: Overlap detected between tasks at time {timeline[i][1]:.2f}")

@tool(return_direct=True, examples=["Run the genetic algorithm"])
def main(input_by_llm, cat):
    """Run the genetic algorithm to optimize the schedule, no input required"""

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = dynamodb.Table('studentInfo-euj5j6m525e2jbu6e466ge7iue-NONE')
    response = table.scan()

    # Convert DynamoDB response to the format expected by the GA
    students = {}
    for item in response['Items']:
        students[item['id']] = {
            'name': item['name'],
            'cognitive_power': float(item['cognitivePower']),
            'availability': item['availableHours'],
            'skills': {
                'programming': float(item['programming']),
                'design': float(item['design']),
                'documentation': float(item['documentation']),
                'writing': float(item['writing']),
                'testing': float(item['testing']),
                'analysis': float(item['analysis'])
            }
        }
    
    cat.send_chat_message(f"Loaded {students} students from DynamoDB")

    # Load data

    tasks, students_old = load_data("generated_tasks.json")
    if not tasks or not students:
        cat.send_error("Failed to load data missing tasks or students")
        return
    
    # Create and run island model
    from cat.plugins.NaturalComputingPlugIn.ga_island import IslandModel
    island_ga = IslandModel(
        tasks=tasks,
        students=students,
        num_islands=4,          # Number of parallel populations
        migration_interval=10,   # Migrate every 10 generations
        migration_size=3        # Number of solutions to migrate
    )
    
    # Run the algorithm
    best_solution, best_fitness = island_ga.run()
    cat.send_notification(f"best fitness is {best_fitness}")
    if best_solution:
        # Validate and print schedule
        is_valid = validate_schedule(tasks, students, best_solution)
        print(f"\nSchedule is {'valid' if is_valid else 'invalid'}")

        promt = f"""
        
        create a json object using the data provide here: {best_solution}, knowing that T01 is the name of tasks and S3 is an example of student, and the following number is the best starting time 
        the json object should be in the following format:
        {{
            "Student1": {{
                "task_1": "task_id",
                "task_2": "task_id",
                "task_3": "task_id",
            }},
            "Student2": {{
                "task_1": "task_id",
                "task_2": "task_id",
                "task_3": "task_id",
            }}  
        }}
        return only the json object, no other text or comments are allowed. Make sure to use the exact same format as the example above and all the tasks are assigned to a student.
        """
        

        output = cat.llm(promt)
        output = output.replace("```json", "").replace("```", "").strip()
        return output
    else:
        cat.send_error("No valid solution found")
        return None
