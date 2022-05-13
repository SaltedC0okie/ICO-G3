from jmetal.core.problem import PermutationProblem
from jmetal.core.solution import PermutationSolution
import random


class TimeTablingProblem(PermutationProblem):

    def __init__(self, lessons: list, classrooms: list, metrics: list):
        super(PermutationProblem, self).__init__()

        self.lessons = lessons
        self.classrooms = classrooms
        self.metrics = metrics

        self.number_of_objectives = len(metrics)
        self.number_of_variables = max(len(self.lessons), len(self.classrooms))
        #self.number_of_variables = len(self.classrooms)
        self.number_of_constraints = 0

        self.obj_directions = [m.objective for m in metrics] # metrics[0].objective
        # self.obj_labels = ['Lower_half']

    def evaluate(self, solution: PermutationSolution):
        created_schedule = []

        for i, classroom_index in enumerate(solution.variables):
            if i >= len(self.lessons):
                break
            if classroom_index > -1:
                #print("c:", classroom_index, " i:", i)
                if self.classrooms[classroom_index].is_available(self.lessons[i].time_blocks):
                    created_schedule.append((self.lessons[i], self.classrooms[classroom_index]))
                else:
                    created_schedule.append((self.lessons[i], None))
            else:
                created_schedule.append((self.lessons[i], None))
        for i, metric in enumerate(self.metrics):
            #for j in created_schedule:
            #    metric.calculate(j[0], j[1])
            metric.calculate(created_schedule)
            solution.objectives[i] = metric.get_percentage()
            metric.reset_metric()

        return solution

    def create_solution(self) -> PermutationSolution:
        new_solution = PermutationSolution(self.number_of_variables, self.number_of_objectives) # No clue about lower and upper
        if len(self.lessons) < len(self.classrooms):
            #new_solution.variables = random.sample(range(len(self.classrooms)), len(self.classrooms))
            #new_solution.variables = random.sample([i for i in range(len(self.classrooms))], len(self.classrooms))
            new_solution.variables = [i for i in range(len(self.classrooms))]
        else:
            # sample = random.sample(range(len(self.classrooms)), len(self.classrooms))

            variables = []
            for i in range(len(self.lessons)):
                if i < len(self.classrooms):
                    variables.append(i)
                else:
                    variables.append(-1 * i)
            new_solution.variables = variables
        return new_solution

    def get_name(self) -> str:
        return "permutation timetabling";