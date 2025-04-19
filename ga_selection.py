import random

class Selection:
    def __init__(self, ga):
        """Initialize with reference to GA for cached fitness"""
        self.tournament_size = 3
        self.get_fitness = ga.get_fitness  # Store only the fitness function

    def select(self, population):
        """Select individual using tournament selection"""
        tournament = random.sample(population, min(self.tournament_size, len(population)))
        return min(tournament, key=self.get_fitness)

    def tournament_select(self, population):
        """Select individual using tournament selection"""
        return self.select(population)

    def roulette_wheel_select(self, population):
        """Select individual using roulette wheel selection"""
        # Get fitness values and handle edge cases
        try:
            fitnesses = [self.get_fitness(x) for x in population]
            
            # If all fitnesses are equal, return random individual
            if len(set(fitnesses)) == 1:
                return random.choice(population)
            
            # Since we're minimizing, we need to invert the fitness values
            max_fitness = max(fitnesses)
            min_fitness = min(fitnesses)
            
            # Normalize and invert fitness values to range [0.1, 1.0]
            normalized_fitnesses = [(f - min_fitness) / (max_fitness - min_fitness) for f in fitnesses]
            inverted_fitnesses = [1.1 - nf for nf in normalized_fitnesses]  # Add 0.1 to avoid zero probabilities
            
            # Calculate selection probabilities
            total_fitness = sum(inverted_fitnesses)
            if total_fitness == 0:
                return random.choice(population)
                
            probabilities = [f / total_fitness for f in inverted_fitnesses]
            
            # Verify probabilities are valid
            if not all(0 <= p <= 1 for p in probabilities) or abs(sum(probabilities) - 1.0) > 0.0001:
                return self.tournament_select(population)
            
            # Select using the inverted probabilities
            return random.choices(population, weights=probabilities, k=1)[0]
        except Exception as e:
            print(f"Error in roulette_wheel_select: {e}")
            return self.tournament_select(population)
