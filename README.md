# Natural Computing Plugin

A Cheshire Cat AI plugin that implements genetic algorithms and other natural computing techniques for task scheduling and optimization.

## Overview

The Natural Computing Plugin provides a suite of bio-inspired computing algorithms, primarily focused on genetic algorithms for task scheduling and optimization. It's designed to work with the Cheshire Cat AI system to provide intelligent task scheduling solutions.

## Features

### Core Functionality
- **Genetic Algorithm Implementation** (Implemented in `ga_main.py`)
  - Population initialization (`ga_initialization.py`)
  - Fitness calculation (`ga_fitness.py`)
  - Selection mechanisms (`ga_selection.py`)
  - Crossover operations (`ga_crossover.py`)
  - Mutation strategies (`ga_mutation.py`)
  - Local search optimization (`ga_local_search.py`)
  - Simulated annealing (`ga_simulated_annealing.py`)

### Advanced Features
- **Island Model Support** (Implemented in `ga_island.py`)
  - Parallel processing capabilities
  - Population migration
  - Multiple evolution strategies

- **Optimization Techniques**
  - Local search optimization
  - Simulated annealing
  - Fitness caching
  - Customizable parameters

## Testing Plan

### Overview
The Natural Computing Plugin implements a comprehensive testing strategy to ensure reliability, performance, and correctness. The testing plan covers all aspects of the genetic algorithm implementation and its integration with the Cheshire Cat system.

### Test Categories

#### 1. Unit Testing
Located in `tests/unit/`:

```python
# tests/unit/test_fitness.py
def test_fitness_calculation():
    """Test basic fitness calculation"""
    solution = create_test_solution()
    fitness = calculate_fitness(solution)
    assert fitness >= 0
    assert fitness <= 1

def test_skill_matching():
    """Test skill matching component"""
    student_skills = {"programming": 0.8}
    task_requirements = {"programming": 0.6}
    match_score = calculate_skill_match(student_skills, task_requirements)
    assert match_score > 0

# tests/unit/test_selection.py
def test_tournament_selection():
    """Test tournament selection mechanism"""
    population = create_test_population()
    parents = tournament_selection(population, tournament_size=3)
    assert len(parents) == 2
    assert parents[0] != parents[1]
```

#### 2. Integration Testing
Located in `tests/integration/`:

```python
# tests/integration/test_workflow.py
def test_complete_evolution():
    """Test complete evolution process"""
    input_data = load_test_data()
    result = run_genetic_algorithm(input_data)
    assert is_valid_solution(result)
    assert meets_constraints(result)

# tests/integration/test_io.py
def test_input_validation():
    """Test input validation"""
    invalid_input = create_invalid_input()
    with pytest.raises(ValidationError):
        validate_input(invalid_input)
```

#### 3. Performance Testing
Located in `tests/performance/`:

```python
# tests/performance/test_convergence.py
def test_convergence_speed():
    """Test algorithm convergence speed"""
    start_time = time.time()
    result = run_genetic_algorithm(input_data)
    convergence_time = time.time() - start_time
    assert convergence_time < max_allowed_time

# tests/performance/test_memory.py
def test_memory_usage():
    """Test memory consumption"""
    memory_before = get_memory_usage()
    result = run_genetic_algorithm(input_data)
    memory_after = get_memory_usage()
    assert memory_after - memory_before < max_memory_increase
```

#### 4. Usability Testing
Located in `tests/usability/`:

```python
# tests/usability/test_config.py
def test_config_interface():
    """Test configuration interface"""
    config = load_config()
    assert config.is_valid()
    assert config.is_user_friendly()

# tests/usability/test_messages.py
def test_error_messages():
    """Test error message clarity"""
    error = generate_error("invalid_input")
    assert error.is_clear()
    assert error.suggests_solution()
```

### Test Environment Setup

1. **Prerequisites**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows

   # Install test dependencies
   pip install -r requirements-test.txt

   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

2. **Running Tests**
   ```bash
   # Run all tests
   python -m pytest tests/

   # Run specific test categories
   python -m pytest tests/unit/      # Unit tests
   python -m pytest tests/integration/  # Integration tests
   python -m pytest tests/performance/  # Performance tests
   python -m pytest tests/usability/   # Usability tests

   # Run with coverage report
   python -m pytest --cov=ga_main tests/
   ```

3. **Continuous Integration**
   The plugin uses GitHub Actions for CI:
   ```yaml
   name: Test
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt
             pip install -r requirements-test.txt
         - name: Run tests
           run: |
             python -m pytest tests/ --cov=ga_main
   ```

### Test Coverage Goals
- Unit Tests: >90% coverage
- Integration Tests: >80% coverage
- Performance Tests: All critical paths
- Usability Tests: All user-facing features

### Test Data Management
1. **Sample Data**
   - Located in `tests/data/`
   - Includes various input scenarios
   - Covers edge cases and common use cases

2. **Data Generation**
   ```python
   def create_test_solution():
       """Generate a valid test solution"""
       return {
           "tasks": generate_tasks(),
           "assignments": generate_assignments(),
           "schedule": generate_schedule()
       }
   ```

### Error Handling Tests
1. **Input Validation**
   - Invalid JSON formats
   - Missing required fields
   - Incorrect data types
   - Out-of-range values

2. **Algorithm Errors**
   - Convergence failures
   - Invalid solutions
   - Resource constraints
   - Timeout scenarios

