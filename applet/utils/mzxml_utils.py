from pyteomics import mzxml, mzml


def read_ms_info(mzxml_path):
    return read_mzml(mzxml_path)


def read_mzxml(mzxml_path):
    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/msInstrument/msModel')
    ms_model = 'DEFAULT'
    for msModel in rawdata_reader:
        ms_model = msModel['value']
        break

    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/parentFile')
    file_type = None
    for msModel in rawdata_reader:
        file_type = msModel['fileType']
        break

    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/msInstrument')
    ins_id = None
    for msModel in rawdata_reader:
        ins_id = str(msModel['msInstrumentID'])
        break
    return ins_id, ms_model


def read_mzml(mzxml_path):
    rawdata_reader = mzml.iterfind(mzxml_path, 'referenceableParamGroupList/referenceableParamGroup')
    ms_model = 'DEFAULT'
    for msModel in rawdata_reader:
        ms_model = msModel['value']
        break

    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/parentFile')
    file_type = None
    for msModel in rawdata_reader:
        file_type = msModel['fileType']
        break

    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/msInstrument')
    ins_id = None
    for msModel in rawdata_reader:
        ins_id = str(msModel['msInstrumentID'])
        break
    return ins_id, ms_model

