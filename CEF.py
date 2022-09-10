# UDN1HC
import os, stat


def collect_files(p_file_name, p_directory, p_file_match_list):
    """get necessary file paths related to XCP"""

    for root, dirs, files in os.walk(p_directory):
        for file in files:
            for item in p_file_name:
                if item in file:
                    p_file_match_list.append(root+'\\'+str(file))


def parse_error_log(p_error_log, p_error_list, p_file_match_list):
    """search error log for typical errors in XCP"""
    p_error_set = set([])
    file = open(p_error_log, 'rt')
    for line in file:
        if 'ERROR' in line and 'adding variable:' in line:
            first_index = line.index('"_')
            t_error_element = line[first_index+1:len(line)-2]
            p_error_list.add(t_error_element)
        elif 'ERROR' in line and 'adding variableInfoData_p2' in line:
            first_index = line.index('"_')
            t_error_element = line[first_index+1:len(line)-2]
            p_error_list.add(t_error_element)

    file.close()
    # print(p_error_list)
    for error in p_error_list:
        for cpp_file in p_file_match_list:
            if 'CXcpMeasureT20Even.cpp' in cpp_file or 'CXcpBypassingDsp.cpp' in cpp_file or 'CXcpMeasureTC.cpp' or 'CXcpMeasureT10.cpp' or 'CXcpMeasC0T20.cpp' in cpp_file:
                t_file = open(cpp_file, 'r')
                for line in t_file:
                    if error in line:
                        last_index_comma = line.rfind(',')
                        last_index_eol = line.rfind(')')
                        update_error = line[last_index_comma+1: last_index_eol].strip()
                        p_error_set.add(update_error)
                        break
                t_file.close()

    p_error_list.clear()
    p_error_list.update(p_error_set)


def fix_error_log(p_error_list, p_file_match_list):
    """disable LOCs caused error"""
    for file in p_file_match_list:
        input_file = open(file, 'r')
        output_file = open('CEFtemporary.txt', 'w')

        for line in input_file:
            for error in p_error_list:
                if error in line and '//@CorrectedByTool' not in line:
                    line = '//@CorrectedByTool ' + line
            output_file.write(line)

        output_file.close()
        input_file.close()
        # copy content from temporary file to original files
        os.chmod(file, stat.S_IRWXU)
        input_file = open(file, 'w')
        output_file = open('CEFtemporary.txt', 'r')

        for line in output_file:
            input_file.write(line)
        output_file.close()
        input_file.close()


def run_compiler_error_fix(p_directory, p_error_log):
    p_file_name = ['CXcpMeasureT20Even.cpp', 'CXcpMeasureT20Even.h',
                   'CXcpMeasureT10.cpp', 'CXcpMeasureT10.h',
                 'CCfgXcpMeasurement.cpp',
                 'CXcpBypassingDsp.cpp', 'CXcpBypassingDsp.h',
                 'CXcpMeasureTC.cpp', 'CXcpMeasureTC.h',
                   'CXcpMeasC0T20.cpp', 'CXcpMeasC0T20.h'
                   ]
    p_file_match_list = []
    p_error_list = set([])
    collect_files(p_file_name, p_directory, p_file_match_list)
    parse_error_log(p_error_log, p_error_list, p_file_match_list)
    fix_error_log(p_error_list, p_file_match_list)


def determine_data_type(p_signal_name):
    p_temp = p_signal_name.lower()
    p_data_type = 'uint8_t'
    if p_temp.endswith('_b'):
        p_data_type = 'uint8_t'
    elif p_temp.endswith('_uw'):
        p_data_type = 'uint16_t'
    elif p_temp.endswith('_sw'):
        p_data_type = 'int16_t'
    elif p_temp.endswith('_ub'):
        p_data_type = 'uint8_t'
    elif p_temp.endswith('_b1'):
        p_data_type = 'uint8_t'
    elif p_temp.endswith('_ul'):
        p_data_type = 'uint32_t'
    elif p_temp.endswith('_sl'):
        p_data_type = 'int32_t'

    # p_label = '_' + p_signal_name.replace('.', '._')
    # p_xcp = '_' + p_signal_name.replace('.', '_')

    p_label = p_signal_name  # LINK_MAP in a2l
    p_xcp = p_signal_name.replace('.', '_')
    return p_data_type, p_label, p_xcp


