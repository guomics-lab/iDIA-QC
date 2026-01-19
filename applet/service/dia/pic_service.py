import os.path
import shutil

from pyecharts import options as opts
from pyecharts.charts import Page, HeatMap, Line, Grid
from pyecharts.commons.utils import JsCode
from pyecharts.globals import Environment, FileSystemLoader
from wx.lib.masked import value

from applet.db import db_utils_run_data
from applet.obj.Entity import FileInfo
from applet.obj.PeptInfo import f_3_pept_list, f_15_16_pept_list, f3_and_f15_pept_list
from applet.service import common_service

y_num_format_jscode = JsCode('''
    function (value) {
        if (Math.abs(value) >= 10000) {
            if (value == 0) {
                return '0';
            } else if ((value + '').indexOf('e') > 0) {
                return (value + '').replace(/e/, 'E');
            } else {
                var res = value.toString();
                var numN1 = 0;
                var numN2 = 0;
                var num1 = 0;
                var num2 = 0;
                var t1 = 1;
                for (var k = 0; k < res.length; k++) {
                    if (res[k] == '.')
                        t1 = 0;
                    if (t1)
                        num1++;
                    else
                        num2++;
                }
                if (Math.abs(value) < 1) {
                    for (var i = 2; i < res.length; i++) {
                        if (res[i] == '0') {
                            numN2++;
                        } else if (res[i] == '.')
                            continue;
                        else
                            break;
                    }
                    var v = parseFloat(value);
                    v = v * Math.pow(10, numN2);
                    v = v.toFixed(1);
                    return v.toString() + 'E-' + numN2;
                } else if (num1 > 1) {
                    numN1 = num1 - 1;
                    var v = parseFloat(value);
                    v = v / Math.pow(10, numN1);
                    if (num2 > 1) {
                        v = v.toFixed(1);
                    }
                    return v.toString() + 'E' + numN1;
                }
            }
        } else {
            var formatVal = new Intl.NumberFormat('en-US', {
              minimumFractionDigits: 1,
              maximumFractionDigits: 1
            }).format(value);
            if(isNaN(formatVal)){
                return 'NA';
            }
            return formatVal
        }
    }
    ''')

y_integer_num_format_jscode = JsCode('''
    function (value) {
        if (Math.abs(value) >= 10000) {
            if (value == 0) {
                return '0';
            } else if ((value + '').indexOf('e') > 0) {
                return (value + '').replace(/e/, 'E');
            } else {
                var res = value.toString();
                var numN1 = 0;
                var numN2 = 0;
                var num1 = 0;
                var num2 = 0;
                var t1 = 1;
                for (var k = 0; k < res.length; k++) {
                    if (res[k] == '.')
                        t1 = 0;
                    if (t1)
                        num1++;
                    else
                        num2++;
                }
                if (Math.abs(value) < 1) {
                    for (var i = 2; i < res.length; i++) {
                        if (res[i] == '0') {
                            numN2++;
                        } else if (res[i] == '.')
                            continue;
                        else
                            break;
                    }
                    var v = parseFloat(value);
                    v = v * Math.pow(10, numN2);
                    v = v.toFixed(1);
                    return v.toString() + 'E-' + numN2;
                } else if (num1 > 1) {
                    numN1 = num1 - 1;
                    var v = parseFloat(value);
                    v = v / Math.pow(10, numN1);
                    if (num2 > 1) {
                        v = v.toFixed(1);
                    }
                    return v.toString() + 'E' + numN1;
                }
            }
        } else {
            return new Intl.NumberFormat('en-US', {
              minimumFractionDigits: 0,
              maximumFractionDigits: 0
            }).format(value);
        }
    }
    ''')

label_number_format_jscode = JsCode('''
    function (datas) {
        var value = datas.value;
        if (Math.abs(value) >= 100000) {
            if (value == 0) {
                return '0';
            } else if ((value + '').indexOf('e') > 0) {
                return (value + '').replace(/e/, 'E');
            } else {
                var res = value.toString();
                var numN1 = 0;
                var numN2 = 0;
                var num1 = 0;
                var num2 = 0;
                var t1 = 1;
                for (var k = 0; k < res.length; k++) {
                    if (res[k] == '.')
                        t1 = 0;
                    if (t1)
                        num1++;
                    else
                        num2++;
                }
                if (Math.abs(value) < 1) {
                    for (var i = 2; i < res.length; i++) {
                        if (res[i] == '0') {
                            numN2++;
                        } else if (res[i] == '.')
                            continue;
                        else
                            break;
                    }
                    var v = parseFloat(value);
                    v = v * Math.pow(10, numN2);
                    v = v.toFixed(1);
                    return v.toString() + 'E-' + numN2;
                } else if (num1 > 1) {
                    numN1 = num1 - 1;
                    var v = parseFloat(value);
                    v = v / Math.pow(10, numN1);
                    if (num2 > 1) {
                        v = v.toFixed(1);
                    }
                    return v.toString() + 'E' + numN1;
                }
            }
        } else {
            return new Intl.NumberFormat('en-US', {
              minimumFractionDigits: 1,
              maximumFractionDigits: 1
            }).format(value);
        }
    }
    ''')

