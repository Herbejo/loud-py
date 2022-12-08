#--------------todo list----------------
# - logging 
# - remove shell=true, pass all arguments as list 
# - FSTRINg 
# - use stereo tools to mono 
#------------Longterm todo ------------------------------
# - make program use pipe and numpi not temp files 
# - make ffmpeg function, it seems a bit silly running it in 4 different funtions

import os
import tempfile
import subprocess
from subprocess import PIPE, Popen
import shutil
import configparser
import stats

    

def fix_dynamics(file):
    loudness_info = stats.get_loudness_info(file)
    astats = stats.get_astats(file)
    settings = dict(config['compressor'])
    settings['threshold'] = choose_thresh(loudness_info, astats)
    if float(loudness_info['measured_LRA']) >= float(settings['lra_threshold']):
        compressed_file = compress(file, loudness_info, settings)
        loudness_info = stats.get_loudness_info(compressed_file)
        #2nd pass of compression if needed
        if float(loudness_info['measured_LRA']) >= float(settings['lra_threshold']) :
            compressed_file = compress(compressed_file, loudness_info, settings)
            loudness_info = stats.get_loudness_info(compressed_file)
            return(compressed_file, loudness_info)
        else:
            return(compressed_file, loudness_info)
    else:
        return(file, loudness_info)
    
    
    

def choose_thresh(loudness_info, astats):
    # this used to be complex probably remove
    thresh = astats['RMS level dB']

    return(thresh)


    
def compress(file, loudness_info, settings):
    offset = float(settings['offset'])
    temp_path = get_temp_path()
    threshold = int(float(settings['threshold']))
    thresh = 10**(threshold/20) #covert theshold to ratio
    if thresh >= 0.00097563 and thresh <= 1: #make sure the theshold isnt to low or high
        command = 'ffmpeg -y -i "'+ file +'" -af acompressor=threshold=' + str(thresh) + \
        ':ratio=' + settings['ratio'] + \
        ':attack=' + settings['attack'] + \
        ':release=' + settings['release'] + \
        ':detection=peak  ' + temp_path
        #print(command)
        print('LRA is ' + loudness_info['measured_LRA'] +' compressing with theshold at '  + str(threshold))
        run = subprocess.run(command, shell=True, capture_output=True, text=True)
        if run.returncode == 0 :
            print('compression sucessful')
            return temp_path
        else :
            print('compression error')
            print(run.stdout)
            return file
    else:
        print('thrshold out of range, audio file could be silent')
        return file
        


def normalize(file, loudness_info, output_file): #last process writes to output folder
    target_I = config['loudness_targets']['target_I']
    target_LRA = config['loudness_targets']['target_LRA']
    target_TP = config['loudness_targets']['target_TP']
    
    command = 'ffmpeg -y -i "'+ file \
        +'" -af loudnorm=I=' + target_I \
        + ':TP=' + target_TP \
        + ':LRA=' + target_LRA \
        + ':measured_I=' + loudness_info['measured_I'] \
        + ':measured_LRA=' + loudness_info['measured_LRA'] \
        + ':measured_TP=' + loudness_info['measured_TP'] \
        + ':measured_thresh=' + loudness_info['measured_thresh'] \
        + ':offset=' + loudness_info['offset'] \
        + ':linear=false -ar 44100 ' + output_file
        
    print('normalizing ' + output_file)
    run = subprocess.run(command, shell=True, capture_output=True, text=True)
    if run.returncode == 0 :
        print('normalization sucessful' + output_file + '\n')
        return run.returncode
    else :
        print('normalisation error ')
        print(run.stdout)



def fix_stereo(file):
    temp_path = get_temp_path()
    split, corrilation = stats.is_split(file)
    temp_path = get_temp_path()
    if split and float(corrilation) > -0.3 :
        command = 'ffmpeg -y -i "' + file + '" -af "pan=stereo|c0<c0+c1|c1<c0+c1" ' + temp_path
        run = subprocess.run(command, shell=True, capture_output=True)
        if run.returncode == 0 :
            print('file is split stereo, mono-ing ')
            return temp_path
        else :
            print('error mono-ing')
    #polarity correction
    elif float(corrilation) <= -0.3:
        command = 'ffmpeg -y -i "' + file + '" -af "pan=stereo|c0<c0|c1=-1*c1" ' + temp_path
        run = subprocess.run(command, shell=True, capture_output=True)
        if run.returncode == 0 :
            print('file is polarity inverted, fixing ')
            return temp_path
        else :
            print('error pol inverting')
    else:
        print('file has no stereo issues')
        return file

    
def get_temp_path():
    tmp_folder = config['defult']['tmp_folder']
    path = os.path.join(tmp_folder + next(tempfile._get_candidate_names()) + '.wav')
    return path


def clean_up():
    shutil.rmtree('tmp')
    os.makedirs('tmp')
    print('tempory files removed')
    
    
def main():
    input_path = config['defult']['input_path']
    output_path = config['defult']['output_path']
    tmp_folder = config['defult']['tmp_folder']
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder)
        


    ext = ('.wav')
    for files in os.listdir(input_path):
        if files.endswith(ext):
            to_process = input_path + files
            
            input_name = files.split('.')
            output_file = '"' + output_path + input_name[0] + ' -checked.wav"'
            
            to_process = fix_stereo(to_process)
            to_process, loudness_info = fix_dynamics(to_process) 
            normalize(to_process, loudness_info, output_file) 
        else:
            print(files + ' is not a wav file')
            continue
    clean_up()

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('config.ini')
    main()




#--------------compressor algorthym ideas-----------------------
# - threshold could be decided somewhere inbetween RMS level dB and RMS peak dB
# - ratio could be dependant on entrapy and maybe mean difference 
# - difference betwwen rms peak and rms mean, as well as sample peak and rms peak 
# - somthing to decide release 