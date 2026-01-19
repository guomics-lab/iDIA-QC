import os
import time
import xml.sax
from threading import Lock

from applet.obj.Entity import FileInfo
from applet.service import common_service


class S4Service(common_service.CommonService):

    def __init__(self, base_output_path, s4_output_path, s4_output_file_path, file_list: [FileInfo], logger, step=6,
                 pub_channel='analysis_info', start_time=0, conn_send=None):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time, conn_send=conn_send)
        self.s4_output_path = s4_output_path
        self.s4_output_file_path = s4_output_file_path

    def deal_process(self):
        logger = self.logger
        try:
            ts31 = time.time()
            self.is_running = True
            self.send_msg(0, 'Processing F4 extraction', with_time=True)
            result_csv_dir = os.path.join(self.s4_output_path)
            if not os.path.exists(result_csv_dir):
                os.mkdir(result_csv_dir)
            result_tsv_writer_path = self.s4_output_file_path
            result_tsv_writer = open(result_tsv_writer_path, 'w')
            build_csv_head(result_tsv_writer)

            run_file_list = self.file_list
            logger.info('deal S4 process, mzXML file count is: {}, file size is: {} MB'.format(len(run_file_list),
                                                                                               int(sum(map(lambda
                                                                                                               x: x.get_mzxml_file_size(),
                                                                                                           run_file_list)) / float(
                                                                                                   1024 * 1024))))

            #
            for run_file_parameter in run_file_list:
                self.send_msg(9, 'Loading run {}'.format(run_file_parameter.mzXML_file_path))
                handle_a_mzxml(run_file_parameter.mzXML_file_path, run_file_parameter.run_name, result_tsv_writer)
            result_tsv_writer.flush()
            result_tsv_writer.close()
            # self.send_msg(1, 'Success deal S4')
            ts32 = time.time()
            logger.info('s4_time, file: {}, run_prefix: {}, speed_time: {}, '.format(self.file_list[0].file_name, self.file_list[0].run_prefix, ts32 - ts31))
            return True
        except Exception as e:
            logger.exception('Deal S4 exception')
            self.send_msg(3, 'Deal S4 exception: {}'.format(e))
            return False
        finally:
            self.is_running = False


signal_ratio = 3
water_size = 10
fake_signal_ratio = 10
apex_drt = 60
min_length_between_start_and_end = 1000
start_check_width = 500
sigma = 9
lock = Lock()

global file_size_count


class MzxmlHandler(xml.sax.handler.ContentHandler):
    def __init__(self, ms1_scan_list, ms2_scan_list):
        super().__init__()
        self.ms1_scan_list = ms1_scan_list
        self.ms1_scan_index = 0
        self.ms2_scan_list = ms2_scan_list
        self.ms2_scan_index = 0

    def startElement(self, tag, attributes):
        if tag == "scan":
            ms_level = int(attributes['msLevel'])
            scan_num = int(attributes['num'])
            retentionTime = float(attributes['retentionTime'][2: -1])
            bpi = float(attributes['basePeakIntensity'])
            tic = float(attributes['totIonCurrent'])
            if ms_level == 1:
                self.ms1_scan_list.append([
                    ms_level,
                    self.ms1_scan_index,
                    scan_num,
                    retentionTime,
                    bpi,
                    tic
                ])
                self.ms1_scan_index += 1
            if ms_level == 2:
                self.ms2_scan_list.append([
                    ms_level,
                    self.ms2_scan_index,
                    scan_num,
                    retentionTime,
                    bpi,
                    tic
                ])
                self.ms2_scan_index += 1


def handle_a_mzxml(mzxml_path, file_tag, result_writer):
    start_time = time.time()
    # logger.info('deal S4 process, handle_a_mzxml start, file_tag is: {}'.format(file_tag))
    ms1_scan_list = []
    ms2_scan_list = []
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    parser.setContentHandler(MzxmlHandler(ms1_scan_list, ms2_scan_list))
    parser.parse(mzxml_path)
    write_data_to_tsv(result_writer, file_tag, ms1_scan_list, ms2_scan_list)


def write_data_to_tsv(result_writer, file_tag, ms1_scan_list, ms2_scan_list):
    with lock:
        for ms_scan_list in [ms1_scan_list, ms2_scan_list]:
            for ms_info in ms_scan_list:
                result_writer.write(
                    file_tag + "\t" +
                    str(ms_info[0]) + "\t" +
                    str(ms_info[1]) + "\t" +
                    str(ms_info[2]) + "\t" +
                    str(ms_info[3]) + "\t" +
                    str(ms_info[4]) + "\t" +
                    str(ms_info[5]) + "\n")

        result_writer.flush()


def dir_list(dir_path):
    run_file_list = []
    current_path_list = os.listdir(dir_path)
    for filename in current_path_list:
        if filename.startswith(".") or filename.startswith("lost"):
            continue
        current_file_path = os.path.join(dir_path, filename)
        if os.path.isdir(current_file_path):
            continue
        if filename.endswith(".mzXML"):
            file_tag = filename[:-6]
            run_file_list.append([
                os.path.join(dir_path, filename),
                file_tag,
                os.path.getsize(os.path.join(dir_path, filename))
            ])
    return run_file_list


def build_csv_head(result_writer):
    result_writer.write(
        "Run name\t" +
        "mslevel\t" +
        "level.index\t" +
        "scan.num\t" +
        "retentionTime\t" +
        "basePeakIntensity\t" +
        "totIonCurrent\n")
