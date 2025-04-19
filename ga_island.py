import random
from cat.plugins.NaturalComputingPlugIn.ga_main import GeneticAlgorithm
from cat.plugins.NaturalComputingPlugIn.ga_initialization import InitializationStrategy

class IslandModel:
    def __init__(self, tasks, students, num_islands=4, migration_interval=10, migration_size=2):
        self.tasks = tasks
        self.students = students
        self.num_islands = num_islands
        self.migration_interval = migration_interval
        self.migration_size = migration_size
        self.best_solution = None
        self.best_solution_fitness = float('inf')
        self.island_fitness_history = [[] for _ in range(num_islands)]  # Track fitness for each island
        self.best_fitness_history = [[] for _ in range(num_islands)]  # Track best fitness history per island
        
        # Initialize islands with different configurations
        self.islands = []
        for i in range(num_islands):
            config = self._get_island_config(i)
            ga = GeneticAlgorithm(
                tasks=tasks,
                students=students,
                population_size=config['population_size'],
                generations=config['generations'],
                mutation_rate=config['mutation_rate'],
                crossover_rate=config['crossover_rate'],
                init_strategy=config['init_strategy'],
                crossover_strategy=config['crossover_strategy'],
                use_simulated_annealing=config['use_sa']
            )
            self.islands.append(ga)

    def run(self):
        """Run the island model"""
        print(f"\nStarting Island Model GA with {self.num_islands} islands")
        
        # Initialize all islands
        for i, island in enumerate(self.islands):
            print(f"\nInitializing Island {i}")
            island.initialize_population()
        
        # Run for specified number of generations
        for generation in range(100):
            print(f"\n=== Generation {generation + 1} ===")
            
            # Evolve each island
            for i, island in enumerate(self.islands):
                print(f"\nIsland {i}:")
                island.evolve_generation(generation)
                
                # Track fitness history for this island
                current_fitness = [island.get_fitness(sol) for sol in island.current_population]
                self.island_fitness_history[i].append(current_fitness)
                self.best_fitness_history[i].append(min(current_fitness))  # Track best fitness this generation
                
                # Update best solution
                if island.best_solution_fitness < self.best_solution_fitness:
                    self.best_solution = [row[:] for row in island.best_solution]  # Deep copy
                    self.best_solution_fitness = island.best_solution_fitness
                    print(f"New global best fitness: {self.best_solution_fitness:.2f}")
                
                # Print island statistics
                print(f"Island {i} Statistics:")
                print(f"  Best Fitness: {min(current_fitness):.2f}")
                print(f"  Average Fitness: {sum(current_fitness)/len(current_fitness):.2f}")
                print(f"  Population Fitness: {current_fitness}")
            
            # Migrate solutions between islands
            if generation % self.migration_interval == 0:
                self._migrate_solutions()
        
        print("\n=== Island Model GA Complete ===")
        print(f"Best fitness found: {self.best_solution_fitness:.2f}")
        print("\nFinal Island Statistics:")
        for i, history in enumerate(self.island_fitness_history):
            final_fitness = history[-1]  # Get the last generation's fitness values
            print(f"\nIsland {i}:")
            print(f"  Best Fitness: {min(final_fitness):.2f}")
            print(f"  Average Fitness: {sum(final_fitness)/len(final_fitness):.2f}")
            print(f"  Population Fitness: {final_fitness}")
            print(f"  Best Fitness History: {self.best_fitness_history[i]}")
            
        print("\nBest Fitness Progression Across All Generations:")
        # e
        
        return self.best_solution, self.best_solution_fitness

    def _migrate_solutions(self):
        """Migrate solutions between islands in a ring topology"""
        print("\nPerforming migration...")
        
        # For each island
        for i in range(self.num_islands):
            # Get source and destination islands
            source = i
            dest = (i + 1) % self.num_islands
            
            # Get best solutions from source island
            source_pop = self.islands[source].current_population
            if not source_pop:
                continue
            
            # Sort by fitness and select best solutions
            migrants = sorted(source_pop, 
                           key=lambda x: self.islands[source].get_fitness(x))[:self.migration_size]
            
            # Replace worst solutions in destination island
            dest_pop = self.islands[dest].current_population
            if dest_pop:
                # Sort by fitness (worst first)
                sorted_dest = sorted(dest_pop,
                                  key=lambda x: self.islands[dest].get_fitness(x),
                                  reverse=True)
                
                # Replace worst solutions with migrants
                for j, migrant in enumerate(migrants):
                    if j < len(sorted_dest):
                        idx = dest_pop.index(sorted_dest[j])
                        dest_pop[idx] = [row[:] for row in migrant]  # Deep copy
                
                # print(f"Migrated {len(migrants)} solutions from Island {source} to Island {dest}")
    
    def _get_island_config(self, island_id):
        """Get configuration for each island to promote diversity"""
        configs = [
            # Island 0: Standard configuration
            {
                'population_size': 50,
                'generations': 100,
                'mutation_rate': 0.1,
                'crossover_rate': 0.8,
                'init_strategy': InitializationStrategy.INTELLIGENT,
                'crossover_strategy': 'single_point',
                'use_sa': True
            },
            # Island 1: Higher mutation, lower crossover
            {
                'population_size': 50,
                'generations': 100,
                'mutation_rate': 0.2,
                'crossover_rate': 0.6,
                'init_strategy': InitializationStrategy.INTELLIGENT,
                'crossover_strategy': 'two_point',
                'use_sa': False
            },
            # Island 2: Lower mutation, higher crossover
            {
                'population_size': 50,
                'generations': 100,
                'mutation_rate': 0.05,
                'crossover_rate': 0.9,
                'init_strategy': InitializationStrategy.HYBRID,
                'crossover_strategy': 'single_point',
                'use_sa': False
            },
            # Island 3: Balanced with SA
            {
                'population_size': 50,
                'generations': 100,
                'mutation_rate': 0.1,
                'crossover_rate': 0.8,
                'init_strategy': InitializationStrategy.HYBRID,
                'crossover_strategy': 'single_point',
                'use_sa': True
            }
        ]
        return configs[island_id % len(configs)]
