import os
import time
from collections import Counter

import numpy as np
import pandas as pd
from pyteomics import mzxml

from applet.obj.Entity import FileInfo
from applet.service import common_service
from applet.service.dia import f17_process


class S3Service(common_service.CommonService):

    def __init__(self, base_output_path, s3_output_path, file_list: [FileInfo], logger, step=5,
                 pub_channel='analysis_info', start_time=0, conn_send=None):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time, conn_send=conn_send)
        self.s3_output_path = s3_output_path

    def deal_process(self):
        logger = self.logger
        try:
            ts31 = time.time()
            self.is_running = True
            logger.info('start S3 process')
            self.send_msg(9, self.build_start_diaqc_cmd())
            self.send_msg(0, 'Processing S3 step to obtain the F5, F6, F7, F10, F13, F14 and F17', with_time=True)
            if not os.path.exists(self.s3_output_path):
                os.mkdir(self.s3_output_path)
            savedict = {
                'F3_Charge_distribution_all_data.tsv': 'Run\tcharge state\n',
                'F4_MS1_scan_intensity_jumps.tsv': 'Run\tIntensity jumps\n',
                'F6_MS1_mz_deviation.tsv': 'Run\tMedian.Mass.Acc.MS1\n',
                'F7_MS2_mz_deviation.tsv': 'Run\tMedian.Mass.Acc.MS2\n',
                'F12_total_number_of_identified_peptides.tsv': 'Run\tPeptide Number\n',
                'F13_total_number_of_identified_proteins.tsv': 'Run\tProtein Number\n',
            }
            feadata = {}
            for key, value in savedict.items():
                init_write(self.s3_output_path, feadata, key, value)
            feadata['ERROR'] = open(self.s3_output_path + '/ERROR_Files.txt', 'w')
            deal_file_count = 0
            file_number = len(self.file_list)

            run_ins_id_dict = {}
            for run_file_parameter in self.file_list:
                deal_file_count = deal_file_count + 1
                if run_file_parameter.jump_deal:
                    continue
                run_ins_id_dict.setdefault(run_file_parameter.run_prefix, {})[
                    run_file_parameter.run_name] = run_file_parameter.run_id
                handler_result = self.handle_mzxml_diann_result(run_file_parameter.mzxml_file_relative_path,
                                                                run_file_parameter.main_file_relative_path,
                                                                run_file_parameter.stats_file_relative_path,
                                                                feadata, savedict, self.base_output_path)
                logger.info('handle_mzxml_diann_result, Files: {}/{}'.format(deal_file_count, file_number))
                if not handler_result:
                    self.send_msg(3, 'Deal S3 exception')
                    return False

            for key in feadata.keys():
                feadata[key].flush()
                feadata[key].close()

            ########### old feature 2 new feature name###########
            for ins in run_ins_id_dict.keys():
                ins_out_dir = os.path.join(self.s3_output_path, ins)
                if not os.path.exists(ins_out_dir):
                    os.mkdir(ins_out_dir)
            #
            # % f5 <-old F3
            if not self.run_flag:
                self.send_msg(2)
                return False
            # self.send_msg(9, 'Deal F5 data')
            self.deal_f5(self.s3_output_path, run_ins_id_dict)
            if not self.run_flag:
                self.send_msg(2)
                return False
            # self.send_msg(9, 'Deal F6 data')
            self.deal_f6(self.s3_output_path, run_ins_id_dict)
            if not self.run_flag:
                self.send_msg(2)
                return False
            # self.send_msg(9, 'Deal F7 data')
            self.deal_f7(self.s3_output_path, run_ins_id_dict)
            if not self.run_flag:
                self.send_msg(2)
                return False
            # self.send_msg(9, 'Deal F10 data')
            self.deal_f10(self.s3_output_path, run_ins_id_dict)
            if not self.run_flag:
                self.send_msg(2)
                return False
            # self.send_msg(9, 'Deal F13 data')
            self.deal_f13(self.s3_output_path, run_ins_id_dict)
            if not self.run_flag:
                self.send_msg(2)
                return False
            # self.send_msg(9, 'Deal F14 data')
            self.deal_f14(self.s3_output_path, run_ins_id_dict)
            if not self.run_flag:
                self.send_msg(2)
                return False
            # self.send_msg(9, 'Deal F17 data')
            f17_process.deal(self.s3_output_path, self.file_list)
            ts32 = time.time()
            logger.info('s3_time, file: {}, run_prefix: {}, speed_time: {}, '.format(self.file_list[0].file_name, self.file_list[0].run_prefix, ts32 - ts31))

            self.send_msg(1, 'Saving F5, F6, F7, F10, F13, F14 and F17 results', with_time=True)
            return True
        except Exception as e:
            logger.exception('Deal S3 exception')
            self.send_msg(3, 'Deal S3 exception: {}'.format(e))
            return False
        finally:
            self.is_running = False

    def build_start_diaqc_cmd(self):
        mzxml_file_list = [' --f "{}"'.format(f.mzXML_file_path) for f in self.file_list]
        return '"./iDIAQC.exe" {} --out "{}"'.format(' '.join(mzxml_file_list), self.base_output_path)

    def handle_mzxml_diann_result(self, mzxml_file,
                                  diann_main_file, diann_stats_file, feadata, savedict, base_output_path):
        logger = self.logger
        try:
            mzxml_result = get_mzxml_result_data(base_output_path, mzxml_file)
            main_result, stats_result = get_diann_result_data(base_output_path, diann_main_file, diann_stats_file)
            check_single_run(mzxml_result, main_result, stats_result)
            ########feature##########
            f3_charge = get_charge_state(main_result)
            f4_jumps = get_intensity_jumps_fails(mzxml_result)
            f6_ms1_acc, f7_ms2_acc = get_MMAcc(stats_result)
            f12, f13 = get_total_number(stats_result, main_result)

            fealist = [f3_charge, f4_jumps, f6_ms1_acc, f7_ms2_acc, f12, f13]
            for i, key in enumerate(savedict.keys()):
                feadata_write(feadata, key, fealist[i])
            return True
        except Exception as e:
            logger.exception('handle_mzxml_diann_result exception')
            feadata['ERROR'].write(
                mzxml_file + '\t' +
                diann_main_file + '\t' +
                diann_stats_file + '\n'
            )
            return False

    def deal_f5(self, s3_output_path, run_ins_id_dict):
        logger = self.logger
        logger.info('start deal f5')
        f5 = pd.read_csv(os.path.join(s3_output_path, 'F3_Charge_distribution_all_data.tsv'), sep='\t')
        fea = f5.copy()
        fea.columns = ['Run_ID', 'Charge_state']
        cols = ['Run_ID', 'Precursor_number', '+1', '+2', '+3', '+4', '+5', '+6', 'Charge_state_mean',
                '+1_percent', '+2_percent', '+3_percent', '+4_percent', '+5_percent', '+6_percent']
        for ins in run_ins_id_dict.keys():
            tanno = run_ins_id_dict.get(ins)
            logger.info('deal S3, F5 process, ins is: {}'.format(ins))
            tfea = fea.loc[fea['Run_ID'].isin(list(tanno.keys())), :]
            tfea['Run_ID'] = tfea['Run_ID'].map(tanno)

            tfea['Charge_state'] = tfea['Charge_state'].astype(int)
            tmp1 = _get_wide_from_long(tfea, 'Charge_state', [len, lambda x: counter(x, 1), \
                                                              lambda x: counter(x, 2), \
                                                              lambda x: counter(x, 3), \
                                                              lambda x: counter(x, 4), \
                                                              lambda x: counter(x, 5), \
                                                              lambda x: counter(x, 6), \
                                                              np.mean, \
                                                              lambda x: counter_per(x, 1), \
                                                              lambda x: counter_per(x, 2), \
                                                              lambda x: counter_per(x, 3), \
                                                              lambda x: counter_per(x, 4), \
                                                              lambda x: counter_per(x, 5), \
                                                              lambda x: counter_per(x, 6),
                                                              ], key='Run_ID')
            tfea = tmp1.reset_index()
            tfea.columns = cols
            tfea['Charge_state_mean'] = [float('%.4g' % elem) for elem in tfea['Charge_state_mean']]
            if len(tfea) != len(tanno):
                logger.error(
                    'deal S3, F5 error, ins is: {}, tfea count is: {}, tanno count is: {}'.format(ins, len(tfea),
                                                                                                  len(tanno)))
            f5_csv_path = os.path.join(s3_output_path, ins, ins + '_' + 'F5.csv')
            logger.info('F5 csv path: {}'.format(f5_csv_path))
            tfea.to_csv(f5_csv_path, index=False)
        logger.info('end deal f5')

    def deal_f6(self, s3_output_path, run_ins_id_dict):
        logger = self.logger
        logger.info('start deal f6')
        # % F6<-oF4
        f6 = pd.read_csv(os.path.join(s3_output_path, 'F4_MS1_scan_intensity_jumps.tsv'), sep='\t')
        ##
        fea = f6.copy()
        cols = ['Run_ID', 'Intensity_variation(%)']
        for ins in run_ins_id_dict.keys():
            logger.info('deal S3, F6 process, ins is: {}'.format(ins))
            tanno = run_ins_id_dict.get(ins)
            tfea = fea.loc[fea['Run'].isin(list(tanno.keys())), :]
            tfea['Run'] = tfea['Run'].map(tanno)
            tfea.columns = cols
            tfea['Intensity_variation(%)'] = ['%.4g%%' % (elem * 100) for elem in tfea['Intensity_variation(%)']]
            if len(tfea) != len(tanno):
                logger.error(
                    'deal S3, F6 error, ins is: {}, tfea count is: {}, tanno count is: {}'.format(ins, len(tfea),
                                                                                                  len(tanno)))

            f6_csv_path = os.path.join(s3_output_path, ins, ins + '_' + 'F6.csv')
            logger.info('F6 csv path: {}'.format(f6_csv_path))

            tfea.to_csv(f6_csv_path, index=False)
        logger.info('end deal f6')

    def deal_f7(self, s3_output_path, run_ins_id_dict):
        logger = self.logger
        logger.info('start deal f7')
        # % F7 <-oF6
        f7 = pd.read_csv(os.path.join(s3_output_path, 'F6_MS1_mz_deviation.tsv'), sep='\t')
        ##
        fea = f7.copy()
        cols = ['Run_ID', 'Median.Mass.Acc.MS1(ppm)']
        for ins in run_ins_id_dict.keys():
            logger.info('deal S3, F7 process, ins is: {}'.format(ins))
            #
            tanno = run_ins_id_dict.get(ins)
            tfea = fea.loc[fea['Run'].isin(list(tanno.keys())), :]
            tfea['Run'] = tfea['Run'].map(tanno)
            tfea.columns = cols
            tfea['Median.Mass.Acc.MS1(ppm)'] = ['%.4g' % elem for elem in tfea['Median.Mass.Acc.MS1(ppm)']]
            if len(tfea) != len(tanno):
                logger.error(
                    'deal S3, F7 error, ins is: {}, tfea count is: {}, tanno count is: {}'.format(ins, len(tfea),
                                                                                                  len(tanno)))

            f7_csv_path = os.path.join(s3_output_path, ins, ins + '_' + 'F7.csv')
            logger.info('F7 csv path: {}'.format(f7_csv_path))
            tfea.to_csv(f7_csv_path, index=False)
        logger.info('end deal f7')

    def deal_f10(self, s3_output_path, run_ins_id_dict):
        logger = self.logger
        logger.info('start deal f10')
        # % F10 <-oF7
        f10 = pd.read_csv(os.path.join(s3_output_path, 'F7_MS2_mz_deviation.tsv'), sep='\t')
        ##
        fea = f10.copy()
        cols = ['Run_ID', 'Median.Mass.Acc.MS2(ppm)']
        for ins in run_ins_id_dict.keys():
            logger.info('deal S3, F10 process, ins is: {}'.format(ins))
            tanno = run_ins_id_dict.get(ins)
            tfea = fea.loc[fea['Run'].isin(list(tanno.keys())), :]
            tfea['Run'] = tfea['Run'].map(tanno)
            tfea.columns = cols
            tfea['Median.Mass.Acc.MS2(ppm)'] = ['%.4g' % elem for elem in tfea['Median.Mass.Acc.MS2(ppm)']]
            if len(tfea) != len(tanno):
                logger.error(
                    'deal S3, F10 error, ins is: {}, tfea count is: {}, tanno count is: {}'.format(ins, len(tfea),
                                                                                                   len(tanno)))

            f10_csv_path = os.path.join(s3_output_path, ins, ins + '_' + 'F10.csv')
            logger.info('F10 csv path: {}'.format(f10_csv_path))
            tfea.to_csv(f10_csv_path, index=False)
        logger.info('end deal f10')

    def deal_f13(self, s3_output_path, run_ins_id_dict):
        logger = self.logger
        logger.info('start deal f13')
        # % f13<-of12
        f13 = pd.read_csv(os.path.join(s3_output_path, 'F12_total_number_of_identified_peptides.tsv'), sep='\t')

        fea = f13.copy()
        cols = ['Run_ID', 'Peptide_number']
        for ins in run_ins_id_dict.keys():
            logger.info('deal S3, F13 process, ins is: {}'.format(ins))
            tanno = run_ins_id_dict.get(ins)
            tfea = fea.loc[fea['Run'].isin(list(tanno.keys())), :]
            tfea['Run'] = tfea['Run'].map(tanno)
            tfea.columns = cols
            if len(tfea) != len(tanno):
                logger.error(
                    'deal S3, F13 error, ins is: {}, tfea count is: {}, tanno count is: {}'.format(ins, len(tfea),
                                                                                                   len(tanno)))

            f13_csv_path = os.path.join(s3_output_path, ins, ins + '_' + 'F13.csv')
            logger.info('F13 csv path: {}'.format(f13_csv_path))
            tfea.to_csv(f13_csv_path, index=False)
        logger.info('end deal f13')

    def deal_f14(self, s3_output_path, run_ins_id_dict):
        logger = self.logger
        logger.info('start deal f14')
        # % f14<-of13
        f14 = pd.read_csv(os.path.join(s3_output_path, 'F13_total_number_of_identified_proteins.tsv'), sep='\t')
        fea = f14.copy()
        cols = ['Run_ID', 'Protein_number']
        for ins in run_ins_id_dict.keys():
            logger.info('deal S3, F14 process, ins is: {}'.format(ins))
            tanno = run_ins_id_dict.get(ins)
            tfea = fea.loc[fea['Run'].isin(list(tanno.keys())), :]
            tfea['Run'] = tfea['Run'].map(tanno)
            tfea.columns = cols
            if len(tfea) != len(tanno):
                logger.error(
                    'deal S3, F14 error, ins is: {}, tfea count is: {}, tanno count is: {}'.format(ins, len(tfea),
                                                                                                   len(tanno)))

            f14_csv_path = os.path.join(s3_output_path, ins, ins + '_' + 'F14.csv')
            logger.info('F14 csv path: {}'.format(f14_csv_path))
            tfea.to_csv(f14_csv_path, index=False)

        logger.info('end deal f14')


