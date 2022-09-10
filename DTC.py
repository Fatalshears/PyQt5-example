# UDN1HC


def generate_DTC_py(p_file_name):
    t_file = open(p_file_name,'r')
    o_file = open('output\_prj_para\DTC.py','w')

    start_process = False

    o_file.write(r'import claraNG')
    o_file.write('\n')
    o_file.write(r'from framework import *')
    o_file.write('\n')
    o_file.write('\n')
    o_file.write(r'DTC = CParameterContainer("DTC")')
    o_file.write('\n')
    o_file.write('\n')
    o_file.write(r'DTC.NODTC = CParameterContainer("NODTC")')
    o_file.write('\n')
    o_file.write(r'DTC.NODTC.Code = "0x0"')
    o_file.write('\n')
    o_file.write(r'DTC.NODTC.Priority = "0"')
    o_file.write('\n')
    o_file.write(r'DTC.NODTC.Group = ""')
    o_file.write('\n')
    o_file.write(r'DTC.NODTC.ReferenceDict = {}')
    o_file.write('\n')
    o_file.write('\n')

    for line in t_file:
        if 'define aliases for dtcids' in line:
            start_process = True
            continue
        if start_process is True:
            try:
                def_t, dtc_id, dtc_name = line.split()
            except ValueError as e:
                if 'genInfo' in line:
                    break
                if line.startswith('/* List'):
                    break
                continue
            if 'DemConf_DemDTCClass_' in dtc_name:
                dtc_id = dtc_id.replace('DEM_DTCID_', '')
                dtc_name = dtc_name.replace('DemConf_DemDTCClass_', '')
            else:
                dtc_id = dtc_id.replace('DTCID_', '')
                dtc_name = dtc_name.replace('DTCID_', 'DTC_')
            o_file.write(f'DTC.{dtc_name} = CParameterContainer("{dtc_name}")')
            o_file.write('\n')
            o_file.write(f'DTC.{dtc_name}.Code = "{dtc_id}"')
            o_file.write('\n')
            o_file.write(f'DTC.{dtc_name}.Priority = "1"')
            o_file.write('\n')
            o_file.write(f'DTC.{dtc_name}.Group = ""')
            o_file.write('\n')
            bra = '{}'
            o_file.write(f'DTC.{dtc_name}.ReferenceDict = {bra}')
            o_file.write('\n')
            o_file.write('\n')
            continue
    o_file.close()
    t_file.close()

