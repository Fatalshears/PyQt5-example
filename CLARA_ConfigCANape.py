#===============================================================================
#udm1hc
#refer from CT Project, author: chh1hc
#===============================================================================

import os
import re


###############
# call edit_config_canape function with input parameter is the SW path
###############

# Enter SW path
# sw_path = r'D:\udm1hc\Tools\SAIC_AS23_MCE_R1.0_I0_internal'

#Global Function
def findfolder(pattern, path):
    result = {'path' : '', 'name': ''}
    for root, dirs, files in os.walk(path):
        for name in dirs:
            if search_f(name, pattern):
                result['path'] = os.path.join(root, name).replace('\\', '/')
                result['name'] = name        
                return result
    return result

def findfile(pattern, path, extension = ''):
    result = {'path' : '', 'name': ''}
    for root, dirs, files in os.walk(path):
        for name in files:            
            if extension != '':
                if name.endswith(extension) == False:
                    continue        
            if search_f(name, pattern):                
                result['path'] = os.path.join(root, name).replace('\\', '/')
                result['name'] = name  
                break
    return result

def replace_f(strInput, Pattern, strRplace):    
    if re.search(Pattern, strInput, re.IGNORECASE) != None : 
        return re.sub(Pattern, strRplace, re.search(Pattern, strInput, re.IGNORECASE).group(), re.IGNORECASE)

def search_f(strInput, Pattern):   
    if re.search(Pattern, strInput, re.IGNORECASE) != None : 
        return re.search(Pattern, strInput, re.IGNORECASE).group()
    else:
        return ""
def write(str):
    print('## ' +str + ' ##\n')

#Function
def PreCheck(sw_path):
    canapePath = findfolder('canape', sw_path)['path']
    cnaPath = os.path.join(canapePath, "MRR1plus.cna")
    f = open(cnaPath, "r")
    data = f.read()    
    if 'ClaraTest_ACC' in data:
        write('Pre Check: did it')
        return 'did it'
    else:
        write('Pre Check: not yet')
        return 'not yet'

def configIPflash(sw_path): 
    flashPath = findfolder("flash_all", sw_path)['path']
    canIniPath = os.path.join(flashPath, "canape.ini")
    f = open(canIniPath, "r")
    data = f.read()
    #Change IP
    regex = r'\[module.*?radar.*?\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        ipstr = search_f(tmatch, 'HOST=(.+?)\n')
        if ipstr != '':            
            tmatchK1 = tmatch
            tmatch = tmatch.replace(ipstr, 'HOST=' + '133.65.1.1' + '\n')
            data = data.replace(tmatchK1, tmatch)
            write('Correct IP flash: ' + '133.65.1.1' + '\n') 
            break
    #Write back
    f = open(canIniPath, "w")
    f.write(data)
    f.close

def configAtoL(sw_path):
    write('Config A2L')
    databasePath = findfolder('database', sw_path)['path']
    atol = findfile('.a2l', databasePath)
    f = open(atol['path'], "r")
    data = f.read()

    #Change IP
    regex = r'begin XCP_ON_TCP_IP[^`]+end XCP_ON_TCP_IP'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        ipstr = search_f(tmatch, 'ADDRESS(.+?)\n')
        if ipstr != '':            
            tmatchK1 = tmatch
            tmatch = tmatch.replace(ipstr, 'ADDRESS \"' + '133.65.1.1' + '\"\n')
            data = data.replace(tmatchK1, tmatch)
            print('Correct IP ' + '133.65.1.1' + '\n') 
            break
    
    #Change sector flash
    regex = r'begin SECTOR[^`]+end SECTOR'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        sectorstr = search_f(tmatch, '0x(.+?)\n[^`]+0x(.+?)')
        if sectorstr != '':        
            tmatchK1 = tmatch
            sectorstrlist = sectorstr.split('\n')
            tmatch = tmatch.replace(sectorstrlist[1].strip(), '0x800000')
            tmatch = tmatch.replace(sectorstrlist[2].strip(), '0x010000')
            data = data.replace(tmatchK1, tmatch)
            print('Correct sector' + '\n')
            break
    #Write back
    f = open(atol['path'], "w")
    f.write(data)
    f.close