def get_total_number(stats_result, main_result):

    name = main_result['Run'].unique()[0]
    return pd.DataFrame([{'Run': name, 'Peptide Number': stats_result['Precursors.Identified'].tolist()[0]}]), \
        pd.DataFrame([{'Run': name, 'Protein Number': stats_result['Proteins.Identified'].tolist()[0]}])


def __stats_from_stats(base_output_path, diann_stats_file):
    name = diann_stats_file.rsplit('/', 1)[1].split('_mainoutput')[0]
    sdata = pd.read_csv(os.path.join(base_output_path, diann_stats_file), sep='\t')
    slist = ['FWHM.Scans',
             'Median.Mass.Acc.MS1',
             'Median.Mass.Acc.MS2',
             'Precursors.Identified',
             'Proteins.Identified',
             'Total.Quantity',
             'MS1.Signal',
             'MS2.Signal',
             'FWHM.RT',
             'MS2.Mass.Instability',
             'Median.RT.Prediction.Acc']
    sdf = sdata.loc[:, slist]
    sdf.insert(0, 'Run', name)
    return sdf


def __main_from_main(base_output_path, diann_main_file):
    data = pd.read_csv(os.path.join(base_output_path, diann_main_file), sep='\t')
    mlist = [
        'Run',
        'Modified.Sequence',
        'Precursor.Charge',
        'Protein.Ids',
        'CScore', 'Decoy.CScore',
        'RT.Stop', 'RT.Start',
        'RT',
        'Ms1.Area',
        'Precursor.Quantity',
        'Q.Value',
        'Proteotypic',
        'Fragment.Correlations',
        'Fragment.Quant.Raw'
    ]
    df = data.loc[:, mlist]
    df['Precursor.Id'] = df['Modified.Sequence'] + df['Precursor.Charge'].astype(str)
    return df


