class Progress:

    def __init__(self):
        self.total_tasks_simple = -1
        self.total_tasks_weekly_det = -1
        self.total_tasks_weekly_jmp = -1
        self.total_tasks_overbooking_det = -1
        self.total_tasks_overbooking_jmp = -1
        self.total_tasks_metrics = -1
        self.cur_tasks_simple = 0
        self.cur_tasks_weekly_det = 0
        self.cur_tasks_weekly_jmp = 0
        self.cur_tasks_overbooking_det = 0
        self.cur_tasks_overbooking_jmp = 0
        self.cur_tasks_metrics = 0

    def set_total_tasks_simple(self, value):
        self.total_tasks_simple = value

    def set_total_tasks_weekly_det(self, value):
        self.total_tasks_weekly_det = value

    def set_total_tasks_weekly_jmp(self, value):
        self.total_tasks_weekly_jmp = value

    def set_total_tasks_overbooking_det(self, value):
        self.total_tasks_overbooking_det = value

    def set_total_tasks_overbooking_jmp(self, value):
        self.total_tasks_overbooking_jmp = value

    def set_total_tasks_metrics(self, value):
        self.total_tasks_metrics = value

    def get_progress(self):
        percent = 0
        if self.total_tasks_simple != -1:
            percent += (self.cur_tasks_simple / self.total_tasks_simple) * 25
        if self.total_tasks_weekly_det != -1:
            percent += (self.cur_tasks_weekly_det / self.total_tasks_weekly_det) * 12
        if self.total_tasks_weekly_jmp != -1:
            percent += (self.cur_tasks_weekly_jmp / self.total_tasks_weekly_jmp) * 13
        if self.total_tasks_overbooking_det != -1:
            percent += (self.cur_tasks_overbooking_det / self.total_tasks_overbooking_det) * 12
        if self.total_tasks_overbooking_jmp != -1:
            percent += (self.cur_tasks_overbooking_jmp / self.total_tasks_overbooking_jmp) * 13
        if self.total_tasks_metrics != -1:
            percent += (self.cur_tasks_metrics / self.total_tasks_metrics) * 25

        return percent

    def inc_cur_tasks_simple(self):
        self.cur_tasks_simple += 1

    def reset_cur_tasks_simple(self):
        self.cur_tasks_simple = 0

    def inc_cur_tasks_weekly_det(self):
        self.cur_tasks_weekly_det += 1

    def reset_cur_tasks_weekly_det(self):
        self.cur_tasks_weekly_det = 0

    def inc_cur_tasks_weekly_jmp(self):
        self.cur_tasks_weekly_jmp += 1

    def reset_cur_tasks_weekly_jmp(self):
        self.cur_tasks_weekly_jmp = 0

    def inc_cur_tasks_overbooking_det(self):
        self.cur_tasks_overbooking_det += 1

    def reset_cur_tasks_overbooking_det(self):
        self.cur_tasks_overbooking_det = 0

    def inc_cur_tasks_overbooking_jmp(self):
        self.cur_tasks_overbooking_jmp += 1

    def reset_cur_tasks_overbooking_jmp(self):
        self.cur_tasks_overbooking_jmp = 0

    def inc_cur_tasks_metrics(self):
        self.cur_tasks_metrics += 1

    def reset_cur_tasks_metrics(self):
        self.cur_tasks_metrics = 0