def configCanape(sw_path):
    write('Config Canape')
    canapePath = findfolder('canape', sw_path)['path']
    canIniPath = os.path.join(canapePath, "canape.ini")
    f = open(canIniPath, "r")
    data = f.read()    

    # Add dll
    print('Add dll' + '\n')
    diatesterPath = findfolder('diatester', sw_path)['path']
    dllFolder = findfolder('dll', diatesterPath)['path']
    regex = r'\[FUNCTION_DLL_ADDON\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tmatchK1 = tmatch
        tCountStr = search_f(tmatch, 'COUNT=(.+?)\n')
        try:
            tCount = replace_f(tCountStr, 'COUNT=(.+?)\n', r'\1')        
        except:
            tCount = 0
        dllPath = ''
        for root, dirs, files in os.walk(dllFolder):
            for name in files:            
                if  name.endswith('dll'):     
                    dll = os.path.join(root, name)               
                    path = os.path.relpath(dll, canapePath)
                    if path not in tmatch:
                        tCount = str(int(tCount) + 1)
                        dllPath = dllPath + 'FUN_DLL_PATH_' + tCount + '='  + path + '\n'
        oldStr = search_f(tmatch, 'FUN_DLL_PATH.*?=(.+?)\n')
        newStr = oldStr + dllPath
        if oldStr != '':
            tmatch = tmatch.replace(oldStr, '\n' + newStr)            
        else:
            tmatch = tmatch + newStr + '\n'  
        tmatch = tmatch.replace(tCountStr, 'COUNT='+ tCount)        
        data = data.replace(tmatchK1, tmatch)    

    # Add Diatester
    print('Add Diatester' + '\n')
    regex = r'\[MODULES\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        if (tmatch.find('DiaTester') == -1):
            tmatchK1 = tmatch
            matchlist =  tmatch.split("\n")
            tCount = 0
            for i in range(0, len(matchlist)-1):
                tCountStr = search_f(matchlist[i], '(\d+)=(.+)')
                try:
                    if tCount < int(replace_f(tCountStr, '(\d+)=(.+)', r'\1')):
                        tCount = int(replace_f(tCountStr, '(\d+)=(.+)', r'\1'))
                except:
                    pass
            oldStr = search_f(tmatch, str(tCount)+'=(.+), 0\n')
            tmatch = tmatch.replace(oldStr, oldStr +  str(tCount+1)+'=99999, \"DiaTester\", 0\n')
            tCountStr = search_f(tmatch, 'COUNT=(.+?)\n')
            tmatch = tmatch.replace(tCountStr, 'COUNT='+ str(tCount+1)+'\n')
            data = data.replace(tmatchK1, tmatch)

    regex = r'\[NETWORK_1\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        if (tmatch.find('DiaTester') == -1):
            tmatchK1 = tmatch
            tCountStr = search_f(tmatch, 'DeviceCount=(.+?)\n')
            try:
                tCount = replace_f(tCountStr, 'DeviceCount=(.+?)\n', r'\1')        
            except:
                tCount = 0
            oldStr = search_f(tmatch, 'Device_' + str(int(tCount)-1)+'=(.+)\n')
            tmatch = tmatch.replace(oldStr, oldStr + 'Device_' + str(tCount)+'=DiaTester\n')
            tCountStr = search_f(tmatch, 'DeviceCount=(.+?)\n')
            tmatch = tmatch.replace(tCountStr, 'DeviceCount='+ str(int(tCount)+1)+'\n')
            data = data.replace(tmatchK1, tmatch)

    #delete exist diatester
    regex = r'\[module.*?diatester.*?\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        data = data.replace(tmatch, '')
    MDiaTesterData = '[Module_DiaTester]\n' + 'ACTIVE_STATE=0\n' + 'AUTOSAVE_DATAFILE=0\n' + 'CALIBRATION_MODE_DIRECT=1\n' + 'CALPAGE_SINGLE_SEGMENT_SWITCHING=0\n' + \
                        'CALPAGE_XCP_INITIAL_PAGE=0\n' + 'CALRAMAUTOSEGMENTS=0\n' + 'CALRAM_ALT_FILE=\n' + 'CALRAM_BACKUP_FILE=\n' + 'CALRAM_CACHE=0\n' + 'CALRAM_DEF_ACTION_READONLY=0\n' + \
                        'CALRAM_DEF_ACTION_TEMPREADONLY=0\n' + 'CALRAM_DEF_ACTION_WRITABLE=3\n' + 'CALRAM_DO_BACKUP_ON_UPLOAD=0\n' + 'CALRAM_EXECUTE_DEF_ACTION=0\n' + \
                        'CALRAM_FLASH_OFFSET=0x00000000\n' + 'CALRAM_IMPORT_CODE_SEGMENTS=0\n' + 'CALRAM_MERGE_TO_HEXFILE=0\n' + 'CALRAM_NAME_DB=0\n' + 'CALRAM_OFFLINE=0\n' + \
                        'CALRAM_SECTOR_COUNT=0\n' + 'CALRAM_USE_ALT_FILE_ON_DOWNLOAD=0\n' + 'CALRAM_WRITE_OPT=0\n' + 'CANDELA_ACTIVATION_LINE=1\n' + \
                        'CANDELA_ACTIVATION_LINE_STARTUP_TIME=-1\n' + 'CANDELA_ADDRESS_EXT=-1\n' + 'CANDELA_AUDIENCE=\n' + 'CANDELA_AUTOM_DETECT=1\n' + \
                        'CANDELA_BASE_ADDRESS=-1\n' + 'CANDELA_BAUDRATE=500000\n' + 'CANDELA_BLOCKSIZE=-1\n' + 'CANDELA_BROADCASTIPADDRESS=\n' + 'CANDELA_CANFD_BAUDRATE=-1\n' + \
                        'CANDELA_CANFD_SJW=-1\n' + 'CANDELA_CANFD_TSEG1=-1\n' + 'CANDELA_CANFD_TSEG2=-1\n' + 'CANDELA_DISPLAY_ALL_PARAMETERS=1\n' + 'CANDELA_ECU_ADDRESS=-1\n' + \
                        'CANDELA_FAULT_MEM_CONT_ON_ERROR=1\n' + 'CANDELA_FUNC_ADDRESS=-1\n' + 'CANDELA_INTERFACE=Diagnostics_On_CAN\n' + 'CANDELA_LANGUAGE=en-US\n' + \
                        'CANDELA_LOGGING=0\n' + 'CANDELA_LOGICAL_ECU_ADR=-1\n' + 'CANDELA_LOGICAL_GW_ADR=-1\n' + 'CANDELA_LOGICAL_TESTER_ADR=-1\n' + 'CANDELA_MULT_RX_ID_1=-1\n' + \
                        'CANDELA_MULT_RX_ID_2=-1\n' + 'CANDELA_MULT_RX_ID_3=-1\n' + 'CANDELA_MULT_RX_ID_4=-1\n' + 'CANDELA_OVERRIDE_COMM=0\n' + 'CANDELA_P2EXTIMEOUT=-1\n' + \
                        'CANDELA_P2TIMEOUT=-1\n' + 'CANDELA_P3TIME=-1\n' + 'CANDELA_P6EXTIMEOUT=-1\n' + 'CANDELA_P6TIMEOUT=-1\n' + 'CANDELA_PLUG=0\n' + \
                        'CANDELA_PROTECT_CONST_PARAMETERS=1\n' + 'CANDELA_RX_ECU_ADDRESS=-1\n' + 'CANDELA_RX_ECU_ADDRESS_ON=0\n' + 'CANDELA_RX_ID=-1\n' + \
                        'CANDELA_SAM=0\n' + 'CANDELA_SJW=1\n' + 'CANDELA_STMIN=-1\n' + 'CANDELA_SUGGESTED_ECU_ID=-1\n' + 'CANDELA_SUGGESTED_TESTER_ID=-1\n' + \
                        'CANDELA_T1_TIME=-1\n' + 'CANDELA_T3_TIME=-1\n' + 'CANDELA_TESTER_ADDRESS=-1\n' + 'CANDELA_TEST_MESSAGE_LENGTH=1\n' + 'CANDELA_TIMESTAMP=0\n' + \
                        'CANDELA_TP_ACTIVE=1\n' + 'CANDELA_TRACING=0\n' + 'CANDELA_TRANSFER_ACCELERATION=1\n' + 'CANDELA_TRANSFER_ACCELERATION_SIZE=64\n' + 'CANDELA_TSEG1=4\n' + \
                        'CANDELA_TSEG2=3\n' + 'CANDELA_TX_ID=-1\n' + 'CANDELA_TX_PRIO=-1\n' + 'CANDELA_VARIANT=CommonDiagnostics\n' + 'CANDELA_VEHICLE_ADR=\n' + \
                        'CHECKSUM_DLL_NAME=chksum.dll\n' + 'CHECKSUM_ENABLED=0\n' + 'CHECKSUM_MAX_BLOCKSIZE=4294967295\n' + 'CHECKSUM_TYPE=0\n' + 'CHECKSUM_TYPE_INCA=0x0\n' + \
                        'CHECKSUM_TYPE_MAPPING_2=3\n' + 'CHECK_CODE_CHECKSUM=0\n' + 'CHECK_EPROM_IDENTIFIER=0\n' + 'COMMENT= Excuse me wtf\n' + 'CONFIG_OPTIONS=\n' + \
                        'CONFIG_TOOL=\n' + 'DATABASE_DIR=<CDDPath>\n' + 'DRIVER=17\n' + 'DATABASE_NAME=DiaTester.cdd\n' + 'DATABASE_NETWORK=\n' + 'DATAFILE_DIR=\n' + \
                        'DATAFILE_NAME=\n' + 'DETECT_DATABASE=0\n' + 'DIAG_ADDRESS_TYPE_PHYS=-1\n' + 'DIAG_AOA_ASAP2_FILE_NAME=\n' + 'DIAG_AOA_CALRAM_CACHE=0\n' + \
                        'DIAG_AOA_CALRAM_FLASH_OFFSET=0\n' + 'DIAG_AOA_CALRAM_OFFLINE=0\n' + 'DIAG_AOA_CALRAM_SECTOR_COUNT=0\n' + 'DIAG_AOA_CALRAM_WRITE_OPT=0\n' + \
                        'DIAG_AOA_ENABLED=0\n' + 'DIAG_AOA_HEX_FILE_NAME=\n' + 'DIAG_AOA_RMBA_SERVICE=\n' + 'DIAG_AOA_WMBA_ENABLED=0\n' + 'DIAG_AOA_WMBA_SERVICE=\n' + \
                        'DIAG_AUTOM_DETECT_FUNC=1\n' + 'DIAG_BANDWIDTH_CONTROL=-1\n' + 'DIAG_BUFFERSIZE=-1\n' + 'DIAG_CONNECTION_MODE_PHYS=-1\n' + \
                        'DIAG_CUSTOM_TESTER_PRESENT_MESSAGE=\n' + 'DIAG_DEBUG_LOGFILE_NAME=\n' + 'DIAG_DETECT_SUPPORTED_VSG=1\n' + 'DIAG_DTC_DELTA_LOGGING=0\n' + \
                        'DIAG_ECU=Radar\n' + 'DIAG_FUNCTIONAL_GROUP=\n' + 'DIAG_FUNC_TX_ID=-1\n' + 'DIAG_IS_FUNCTIONAL_CHANNEL=0\n' + 'DIAG_MESSAGE_LENGTH_PHYS=-1\n' + \
                        'DIAG_PADDING_BYTE=-1\n' + 'DIAG_PADDING_ON=1\n' + 'DIAG_PDU_LIST_REQ_PHYS=\n' + 'DIAG_PDU_LIST_REQ_PHYS_SIZE=0\n' + 'DIAG_PDU_LIST_RES=\n' + \
                        'DIAG_PDU_LIST_RES_SIZE=0\n' + 'DIAG_SECURITY_JOB=\n' + 'DIAG_SECURITY_KEY_BUFFER_SIZE=1\n' + 'DIAG_SEED_AND_KEY_DLL=SeednKey.dll\n' + \
                        'DIAG_SERVICE_CLEAR_ALL_DTC=\n' + 'DIAG_SERVICE_CLEAR_DTC=\n' + 'DIAG_SERVICE_READ_DTC=\n' + 'DIAG_SERVICE_READ_DTC_SUPPORTED=\n' + \
                        'DIAG_SERVICE_READ_ENVDATA=\n' + 'DIAG_SERVICE_READ_ENVDATA_POSTFIX=00\n' + 'DIAG_SHOW_CONNECTION_DEBUG_OUTPUT=0\n' + 'DIAG_SHOW_GAP_OBJECTS=0\n' + \
                        'DIAG_TESTER_IP_ADDRESS=\n' + 'DIAG_TP_MODE=0\n' + 'DIAG_USE_CUSTOM_TESTER_PRESENT_MESSAGE=0\n' + 'DIAG_USE_FIX_SECURITY_KEY_BUFFER_SIZE=0\n' + \
                        'DISCONNECT_AFTER_FLASHING=1\n' + 'ECDM_DEVICE=0\n' + 'ENABLE_CHECKSUM_OUTPUT=0\n' + 'FLAGS=1\n' + 'FLASH_CLEAR_TIMEOUT=10000\n' + 'FLASH_DEFAULT_CONTENT=255\n' + \
                        'FLASH_DELETE_WHOLE_GROUP=0\n' + 'FLASH_DISABLE_PAGE_SWITCHING=0\n' + 'FLASH_EXTERNAL_CONVERTER=\n' + 'FLASH_GRANULARITY=210\n' + 'FLASH_GROUP_COUNT=0\n' + \
                        'FLASH_KERNEL_FILE_ADDR=0\n' + 'FLASH_KERNEL_FILE_NAME=Direct\n' + 'FLASH_KERNEL_RAM_ADDR=0\n' + 'FLASH_KERNEL_RAM_START=0\n' + 'FLASH_KERNEL_SIZE=0\n' + \
                        'FLASH_KERNEL_TYPE=0\n' + 'FLASH_KERNEL_USE_SECTORS=1\n' + 'FLASH_KERNEL_VERSION=(unknown)\n' + 'FLASH_OPTIMIZATION=0\n' + 'FLASH_PAGE_ADDRESS_MAPPING_ENABLED=1\n' + \
                        'FLASH_PROGRAM_VERIFY=0\n' + 'FLASH_PROGRAM_VERIFY_EXTERNAL=1\n' + 'FLASH_RECONNECT=0\n' + 'FLASH_RECONNECT_DELAY=2000\n' + 'FLASH_SECTOR_COUNT=0\n' + \
                        'FLASH_SIGN_ADDR=0x00000000\n' + 'FLASH_SIGN_ENABLED=0\n' + 'FLASH_SIGN_SIZE=0\n' + 'FLASH_SKIP_FF=0\n' + 'FLASH_START_TIMEOUT=10000\n' + 'FLASH_TOOL=Protocol\n' + \
                        'FLASH_VFLASH_DEACTIVATE_NETWORK=1\n' + 'FLASH_VFLASH_PROJECT_DIR=\n' + 'FLASH_VFLASH_PROJECT_FILE=\n' + 'INIT_CAL_PAGE=0\n' + 'IdentifyBySignalNameOnly=0\n' + \
                        'LOAD_LAST_DATABASE=1\n' + 'LOGFILE_NAME=communication_DiaTester.txt\n' + 'MAPFILE_DIR=\n' + 'MAP_COUNT=0\n' + 'MAP_COUNTER=0\n' + 'MAP_EXPAND_MAP_NAMES=0\n' + \
                        'MAP_INVAL_OBJ_WITH_INVAL_REF=0\n' + 'MAP_NAMING_CONVENTION=0\n' + 'MAP_READ_IF_NEWER=0\n' + 'MAP_USAGE=0\n' + 'MEMORY_SEGMENTS_V8_COMPATIBILITY_MODE=0\n' + \
                        'MEMORY_SEGMENT_COUNT=0\n' + 'ModuleExtensionCompany=\n' + 'ModuleExtensionDll=\n' + 'NETCHANNEL=1\n' + 'NETDEVICE=Vector\n' + 'NETWORK=1\n' + \
                        'ONLINE_CALIBRATION_ACTIVE=1\n' + 'PARAMETER_DIR=\n' + 'PROGRAM_VERIFY_TYPE=0\n' + 'PROGRAM_VERIFY_TYPE_USERDEF=256\n' + 'PROGRAM_VERIFY_VALUE=0\n' + \
                        'PROTECT_DATABASE=0\n' + 'RAM_PAGE_ID=0x0\n' + 'RAM_PAGE_ID_EXT=0x0\n' + 'RESTART_MEASUREMENT_ON_ERROR=0\n' + 'ROM_PAGE_ID=0x0\n' + 'ROM_PAGE_ID_EXT=0x0\n' + \
                        'ReadOnlyDatabase=0\n' + 'SAVE_ORIGINAL_IF_DATA=0\n' + 'SELECT_CAL_PAGE=0\n' + 'SET_CALPAGE_SEPARATLY=0\n' + 'SPECIFIC_FILTER_COUNT=0\n' + 'SPECIFIC_FILTER_TYPE=0\n' + \
                        'SPECIFIC_FILTER_USE4ALL_COLUMNS_INCDM=0\n' + 'SPECIFIC_FILTER_USE_IN_CDM=1\n' + 'THESAURUS_ACTIVE=1\n' + 'THESAURUS_FILE_COUNT=0\n' + \
                        'USE_DATABASENAME_FROM_ECU=0\n' + 'UserFilterCount=0\n\n'
    #get CDD Path
    cddFolder = findfolder('cdd', diatesterPath)['path']
    path = os.path.relpath(cddFolder, canapePath)        
    MDiaTesterData = MDiaTesterData.replace('<CDDPath>', path)
    #add diatester
    regex = r'\[module.*?radar.*?\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tmatchK1 = tmatch
        tmatch = tmatch + MDiaTesterData + '\n'
        data = data.replace(tmatchK1, tmatch)
        break
            
    # Config group flash
    print('Config group flash' + '\n')
    regex = r'\[module.*?radar.*?\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        #Group flash
        tmatchK1 = tmatch
        tStr = search_f(tmatch, 'FLASH_GROUP_[^`]+FLASH_GROUP_.+')
        if tStr != '':
            newStr = 'FLASH_GROUP_COUNT=1\n'+'FLASH_GROUP_NAME_1=nvm\n'+'FLASH_GROUP_DATAFILE_1=\n'+'FLASH_GROUP_SELECTED_1=1\n'+'FLASH_GROUP_1_RANGE_COUNT=1\n'+'FLASH_GROUP_1_RANGE_NAME_1=nvm\n'
            newStr = newStr +'FLASH_GROUP_1_RANGE_SIZE_1=0x00010000\n'+'FLASH_GROUP_1_RANGE_ADDR_1=0x00800000\n'+'FLASH_GROUP_1_RANGE_ADDR_EXT_1=0x00\n' 
            tmatch = tmatch.replace(tStr, newStr)
            data = data.replace(tmatchK1, tmatch)

    #SHOW_MESSAGES=251
    data = data.replace('SHOW_MESSAGES=255', 'SHOW_MESSAGES=251')

    #Write back
    f = open(canIniPath, "w")
    f.write(data)
    f.close