def cv(x):
    return x.std() / x.mean()

    # Lead function


def _get_wide_from_long(data, value, func, key='Run'):
    return data.groupby(key)[value].agg(func)


def get_diann_result_data(base_output_path, main_string, stats_string):
    if not main_string.endswith('.csv'):
        data = __main_from_main(base_output_path, main_string)
    else:
        data = pd.read_csv(os.path.join(base_output_path, main_string))
    if not stats_string.endswith('.csv'):
        sdata = __stats_from_stats(base_output_path, stats_string)
    else:
        sdata = pd.read_csv(os.path.join(base_output_path, stats_string))
    return data, sdata

    ## Extract mzXML


def __mzxml_result_data_from_mzxml(base_output_path, mzxml_file):
    reader = mzxml.read(os.path.join(base_output_path, mzxml_file))
    name = os.path.split(mzxml_file)[1].split('.mzXML')[0]
    scanlist = [elem for elem in reader]
    data = pd.DataFrame(scanlist)
    data.insert(0, 'Run', name)
    return data


def get_mzxml_result_data(base_output_path, mzxml_string: str):
    if mzxml_string.endswith('.mzXML'):
        data = __mzxml_result_data_from_mzxml(base_output_path, mzxml_string)
    else:
        data = pd.read_csv(mzxml_string)
    data = data.sort_values('retentionTime').reset_index(drop=True)
    return data


