import os.path
import pickle
import uuid

import numpy as np
import pandas as pd

from applet.db import db_utils_run_data
from applet.obj.DBEntity import DIAOutputInfo
from applet.obj.DBEntity import RunInfo, RunData, RunDataF4, RunDataS7
from applet.obj.Entity import FileInfo, FileTypeEnum
from applet.obj.PeptInfo import f_3_pept_list, f_15_16_pept_list, f3_and_f15_pept_list
from applet.service import common_service

sequence_gravy_dict = {'LSVLLLER': 1.325, 'LYDNLLEQNLIR': -0.3, 'TGQAAGFSYTDANK': -0.75, 'FDDGAGGDNEVQR': -1.376923077,
                       'DLQNVNITLR': -0.29, 'TKPYIQVDIGGGQTK': -0.706666667, 'FGLGSIAGAVGATAVYPIDLVK': 1.172727273,
                       'LAANAFLAQR': 0.61, 'GGENIYPAELEDFFLK': -0.35, 'LSISGNYNLK': -0.21,
                       'GANAVGYTNYPDNVVFK': -0.270588235, 'LGPNEQYK': -1.7375, 'FAELAQIYAQR': 0.018181818,
                       'TFESLVDFCK': 0.37, 'AVSNVIASLIYAR': 1.207692308, 'FYSVNVDYSK': -0.39,
                       'SETAPAAPAAPAPAEK': -0.3875, 'LEAALADVPELAR': 0.476923077, 'IEDVTPIPSDSTR': -0.615384615,
                       'LTITYGPK': -0.0375, 'SVGEVMAIGR': 0.7, 'IALGIPLPEIK': 1.081818182, 'AGLQFPVGR': 0.244444444,
                       'LLLPGELAK': 0.844444444, 'AIAEELAPER': -0.29, 'FLEEATR': -0.542857143, 'MPEFYNR': -1.385714286,
                       'LFAEAVQK': 0.4375, 'IMGTSPLQIDR': -0.027272727}


