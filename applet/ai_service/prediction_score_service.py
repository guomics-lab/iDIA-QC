import collections
import os

import pandas as pd
import xgboost
from pycaret.classification import *

from applet.db import db_utils_run_data
from applet.obj.DBEntity import PredInfo
from applet.obj.Entity import FileInfo
from applet.service import common_service
from applet.utils import ai_pred_data_build_util

# Score_1.0
SCORE_1_FLAG = 'prediction_score_1'
SCORE_0_FLAG = 'prediction_score_0'
# Label
LABEL_FLAG = 'label'

PREDICTION_SCORE_FLAG = 'pred_1_score'
PREDICTION_LABEL_FLAG = 'prediction_label'


class PredictionScoreService(common_service.CommonService):

    def __init__(self, model_dir, base_output_path, file_list: [FileInfo], logger, step=10,
                 pub_channel='analysis_info', start_time=0, conn_send=None):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time, conn_send=conn_send)
        self.model_dir = model_dir
        self.logger = logger
        self.models = self.load_models()

    def load_models(self):
        models = collections.defaultdict(dict)
        try:
            if self.logger:
                self.logger.info(
                    'load model, dir: {}, xgboost.__version__ = {}'.format(self.model_dir, xgboost.__version__))

            for name in os.listdir(self.model_dir):
                if self.logger:
                    self.logger.info('load model, name: {}'.format(name))
                name = name.replace('.pkl', '')
                name_parts = [partn for partn in name.split('_') if partn]
                feat_name = name_parts[-1]
                mpath = os.path.join(self.model_dir, name.replace('.pkl', ''))
                model = load_model(mpath)
                models[feat_name] = model
            if self.logger:
                self.logger.info('end load model')
        except Exception:
            if self.logger:
                self.logger.exception('load model exception')
        return models

    def deal_process(self):
        pass

    def deal_prediction_score(self, save_data_list):
        self.send_msg(0, '{} Predicting the LC-MS performance by the machine learning model'.format(self.get_now_use_time()))
        self.send_msg(9, '{} Processing'.format(self.get_now_use_time()))
        save_pred_info_list = []
        #
        for thiz_save_data in save_data_list:
            run_info = thiz_save_data[0]
            run_data_list = thiz_save_data[1]
            f4_data_list = thiz_save_data[2]
            s7_data_list = thiz_save_data[3]
            pred_info_list = self.prediction_all_score(run_info, run_data_list, f4_data_list,
                                                       s7_data_list)
            save_pred_info_list.extend(pred_info_list)
        self.send_msg(1, '{} Finished the prediction'.format(self.get_now_use_time()))
        return save_pred_info_list

    '''
    prediction
    '''

    def prediction_score(self, data, feat_tsname):
        model = self.models[feat_tsname]
        pred_rlts = predict_model(model, data=data, raw_score=True)
        pred_out = {}
        if feat_tsname == 'F2':
            pred_out[PREDICTION_SCORE_FLAG] = pred_rlts[SCORE_0_FLAG].tolist()[0]
            pred_out[PREDICTION_LABEL_FLAG] = 1 - pred_rlts[PREDICTION_LABEL_FLAG].tolist()[0]
        else:
            pred_out[PREDICTION_SCORE_FLAG] = pred_rlts[SCORE_1_FLAG].tolist()[0]
            pred_out[PREDICTION_LABEL_FLAG] = pred_rlts[PREDICTION_LABEL_FLAG].tolist()[0]
        if self.logger:
            self.logger.info('prediction score over, score: {}, pred_label: {}, feat_tsname: {}'.format(pred_out[PREDICTION_SCORE_FLAG],
                                                                                                        pred_out[PREDICTION_LABEL_FLAG], feat_tsname))

        return pred_out

    def batch_prediction_score(self, data, feat_tsname):
        model = self.models[feat_tsname]
        pred_rlts = predict_model(model, data=data, raw_score=True)
        return pred_rlts

    def prediction_all_score(self, run_info, run_data_list, f4_data_list, s7_data_list):
        df_lc_data, df_ms_data = ai_pred_data_build_util.build_data(run_info, run_data_list, f4_data_list, s7_data_list)
        run_id = run_info.run_id
        seq_id = run_info.seq_id
        pred_info_list = []
        for feat_name in ['lc', 'F1', 'F2', 'F3']:
            pred_info = PredInfo()
            lc_pred_out = self.prediction_score(df_lc_data, feat_name)
            pred_info.run_id = run_id
            pred_info.seq_id = seq_id
            pred_info.pred_key = feat_name
            pred_info.pred_score = round(float(lc_pred_out[PREDICTION_SCORE_FLAG]), 3)
            pred_info.pred_label = int(lc_pred_out[PREDICTION_LABEL_FLAG])
            pred_info_list.append(pred_info)

        for feat_name in ['ms', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15']:
            ms_pred_out = self.prediction_score(df_ms_data, feat_name)
            pred_info = PredInfo()
            pred_info.run_id = run_id
            pred_info.seq_id = seq_id
            pred_info.pred_key = feat_name
            pred_info.pred_score = round(float(ms_pred_out[PREDICTION_SCORE_FLAG]), 3)
            pred_info.pred_label = int(ms_pred_out[PREDICTION_LABEL_FLAG])
            pred_info_list.append(pred_info)
        return pred_info_list

    def save_to_csv_old(self, output_path):
        pred_output_path = os.path.join(output_path, 'pred')
        if not os.path.exists(pred_output_path):
            os.mkdir(pred_output_path)

        lc_pred_path = os.path.join(pred_output_path, 'lc_pred')
        ms_pred_path = os.path.join(pred_output_path, 'ms_pred')
        if not os.path.exists(lc_pred_path):
            os.mkdir(lc_pred_path)
        if not os.path.exists(ms_pred_path):
            os.mkdir(ms_pred_path)

        seq_id_list = db_utils_run_data.query_all_seq_id()
        pred_info_list = db_utils_run_data.query_all_pred_info(seq_id_list)
        pred_info_key_dict = {}
        for pred_info in pred_info_list:
            if pred_info.pred_label == 0:
                pred_label = 'qualified '
            elif pred_info.pred_label == 1:
                pred_label = 'unqualified'
            else:
                pred_label = 'unknown'
            pred_info_key_dict.setdefault(pred_info.pred_key, []).append(
                {'Run_ID': pred_info.run_id, 'pred_1_score': pred_info.pred_score, 'pred_label': pred_label})

        for key, val in pred_info_key_dict.items():
            save_df = pd.DataFrame(val)
            if key in ['lc', 'F2', 'F3', 'F4']:
                save_df.to_csv(os.path.join(lc_pred_path, '{}_prediction.csv'.format(key)))
            else:
                save_df.to_csv(os.path.join(ms_pred_path, '{}_prediction.csv'.format(key)))

    def save_to_csv(self, output_path, data_source, run_prefix=None):
        pred_output_path = os.path.join(output_path, 'pred')
        if not os.path.exists(pred_output_path):
            os.mkdir(pred_output_path)

        PRED_KEY_LIST = ['lc', 'F1', 'F2', 'F3', 'ms', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15']

        # seq_id_list = db_utils_run_data.query_all_seq_id()
        run_info_list = db_utils_run_data.query_run_info_all(data_source)
        seq_id_list = [d.seq_id for d in run_info_list]
        pred_info_list = db_utils_run_data.query_all_pred_info(seq_id_list)
        seq_pred_label_dict = collections.defaultdict(dict)
        seq_pred_score_dict = collections.defaultdict(dict)
        for pred_info in pred_info_list:
            if pred_info.pred_label == 0:
                pred_label = 'qualified '
            elif pred_info.pred_label == 1:
                pred_label = 'unqualified'
            else:
                pred_label = 'unknown'
            seq_pred_label_dict[pred_info.seq_id][pred_info.pred_key] = pred_label
            seq_pred_score_dict[pred_info.seq_id][pred_info.pred_key] = pred_info.pred_score

        #
        save_data_list = []
        for run_info in run_info_list:
            run_id = run_info.run_id
            save_data = {'Run_ID': run_id}
            for pred_key in PRED_KEY_LIST:
                if run_info.file_type != 'D' and pred_key == 'F15':
                    save_data[str(pred_key) + '_score'] = '-'
                    save_data[str(pred_key)] = '-'
                else:
                    save_data[str(pred_key) + '_score'] = seq_pred_score_dict[run_info.seq_id][pred_key]
                    save_data[str(pred_key)] = seq_pred_label_dict[run_info.seq_id][pred_key]
            save_data_list.append(save_data)
        save_df = pd.DataFrame(save_data_list)
        save_df.to_csv(os.path.join(pred_output_path, 'prediction.csv'), mode='w+')