## single check
def check_single_run(mzxml_result, main_result, stats_result):
    for tmp in [mzxml_result, main_result, stats_result]:
        if tmp['Run'].nunique() > 1:
            # TODO
            raise '[ERROR] This script does not support simultaneous input of multiple results'
        elif tmp['Run'].nunique() < 1:
            raise '[ERROR] The result is empty'
        else:
            pass


# old  F3: Charge distribution
def get_charge_state(main_result):
    tmp = main_result.loc[:, ['Run', 'Precursor.Charge']]
    if tmp['Run'].nunique() > 1:
        raise '[ERROR] This script does not support simultaneous input of multiple results'
    elif tmp['Run'].nunique() < 1:
        raise '[ERROR] The result is empty'
    else:
        tmp.columns = ['Run', 'charge state']
        return tmp


# old  F4,F5  Intensity jumps/Intensity fails
def _get_counter_ratio(ticlist, gap, fd=3):
    fd_counter = 0
    scan_number = len(ticlist)
    for i in range(0, scan_number, gap + 1):
        if i + gap + 1 < scan_number:
            if round(ticlist[i + gap + 1] / ticlist[i]) >= fd \
                    or round(ticlist[i + gap + 1] / ticlist[i]) <= 1 / fd:
                fd_counter += 1
    return fd_counter / ((scan_number - 1) / (gap + 1))


