
def init_sql(conn):

    cursor = conn.cursor()
    sql_create_inst_info = '''
    CREATE TABLE if not exists "inst_info" (
      "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      "ms_inst_id" text(10),
      "ms_model" TEXT(200)
    );
    '''

    sql_create_run_data = '''
    CREATE TABLE if not exists "run_data" (
      "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      "seq_id" text(50),
      "data_tag" integer,
      "data_val" TEXT(50)
    );
    '''

    sql_create_run_data_f4 = '''
    CREATE TABLE if not exists "run_data_f4" (
      "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      "seq_id" text,
      "data_index" integer,
      "data_val" TEXT(50),
      "is_delete" integer
    );
    '''

    sql_create_run_data_s7 = '''
    CREATE TABLE if not exists "run_data_s7" (
      "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      "seq_id" text(100),
      "data_tag" integer,
      "pept" text(100),
      "data_val" TEXT(50)
    );
    '''

    sql_create_run_info = '''
    CREATE TABLE if not exists "run_info" (
      "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      "inst_name" text(20),
      "run_prefix" text(50),
      "run_id" text(50),
      "run_name" TEXT(200),
      "file_name" TEXT(200),
      "file_type" TEXT(20),
      "seq_id" text(50),
      "source" integer(5),
      "is_delete" integer,
      "state" integer(5),
      "last_modify_time" integer(50),
      "file_size" integer(50),
      "gmt_create" TEXT
    );
    '''

    sql_create_pred_result = '''
    CREATE TABLE if not exists "pred_result" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "run_id" text(50),
        "seq_id" text(50),
        "pred_key" TEXT(20),
        "pred_score" real(20),
        "pred_label" integer(20)
    );
    '''

    sql_create_increase_info = '''
    CREATE TABLE if not exists "increase_info" (
        "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "run_prefix" TEXT(20),
        "increase_id" INTEGER
    );
    '''

    sql_create_dia_output_info = '''
    CREATE TABLE if not exists "dia_output_info" (
      "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      "seq_id" text(50),
      "run_prefix" TEXT(50),
      "file_name" TEXT(100),
      "data_source" integer(2),
      "precursor_ident" integer,
      "protein_ident" integer,
      "total_quantity" integer,
      "ms1_signal" integer,
      "ms2_signal" integer,
      "fwhm_scans" real,
      "fwhm_rt" real,
      "acc_ms1" real,
      "acc_ms1_corr" real,
      "acc_ms2" real,
      "acc_ms2_corr" real,
      "ms2_instability" real
    );
    '''

    create_pred_result_index_sql = '''
    CREATE INDEX "seq_id"
    ON "pred_result" (
      "seq_id"
    );
    '''

    create_run_data_index_sql = '''
    CREATE INDEX "run_data_seq_id"
    ON "run_data" (
      "seq_id"
    );
    '''

    create_f4_index_sql = '''
    CREATE INDEX "f4_seq_id"
    ON "run_data_f4" (
      "seq_id"
    );
    '''

    create_s7_index_sql = '''
    CREATE INDEX "s7_seq_id"
    ON "run_data_s7" (
      "seq_id"
    );
    '''

    create_run_info_index_sql1 = '''
    CREATE INDEX "run_id"
    ON "run_info" (
      "run_id"
    );
    '''

    create_run_info_index_sql2 = '''
    CREATE INDEX "run_name"
    ON "run_info" (
      "run_name"
    );
    '''


    cursor.execute(sql_create_inst_info)
    cursor.execute(sql_create_run_data)
    cursor.execute(sql_create_run_data_f4)
    cursor.execute(sql_create_run_data_s7)
    cursor.execute(sql_create_run_info)
    cursor.execute(sql_create_pred_result)
    cursor.execute(sql_create_increase_info)
    cursor.execute(sql_create_dia_output_info)

    try:
        cursor.execute(create_run_info_index_sql1)
    except Exception:
        pass
    try:
        cursor.execute(create_run_info_index_sql2)
    except Exception:
        pass
    try:
        cursor.execute(create_pred_result_index_sql)
    except Exception:
        pass
    try:
        cursor.execute(create_run_data_index_sql)
    except Exception:
        pass
    try:
        cursor.execute(create_f4_index_sql)
    except Exception:
        pass
    try:
        cursor.execute(create_s7_index_sql)
    except Exception:
        pass

    conn.commit()
