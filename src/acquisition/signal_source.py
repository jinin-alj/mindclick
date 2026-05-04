class IdealSignalSource(SignalSource):
    def __init__(self, target_row_index, target_column_index):
        self.target_row_index = target_row_index
        self.target_column_index = target_column_index

    def predict_target_flash(self, group_type, group_index):
        if group_type == "row" and group_index == self.target_row_index:
            return True
        if group_type == "column" and group_index == self.target_column_index:
            return True
        return False