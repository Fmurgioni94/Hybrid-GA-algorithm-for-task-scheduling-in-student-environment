import random
import copy

class Crossover:
    def __init__(self, tasks, population_initializer):
        self.tasks = tasks
        self.population_initializer = population_initializer

    def crossover(self, parent1, parent2):
        """Perform crossover between two parents using single-point crossover"""
        # Create copies of parents to avoid modifying the originals
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)

        # Get the length of the chromosome (task sequence)
        chromosome_length = len(child1)
        
        if chromosome_length <= 1:
            return child1, child2  # Return both parents if chromosome is too short

        # Select a random crossover point
        crossover_point = random.randint(1, chromosome_length - 1)
        
        # Perform crossover
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2

    def two_point_crossover(self, parent1, parent2):
        """Perform two-point crossover between two parents"""
        # Create copies of parents
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)

        chromosome_length = len(parent1)
        
        if chromosome_length <= 2:
            return child1, child2  # Return both parents if chromosome is too short

        # Select two random crossover points
        point1 = random.randint(1, chromosome_length - 2)
        point2 = random.randint(point1 + 1, chromosome_length - 1)
        
        # Perform crossover
        child1 = (
            parent1[:point1] +
            parent2[point1:point2] +
            parent1[point2:]
        )
        
        child2 = (
            parent2[:point1] +
            parent1[point1:point2] +
            parent2[point2:]
        )
        
        return child1, child2

    def uniform_crossover(self, parent1, parent2, swap_probability=0.5):
        """Perform uniform crossover between two parents"""
        # Create a copy of first parent as the base
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # For each gene, swap with probability p
        for i in range(len(parent1)):
            if random.random() < swap_probability:
                child1[i] = parent2[i]
                child2[i] = parent1[i]
        
        return child1, child2