class DIADataSaveService(common_service.CommonService):

    def __init__(self, data_source, base_output_path, s3_dir_path, s7_dir_path, file_list: [FileInfo], logger, step=9,
                 pub_channel='analysis_info', start_time=0, conn_send=None):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time, conn_send=conn_send)
        self.s3_dir_path = s3_dir_path
        # F4
        self.f4_file_path = None
        # F8
        self.f8_file_path = None
        # F11
        self.f11_file_path = None
        self.data_source = data_source

        self.s7_dir_path = s7_dir_path

        self.run_id_seq_dict = {}
        self.run_name_seq_dict = {}

    def build_run_info(self, file_info: [FileInfo]):
        delete_flag = False
        run_info = RunInfo()
        run_info.run_prefix = file_info.run_prefix
        run_info.inst_name = file_info.inst_name
        run_info.run_id = file_info.run_id
        run_info.run_name = file_info.run_name
        run_info.file_name = file_info.file_name
        run_info.file_type = file_info.file_type.name
        run_info.is_delete = 0
        run_info.source = self.data_source
        run_info.seq_id = str(uuid.uuid4())
        run_info.last_modify_time = file_info.last_modify_time
        run_info.file_size = file_info.file_size
        self.run_id_seq_dict[run_info.run_id] = run_info.seq_id
        self.run_name_seq_dict[run_info.run_name] = run_info.seq_id
        return delete_flag, run_info

    def build_save_data(self):
        logger = self.logger
        try:
            self.is_running = True
            logger.info('Start deal data save, read data')
            delete_run_info = []

            save_data = []
            diann_data_list = []
            for file_info in self.file_list:
                save_run_data_list = []
                save_run_data_f4 = []
                save_run_data_s7 = []

                delete_flag, run_info = self.build_run_info(file_info)
                if delete_flag:
                    delete_run_info.append(file_info.run_name)
                f4_data_list = self.read_f4(file_info)
                f5_data_list = self.read_f5(file_info)
                f6_data_list = self.read_f6(file_info)
                f7_data_list = self.read_f7(file_info)
                f8_data_list = self.read_f8(file_info)
                f9_data_list = self.read_f9(file_info)
                f10_data_list = self.read_f10(file_info)
                f11_data_list = self.read_f11(file_info)
                f12_data_list = self.build_f12(f8_data_list, f11_data_list)
                f13_data_list = self.read_f13(file_info)
                f14_data_list = self.read_f14(file_info)

                f17_data_list = self.read_f17(file_info)

                f3_data_list, f15_data_list, f16_data_list, f103_data_list = self.read_f3_f15_f16(file_info)

                save_run_data_list.extend(f5_data_list)
                save_run_data_list.extend(f6_data_list)
                save_run_data_list.extend(f7_data_list)
                save_run_data_list.extend(f8_data_list)
                save_run_data_list.extend(f9_data_list)
                save_run_data_list.extend(f10_data_list)
                save_run_data_list.extend(f11_data_list)
                save_run_data_list.extend(f12_data_list)
                save_run_data_list.extend(f13_data_list)
                save_run_data_list.extend(f14_data_list)
                save_run_data_list.extend(f17_data_list)

                save_run_data_f4.extend(f4_data_list)

                save_run_data_s7.extend(f3_data_list)
                save_run_data_s7.extend(f103_data_list)
                save_run_data_s7.extend(f15_data_list)
                save_run_data_s7.extend(f16_data_list)

                diann_output_df = pd.read_csv(file_info.diann_result_stats_file_path, sep='\t')
                row_data = diann_output_df.iloc[0]
                diann_data = DIAOutputInfo()
                diann_data.seq_id = run_info.seq_id
                diann_data.file_name = file_info.file_name
                diann_data.data_source = self.data_source
                diann_data.precursor_ident = int(row_data['Precursors.Identified'])
                diann_data.protein_ident = int(row_data['Proteins.Identified'])
                diann_data.total_quantity = int(row_data['Total.Quantity'])
                diann_data.ms1_signal = int(row_data['MS1.Signal'])
                diann_data.ms2_signal = int(row_data['MS2.Signal'])
                diann_data.fwhm_scans = float(row_data['FWHM.Scans'])
                diann_data.fwhm_rt = float(row_data['FWHM.RT'])
                diann_data.acc_ms1 = float(row_data['Median.Mass.Acc.MS1'])
                diann_data.acc_ms1_corr = float(row_data['Median.Mass.Acc.MS1.Corrected'])
                diann_data.acc_ms2 = float(row_data['Median.Mass.Acc.MS2'])
                diann_data.acc_ms2_corr = float(row_data['Median.Mass.Acc.MS2.Corrected'])
                diann_data.ms2_instability = float(row_data['MS2.Mass.Instability'])
                diann_data.run_prefix = file_info.run_prefix
                #
                diann_data_list.append(diann_data)

                save_data.append((run_info, save_run_data_list, save_run_data_f4, save_run_data_s7))
            return delete_run_info, save_data, diann_data_list
        except Exception as e:
            logger.exception('Deal save data exception %s', e)
            return False
        finally:
            self.is_running = False

    def deal_data_save(self, delete_run_info, save_data_list, pred_info_list, diann_data_list):
        logger = self.logger
        try:
            self.is_running = True
            logger.info('Start deal data save')
            save_run_info = []
            save_run_data_list = []
            save_run_data_f4 = []
            save_run_data_s7 = []
            for base_save_data in save_data_list:
                save_run_info.append(base_save_data[0])
                save_run_data_list.extend(base_save_data[1])
                save_run_data_f4.extend(base_save_data[2])
                save_run_data_s7.extend(base_save_data[3])
            return db_utils_run_data.add_thiz_data(delete_run_info, save_run_info,
                                                   save_run_data_list, save_run_data_f4, save_run_data_s7,
                                                   pred_info_list, diann_data_list)
        except Exception as e:
            logger.exception('Deal save data exception %s', e)
            return False
        finally:
            self.is_running = False

    def calc_delt_rt(self, str_seq, diann_rt):
        # △RT (predict RT- DIA-NN RT)
        with open('resource/model/T.pkl', mode='rb') as f:
            model_data = pickle.load(f)
        org_vaa = np.array(sequence_gravy_dict.get(str_seq, 0)).reshape(-1, 1)
        pred_rt = model_data.predict(org_vaa).tolist()[0]
        return pred_rt - diann_rt

    def read_f3_f15_f16(self, file_info):
        logger = self.logger
        logger.info('Start read f3')
        f3_data_list = []
        f103_data_list = []
        f15_data_list = []
        f16_data_list = []
        run_name = file_info.run_name
        main_file_abs_path = os.path.join(file_info.diann_result_file_path)
        df = pd.read_csv(main_file_abs_path, sep='\t')
        df = df.sort_values(by='Precursor.Quantity', ascending=False, ignore_index=True)
        f3_df = df[df['Stripped.Sequence'].isin(f3_and_f15_pept_list)]
        f15_16_df = df[df['Stripped.Sequence'].isin(f3_and_f15_pept_list)]
        exist_pept_name = []

        f3_df_new = f3_df[
            (f3_df['Precursor.Charge'] == 2) & (~f3_df['Precursor.Id'].str.contains('(UniMod:35)'))]
        exist_seq_data = {}
        for iii, each_row in f3_df_new.iterrows():
            str_seq = each_row['Stripped.Sequence']
            diann_rt = each_row['RT']
            exist_seq_data[str_seq] = diann_rt

        for each_f3_seq in f3_and_f15_pept_list:
            diann_rt = exist_seq_data.get(each_f3_seq)
            if diann_rt is None:
                diann_rt = 0
            deltra_rt = self.calc_delt_rt(each_f3_seq, diann_rt)
            run_data_s7 = RunDataS7()
            run_data_s7.seq_id = self.run_name_seq_dict[run_name]
            run_data_s7.data_tag = 3
            run_data_s7.pept = each_f3_seq
            run_data_s7.data_val = deltra_rt
            f3_data_list.append(run_data_s7)

            run_data_s7_103 = RunDataS7()
            run_data_s7_103.seq_id = self.run_name_seq_dict[run_name]
            run_data_s7_103.data_tag = 103
            run_data_s7_103.pept = each_f3_seq
            run_data_s7_103.data_val = diann_rt
            f103_data_list.append(run_data_s7_103)

        exist_pept_name = []
        for index, row in f15_16_df.iterrows():
            pept_name = str(row['Stripped.Sequence'])
            if pept_name in exist_pept_name:
                continue
            exist_pept_name.append(pept_name)
            f15_val = round(float(row['Ms1.Area']), 2)
            f16_val = round(float(row['Precursor.Quantity']), 2)

            run_data_s15 = RunDataS7()
            run_data_s15.seq_id = self.run_name_seq_dict[run_name]
            run_data_s15.run_name = run_name
            run_data_s15.data_tag = 15
            run_data_s15.pept = pept_name
            run_data_s15.data_val = f15_val
            f15_data_list.append(run_data_s15)

            run_data_s16 = RunDataS7()
            run_data_s16.seq_id = self.run_name_seq_dict[run_name]
            run_data_s16.run_name = run_name
            run_data_s16.data_tag = 16
            run_data_s16.pept = pept_name
            run_data_s16.data_val = f16_val
            f16_data_list.append(run_data_s16)

        return f3_data_list, f15_data_list, f16_data_list, f103_data_list

    def read_f4(self, run_info):
        logger = self.logger
        logger.info('Start read f4')
        data_list = []
        df = pd.read_csv(self.f4_file_path)
        run_name = run_info.run_name
        run_info_data_list = list(df[run_name])
        for index in range(len(run_info_data_list)):
            run_data_f4 = RunDataF4()
            run_data_f4.seq_id = self.run_name_seq_dict[run_name]
            run_data_f4.data_index = index
            run_data_f4.data_val = run_info_data_list[index]
            data_list.append(run_data_f4)
        return data_list

    def read_f5(self, file_info):
        logger = self.logger
        logger.info('Start read f5')
        data_list = []
        run_prefix = file_info.run_prefix
        ins_s3_dir_path = os.path.join(self.s3_dir_path, run_prefix)
        f5_file_path = os.path.join(ins_s3_dir_path, run_prefix + '_F5.csv')
        df = pd.read_csv(f5_file_path)
        for index, row in df.iterrows():
            run_id = row['Run_ID']
            if run_id != file_info.run_id:
                continue
            data_5_1 = str(row['+1_percent']).replace('%', '')
            data_5_2 = str(row['+2_percent']).replace('%', '')
            data_5_3 = str(row['+3_percent']).replace('%', '')
            data_5_4 = str(row['+4_percent']).replace('%', '')
            data_5_5 = str(row['+5_percent']).replace('%', '')
            data_5_6 = str(row['+6_percent']).replace('%', '')
            run_data_51 = RunData()
            run_data_51.seq_id = self.run_id_seq_dict[run_id]
            run_data_51.data_tag = 51
            run_data_51.data_val = data_5_1

            run_data_52 = RunData()
            run_data_52.seq_id = self.run_id_seq_dict[run_id]
            run_data_52.data_tag = 52
            run_data_52.data_val = data_5_2

            run_data_53 = RunData()
            run_data_53.seq_id = self.run_id_seq_dict[run_id]
            run_data_53.data_tag = 53
            run_data_53.data_val = data_5_3

            run_data_54 = RunData()
            run_data_54.seq_id = self.run_id_seq_dict[run_id]
            run_data_54.data_tag = 54
            run_data_54.data_val = data_5_4

            run_data_55 = RunData()
            run_data_55.seq_id = self.run_id_seq_dict[run_id]
            run_data_55.data_tag = 55
            run_data_55.data_val = data_5_5

            run_data_56 = RunData()
            run_data_56.seq_id = self.run_id_seq_dict[run_id]
            run_data_56.data_tag = 56
            run_data_56.data_val = data_5_6

            data_list.append(run_data_51)
            data_list.append(run_data_52)
            data_list.append(run_data_53)
            data_list.append(run_data_54)
            data_list.append(run_data_55)
            data_list.append(run_data_56)

            for ii in range(1, 7):
                data_5_0 = str(row['+' + str(ii)])
                run_data_50 = RunData()
                run_data_50.seq_id = self.run_id_seq_dict[run_id]
                run_data_50.data_tag = 500 + ii
                run_data_50.data_val = data_5_0
                data_list.append(run_data_50)
        return data_list

    def read_f6(self, file_info):
        logger = self.logger
        logger.info('Start read f6')
        data_list = []
        run_prefix = file_info.run_prefix
        ins_s3_dir_path = os.path.join(self.s3_dir_path, run_prefix)
        f5_file_path = os.path.join(ins_s3_dir_path, run_prefix + '_F6.csv')
        df = pd.read_csv(f5_file_path)
        for index, row in df.iterrows():
            run_id = row['Run_ID']
            if run_id != file_info.run_id:
                continue
            inten_var = row['Intensity_variation(%)']
            run_data = RunData()
            run_data.seq_id = self.run_id_seq_dict[run_id]
            run_data.data_tag = 6
            run_data.data_val = inten_var.replace('%', '')
            data_list.append(run_data)
        return data_list

    def read_f7(self, file_info):
        logger = self.logger
        logger.info('Start read f7')
        data_list = []
        run_prefix = file_info.run_prefix
        ins_s3_dir_path = os.path.join(self.s3_dir_path, run_prefix)
        f5_file_path = os.path.join(ins_s3_dir_path, run_prefix + '_F7.csv')
        df = pd.read_csv(f5_file_path)
        for index, row in df.iterrows():
            run_id = row['Run_ID']
            if run_id != file_info.run_id:
                continue
            ms1_ppm = row['Median.Mass.Acc.MS1(ppm)']
            run_data = RunData()
            run_data.seq_id = self.run_id_seq_dict[run_id]
            run_data.data_tag = 7
            run_data.data_val = ms1_ppm
            data_list.append(run_data)
        return data_list

    def read_f8(self, file_info):
        logger = self.logger
        logger.info('Start read f8')
        data_list = []
        df = pd.read_csv(self.f8_file_path)
        for index, row in df.iterrows():
            run_name = row['Run_name']
            if run_name != file_info.run_name:
                continue
            area_val = row['area']
            run_data = RunData()
            run_data.seq_id = self.run_name_seq_dict[run_name]
            run_data.data_tag = 8
            run_data.data_val = area_val
            data_list.append(run_data)
        return data_list

    def read_f9(self, file_info):
        logger = self.logger
        logger.info('Start read f9')
        data_list = []
        run_name = file_info.run_name
        main_file_abs_path = os.path.join(file_info.diann_result_stats_file_path)
        df = pd.read_csv(main_file_abs_path, sep='\t')
        for index, row in df.iterrows():
            f9_val = float(row['FWHM.Scans'])
            run_data = RunData()
            run_data.seq_id = self.run_name_seq_dict[run_name]
            run_data.data_tag = 9
            run_data.data_val = f9_val
            data_list.append(run_data)

            f110_val = float(row['FWHM.RT'])
            run_data110 = RunData()
            run_data110.seq_id = self.run_name_seq_dict[run_name]
            run_data110.data_tag = 110
            run_data110.data_val = f110_val
            data_list.append(run_data110)

        return data_list

    def read_f10(self, file_info):
        logger = self.logger
        logger.info('Start read f10')
        data_list = []
        run_prefix = file_info.run_prefix
        ins_s3_dir_path = os.path.join(self.s3_dir_path, run_prefix)
        f5_file_path = os.path.join(ins_s3_dir_path, run_prefix + '_F10.csv')
        df = pd.read_csv(f5_file_path)
        for index, row in df.iterrows():
            run_id = row['Run_ID']
            if run_id != file_info.run_id:
                continue
            ms2_ppm = row['Median.Mass.Acc.MS2(ppm)']
            run_data = RunData()
            run_data.seq_id = self.run_id_seq_dict[run_id]
            run_data.data_tag = 10
            run_data.data_val = ms2_ppm
            data_list.append(run_data)

        return data_list

    def read_f11(self, file_info):
        logger = self.logger
        logger.info('Start read f11')
        data_list = []
        df = pd.read_csv(self.f11_file_path)
        for index, row in df.iterrows():
            run_name = row['Run_name']
            if run_name != file_info.run_name:
                continue
            area_val = row['area']
            run_data = RunData()
            run_data.seq_id = self.run_name_seq_dict[run_name]
            run_data.data_tag = 11
            run_data.data_val = area_val
            data_list.append(run_data)
        return data_list

    '''
    f12 = f8 / f11 
    '''

    def build_f12(self, f8_data_list, f11_data_list):
        #
        f11_data_dict = {}
        for f11_data in f11_data_list:
            f11_data_dict[f11_data.seq_id] = f11_data.data_val
        f12_data_list = []
        for f8_data in f8_data_list:
            run_data = RunData()
            run_data.seq_id = f8_data.seq_id
            run_data.data_tag = 12
            run_data.data_val = round(f8_data.data_val / f11_data_dict[f8_data.seq_id], 2)
            f12_data_list.append(run_data)
        return f12_data_list

    def read_f13(self, file_info):
        logger = self.logger
        logger.info('Start read f13')
        data_list = []
        run_prefix = file_info.run_prefix
        ins_s3_dir_path = os.path.join(self.s3_dir_path, run_prefix)
        f5_file_path = os.path.join(ins_s3_dir_path, run_prefix + '_F13.csv')
        df = pd.read_csv(f5_file_path)
        for index, row in df.iterrows():
            run_id = row['Run_ID']
            if run_id != file_info.run_id:
                continue
            pept_num = row['Peptide_number']
            run_data = RunData()
            run_data.seq_id = self.run_id_seq_dict[run_id]
            run_data.data_tag = 13
            run_data.data_val = pept_num
            data_list.append(run_data)

        return data_list

    def read_f14(self, file_info):
        logger = self.logger
        logger.info('Start read f14')
        data_list = []
        run_prefix = file_info.run_prefix
        ins_s3_dir_path = os.path.join(self.s3_dir_path, run_prefix)
        f5_file_path = os.path.join(ins_s3_dir_path, run_prefix + '_F14.csv')
        df = pd.read_csv(f5_file_path)
        for index, row in df.iterrows():
            run_id = row['Run_ID']
            if run_id != file_info.run_id:
                continue
            prot_num = row['Protein_number']
            run_data = RunData()
            run_data.seq_id = self.run_id_seq_dict[run_id]
            run_data.data_tag = 14
            run_data.data_val = prot_num
            data_list.append(run_data)
        return data_list

    def read_f17(self, file_info):
        logger = self.logger
        logger.info('Start read f17')
        data_list = []
        if file_info.file_type != FileTypeEnum.D:
            return data_list
        f17_file_path = os.path.join(self.s3_dir_path, 'F17.csv')
        df = pd.read_csv(f17_file_path)
        for index, row in df.iterrows():
            run_id = row['Run_ID']
            if run_id != file_info.run_id:
                continue
            ko_val = row['1/K0 [Vs/cm2]']
            run_data = RunData()
            run_data.seq_id = self.run_id_seq_dict[run_id]
            run_data.data_tag = 18
            run_data.data_val = ko_val

            uv_val = row['U [V]']
            run_data = RunData()
            run_data.seq_id = self.run_id_seq_dict[run_id]
            run_data.data_tag = 17
            run_data.data_val = uv_val
            data_list.append(run_data)
        return data_list