def AddPage(sw_path, name):
    write('Add page: ' + name)
    canapePath = findfolder('canape', sw_path)['path']
    cnaPath = os.path.join(canapePath, "MRR1plus.cna")
    f = open(cnaPath, "r")
    data = f.read()    
    #increate page counter
    regex = r'\[DISPLAY_PAGES\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tmatchK1 = tmatch
        tCountStr = search_f(tmatch, 'Count=(.+?)\n')
        try:
            tCount = replace_f(tCountStr, 'Count=(.+?)\n', r'\1')        
        except:
            tCount = '0'
        pageNo = int(tCount)+1
        tmatch = tmatch.replace(tCountStr, 'Count='+ str(pageNo) + '\n')
        tActiveStr = search_f(tmatch, 'Active=(.+?)\n')
        tmatch = tmatch.replace(tActiveStr, 'Active=' + str(pageNo - 1) + '\n') 
        data = data.replace(tmatchK1, tmatch)
    #Config Page parametor
    regex = r'\[DISPLAY_PAGE_1_DisplayElements\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tstr = '[DISPLAY_PAGE_' + str(pageNo) + ']\n'
        tstr = tstr + 'Name=' + name + '\n'
        tstr = tstr + 'Comment=\n' + 'Maximized=1\n' + 'ActiveWindow=\n' + 'IsReportPage=0\n' + 'TimeAxisSynchronized=0\n' + 'PrintLayout=Default\n\n'
        tstr = tstr + '[DISPLAY_PAGE_' + str(pageNo) + '_DisplayElements]\n' + 'Count=0\n\n'
        tstr = tstr + tmatch
        data = data.replace(tmatch, tstr)
    #Write back
    f = open(cnaPath, "w")
    f.write(data)
    f.close
    return pageNo

