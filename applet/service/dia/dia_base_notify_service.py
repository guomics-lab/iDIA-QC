import requests

from applet import common_utils
from applet.db import db_utils_run_data
from applet.service import common_service

common_config = common_utils.read_yml()

#
mail_host = common_config['notify']['mail_host']  #
mail_user = common_config['notify']['mail_user']  #
mail_pass = common_config['notify']['mail_pass']  #


class DIABaseNotifyService(common_service.CommonService):
    def __init__(self, base_output_path, wx_token_list: str, run_prefix, logger,
                 step=13,
                 pub_channel='analysis_info', start_time=0, conn_send=None):
        common_service.CommonService.__init__(self, base_output_path, [], logger, step, pub_channel, start_time,
                                              conn_send=conn_send)
        self.run_prefix = run_prefix
        self.wx_token_list = wx_token_list

    #
    def deal_process(self):
        logger = self.logger
        try:
            self.send_msg(0, 'Sending the result to: {}'.format(self.wx_token_list), with_time=True)
            #
            diann_data_list = self.query_build_data(self.run_prefix)
            self.deal_send_wx(diann_data_list, self.run_prefix)
            self.send_msg(1, msg='')
            return True
        except Exception as e:
            logger.exception('msg send exception')
            self.send_msg(3, msg='Notify send exception: {}'.format(e))
        return True

    def deal_send_by_run_prefix(self, run_prefix):
        logger = self.logger
        try:
            self.send_msg(0, 'Sending the result to: {}'.format(self.wx_token_list), with_time=True)
            #
            diann_data_list = self.query_build_data(self.run_prefix)
            self.deal_send_wx(diann_data_list, self.run_prefix)
            self.send_msg(1, msg='')
            return True
        except Exception as e:
            logger.exception('msg send exception')
            self.send_msg(3, msg='Notify send exception: {}'.format(e))
        return True

    def query_build_data(self, run_prefix):
        diann_data_list = db_utils_run_data.query_diann_data_list_recent(5, run_prefix)
        return diann_data_list

    '''
    
    '''

    def deal_send_wx(self, diann_data_list, run_prefix):
        logger = self.logger
        try:
            wx_notify_token = self.wx_token_list
            if wx_notify_token is None or len(wx_notify_token) == 0:
                self.send_msg(1, msg='There is no need email to notify')
                return True
            #
            title, markdown_content = self.build_wx_msg_markdown_content(diann_data_list, run_prefix)
            token_list = wx_notify_token.split(';')
            for token in token_list:
                self.send_wx_msg(token, title, markdown_content)
        except Exception as e:
            logger.exception('wx send exception')
            self.send_msg(3, msg='Email send exception: {}'.format(e))

    def send_wx_msg(self, token, title, markdown_content):
        logger = self.logger
        try:
            url = 'http://www.pushplus.plus/send'
            data_json = {
                'token': token,
                'template': 'markdown',
                'title': title,
                'content': markdown_content
            }
            logger.info('push wx msg：{}'.format(data_json))
            resp = requests.post(url, json=data_json)
            logger.info('push wx success：{}'.format(resp.text))
        except Exception:
            logger.exception('push wx exception')

    def build_wx_msg_markdown_content(self, diann_data_list, run_prefix):

        if len(diann_data_list) > 0:
            title = 'DIA base-' + run_prefix
        else:
            title = 'DIA base'

        markdown_content_list = []
        markdown_content1 = '|Run name | Identified peptides | Identified proteins|'
        markdown_content2 = '|-------- | ----- | ----- |'

        markdown_content_list.append(markdown_content1)
        markdown_content_list.append(markdown_content2)
        for run_info in diann_data_list:
            markdown_content_list.append(
                '|{} | {} | {}|'.format(run_info['file_name'], run_info['precursor_ident'],
                                        run_info['protein_ident']))

        markdown_content = '\n'.join(markdown_content_list)
        return title, markdown_content