label_integer_number_format_jscode = JsCode('''
    function (datas) {
        var value = datas.value[1];
        if (Math.abs(value) > 10) {
            if (value == 0) {
                return '0';
            } else if ((value + '').indexOf('e') > 0) {
                return (value + '').replace(/e/, 'E');
            } else {
                var res = value.toString();
                var numN1 = 0;
                var numN2 = 0;
                var num1 = 0;
                var num2 = 0;
                var t1 = 1;
                for (var k = 0; k < res.length; k++) {
                    if (res[k] == '.')
                        t1 = 0;
                    if (t1)
                        num1++;
                    else
                        num2++;
                }
                if (Math.abs(value) < 1) {
                    for (var i = 2; i < res.length; i++) {
                        if (res[i] == '0') {
                            numN2++;
                        } else if (res[i] == '.')
                            continue;
                        else
                            break;
                    }
                    var v = parseFloat(value);
                    v = v * Math.pow(10, numN2);
                    v = v.toFixed(1);
                    return v.toString() + 'E-' + numN2;
                } else if (num1 > 1) {
                    numN1 = num1 - 1;
                    var v = parseFloat(value);
                    v = v / Math.pow(10, numN1);
                    if (num2 > 1) {
                        v = v.toFixed(1);
                    }
                    return v.toString() + 'E' + numN1;
                }
            }
        } else {
            return new Intl.NumberFormat('en-US', {
              minimumFractionDigits: 0,
              maximumFractionDigits: 0
            }).format(value);
        }
    }
    ''')


heat_map_format_jscode = JsCode('''
    function (value) {
        var org_file_name = value.data['org_file_name'];
        var yNameList = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15', 'LC', 'MS'];
        var xName = value.name;
        var yName = yNameList[value.data['value'][1]];
        var orgVal = value.data['value'][2];
        if(orgVal==0){
            return org_file_name + '<br> ' + value.marker + '    ' +  yName + ': Qualified';
        }else if(orgVal==1){
            return org_file_name + '<br> ' + value.marker + '    ' +  yName + ': Unqualified';
        }else if(orgVal==-1){
            return org_file_name + '<br> ' + value.marker + '    ' +  yName + ': Do not use';
        }
    }
''')


linemap_format_jscode = JsCode('''
    function (valueArr) {
        var fileName = valueArr[0]['data']['name'];
        var returnStr = fileName;
        valueArr.forEach((eachData, index, e)=>{
            var dataVal = eachData['data']['value'];
            var v = parseFloat(dataVal);
            if(isNaN(v)){
                v = 'NA';
            }else{
                v = v.toFixed(1);
            }
            returnStr = returnStr + '<br> ' + eachData.marker + '    ' + eachData.seriesName + ': ' + v;
        });
        
        return returnStr;
    }
''')

F3_linemap_format_jscode = JsCode('''
    function (valueData) {
        return valueData.marker + '    ' + valueData.seriesName;
    }
''')

F4_linemap_format_jscode = JsCode('''
    function (valueArr) {
        var fileName = valueArr[0]['data']['name'];
        var returnStr = fileName;
        valueArr.forEach((eachData, index, e)=>{
            var dataVal = eachData['data']['value'];
            var v = parseFloat(dataVal);
            v = v.toFixed(1);
            returnStr = returnStr + '<br> ' + eachData.marker + '    ' + eachData.seriesName + ': ' + v + '%';
        });

        return returnStr;
    }
''')


F7_linemap_format_jscode = JsCode('''
    function (valueArr) {
        var fileName = valueArr[0]['data']['name'];
        var returnStr = fileName;
        valueArr.forEach((eachData, index, e)=>{
            var dataVal = eachData['data']['value'];
            var value = parseFloat(dataVal);
            var displayVal = 'NA';
            if (Math.abs(value) > 0) {
                if (value == 0) {
                    displayVal = '0';
                } else if ((value + '').indexOf('e') > 0) {
                    displayVal = (value + '').replace(/e/, 'E');
                } else {
                    var res = value.toString();
                    var numN1 = 0;
                    var numN2 = 0;
                    var num1 = 0;
                    var num2 = 0;
                    var t1 = 1;
                    for (var k = 0; k < res.length; k++) {
                        if (res[k] == '.')
                            t1 = 0;
                        if (t1)
                            num1++;
                        else
                            num2++;
                    }
                    if (Math.abs(value) < 1) {
                        for (var i = 2; i < res.length; i++) {
                            if (res[i] == '0') {
                                numN2++;
                            } else if (res[i] == '.')
                                continue;
                            else
                                break;
                        }
                        var v = parseFloat(value);
                        v = v * Math.pow(10, numN2);
                        v = v.toFixed(1);
                        displayVal = v.toString() + 'E-' + numN2;
                    } else if (num1 > 1) {
                        numN1 = num1 - 1;
                        var v = parseFloat(value);
                        v = v / Math.pow(10, numN1);
                        
                        v = v.toFixed(1);
                        displayVal = v.toString() + 'E' + numN1;
                    }
                }
            }
            
            returnStr = returnStr + '<br> ' + eachData.marker + '    ' + eachData.seriesName + ': ' + displayVal;
        });

        return returnStr;
    }
''')