def AddGraphicWindow(sw_path, pageNo):
    write('Add Graphic Window to page: ' + str(pageNo))
    canapePath = findfolder('canape', sw_path)['path']
    cnaPath = os.path.join(canapePath, "MRR1plus.cna")
    f = open(cnaPath, "r")
    data = f.read()    
    #increate Window counter
    regex = r'\[WINDOWS\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tmatchK1 = tmatch
        tCountStr = search_f(tmatch, 'Count=(.+?)\n')
        try:
            tCount = replace_f(tCountStr, 'Count=(.+?)\n', r'\1')        
        except:
            tCount = '0'
        Count = int(tCount)
        tmatch = tmatch.replace(tCountStr, 'Count='+ str(Count + 2) + '\n')
        data = data.replace(tmatchK1, tmatch)
    #Get window number
    regex = r'\[WINDOW_.+?\][^`]+?(?=\[)'
    widowNo = Count - 2
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tNoStr = search_f(tmatch, 'Number=(.+?)\n')
        try:
            tNo = int(replace_f(tNoStr, 'Number=(.+?)\n', r'\1'))
        except:
            tNo = 0
        if tNo > widowNo:
            widowNo = tNo

    #Config Graphic widow parametor
    tmatch = search_f(data, r'\[WINDOW_' + tCount +'_.+?\][^`]+?(?=\[)')
    if tmatch == '':
        tmatch = search_f(data, r'\[WINDOW_' + tCount + '\][^`]+?(?=\[)')
    if tmatch != '':
        tstr = '[WINDOW_' + str(Count + 1) + ']\n' + 'ComponentCount=1\n' + 'Title=\n' + 'Type=65536\n' + 'Comment=Multi view window\n' + 'Number=' + str(widowNo + 1) + '\n' + \
                'Position=0, 125, 125, 500, 200, -1, -1 ;cmd, x, y, w, h, xmin, ymin\n' + 'Position_Page' + str(pageNo) +'=0, 125, 125, 500, 200, -1, -1 ;cmd, x, y, w, h, xmin, ymin\n' + \
                'FloatingWindow=0\n' + 'ShowSignalComments=1\n' + 'DisplayMask=' + str(2**(pageNo-1)) + ' ; pages ' + str(pageNo) + '\n\n'
        tstr = tstr + '[WINDOW_' + str(Count + 2) + ']\n' + 'XLen=20000\n' + 'XMin=0\n' + 'XMax=30000\n' + 'Grid=1\n' + 'Mark=1\n' + 'YValue=1\n' + 'ShowLegend=2\n' + 'ShowLegendHeader=1\n' + \
                'LegendPixWidth=259\n' + 'LegendPixHeight=105\n' + 'LegendPos=2\n' + 'Optimize=1\n' + 'Average=0\n' + 'ShowMinMax=1\n' + 'XYModeIndexP1=-1\n' + 'DisplayModeAuto=0\n' + \
                'XStart=0\n' + 'AbsoluteTimeMode=0\n' + 'YAxisWidth=32\n' + 'RightYAxisWidth=0\n' + 'ObjectMode=0\n' + 'DisplayMode=0\n' + 'ShowSignalMode=0\n' + 'AxisScrollPos2=0\n' + \
                'LegendScrollPos=0\n' + 'LegendShowLifeValues=1\n' + 'ShowXScrollbar=1\n' + 'YAxisDynScaleEnabled=0\n' + 'YAxisDynScaleEnlarge=25\n' + 'TimeStickToZero=0\n' + \
                'XYModeRedrawEnabled=0\n' + 'XYmodeUseXDisplayTime=1\n' + 'MARKER_TIME_1=5000000000\n' + 'MARKER_TIME_2=15000000000\n' + 'OscilloscopeEnabled=0\n' + 'OsciEventCount=0\n' + \
                'EventCompareModeEnabled=0\n' + 'ObjectCount=0\n' + 'Title=Graphic {DISPLAYED_FILENAME}\n' + 'Type=1\n' + 'Comment=Graphic window\n' + 'Number=' + str(widowNo + 2) + '\n' + \
                'Position=0, 0, 0, 0, 0, -1, -1 ;cmd, x, y, w, h, xmin, ymin\n' + 'Position_Page' + str(pageNo) +'=0, 0, 0, 0, 0, -1, -1 ;cmd, x, y, w, h, xmin, ymin\n' + 'FloatingWindow=0\n' + \
                'JointIndex=' + str(widowNo + 1) + '\n' + 'ShowSignalComments=1\n' + 'ComponentOrder=0\n' + 'ComponentSpace=100\n' + 'LEGEND_HSCROLL_POS=0\n' + 'LEGEND_SHARED_COLUMNS=1\n' + \
                'TimeAxisTemplate=<default>\n' + 'DisplayMask=' + str(2**(pageNo-1)) + ' ; pages ' + str(pageNo) + '\n\n'
        tstr = tstr + '[WINDOW_' + str(Count + 2) + '_LEG_COLUMNS]\n' + 'COUNT=1\n' + 'COL_0=31, 259' + '\n\n'
        tstr = tmatch + tstr
        data = data.replace(tmatch, tstr)
    #Write back
    f = open(cnaPath, "w")
    f.write(data)
    f.close
    widowNo += 2
    return widowNo

