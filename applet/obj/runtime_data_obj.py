

class RuntimeData(object):

    def __init__(self):
        self.msconvert_deal_count = 0

        self.diann_deal_count = 0

        self.deal_step = 0
        self.all_step_count = 11
        self.choose_file_list = []

        self.diann_all_count = len(self.choose_file_list)
        self.msconvert_all_count = len(self.choose_file_list)

        self.analysis_thread = None

        self.RUNNING_COLOR = '#f8c108'
        self.OVER_COLOR = '#27c14c'
        self.ERROR_COLOR = '#e91b40'


class MonitorConfigDataObj(object):
    def __init__(self):
        self.data_index = None
        self.monitor_dir = None
        self.lib_path = None
        self.raw_file_type = None
        self.filter_type_remark = None
        self.ins_select_id = None
        self.inst_name = None
        self.run_prefix = None
        self.output_dir = None
        self.file_filter_size = None
        self.filter_type = None
        self.filter_file_name = None



class RuntimeMonitorConfigData(object):
    def __init__(self):
        self.config_data_list = []


runtime_data = RuntimeData()

runtime_monitor_config_data = RuntimeMonitorConfigData()
