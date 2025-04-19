class FitnessCalculator:
    def __init__(self, tasks, students):
        self.tasks = tasks
        self.students = students
        # Weight constants
        self.w1 = 1.0  # time penalty weight
        self.w2 = 3.0  # dependency penalty weight
        self.w3 = 2.0  # skill penalty weight
        self.w4 = 1.0  # workload balance weight
        self.w5 = 4.0  # overlap penalty weight

    def calculate_fitness(self, solution):
        """Calculate fitness based on the mathematical formulation F(s) = w₁P_time + w₂P_dep + w₃P_skill + w₄P_load + w₅P_overlap"""
        if not solution:
            return float('inf')

        # Calculate completion times and total duration
        completion_times = {}
        start_times = {}
        total_task_duration = sum(float(task['estimated_time']) for task in self.tasks.values())
        student_workloads = {s: 0.0 for s in self.students}
        student_timelines = {s: [] for s in self.students}  # For overlap detection

        # First pass: calculate completion times and workloads
        for task_id, student_id, start_time in solution:
            task = self.tasks[task_id]
            duration = float(task['estimated_time'])
            start_time = float(start_time)
            completion_time = start_time + duration
            
            completion_times[task_id] = completion_time
            start_times[task_id] = start_time
            student_workloads[student_id] += duration
            student_timelines[student_id].append((start_time, completion_time))

        # Check for missing tasks
        if len(completion_times) != len(self.tasks):
            return float('inf')

        # 1. Time Penalty (P_time)
        total_completion_time = max(completion_times.values()) - min(start_times.values())
        p_time = (total_completion_time / total_task_duration) * 100

        # 2. Dependency Penalty (P_dep)
        p_dep = 0
        for task_id, task in self.tasks.items():
            for dep_id in task['dependencies']:
                if dep_id not in completion_times:
                    return float('inf')
                if start_times[task_id] < completion_times[dep_id]:
                    violation = completion_times[dep_id] - start_times[task_id]
                    p_dep += 300 * (violation / total_task_duration)

        # 3. Skill Penalty (P_skill)
        p_skill = 0
        for task_id, student_id, _ in solution:
            task = self.tasks[task_id]
            student = self.students[student_id]
            for skill, required_level in task['skill_requirements'].items():
                student_level = student['skills'].get(skill, 0)
                if student_level < required_level:
                    p_skill += 200 * (required_level - student_level)

        # 4. Workload Balance Penalty (P_load)
        max_workload = max(student_workloads.values())
        min_workload = min(student_workloads.values())
        avg_workload = total_task_duration / len(self.students)
        
        if avg_workload == 0:
            p_load = float('inf')
        else:
            p_load = 100 * (max_workload - min_workload) / avg_workload

        # 5. Overlap Penalty (P_overlap)
        p_overlap = 0
        for student_id, timeline in student_timelines.items():
            timeline.sort()  # Sort by start time
            for i in range(len(timeline) - 1):
                if timeline[i][1] > timeline[i + 1][0]:
                    overlap_duration = timeline[i][1] - timeline[i + 1][0]
                    p_overlap += 400 * (overlap_duration / total_task_duration)

        # Calculate final fitness
        fitness = (self.w1 * p_time + 
                  self.w2 * p_dep + 
                  self.w3 * p_skill + 
                  self.w4 * p_load +
                  self.w5 * p_overlap)

        return fitness