def collectObjectA2L(sw_path):
    databasePath = findfolder('database', sw_path)['path']
    atol = findfile('.a2l', databasePath)
    f = open(atol['path'], "r")
    data = f.read()
    objectSig = {}
    objectSig['opcT20'] = []
    objectSig['cgsf_x_t20'] = []
    objectSig['function_status'] = []
    regex = r'begin MEASUREMENT opcT20.+'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tobjectSig = search_f(tmatch, 'opcT20.+_b')
        if tobjectSig != '':
            objectSig['opcT20'].append(tobjectSig)

    regex = r'begin MEASUREMENT cgsf_x_t20\.CriteriaControls\..+?_b1.+'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tobjectSig = search_f(tmatch, 'cgsf_x_t20\.CriteriaControls\..+?_b1')
        if tobjectSig != '':
            objectSig['cgsf_x_t20'].append(tobjectSig)
    
    regex = r'begin MEASUREMENT function.+?t20\..+__b_FunctionBaseT20\.status.+'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tobjectSig = search_f(tmatch, 'function.+?t20\..+__b_FunctionBaseT20\.status')
        if tobjectSig != '':
            objectSig['function_status'].append(tobjectSig)
    return objectSig

def AddClassObject(cnaPath, key, objectSig):
    f = open(cnaPath, "r")
    data = f.read()

    tStr = search_f(data, '\$' + key + '\$')
    if tStr != '':
        #add measurement object class
        regex = r'\[MEASUREMENT_OBJECT_\w+\][^`]+?(?=\[)'
        for tmatch in re.findall(regex, data, re.IGNORECASE):
            tStr = search_f(tmatch, 'Name=\$'+ key + '\$\n')
            if tStr != '':
                objClassStr = tmatch
                objectName = replace_f(tmatch, '\[(MEASUREMENT_OBJECT_\w+)\]', r'\1')
                tComponents = search_f(tmatch, 'Components=.+\n')
                componentsNo = int(replace_f(tComponents, 'Components=(.+)\n', r'\1'))
        measurementObjectStr = search_f(data, '\[' + objectName + '_CO' + str(componentsNo) + '\][^`]+?(?=\[)')
        if componentsNo == 0:
            measurementObjectStr = objClassStr
        tstr = ''
        for tobjectSig in objectSig:
            if search_f(data, tobjectSig +'\n') == '' and (replace_f(key, '_(\w+)', r'\1') in tobjectSig):
                componentsNo = componentsNo + 1
                tstr = tstr + '[' + objectName + '_CO' + str(componentsNo) + ']\n' + 'Name=$'+ key + '$' + tobjectSig + '\n' + 'IsFallback=1\n' + 'DisplayCount=0\n\n'
        data = data.replace(measurementObjectStr, measurementObjectStr + tstr)
        objClassStrK1 = objClassStr
        objClassStr = objClassStr.replace(tComponents, 'Components='+ str(componentsNo) + '\n')
        data = data.replace(objClassStrK1, objClassStr)
        f = open(cnaPath, "w")
        f.write(data)
        f.close