def run_signal_measure_calib(p_signal_name, p_type, p_directory):
    p_file_match_list = []
    p_file_name =[]
    p_data_type, p_label, p_xcp = determine_data_type(p_signal_name)
    if p_type == 'mTC':
        p_file_name = ['CXcpMeasureTC.cpp', 'CXcpMeasureTC.h', 'CCfgXcpMeasurement.cpp']
    elif p_type == 'mT10':
        p_file_name = ['CXcpMeasureT10.cpp', 'CXcpMeasureT10.h', 'CCfgXcpMeasurement.cpp']
    elif p_type == 'mT20':
        p_file_name = ['CXcpMeasureT20Even.cpp', 'CXcpMeasureT20Even.h', 'CCfgXcpMeasurement.cpp']
    elif p_type == 'calib':
        p_file_name = ['CXcpCalibrate.cpp', 'CXcpCalibrate.h', 'CCfgXcpCalibration.cpp']
    collect_files(p_file_name, p_directory, p_file_match_list)

    for file in p_file_match_list:
        input_file = open(file, 'r')
        output_file = open('SIGtemporary.txt', 'w')
        check_bracket0 = False
        check_bracket1 = False
        not_done = True
        for line in input_file:
            output_file.write(line)
            if not_done and ('CXcpMeasureTC.h' in file or 'CXcpMeasureT10.h' in file or 'CXcpMeasureT20Even.h' in file or 'CXcpCalibrate.h' in file):
                if 'initXcpSignals();' in line:
                    add_signal = f'CXcpSignal<{p_data_type}> {p_xcp}; //Added by Tool\n'
                    output_file.write(add_signal)
                    not_done = False
            elif not_done and ('CXcpMeasureTC.cpp' in file or 'CXcpMeasureT10.cpp' in file or 'CXcpMeasureT20Even.cpp' in file):
                if '::initXcpSignals()' in line:
                    check_bracket0 = True
                    continue
                if check_bracket0 and '{' in line:
                    add_signal = f'addSignalMeas( "\\"{p_label}\\"", {p_xcp} ); //Added by Tool\n'
                    check_bracket0 = False
                    output_file.write(add_signal)
                    not_done = False
            elif not_done and ('CXcpCalibrate.cpp' in file):
                if '::initXcpSignals()' in line:
                    check_bracket1 = True
                    continue
                if check_bracket1 and '{' in line:
                    add_signal = f'addSignalCali( "\\"{p_label}\\"", {p_xcp} ); //Added by Tool\n'
                    check_bracket1 = False
                    output_file.write(add_signal)
                    not_done = False
            elif not_done and 'CCfgXcpCalibration.cpp' in file:
                if '#endif' in line:
                    add_signal = f'append( "XcpCalibrate.{p_label}", XcpCalibrate.{p_xcp}); //Added by Tool\n'
                    output_file.write(add_signal)
                    not_done = False
            elif not_done and 'CCfgXcpMeasurement.cpp' in file:
                if '#ifdef XCP_MEASUREMENT' in line:
                    if p_type == 'mTC':
                        add_signal = f'append( "XcpTC.{p_label}", XcpTC.{p_xcp} ); //Added by Tool\n'
                        output_file.write(add_signal)
                        not_done = False
                    elif p_type == 'mT10':
                        add_signal = f'append( "XcpT10.{p_label}", XcpT10.{p_xcp} ); //Added by Tool\n'
                        output_file.write(add_signal)
                        not_done = False
                    elif p_type == 'mT20':
                        add_signal = f'append( "XcpT20Even.{p_label}", XcpT20Even.{p_xcp} ); //Added by Tool\n'
                        output_file.write(add_signal)
                        not_done = False

        not_done = True
        output_file.close()
        input_file.close()
        # copy content from temporary file to original files
        input_file = open(file, 'w')
        output_file = open('SIGtemporary.txt', 'r')

        for line in output_file:
            input_file.write(line)
        output_file.close()
        input_file.close()

# if __name__ == '__main__':
#     file_name = ['CXcpMeasureT20Even.cpp', 'CXcpMeasureT20Even.h',
#                  'CCfgXcpMeasurement.cpp',
#                  'CXcpBypassingDsp.cpp', 'CXcpBypassingDsp.h',
#                  'CXcpMeasureTC.cpp', 'CXcpMeasureTC.h']
#     directory = r'X:\claraNG\_prj_C211NE14T_evo14_V1\simulation'
#     file_match_list = []
#     error_log = r'D:\FirstPj\reference.txt'
#     error_list = set([])
#
#     collect_files(file_name, directory, file_match_list)
#     parse_error_log(error_log, error_list, file_match_list)
#     fix_error_log(error_list, file_match_list)