int_linemap_format_jscode = JsCode('''
    function (valueArr) {
        var fileName = valueArr[0]['data']['name'];
        var returnStr = fileName;
        valueArr.forEach((eachData, index, e)=>{
            var dataVal = eachData['data']['value'];
            var value = parseFloat(dataVal);
            
            var displayVal = new Intl.NumberFormat('en-US', {
              minimumFractionDigits: 0,
              maximumFractionDigits: 0
            }).format(value);

            returnStr = returnStr + '<br> ' + eachData.marker + '    ' + eachData.seriesName + ': ' + displayVal;
        });

        return returnStr;
    }
''')


line_click_event_jscode = '''
    .on('click', function (params) { 
        console.log(params);
    });
    '''



y_font_size = 18
y_rotate = 45

x_font_size = 18
x_rotate = 10
x_font_family = 'Arial'
y_font_family = 'Arial'
title_font_family = 'Arial'
title_font_size = 18
default_y_label = 'Peak asymmetry'

line_width = 3

line_symbol = 'diamond'
line_symbol_size = 15

echars_width = '1200px'
echars_height = '600px'

x_axislabel_opts = opts.LabelOpts(margin=20, font_family=x_font_family, font_weight='bolder', font_style='normal',
                                  font_size=8, rotate=10)

y_axislabel_opts = opts.LabelOpts(formatter=y_num_format_jscode, margin=20, font_family=x_font_family,
                                  font_weight='bolder', font_style='normal',
                                  font_size=x_font_size)

y_int_axislabel_opts = opts.LabelOpts(formatter=y_integer_num_format_jscode, margin=20, font_family=x_font_family,
                                      font_weight='bolder', font_style='normal',
                                      font_size=x_font_size)

y_axislabel_opts_without_num = opts.LabelOpts(margin=20, font_family=x_font_family, font_weight='bolder',
                                              font_style='normal',
                                              font_size=x_font_size)

label_text_style = opts.TextStyleOpts(font_weight='bolder', font_style='normal',
                                      font_family='Arial', font_size=x_font_size)

lagent_label_text_style = opts.TextStyleOpts(font_weight='bolder', font_style='normal',
                                             font_family='Arial', font_size=14)

F3_lagent_label_text_style = opts.TextStyleOpts(font_weight='bolder', font_style='normal',
                                             font_family='Arial', font_size=8)

init_opts = opts.InitOpts(width=echars_width, height=echars_height)