def AddMeasurementObject(sw_path, objectSig):
    canapePath = findfolder('canape', sw_path)['path']
    cnaPath = os.path.join(canapePath, "MRR1plus.cna")
    f = open(cnaPath, "r")
    data = f.read()

    #add measurement object to opcT20 class
    AddClassObject(cnaPath, '_opcT20', objectSig['opcT20'])

    #add measurement object to cgsf_x_t20 class
    AddClassObject(cnaPath, '_cgsf_x_t20', objectSig['cgsf_x_t20'])

    #add measurement object to function_status class
    for tobjectSig in objectSig['function_status']:
        if search_f(data, tobjectSig +'\n') == '':
            objKey = '_' + replace_f(tobjectSig, '(function.+?t20)\..+__b_FunctionBaseT20\.status', r'\1')
            AddClassObject(cnaPath, objKey, objectSig['function_status'])

def AddSignal(sw_path, windowNo, signame, index):
    colorlist = ['65535', '2303', '589568', '16777215', '16711680', '33023', '16711935', '16776960']
    canapePath = findfolder('canape', sw_path)['path']
    cnaPath = os.path.join(canapePath, "MRR1plus.cna")
    f = open(cnaPath, "r")
    data = f.read()
    #find measurement object
    regex = r'\[MEASUREMENT_OBJECT_\w+\][^`]+?(?=\[)'
    for tmatch in re.findall(regex, data, re.IGNORECASE):
        tmatchK1 = tmatch
        tStr = search_f(tmatch, signame +'\n')
        if tStr != '':
            #find measurement object number
            tobjectNo = search_f(tmatch, '\[MEASUREMENT_OBJECT_(\w+)\]')
            objectNo = replace_f(tobjectNo, '\[MEASUREMENT_OBJECT_(\w+)\]', r'\1')

            #increate DisplayCount
            tCountStr = search_f(tmatch, 'DisplayCount=(.+?)\n')
            try:
                tCount = int(replace_f(tCountStr, 'DisplayCount=(.+?)\n', r'\1'))       
            except:
                tCount = 0
            tmatch = tmatch.replace(tCountStr, 'DisplayCount='+ str(tCount + 1) + '\n')
            
            #config display
            configStr = '[MEASUREMENT_OBJECT_' + objectNo + '_DISPLAY_' + str(tCount + 1) + ']\n' + 'Window=' + str(windowNo) + '\n' + 'Index=' + str(index) + '\n' + 'Color=' + colorlist[index % 7] + '\n' + 'ColorFunction=0\n' + \
                        'ColorFunctionScope=1\n' + 'LineTyp=2\n' + 'YMinHome=\n' + 'YMaxHome=\n' + 'YMin=\n' + 'YMax=\n' + 'XOffsetNS=0\n' + 'XOffset=0\n' + \
                        'ValueFormat=3\n' + 'BitMask=1\n' + 'ShowYAxis=1\n' + 'Width=10\n' + 'LineStyle=1\n' + 'MarkerType=1\n' + 'LineWidth=1\n' + 'Precision=-2\n' + \
                        'Digits=6\n' + 'Enabled=1\n' + 'StoredFocused=0\n' + 'SublMask=1\n' + 'MeaSublMask=3\n' + 'LockScaling=0\n' + 'MapMode=2\n' + 'OverlayGridColor=16777216\n' + \
                        'ShadingMode=3\n' + 'EditOffset=1\n' + 'EditFactor=2\n' + 'AxisCaption=\n' + 'Row=0\n' + 'Col=0\n' + 'YAxis_ID=0\n' + 'AxisTemplate=\n\n'
            if tCount > 0:
                data = data.replace(tmatchK1, tmatch)
                objDisplayStr = search_f(data, r'\[MEASUREMENT_OBJECT_' + objectNo +'_DISPLAY_' + str(tCount) + '\][^`]+?(?=\[)')
                data = data.replace(objDisplayStr, objDisplayStr + configStr)
            else:
                data = data.replace(tmatchK1, tmatch + configStr)
            index = index + 1
            write('Add signal ' + tStr.replace('\n','') + ' to window ' + str(windowNo) + ' successful')
            # break
    #Write back
    f = open(cnaPath, "w")
    f.write(data)
    f.close
    return index

