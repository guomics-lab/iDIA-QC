import os.path
import sqlite3

from applet.db import db_util_init

from loguru import logger
from applet.obj.DBEntity import RunInfo, PredInfo

db_dir_path = os.path.join(os.getcwd(), 'db')
if not os.path.exists(db_dir_path):
    os.mkdir(db_dir_path)

db_file_path = os.path.join(db_dir_path, 'diaqc.db')
conn = sqlite3.connect(db_file_path, check_same_thread=False)

db_util_init.init_sql(conn)

RUN_INFO_SELECT_SQL = 'inst_name, run_id, run_name, seq_id, file_name, state, last_modify_time, file_size, run_prefix, file_type '


def query_max_run_info_id():
    sql = 'SELECT max(id) from run_info '
    try:
        c = conn.cursor()
        c.execute(sql)
        results = c.fetchall()
        if results[0][0]:
            return results[0][0]
        return 0
    except Exception as e:
        logger.exception('query max run info id error, %s', e)


def query_max_run_increase_id(inst_name):
    sql = 'SELECT max(increase_id) from increase_info where run_prefix = ? '
    try:
        c = conn.cursor()
        c.execute(sql, (inst_name,))
        results = c.fetchall()
        return results[0][0]
    except Exception as e:
        logger.exception('query max run info id error, %s', e)


def insert_run_increase_id(run_prefix, increase_id):
    sql = 'insert into increase_info(run_prefix, increase_id) values(?, ?) '
    try:
        c = conn.cursor()
        c.execute(sql, (run_prefix, increase_id))
        conn.commit()
    except Exception as e:
        logger.exception('insert into increase_info error')


def update_run_increase_id(run_prefix, increase_id):
    sql = 'update increase_info set increase_id = ? where run_prefix = ? '
    try:
        c = conn.cursor()
        c.execute(sql, (increase_id, run_prefix))
        conn.commit()
    except Exception as e:
        logger.exception('update_run_increase_id error')


def query_run_info_exist(run_name) -> RunInfo:
    sql = 'SELECT ' + RUN_INFO_SELECT_SQL + ' from run_info where run_name = ? and is_delete = 0'
    try:
        c = conn.cursor()
        c.execute(sql, (run_name,))
        results = c.fetchall()
        if len(results) == 0:
            return None
        return convert_run_info(results[0])
    except Exception as e:
        logger.exception('query run info exist error, %s', e)



def query_run_info(run_id) -> RunInfo:
    sql = 'SELECT ' + RUN_INFO_SELECT_SQL + ' from run_info where run_id = ? and is_delete = 0'
    try:
        c = conn.cursor()
        c.execute(sql, (run_id,))
        results = c.fetchall()
        if len(results) == 0:
            return None
        return convert_run_info(results[0])
    except Exception as e:
        logger.exception('query run info exist error, %s', e)


def query_run_info_by_file_name(file_name, source) -> RunInfo:
    sql = 'SELECT ' + RUN_INFO_SELECT_SQL + ' from run_info where file_name = ? and source = ? and is_delete = 0 order by id desc '
    try:
        c = conn.cursor()
        c.execute(sql, (file_name, source))
        results = c.fetchall()
        if len(results) == 0:
            return None
        return convert_run_info(results[0])
    except Exception as e:
        logger.exception('query run info exist error, %s', e)



def query_wait_predict_record() -> [RunInfo]:
    sql = 'SELECT ' + RUN_INFO_SELECT_SQL + ' from run_info where state = 0 and is_delete = 0'
    result_list = []
    try:
        c = conn.cursor()
        c.execute(sql)
        results = c.fetchall()
        if len(results) == 0:
            return result_list
        for row in results:
            run_info = convert_run_info(row)
            result_list.append(run_info)
    except Exception as e:
        logger.exception('query run info exist error, %s', e)
    return result_list


#
def update_all_run_data_no_pred():
    try:
        c = conn.cursor()
        #
        update_sql = 'update run_info set state = 0 where is_delete = 0'
        c.execute(update_sql)
        conn.commit()
    except Exception as e:
        logger.exception('update_all_run_data_no_pred error, %s', e)


def update_selected_run_data_no_pred(selected_run_id_list):
    try:
        c = conn.cursor()
        param_str = ','.join("'" + run_name + "'" for run_name in selected_run_id_list)
        update_sql = 'update run_info set state = 0 where run_id in (' + param_str + ') and is_delete = 0'
        c.execute(update_sql)
        conn.commit()
    except Exception as e:
        logger.exception('update_selected_run_data_no_pred error, %s', e)



def update_pred_result(run_info: RunInfo, pred_info_list: [PredInfo]):
    try:
        run_id = run_info.run_id
        seq_id = run_info.seq_id

        c = conn.cursor()
        #
        delete_sql = 'delete from pred_result where run_id = ?'
        c.execute(delete_sql, [run_id])

        #
        update_sql = 'update run_info set state = 1 where run_id = ? and seq_id = ? '
        c.execute(update_sql, [run_id, seq_id])
        #
        save_pred_info_sql = 'insert into pred_result(run_id, seq_id, pred_key, pred_score, pred_label) values (?, ?, ?, ?, ?) '
        batch_insert_run_info_list = []
        for pred_info in pred_info_list:
            batch_insert_run_info_list.append(pred_info.get_key_val())
        c.executemany(save_pred_info_sql, batch_insert_run_info_list)
        conn.commit()
    except Exception as e:
        logger.exception('update_pred_result error, %s', e)


def convert_run_info(data):
    run_info = RunInfo()
    run_info.inst_name = data[0]
    run_info.run_id = data[1]
    run_info.run_name = data[2]
    run_info.seq_id = data[3]

    run_info.file_name = data[4]
    run_info.state = data[5]
    run_info.last_modify_time = data[6]
    run_info.file_size = data[7]
    run_info.run_prefix = data[8]
    run_info.file_type = data[9]
    return run_info