def get_intensity_jumps_fails(mzxml_result):
    tmp = mzxml_result.loc[mzxml_result['msLevel'] == 1,
    ['Run', 'retentionTime', 'totIonCurrent']].reset_index(drop=True)
    name = tmp['Run'].unique()[0]
    jumps, fails = _get_counter_ratio(tmp['totIonCurrent'], 0), \
        _get_counter_ratio(tmp['totIonCurrent'], 3)
    return pd.DataFrame([{'Run': name, 'Intensity jumps': jumps}])
    # ,\
    #    pd.DataFrame([{'Run':name,'Intensity fails':fails}])


# old F6,F7 MS1/2 m/z deviation
def get_MMAcc(stats_result):
    return stats_result.loc[:, ['Run', 'Median.Mass.Acc.MS1']], \
        stats_result.loc[:, ['Run', 'Median.Mass.Acc.MS2']]


# old F12./F13 total number of identified peptides/total number of identified proteins


####################
def init_write(s3_output_path, feadata, key, str):
    feadata[key] = open(s3_output_path + '/' + key, 'w')
    feadata[key].write(str)
    feadata[key].flush()


def feadata_write(feadata, key, data):
    for _i in range(len(data)):
        feadata[key].write('\t'.join([str(elem) for elem in data.iloc[_i, :]]) + '\n')
    feadata[key].flush()


def _get_wide_from_long(data, value, func, key='Run'):
    return data.groupby(key)[value].agg(func)


def counter(lis, key):
    return Counter(lis)[key]


def counter_per(lis, key):
    return '%.4g%%' % (Counter(lis)[key] / len(lis) * 100)