def edit_config_canape(sw_path):
    if PreCheck(sw_path) == 'not yet':
        configIPflash(sw_path)
        configAtoL(sw_path)
        configCanape(sw_path)

        objectSig = collectObjectA2L(sw_path)
        AddMeasurementObject(sw_path, objectSig)

        #ACC
        pageNo = AddPage(sw_path, 'ClaraTest_ACC')
        windowNo = AddGraphicWindow(sw_path, pageNo)
        index = AddSignal(sw_path, windowNo, r'ast_x_pri\.SSOC\.b\..+?_b', 0)
        index = AddSignal(sw_path, windowNo, r'ast_x_pri\.ISOC\.b\..+?_b', index)
        index = AddSignal(sw_path, windowNo, r'ast_x_pri\.APC\.b\..+?_b', index)
        index = AddSignal(sw_path, windowNo, r'Fgs_x._.targetObjectHandleEgoLane.dxv', index)
        index = AddSignal(sw_path, windowNo, r'Fgs_x._.targetObjectHandleEgoLane.vxv', index)
        index = AddSignal(sw_path, windowNo, r'Fgs_x._.targetObjectHandleEgoLane.Handle', index)
        index = AddSignal(sw_path, windowNo, r'evi.General_T20.axvRef', index)
        index = AddSignal(sw_path, windowNo, r'evi.General_T20.vxvRef', index)
        index = AddSignal(sw_path, windowNo, r'ast_x_pri.CurrentState', index)

        #PSS
        pageNo = AddPage(sw_path, 'ClaraTest_PSS')
        windowNo = AddGraphicWindow(sw_path, pageNo)
        index = AddSignal(sw_path, windowNo, r'opcT20\.FuncOpcInfoInterruption\..+?_b', 0)
        index = AddSignal(sw_path, windowNo, r'opcT20\.FuncOpcInfoSuppression\..+?_b', index)
        index = AddSignal(sw_path, windowNo, r'opcT20\.GeneralCriterion\.BlockingTimer\..+?_b', index)
        index = AddSignal(sw_path, windowNo, r'opcT20\.GeneralCriterion\.HMIActivation\..+?_b', index)
        index = AddSignal(sw_path, windowNo, r'opcT20\.GeneralCriterion\.ExcOpSitFlags\..+?_b', index)
        index = AddSignal(sw_path, windowNo, r'opcT20\.GeneralCriterion\.InsDriSitFlags\..+?_b', index)
        index = AddSignal(sw_path, windowNo, r'opcT20\.GeneralCriterion\.ErrorStates\..+?_b', index)
        index = AddSignal(sw_path, windowNo, r'opcT20.GeneralCriterion.EngineOn_b', index)
        index = AddSignal(sw_path, windowNo, r'cgsf_x_t20\.CriteriaControls\..+?_b1', index)
        index = AddSignal(sw_path, windowNo, r'function.+?t20\..+__b_FunctionBaseT20\.status', index)
        index = AddSignal(sw_path, windowNo, r'Fgs_x._.collisionDangerLevelLaneKeeping_ub', index)
        index = AddSignal(sw_path, windowNo, r'Fgs_x._.targetObjectHandleEgoLane.dxv', index)
        index = AddSignal(sw_path, windowNo, r'Fgs_x._.targetObjectHandleEgoLane.vxv', index)
        index = AddSignal(sw_path, windowNo, r'Fgs_x._.targetObjectHandleEgoLane.Handle', index)
        index = AddSignal(sw_path, windowNo, r'evi.General_T20.axvRef', index)
        index = AddSignal(sw_path, windowNo, r'evi.General_T20.vxvRef', index)

# if __name__ == "__main__":
#     main()
#
#     print('Finished!')