3. **Integration Errors**
   - Cheshire Cat communication
   - File system operations
   - Network connectivity
   - Resource availability

### Performance Benchmarks
1. **Metrics**
   - Convergence time
   - Memory usage
   - CPU utilization
   - Solution quality

2. **Thresholds**
   - Maximum execution time
   - Memory limits
   - CPU usage limits
   - Minimum solution quality

## Installation

1. Place the `NaturalComputingPlugIn` folder in your Cheshire Cat plugins directory:
   ```
   core/cat/plugins/NaturalComputingPlugIn/
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the plugin in `plugin.json`:
   ```json
   {
       "name": "Natural Computing Plugin",
       "description": "Genetic algorithms and natural computing techniques",
       "version": "1.0.0",
       "author": "Your Name",
       "entry_point": "ga_main"
   }
   ```

## Usage

### Basic Usage
1. Prepare input data in JSON format (see Expected Input Format)
2. Call the genetic algorithm tool:
   ```python
   result = run_genetic_algorithm(input_data, cat)
   ```
3. Process the results:
   ```python
   solution = json.loads(result)
   print_schedule(tasks, students, solution)
   ```

## Customization

The plugin can be configured through `plugin.json`:
```json
{
    "name": "Natural Computing Plugin",
    "description": "Genetic algorithms and natural computing techniques",
    "version": "1.0.0",
    "author": "Your Name",
    "entry_point": "ga_main",
    "settings": {
        "population_size": 50,
        "generations": 100,
        "mutation_rate": 0.1,
        "crossover_rate": 0.8,
        "use_local_search": true,
        "use_simulated_annealing": false
    }
}
```

## Changelog

### Version 1.0.0
- Initial release
- Basic genetic algorithm implementation
- Island model support
- Local search and simulated annealing
- Integration with Cheshire Cat

### Version 1.0.1 (Planned)
- Enhanced fitness calculation
- Improved mutation strategies
- Additional optimization techniques
- Better error handling

## Dependencies

- Python 3.x
- Cheshire Cat AI system
- Required packages (specified in requirements.txt)

## Troubleshooting

Common issues and solutions:
1. **Convergence Issues**: Adjust population size or mutation rate
2. **Memory Errors**: Reduce population size or generations
3. **Invalid Solutions**: Check input data format
4. **Performance Issues**: Enable parallel processing

## Support

For issues or questions:
1. Check the Cheshire Cat documentation
2. Review the plugin's error logs
3. Create an issue in the repository

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This plugin is licensed under the same terms as the Cheshire Cat AI project.

## How It Works

The Natural Computing Plugin follows a multi-step process to optimize task scheduling:

### 1. Input Processing
- User input is received in JSON format containing tasks, students and their skills are retrieved from a dynamo DB on AWS
- Input is validated for required fields and correct data types
- Data is structured for the genetic algorithm

### 2. Population Initialization
- Initial population of solutions is created using strategies from `ga_initialization.py`
- Each solution represents a possible task assignment schedule
- Population size is determined by configuration settings

### 3. Evolution Process
The algorithm iterates through generations, with each generation following these steps:

1. **Fitness Evaluation** (`ga_fitness.py`)
   - Each solution is evaluated based on:
     * Task completion times
     * Student workload balance
     * Skill matching
     * Dependencies satisfaction
   - Fitness scores are calculated and cached

2. **Selection** (`ga_selection.py`)
   - Parents are selected based on fitness scores
   - Tournament selection is used to maintain diversity
   - Best solutions are preserved (elitism)

3. **Crossover** (`ga_crossover.py`)
   - Selected parents are combined to create offspring
   - Single-point crossover is used by default
   - Task assignments are recombined while maintaining validity

4. **Mutation** (`ga_mutation.py`)
   - Random changes are introduced to maintain diversity
   - Task assignments are swapped between students
   - Start times are adjusted within constraints

5. **Local Search** (`ga_local_search.py`)
   - Optional step to improve solutions
   - Neighboring solutions are explored
   - Best improvements are kept

6. **Simulated Annealing** (`ga_simulated_annealing.py`)
   - Optional step for global optimization
   - Temperature-based acceptance of worse solutions
   - Helps escape local optima

### 4. Island Model (Optional)
If enabled, the process includes:
- Multiple populations evolving in parallel
- Periodic migration of best solutions between islands
- Different evolution strategies per island

### 5. Termination
The process stops when either:
- Maximum generations are reached
- Solution quality plateaus
- Time limit is exceeded

### 6. Output Generation
- Best solution is selected from final population
- Task assignments are formatted into JSON
- Schedule is validated for constraints
- Final output is returned to the user

### Example Workflow
```
Input Data
   ↓
Population Initialization
   ↓
For each generation:
   ├─ Fitness Evaluation
   ├─ Selection
   ├─ Crossover
   ├─ Mutation
   ├─ Local Search (optional)
   └─ Simulated Annealing (optional)
   ↓
Termination Check
   ↓
Output Generation
```

### Key Implementation Files
- `ga_main.py`: Orchestrates the entire process
- `ga_fitness.py`: Implements the fitness function
- `ga_initialization.py`: Handles population creation
- `ga_selection.py`: Manages parent selection
- `ga_crossover.py`: Implements solution recombination
- `ga_mutation.py`: Handles solution variation
- `ga_local_search.py`: Provides local optimization
- `ga_simulated_annealing.py`: Implements global optimization
- `ga_island.py`: Manages parallel processing