class PicService(common_service.CommonService):
    def __init__(self, base_output_path, file_list: [FileInfo], logger, run_id_list=None, step=11,
                 pub_channel='analysis_info', start_time=0, conn_send=None):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time, conn_send=conn_send)
        self.run_id_list = run_id_list
        self.pic_save_path = os.path.join(base_output_path, 'pic')
        self.init_dir()

    def init_dir(self):
        if os.path.exists(self.pic_save_path):
            shutil.rmtree(self.pic_save_path)
        os.makedirs(self.pic_save_path)

    #
    def draw_pic_select(self):
        logger = self.logger
        try:
            self.is_running = True
            run_info_list = db_utils_run_data.query_run_info_list(self.run_id_list)
            self.draw_by_run_info_list('Selected-', run_info_list)
            return True
        except Exception as e:
            logger.exception('Deal draw pic exception')
            return False
        finally:
            self.is_running = False

    def draw_pic_param(self, search_param):
        #
        #
        logger = self.logger
        try:
            self.is_running = True
            inst_id_info_dict = {}
            inst_name = search_param['inst_name']
            search_num = search_param['search_num']
            run_data_type = search_param['run_data_type']
            run_info_list_all = db_utils_run_data.query_run_info_param(inst_name, search_num, run_data_type)
            #
            run_info_list_all.sort(key=lambda x: x.id, reverse=False)
            if len(run_info_list_all) == 0:
                logger.info('Draw no data, ins_name = {}, search_num = {}'.format(inst_name, search_num))
                return True
            for run_info in run_info_list_all:
                inst_id_info_dict.setdefault(run_info.run_prefix, []).append(run_info)

            for run_prefix in inst_id_info_dict.keys():
                run_info_list = inst_id_info_dict[run_prefix]
                self.draw_by_run_info_list(run_prefix, run_info_list)

            return True
        except Exception as e:
            logger.exception('Deal draw pic exception')
            return False
        finally:
            self.is_running = False

    def draw_pic_all(self, source, draw_run_prefix=None):
        #
        #
        logger = self.logger
        try:
            self.send_msg(0, 'Saving the html file, path is: {}'.format(self.pic_save_path), with_time=True)
            self.is_running = True
            inst_id_info_dict = {}
            run_info_list_all = db_utils_run_data.query_run_info_all(source)
            for run_info in run_info_list_all:
                inst_id_info_dict.setdefault(run_info.run_prefix, []).append(run_info)

            for run_prefix in inst_id_info_dict.keys():
                if draw_run_prefix:
                    if run_prefix == draw_run_prefix:
                        run_info_list = inst_id_info_dict[run_prefix]
                        self.draw_by_run_info_list(run_prefix, run_info_list)
                else:
                    run_info_list = inst_id_info_dict[run_prefix]
                    self.draw_by_run_info_list(run_prefix, run_info_list)

            self.send_msg(1, '')
            return True
        except Exception as e:
            logger.exception('Deal draw pic exception')
            return False
        finally:
            self.is_running = False

    '''
    '''
    def build_file_name(self, org_file_name):
        file_name_arr = org_file_name.split('_')
        return file_name_arr[0] + '_' + file_name_arr[-1].split('.')[0]

    def draw_by_run_info_list(self, run_prefix, run_info_list):
        seq_id_list = []
        run_id_list = []
        d_file_run_id_list = []
        run_id_file_name_dict = {}

        seq_run_id_dict = {}
        for d in run_info_list:
            seq_id_list.append(d.seq_id)
            run_id_list.append(d.run_id)
            seq_run_id_dict[d.seq_id] = d.run_id
            if d.file_type == 'D':
                d_file_run_id_list.append(d.run_id)
            run_id_file_name_dict[d.run_id] = self.build_file_name(d.file_name)

        run_data_list = db_utils_run_data.query_run_data(seq_id_list)

        seq_fn_data_dict = {}
        for dd in run_data_list:
            seq_fn_data_dict['{}_{}'.format(dd.seq_id, dd.data_tag)] = dd.data_val

        data_tag_list = ['6', '7', '8', '9', '10', '11', '12', '13', '14', '51', '52', '53', '54', '55', '56',
                         '501', '502',
                         '503', '504', '505']
        fn_data_dict = {}
        for run_info in run_info_list:
            seq_id = run_info.seq_id
            for data_tag in data_tag_list:
                fn_data_dict.setdefault(data_tag, []).append(
                    seq_fn_data_dict.get('{}_{}'.format(seq_id, data_tag)))

        run_data_f4_list = db_utils_run_data.query_run_f4_data(seq_id_list)
        f4_data_dict = {}
        for dd in run_data_f4_list:
            f4_data_dict.setdefault(seq_run_id_dict[dd.seq_id], [None] * 1000)[dd.data_index] = dd.data_val

        s7_seq_data_tag_dict = {}
        s7_data_list = db_utils_run_data.query_run_s7_data(seq_id_list)
        for s7_data in s7_data_list:
            s7_seq_data_tag_dict[
                '{}_{}_{}'.format(s7_data.seq_id, s7_data.data_tag, s7_data.pept)] = s7_data.data_val

        s7_data_dict = {}
        for data_tag in ['103']:
            s7_data_tag_dict = {}
            for pept_name in f3_and_f15_pept_list:
                for run_info in run_info_list:
                    seq_id = run_info.seq_id
                    pept_val = s7_seq_data_tag_dict.get('{}_{}_{}'.format(seq_id, data_tag, pept_name))
                    s7_data_tag_dict.setdefault(pept_name, []).append(pept_val)
            s7_data_dict[data_tag] = s7_data_tag_dict

        for data_tag in ['15', '16']:
            s7_data_tag_dict = {}
            for pept_name in f3_and_f15_pept_list:
                for run_info in run_info_list:
                    seq_id = run_info.seq_id
                    pept_val = s7_seq_data_tag_dict.get('{}_{}_{}'.format(seq_id, data_tag, pept_name))
                    if pept_val and float(pept_val) == 0:
                        pept_val = None
                    s7_data_tag_dict.setdefault(pept_name, []).append(pept_val)
            s7_data_dict[data_tag] = s7_data_tag_dict

        pred_info_dict = {}
        pred_info_list = db_utils_run_data.query_all_pred_info(seq_id_list)
        for pred_info in pred_info_list:
            thiz_run_id = seq_run_id_dict[pred_info.seq_id]
            if thiz_run_id not in d_file_run_id_list and pred_info.pred_key == 'F15':
                continue
            pred_info_dict[
                '{}_{}'.format(thiz_run_id, pred_info.pred_key)] = pred_info.pred_label



        if len(run_info_list) == 1:
            self.page_draw_f_html(run_info_list[0].run_id, run_id_list, fn_data_dict, f4_data_dict, s7_data_dict,
                                  pred_info_dict,
                                  self.pic_save_path, run_id_file_name_dict)
        else:
            self.page_draw_f_html('{}_{}files_report_combination'.format(run_info_list[0].run_id, len(run_info_list)),
                                  run_id_list, fn_data_dict, f4_data_dict, s7_data_dict,
                                  pred_info_dict,
                                  self.pic_save_path, run_id_file_name_dict)

    def page_draw_f_html(self, run_prefix, run_id_list, fn_data_dict: dict, f4_data_dict: dict,
                         s7_data_tag_dict: dict,
                         pred_info_dict: dict, html_dir_path, run_id_file_name_dict: dict):

        echars_list1 = self.draw_f_html(run_id_list, fn_data_dict, run_id_file_name_dict)
        echars_f4 = self.draw_f4_html(run_id_list, f4_data_dict, run_id_file_name_dict)
        echars_list3 = self.draw_s7_html(run_id_list, s7_data_tag_dict, run_id_file_name_dict)
        heat_map_pic = self.draw_heat_map_html(run_id_list, pred_info_dict, run_id_file_name_dict)

        line_pic_list = []
        page = Page(layout=Page.SimplePageLayout, interval=10, page_title='iDIA-QC')
        page.add(heat_map_pic)
        line_pic_list.extend(echars_list1)
        line_pic_list.append(echars_f4)
        line_pic_list.extend(echars_list3)
        line_pic_list.sort(key=lambda x:x.index)
        for line_pic in line_pic_list:
            page.add(line_pic)

        page.render(os.path.join(html_dir_path, run_prefix + '.html'))


    def draw_f_html(self, run_id_list, fn_data_dict: dict, run_id_file_name_dict: dict):

        echart_list = []

        f_tag_list = fn_data_dict.keys()
        for f_tag in f_tag_list:
            display_tag = ''
            f_data_list = fn_data_dict[f_tag]
            y_name = ''
            subtitle = ''
            if f_tag == '51' or f_tag == '52' or f_tag == '53' or f_tag == '54' or f_tag == '55' or f_tag == '56':
                continue
            elif f_tag == '6':
                y_name = '%'
                subtitle = 'Intensity variation of adjacent MS1 scan (%)'
                display_tag = '5'
            elif f_tag == '7':
                y_name = 'ppm'
                subtitle = 'Median MS1 accuracy of identified precursors (ppm)'
                display_tag = '6'
            elif f_tag == '8':
                y_name = 'TIC MS1 signal'
                subtitle = 'TIC MS1 signal'
                display_tag = '7'
            elif f_tag == '9':
                y_name = 'Peak width of targeted precursors'
                subtitle = 'Peak width of targeted precursors'
                display_tag = '1'
            elif f_tag == '10':
                y_name = 'ppm'
                subtitle = 'Median MS2 accuracy of identified precursors (ppm)'
                display_tag = '8'
            elif f_tag == '11':
                y_name = ''
                subtitle = 'TIC MS2 signal'
                display_tag = '9'
            elif f_tag == '12':
                y_name = ''
                subtitle = 'Ratio of MS1 to MS2 signal'
                display_tag = '10'
            elif f_tag == '13':
                y_name = ''
                subtitle = 'Number of identified peptides'
                display_tag = '11'
            elif f_tag == '14':
                y_name = ''
                subtitle = 'Number of identified proteins'
                display_tag = '12'
            elif f_tag == '17':
                y_name = ''
                subtitle = 'Ion mobility accuracy'
                display_tag = '15'
            else:
                continue

            line_pic = Line(init_opts)
            line_pic.add_xaxis([run_id_file_name_dict.get(nnn) for nnn in run_id_list])

            series_data = [opts.LineItem(name=run_id_file_name_dict.get(run_id_list[ppp]), value=f_data, symbol=None, symbol_size=None) for ppp, f_data in enumerate(f_data_list)]

            line_pic.add_yaxis(series_name=subtitle, y_axis=series_data, label_opts=opts.LabelOpts(is_show=False))

            if display_tag == '6' or display_tag == '8' or display_tag == '1' or display_tag == '5':
                val_formatter = y_num_format_jscode
                y_axislabel = y_axislabel_opts
            else:
                val_formatter = y_integer_num_format_jscode
                y_axislabel = y_int_axislabel_opts

            if display_tag == '7' or display_tag == '9':
                tooltip_format = F7_linemap_format_jscode
            elif display_tag == '11' or display_tag == '12':
                tooltip_format = int_linemap_format_jscode
            else:
                tooltip_format = linemap_format_jscode

            line_pic.set_global_opts(
                title_opts=opts.TitleOpts(title='F' + display_tag + ': ' + subtitle, pos_left='center',
                                          title_textstyle_opts=label_text_style),
                tooltip_opts=opts.TooltipOpts(trigger="axis", value_formatter=val_formatter,
                                              textstyle_opts=label_text_style,
                                              formatter=tooltip_format),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name=subtitle,
                    name_location='middle',
                    name_gap=80,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    name_textstyle_opts=label_text_style,
                    axislabel_opts=y_axislabel
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    boundary_gap=True,
                    name='Run ID',
                    name_location='center',
                    name_gap=40,
                    name_textstyle_opts=label_text_style,
                    axislabel_opts=x_axislabel_opts),
                legend_opts=opts.LegendOpts(is_show=False)
            )

            line_pic.set_series_opts(symbol=line_symbol, symbolSize=line_symbol_size,
                                     linestyle_opts=opts.LineStyleOpts(width=line_width))
            grid = (
                Grid(init_opts).add(line_pic, grid_opts=opts.GridOpts(pos_right="15%"), is_control_axis_index=True)
            )
            grid.index = int(display_tag)
            echart_list.append(grid)

        f51_data_list = fn_data_dict["51"]
        f52_data_list = fn_data_dict["52"]
        f53_data_list = fn_data_dict["53"]
        f54_data_list = fn_data_dict["54"]
        f55_data_list = fn_data_dict["55"]
        f56_data_list = fn_data_dict["56"]

        line_pic = Line(init_opts)
        line_pic.index = 4
        x_list = [run_id_file_name_dict.get(nnn) for nnn in run_id_list]
        line_pic.add_xaxis(x_list)

        line_pic.add_yaxis(series_name='+1_percent', y_axis=[
            opts.LineItem(name=run_id_file_name_dict.get(run_id_list[ppp]), value=f_data, symbol=None, symbol_size=None)
            for ppp, f_data in enumerate(f51_data_list)], label_opts=opts.LabelOpts(is_show=False))
        line_pic.add_yaxis(series_name='+2_percent', y_axis=[
            opts.LineItem(name=run_id_file_name_dict.get(run_id_list[ppp]), value=f_data, symbol=None, symbol_size=None)
            for ppp, f_data in enumerate(f52_data_list)], label_opts=opts.LabelOpts(is_show=False))
        line_pic.add_yaxis(series_name='+3_percent', y_axis=[
            opts.LineItem(name=run_id_file_name_dict.get(run_id_list[ppp]), value=f_data, symbol=None, symbol_size=None)
            for ppp, f_data in enumerate(f53_data_list)], label_opts=opts.LabelOpts(is_show=False))
        line_pic.add_yaxis(series_name='+4_percent', y_axis=[
            opts.LineItem(name=run_id_file_name_dict.get(run_id_list[ppp]), value=f_data, symbol=None, symbol_size=None)
            for ppp, f_data in enumerate(f54_data_list)], label_opts=opts.LabelOpts(is_show=False))
        line_pic.add_yaxis(series_name='+5_percent', y_axis=[
            opts.LineItem(name=run_id_file_name_dict.get(run_id_list[ppp]), value=f_data, symbol=None, symbol_size=None)
            for ppp, f_data in enumerate(f55_data_list)], label_opts=opts.LabelOpts(is_show=False))
        line_pic.add_yaxis(series_name='+6_percent', y_axis=[
            opts.LineItem(name=run_id_file_name_dict.get(run_id_list[ppp]), value=f_data, symbol=None, symbol_size=None)
            for ppp, f_data in enumerate(f56_data_list)], label_opts=opts.LabelOpts(is_show=False))

        y_name = 'Charge state distribution (%)'
        subtitle = 'Charge state distribution (%)'
        line_pic.set_global_opts(
            title_opts=opts.TitleOpts(title='F4: ' + subtitle, pos_left='center', text_align=None,
                                      title_textstyle_opts=label_text_style,
                                      ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", value_formatter=y_integer_num_format_jscode,
                                          textstyle_opts=label_text_style,
                                        formatter=F4_linemap_format_jscode),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name=y_name,
                name_location='middle',
                name_gap=80,
                name_textstyle_opts=label_text_style,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=y_int_axislabel_opts,
            ),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                boundary_gap=True,
                name='Run ID',
                name_location='center',
                name_gap=40,
                name_textstyle_opts=label_text_style,

                axislabel_opts=x_axislabel_opts),
            legend_opts=opts.LegendOpts(type_='scroll', orient='vertical', align='auto', pos_right='right',
                                        textstyle_opts=lagent_label_text_style)
        )
        line_pic.set_series_opts(symbol=line_symbol, symbolSize=line_symbol_size,
                                 linestyle_opts=opts.LineStyleOpts(width=line_width))
        grid = (
            Grid(init_opts).add(line_pic, grid_opts=opts.GridOpts(pos_right="15%"), is_control_axis_index=True)
        )
        grid.index = 4
        echart_list.append(grid)
        return echart_list

    #
    def draw_f4_html(self, run_id_list, f4_data_dict: dict, run_id_file_name_dict: dict):

        line_pic = Line(init_opts)
        line_pic.index = 3
        x_list = [str((i + 1)).zfill(3) for i in range(1, 1001)]
        line_pic.add_xaxis(x_list)
        for run_id in run_id_list:
            line_pic.add_yaxis(series_name=run_id_file_name_dict.get(run_id), y_axis=f4_data_dict[run_id],
                               label_opts=opts.LabelOpts(is_show=False),
                               tooltip_opts=opts.TooltipOpts(trigger="item",
                                      textstyle_opts=label_text_style,
                                      formatter=F3_linemap_format_jscode),
                               emphasis_opts=opts.EmphasisOpts(focus='series', linestyle_opts=opts.LineStyleOpts(width=line_width, opacity=1)))

        line_pic.set_global_opts(
            datazoom_opts=opts.DataZoomOpts(range_start=1, range_end=1000, pos_bottom='2px'),
            title_opts=opts.TitleOpts(title='F3: Precursor ion chromatogram', pos_left='center',
                                      title_textstyle_opts=label_text_style,
                                      ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name='Precursor ion chromatogram',
                name_location='middle',
                name_gap=80,
                name_textstyle_opts=label_text_style,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=y_int_axislabel_opts
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=True, name='Index', name_location='end',
                                     name_gap=40,
                                     name_textstyle_opts=label_text_style,
                                     axislabel_opts=x_axislabel_opts),
            legend_opts=opts.LegendOpts(type_='scroll', orient='vertical', align='auto', pos_right='right',
                                        textstyle_opts=F3_lagent_label_text_style),
        )
        line_pic.set_series_opts(linestyle_opts=opts.LineStyleOpts(width=line_width, opacity=0.5))
        grid = (
            Grid(init_opts).add(line_pic, grid_opts=opts.GridOpts(pos_right="15%"), is_control_axis_index=True)
        )
        grid.add_js_events('chart_' + line_pic.get_chart_id() + line_click_event_jscode)

        grid.index = 3
        return grid

    def draw_s7_html(self, run_id_list, s7_data_tag_dict: dict, run_id_file_name_dict: dict):

        file_name_list = [run_id_file_name_dict.get(run_id) for run_id in run_id_list]

        s7_echars_list = []
        for data_tag in s7_data_tag_dict.keys():
            y_name = ''
            subtitle = ''
            display_tag = ''

            if data_tag == '103':
                y_name = 'min'
                subtitle = 'Retention time (min)'
                display_tag = '2'
            elif data_tag == '9':
                y_name = ''
                subtitle = 'Data points per peak'
                display_tag = '1'
            elif data_tag == '15':
                y_name = ''
                subtitle = 'MS1 signal of targeted peptide precursors'
                display_tag = '13'
            elif data_tag == '16':
                y_name = ''
                subtitle = 'MS2 intensity of targeted peptide precursors'
                display_tag = '14'
            y_name = default_y_label
            pept_data_info = s7_data_tag_dict[data_tag]
            pept_list = list(pept_data_info.keys())

            if display_tag == '2':
                tooltip_value_formatter = y_num_format_jscode
                # legend_style = opts.LegendOpts(type_='scroll', orient='vertical', align='auto',pos_right=-150, pos_top=-20,pos_bottom=100, padding=50, border_color='white',textstyle_opts=lagent_label_text_style)
                legend_style = opts.LegendOpts(type_='scroll', orient='vertical', align='auto', pos_right='right',
                                               textstyle_opts=lagent_label_text_style)
            else:
                tooltip_value_formatter = y_integer_num_format_jscode
                legend_style = opts.LegendOpts(type_='scroll', orient='vertical', align='auto', pos_right='right',
                                               textstyle_opts=lagent_label_text_style)

            if display_tag == '13' or display_tag == '14':
                yaxis_type = 'log'
                tooltip_format = F7_linemap_format_jscode
            else:
                yaxis_type = 'value'
                tooltip_format = linemap_format_jscode

            line_pic = Line(init_opts)
            line_pic.index = int(display_tag)

            line_pic.add_xaxis(file_name_list)
            line_pic.set_global_opts(
                title_opts=opts.TitleOpts(title='F' + display_tag + ': ' + subtitle, pos_left='center',
                                          text_align=None,
                                          title_textstyle_opts=label_text_style,
                                          ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", value_formatter=tooltip_value_formatter,
                                              textstyle_opts=label_text_style,
                                              formatter=tooltip_format),
                yaxis_opts=opts.AxisOpts(
                    type_=yaxis_type,
                    name=subtitle,
                    name_location='middle',
                    name_gap=80,
                    name_textstyle_opts=label_text_style,
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    axislabel_opts=y_int_axislabel_opts
                ),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=True, name='Run ID', name_location='center',
                                         name_gap=40,
                                         name_textstyle_opts=label_text_style,
                                         axislabel_opts=x_axislabel_opts),
                legend_opts=legend_style
            )
            for pept in pept_list:
                data_list = pept_data_info[pept]

                y_series_data = [
                    opts.LineItem(name=run_id_file_name_dict.get(run_id_list[ppp]), value=f_data, symbol=None,
                                  symbol_size=None) for ppp, f_data in enumerate(data_list)]

                if pept in f_3_pept_list:
                    line_pic.add_yaxis(series_name=f'{pept}*', y_axis=y_series_data, label_opts=opts.LabelOpts(is_show=False),
                                   emphasis_opts=opts.EmphasisOpts(focus='series', linestyle_opts=opts.LineStyleOpts(width=line_width, opacity=1)))
                else:
                    line_pic.add_yaxis(series_name=pept, y_axis=y_series_data, label_opts=opts.LabelOpts(is_show=False),
                                   emphasis_opts=opts.EmphasisOpts(focus='series', linestyle_opts=opts.LineStyleOpts(width=line_width, opacity=1)))

            if data_tag == '103':
                line_pic.set_series_opts(symbol=line_symbol, symbolSize=line_symbol_size,
                                         linestyle_opts=opts.LineStyleOpts(width=line_width, opacity=0.5))
            else:
                line_pic.set_series_opts(symbol=line_symbol, symbolSize=line_symbol_size,
                                         linestyle_opts=opts.LineStyleOpts(width=line_width, opacity=0.5))
            grid = (
                Grid(init_opts).add(line_pic, grid_opts=opts.GridOpts(pos_right="15%"), is_control_axis_index=True)
            )
            grid.index = int(display_tag)
            s7_echars_list.append(grid)
        return s7_echars_list

    '''
    '''

    def draw_heat_map_html(self, run_id_list, pred_info_dict: dict, run_id_file_name_dict: dict):

        xaxis_list = []
        display_val = []
        display_y_list = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14',
                          'F15', 'LC', 'MS']
        yaxis_list = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14',
                      'F15',
                      'lc', 'ms']


        for x_index, run_id in enumerate(run_id_list):
            xaxis_list.append(run_id_file_name_dict.get(run_id))
            for y_index, pred_key in enumerate(yaxis_list):
                each_val = pred_info_dict.get('{}_{}'.format(run_id, pred_key))
                if each_val is None:
                    each_val = -1
                display_val.append({'value': [x_index, y_index, each_val], 'org_file_name': run_id_file_name_dict.get(run_id)})


        heat_map_pic = HeatMap(init_opts)
        heat_map_pic.add_xaxis(xaxis_list)
        heat_map_pic.add_yaxis(
            "series0",
            display_y_list,
            display_val,
            label_opts=opts.LabelOpts(is_show=True, position="inside"),
        )
        heat_map_pic.set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                                     tooltip_opts=opts.TooltipOpts(formatter=heat_map_format_jscode,
                                                                   textstyle_opts=label_text_style))
        heat_map_pic.set_global_opts(
            title_opts=opts.TitleOpts(title='Metric performance prediction', pos_left='center', text_align=None,
                                      title_textstyle_opts=label_text_style,
                                      ),
            visualmap_opts=opts.VisualMapOpts(pos_top='50px', pos_right='5px', min_=-1, max_=1,
                                              range_color=['gray', '#118C4F', '#BC1211'], is_piecewise=True,
                                              is_show=True,
                                              pieces=[{'value': -1, 'label': 'Do not use', 'color': 'gray'},
                                                      {'value': 0, 'label': 'Qualified'},
                                                      {'value': 1, 'label': 'Unqualified'}],
                                              textstyle_opts=label_text_style),
            yaxis_opts=opts.AxisOpts(
                name_textstyle_opts=label_text_style,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=y_axislabel_opts_without_num
            ),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                boundary_gap=True,
                name='Run ID',
                name_location='center',
                name_gap=40,
                name_textstyle_opts=label_text_style,
                axislabel_opts=x_axislabel_opts),
            legend_opts=opts.LegendOpts(is_show=False),
        )
        heat_map_pic.set_series_opts(itemstyle_opts=opts.ItemStyleOpts(border_color='white', border_width=2))

        grid = (
            Grid(init_opts).add(heat_map_pic, grid_opts=opts.GridOpts(pos_right="15%"), is_control_axis_index=True)
        )
        return grid
