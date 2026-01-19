import os.path

import pandas as pd
from applet.obj.PeptInfo import lc_feature_names, ms_feature_names

def build_data(run_info, run_data_list, f4_data_list, s7_data_list):
    seq_id = run_info.seq_id
    run_id = str(run_info.run_id)
    file_type = str(run_info.file_type)
    d_flag = 0
    r_flag = 0
    w_flag = 0
    if file_type == 'RAW':
        r_flag = 1
    elif file_type == 'D':
        d_flag = 1
    elif file_type == 'WIFF':
        w_flag = 1

    lc_pred_data = {}
    ms_pred_data = {}
    for s7_data in s7_data_list:
        data_tag = s7_data.data_tag
        data_val = s7_data.data_val
        if data_val is not None:
            data_val = float(data_val)
        if data_tag == 3:
            lc_pred_data[s7_data.pept + '_F2'] = data_val
        elif data_tag == 15:
            ms_pred_data[s7_data.pept + '_F13'] = data_val
        elif data_tag == 16:
            ms_pred_data[s7_data.pept + '_F14'] = data_val

    for f4_data in f4_data_list:
        lc_pred_data[str(f4_data.data_index) + '_F3'] = f4_data.data_val

    f8_val = 0
    f11_val = 0
    for run_data in run_data_list:
        data_tag = run_data.data_tag
        data_val = float(run_data.data_val)
        if data_tag > 500:
            ms_pred_data['+{}_F4'.format(data_tag - 500)] = data_val
        elif data_tag > 50:
            ms_pred_data['+{}_percent_F4'.format(data_tag - 50)] = data_val
        elif data_tag == 6:
            ms_pred_data['Intensity_variation(%)_F5'] = data_val
        elif data_tag == 7:
            ms_pred_data['Median.Mass.Acc.MS1(ppm)_F6'] = data_val
        elif data_tag == 8:
            ms_pred_data['TIC_MS1_signal_F7'] = data_val
            f8_val = data_val
        elif data_tag == 10:
            ms_pred_data['Median.Mass.Acc.MS2(ppm)_F8'] = data_val
        elif data_tag == 11:
            ms_pred_data['TIC_MS2_signal_F9'] = data_val
            f11_val = data_val
        elif data_tag == 13:
            ms_pred_data['Peptide_number_F11'] = data_val
        elif data_tag == 14:
            ms_pred_data['Protein_number_F12'] = data_val
        elif data_tag == 17:
            ms_pred_data['U_V_rep_F15'] = data_val
        elif data_tag == 18:
            ms_pred_data['1_K0 _Vs_cm2_rep_F15'] = data_val
        elif data_tag == 9:
            lc_pred_data['FWHM.Scans_F1'] = data_val

    ms_pred_data['Ratio of MS1.MS2_F10'] = round(float(f8_val) / float(f11_val), 2)

    lc_pred_data['D'] = d_flag
    lc_pred_data['R'] = r_flag
    lc_pred_data['W'] = w_flag
    lc_pred_data['Run_ID'] = run_id

    ms_pred_data['D'] = d_flag
    ms_pred_data['R'] = r_flag
    ms_pred_data['W'] = w_flag
    ms_pred_data['Run_ID'] = run_id
    lc_data, ms_data = init_lc_ms_data()
    lc_data, ms_data = fill_data(lc_data, ms_data, lc_pred_data, ms_pred_data)
    df_lc_data = pd.DataFrame([lc_data])
    df_ms_data = pd.DataFrame([ms_data])


    return df_lc_data, df_ms_data


def init_lc_ms_data():
    lc_data = {}
    ms_data = {}
    for key in lc_feature_names:
        lc_data[key] = 0
    for key in ms_feature_names:
        ms_data[key] = 0
    return lc_data, ms_data


def fill_data(lc_data, ms_data, lc_pred_data, ms_pred_data):
    for key in lc_feature_names:
        if lc_pred_data.get(key):
            lc_data[key] = lc_pred_data[key]
        else:
            pass
    for key in ms_feature_names:
        if ms_pred_data.get(key):
            ms_data[key] = ms_pred_data[key]
        else:
            pass
    return lc_data, ms_data

