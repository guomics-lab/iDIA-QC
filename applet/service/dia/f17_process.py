# F17处理.d文件的脚本
import multiprocessing
import os.path
import threading

import numpy as np
import pandas as pd
from timspy.df import TimsPyDF

from loguru import logger
from applet.obj.Entity import FileInfo, FileTypeEnum


class F17Data:
    def __init__(self, path):
        self.path = path
        self.dataset = TimsPyDF(self.path)
        self.all_columns = ('frame', 'scan', 'tof', 'intensity', 'mz', 'inv_ion_mobility', 'retention_time')
        self.mz_ref = 622.0290  # the reference m/z
        self.nppm = 5  # +/- 5 ppm
        self.mz_lower = self.mz_ref * (1 - self.nppm / (10 ** 6))
        self.mz_upper = self.mz_ref * (1 + self.nppm / (10 ** 6))
        # set reference range of 622 ion mobility
        self.im_ref = 0.991459
        # corresponding ion mobility (1/K0) range to 132 voltages +/- 1, strict standards
        self.im_lower = 0.991459 * (1 - 1 / 132)
        self.im_upper = 0.991459 * (1 + 1 / 132)
        self.plot_im622()

    # query the fist 20 MS1 frames to estimate the acuracy of 622 (m/z)
    def plot_im622(self, show=True, im_digits=None, im_equ_v_digits=2):
        # select first 20 MS1 frames
        first20ms1frames = self.dataset.query(frames=self.dataset.ms1_frames[:20], columns=self.all_columns)
        df = first20ms1frames.loc[(first20ms1frames.mz > (self.mz_ref * (1 - 1 / (10 ** 3)))) & (
                first20ms1frames.mz < (self.mz_ref * (1 + 1 / (10 ** 3)))),
             :]  # select peaks with m/z in the range of self.mz_ref +/- 1 ppk
        # then select peaks with intensity larger than 10% of the maximum intensity
        df = df.loc[df.intensity > 0.1 * df.intensity.max()]
        # then group peaks by m/z and aggregate with sum function
        df1 = df[['inv_ion_mobility', 'intensity']].groupby('inv_ion_mobility').agg(np.sum)
        # estimate weighted average mass acuracy
        # xOriginal, yOriginal = df1.index, df1.intensity
        self.im_wavg = (df1.index * df1.intensity).sum() / df1.intensity.sum()
        if im_equ_v_digits != None:
            self.im_equ_v = float(f'{{:.{str(im_equ_v_digits)}f}}'.format(132 * self.im_wavg / self.im_ref))
        if im_digits != None:
            self.im_wavg = float(f'{{:.{str(im_digits)}f}}'.format(float(self.im_wavg)))


def deal_pro(wait_deal_file, output_dir):
    save_data = []
    for file_info in wait_deal_file:
        try:
            logger.info('deal F17: {}'.format(file_info.file_path))
            tn = threading.Thread()
            tn.start()
            tn.join()
            f17_data = F17Data(file_info.file_path)
            run_id = file_info.run_id
            save_data.append({'Run_ID': run_id, '1/K0 [Vs/cm2]': f17_data.im_wavg, 'U [V]': f17_data.im_equ_v})
            logger.info('deal F17 over: {}'.format(file_info.file_path))
        except Exception:
            logger.exception('Deal F17 exception')
    df = pd.DataFrame(save_data)
    df.to_csv(os.path.join(output_dir, 'F17.csv'))


def deal(output_dir, file_list: [FileInfo]):
    logger.info('Start deal F17, file count: {}'.format(len(file_list)))
    wait_deal_file = []
    for file_info in file_list:
        if file_info.file_type == FileTypeEnum.D:
            wait_deal_file.append(file_info)

    logger.info('Start deal F17, .d file count: {}'.format(len(wait_deal_file)))
    if len(wait_deal_file) == 0:
        return

    tn = multiprocessing.Process(target=deal_pro, args=(file_list, output_dir))
    tn.start()
    tn.join()
    logger.info('End deal F17')
