import os

from loguru import logger
from pubsub import pub

from applet.db import db_utils
from applet.obj.Entity import FileScanParam
from applet.utils import file_utils


class FileScanService(object):

    def __init__(self, file_scan_param: FileScanParam):
        self.scan_dir_path = file_scan_param.source_dir_path
        self.interval_time = file_scan_param.interval_time
        self.file_suffix_list = ['.d', '.raw', '.wiff', '.RAW', '.WIFF']
        self.file_filter_size = file_scan_param.file_filter_size
        self.filter_type = file_scan_param.filter_type
        self.filter_file_name_list = file_scan_param.filter_file_name_list
        self.filter_file_name_list_relation = 'or'
        self.explain_filter_file_name_list()

        self.raw_file_type = file_scan_param.raw_file_type

    def recursive_scanning(self):
        pub.sendMessage('sync_msg', msg='Scan dir {}'.format(self.scan_dir_path))
        file_list = self.scan_dir(self.scan_dir_path)
        file_list = self.filter_file_list(file_list)
        file_list = list(set(file_list))
        file_list = self.check_wait_deal_file(file_list)
        return file_list

    def check_wait_deal_file(self, file_list):
        wait_deal_file = []
        for file_info in file_list:
            file_name = file_info[0]
            file_abs_path = file_info[1]
            out_time_limit = file_utils.is_file_modified_days_out_minute(file_abs_path, self.interval_time)
            if not out_time_limit:
                continue
            thiz_file_size = file_utils.get_file_size(file_abs_path)
            thiz_file_mtime = file_utils.get_file_mtime(file_abs_path)

            if self.raw_file_type == 'DIA':
                exist_file_info = db_utils.query_run_info_by_file_name(file_name, 1)
            else:
                raise Exception('')

            if exist_file_info:
                if thiz_file_size is None or thiz_file_mtime is None:
                    continue
                if exist_file_info.file_size == thiz_file_size:
                    continue
                if exist_file_info.file_type == 'D':
                    continue
            wait_deal_file.append(file_info)
        return wait_deal_file

    '''
    
    '''

    def scan_dir(self, dir_path):
        file_list = []
        for file_name in os.listdir(dir_path):
            thiz_file_path = os.path.join(dir_path, file_name)
            if os.path.isdir(thiz_file_path):
                if file_name.endswith('.d'):
                    out_time_limit = file_utils.is_file_modified_days_out_minute(thiz_file_path, self.interval_time)
                    if not out_time_limit:
                        continue
                    file_list.append((file_name, thiz_file_path))
                else:
                    dir_file_list = self.scan_dir(thiz_file_path)
                    file_list.extend(dir_file_list)
            else:
                if not self.check_file_format(file_name):
                    continue
                out_time_limit = file_utils.is_file_modified_days_out_minute(thiz_file_path, self.interval_time)
                if not out_time_limit:
                    continue
                file_list.append((file_name, thiz_file_path))
        return file_list

    def check_file_format(self, file_name: str):

        if not self.file_suffix_list or len(self.file_suffix_list) == 0:
            return True
        for file_type in self.file_suffix_list:
            if file_name.endswith(file_type):
                return True
        return False

    '''
    
    '''

    def filter_file_size(self, file_list):
        file_size_limit = self.file_filter_size
        if file_size_limit == 0:
            return file_list
        new_file_list = []
        file_size_limit_byte = file_size_limit * 1024 * 1024
        for file_info in file_list:
            current_file_size = file_utils.get_file_size(file_info[1])
            if current_file_size is None or current_file_size < file_size_limit_byte:
                continue
            new_file_list.append(file_info)
        return new_file_list

    def filter_file_list(self, file_list):
        logger.debug('Start filter file, limit file size = {}(MB), filter_type = {}, file_name = {}'.format(
            self.file_filter_size, self.filter_type, self.filter_file_name_list))
        if len(file_list) == 0:
            return file_list
        file_list = self.deal_filter_file_name(file_list)
        file_list = self.filter_file_size(file_list)
        return file_list

    '''
    '''

    def deal_filter_file_name(self, file_list):
        if not self.filter_file_name_list or len(self.filter_file_name_list) == 0:
            return file_list
        if self.filter_type == 1:
            return self.white_filter(file_list)
        elif self.filter_type == 2:
            return self.black_filter(file_list)
        else:
            return file_list

    '''
    '''

    def white_filter(self, file_list):
        new_file_list = []
        for file_info in file_list:
            current_file_name = file_info[0]
            if self.filter_file_name_list_relation == 'or':
                for filter_file_name in self.filter_file_name_list:
                    if filter_file_name in current_file_name:
                        new_file_list.append(file_info)
                        break
            else:
                #
                append_flag = True
                for filter_file_name in self.filter_file_name_list:
                    if filter_file_name not in current_file_name:
                        append_flag = False
                        break
                if append_flag:
                    new_file_list.append(file_info)
        return new_file_list

    '''
    '''

    def black_filter(self, file_list):
        remove_list = self.white_filter(file_list)
        return list(set(file_list) - set(remove_list))

    '''
    
    '''

    def deal_rela_path(self, file_list):
        pass

    '''
    
    '''

    def explain_filter_file_name_list(self):
        if not self.filter_file_name_list or len(str(self.filter_file_name_list).strip()) == 0:
            return []
        if '|' in self.filter_file_name_list:
            self.filter_file_name_list = str(self.filter_file_name_list).split('|')
            self.filter_file_name_list_relation = 'or'
        elif '&' in self.filter_file_name_list:
            self.filter_file_name_list = str(self.filter_file_name_list).split('&')
            self.filter_file_name_list_relation = 'and'
        else:
            self.filter_file_name_list = [self.filter_file_name_list]
            self.filter_file_name_list_relation = 'or'
