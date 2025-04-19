import random
from collections import defaultdict
from enum import Enum

class InitializationStrategy(Enum):
    RANDOM = "random"
    INTELLIGENT = "intelligent"
    HYBRID = "hybrid"
    DEPENDENCY_BASED = "dependency_based"
    SKILL_BASED = "skill_based"

class PopulationInitializer:
    def __init__(self, tasks, students, strategy=InitializationStrategy.HYBRID):
        self.tasks = tasks
        self.students = students
        self.strategy = strategy

    def create_population(self, population_size):
        """Create initial population based on selected strategy"""
        if self.strategy == InitializationStrategy.RANDOM:
            return self._create_random_population(population_size)
        elif self.strategy == InitializationStrategy.INTELLIGENT:
            return self._create_intelligent_population(population_size)
        elif self.strategy == InitializationStrategy.HYBRID:
            return self._create_hybrid_population(population_size)
        elif self.strategy == InitializationStrategy.DEPENDENCY_BASED:
            return self._create_dependency_based_population(population_size)
        elif self.strategy == InitializationStrategy.SKILL_BASED:
            return self._create_skill_based_population(population_size)
        else:
            raise ValueError(f"Unknown initialization strategy: {self.strategy}")

    def _create_random_population(self, population_size):
        """Create population with completely random assignments"""
        population = []
        while len(population) < population_size:
            chromosome = self._create_random_chromosome()
            if chromosome:
                population.append(chromosome)
        return population

    def _create_intelligent_population(self, population_size):
        """Create population with intelligent task assignment"""
        population = []
        while len(population) < population_size:
            chromosome = self._create_intelligent_chromosome()
            if chromosome:
                population.append(chromosome)
        return population

    def _create_hybrid_population(self, population_size):
        """Create population with mix of random and intelligent solutions"""
        population = []
        while len(population) < population_size:
            if random.random() < 0.3:  # 30% random
                chromosome = self._create_random_chromosome()
            else:  # 70% intelligent
                chromosome = self._create_intelligent_chromosome()
            if chromosome:
                population.append(chromosome)
        return population

    def _create_dependency_based_population(self, population_size):
        """Create population focusing on task dependencies"""
        population = []
        while len(population) < population_size:
            chromosome = self._create_dependency_based_chromosome()
            if chromosome:
                population.append(chromosome)
        return population

    def _create_skill_based_population(self, population_size):
        """Create population focusing on skill matching"""
        population = []
        while len(population) < population_size:
            chromosome = self._create_skill_based_chromosome()
            if chromosome:
                population.append(chromosome)
        return population

    def _create_random_chromosome(self):
        """Create a completely random chromosome"""
        all_tasks = list(self.tasks.keys())
        random.shuffle(all_tasks)
        
        chromosome = []
        current_time = 0
        
        for task_id in all_tasks:
            student_id = random.choice(list(self.students.keys()))
            start_time = str(current_time)
            chromosome.append((task_id, student_id, start_time))
            task = self.tasks[task_id]
            current_time = float(start_time) + float(task['estimated_time'])
        
        return chromosome

    def _create_intelligent_chromosome(self):
        """Create chromosome considering all factors"""
        ordered_tasks = self._get_task_order()
        chromosome = []
        student_end_times = {sid: 0.0 for sid in self.students}
        
        for task_id in ordered_tasks:
            task = self.tasks[task_id]
            duration = float(task['estimated_time'])
            
            # Find best student based on skills and availability
            best_student = None
            best_score = float('-inf')
            earliest_start = float('inf')
            
            # Check dependencies
            dep_end_time = 0
            for dep in task['dependencies']:
                for dep_task_id, dep_student_id, dep_start in chromosome:
                    if dep_task_id == dep:
                        dep_end = float(dep_start) + float(self.tasks[dep]['estimated_time'])
                        dep_end_time = max(dep_end_time, dep_end)
            
            for student_id in self.students:
                skill_score = self._calculate_skill_match(task_id, student_id)
                workload_score = -student_end_times[student_id]
                total_score = skill_score + workload_score
                
                if total_score > best_score:
                    best_score = total_score
                    best_student = student_id
                    earliest_start = max(dep_end_time, student_end_times[student_id])
            
            start_time = str(earliest_start)
            chromosome.append((task_id, best_student, start_time))
            student_end_times[best_student] = earliest_start + duration
        
        return chromosome

    def _create_dependency_based_chromosome(self):
        """Create chromosome prioritizing dependency satisfaction"""
        ordered_tasks = self._get_task_order()
        chromosome = []
        current_time = 0
        completed_tasks = set()
        
        for task_id in ordered_tasks:
            # Wait for dependencies
            max_dep_time = 0
            for dep in self.tasks[task_id]['dependencies']:
                if dep not in completed_tasks:
                    continue
                for d_task, _, d_start in chromosome:
                    if d_task == dep:
                        dep_end = float(d_start) + float(self.tasks[dep]['estimated_time'])
                        max_dep_time = max(max_dep_time, dep_end)
            
            current_time = max(current_time, max_dep_time)
            student_id = random.choice(list(self.students.keys()))
            start_time = str(current_time)
            
            chromosome.append((task_id, student_id, start_time))
            completed_tasks.add(task_id)
            current_time += float(self.tasks[task_id]['estimated_time'])
        
        return chromosome

    def _create_skill_based_chromosome(self):
        """Create chromosome prioritizing skill matching"""
        all_tasks = list(self.tasks.keys())
        random.shuffle(all_tasks)
        chromosome = []
        current_time = 0
        
        for task_id in all_tasks:
            # Find best skilled student
            best_student = max(self.students.keys(),
                             key=lambda sid: self._calculate_skill_match(task_id, sid))
            
            start_time = str(current_time)
            chromosome.append((task_id, best_student, start_time))
            current_time += float(self.tasks[task_id]['estimated_time'])
        
        return chromosome

    def _calculate_skill_match(self, task_id, student_id):
        """Calculate skill match score between task and student"""
        task = self.tasks[task_id]
        student = self.students[student_id]
        match_score = 0
        
        for skill, required_level in task['skill_requirements'].items():
            student_level = student['skills'].get(skill, 0)
            if student_level >= required_level:
                match_score += 1
            else:
                match_score -= (required_level - student_level)
        
        return match_score

    def _get_task_order(self):
        """Get tasks in topological order respecting dependencies"""
        dependency_graph = self._get_dependency_graph()
        visited = set()
        order = []
        
        def visit(task_id):
            if task_id in visited:
                return
            visited.add(task_id)
            for dep in self.tasks[task_id]['dependencies']:
                visit(dep)
            order.append(task_id)
            
        for task_id in self.tasks:
            visit(task_id)
        return order

    def _get_dependency_graph(self):
        """Build task dependency graph"""
        dependency_graph = defaultdict(list)
        for task_id, task in self.tasks.items():
            for dep in task['dependencies']:
                dependency_graph[dep].append(task_id)
        return dependency_graph
