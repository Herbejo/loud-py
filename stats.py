#collect a bunch os stats about and audio file


import subprocess
from subprocess import PIPE, Popen
import json
from scipy.io import wavfile
from scipy.stats import pearsonr
import pandas as pd
import re 



def load_file(input_file): #takes a path to audio file and returns a dataframe of the samples 
    samplerate, data = wavfile.read(input_file)
    df = pd.DataFrame(data, columns =['ch1', 'ch2'])
    return df

def get_correlation(input_dataFrame): #returns a float of the corriation between column 0 and column 1 of a data frame
    cr = input_dataFrame.corr(method='pearson')._get_value(0, 1,takeable = True)
    return cr
    
def is_split(file_path):
    correlation_theshold = 0.7  #if corrilatio is les than this we will call the file split
    
    data = load_file(file_path)
    correlation = get_correlation(data)
    if correlation <= correlation_theshold :
        result = True
    else: 
        result = False

    return result, correlation


def get_loudness_info(file_path): #returns dictionary of loudness info from file path sring(needs double slashes) 

    command = 'ffmpeg -i "'+ file_path +'" -af loudnorm=print_format=json -f null -'
    print("getting loudness info of " + file_path)
    mesure = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
    product = "\n".join(mesure.communicate()[-1].decode("UTF-8").split("\n")[-13:-1])
    data = json.loads(product)

    output = {
       "measured_I": data["input_i"],
       "measured_TP": data["input_tp"],
       "measured_LRA": data["input_lra"],
       "measured_thresh": data["input_thresh"],
       "offset": data["target_offset"]
    }
    return output

def get_astats(file_path): # returns dictionary of overall astats
    command = 'ffmpeg -i "'+ file_path +'" -hide_banner -nostats -af astats=metadata=1 -f null -'
    print('getting astats')
    mesure = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
    product = "".join(mesure.communicate()[-1].decode("UTF-8"))
    product = re.sub("[\(\[].*?[\)\]]", "", product)
    product = product.splitlines()
    product = product[product.index(' Overall')+1:]
    product = [i.strip(' ') for i in product]
    product = [tuple(i.split(': ')) for i in product]
    stats = dict(product)
    #print(stats)
    return stats



## example loudnorem output

# [Parsed_loudnorm_0 @ 00000204b0eea140]
# {
        # "input_i" : "-26.87",
        # "input_tp" : "-3.39",
        # "input_lra" : "6.90",
        # "input_thresh" : "-37.21",
        # "output_i" : "-23.88",
        # "output_tp" : "-2.00",
        # "output_lra" : "5.90",
        # "output_thresh" : "-34.19",
        # "normalization_type" : "dynamic",
        # "target_offset" : "-0.12"
# }


##example astats output 

# Guessed Channel Layout for Input Stream #0.0 : stereo
# Input #0, wav, from 'audio\coral damage pkg.wav':
  # Metadata:
    # encoder         : Lavf56.30.100
  # Duration: 00:02:33.41, bitrate: 1411 kb/s
  # Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 44100 Hz, 2 channels, s16, 1411 kb/s
# Stream mapping:
  # Stream #0:0 -> #0:0 (pcm_s16le (native) -> pcm_s16le (native))
# Press [q] to stop, [?] for help
# Output #0, null, to 'pipe:':
  # Metadata:
    # encoder         : Lavf59.34.101
  # Stream #0:0: Audio: pcm_s16le, 44100 Hz, stereo, s16, 1411 kb/s
    # Metadata:
      # encoder         : Lavc59.51.101 pcm_s16le
# size=N/A time=00:02:33.39 bitrate=N/A speed=  34x
# video:0kB audio:26427kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: unknown
# [Parsed_astats_0 @ 000001d4af817c40] Channel: 1
# [Parsed_astats_0 @ 000001d4af817c40] DC offset: -0.000016
# [Parsed_astats_0 @ 000001d4af817c40] Min level: -21538.000000
# [Parsed_astats_0 @ 000001d4af817c40] Max level: 27912.000000
# [Parsed_astats_0 @ 000001d4af817c40] Min difference: 0.000000
# [Parsed_astats_0 @ 000001d4af817c40] Max difference: 19947.000000
# [Parsed_astats_0 @ 000001d4af817c40] Mean difference: 313.035552
# [Parsed_astats_0 @ 000001d4af817c40] RMS difference: 713.895771
# [Parsed_astats_0 @ 000001d4af817c40] Peak level dB: -1.392914
# [Parsed_astats_0 @ 000001d4af817c40] RMS level dB: -19.577345
# [Parsed_astats_0 @ 000001d4af817c40] RMS peak dB: -10.241804
# [Parsed_astats_0 @ 000001d4af817c40] RMS trough dB: -84.629314
# [Parsed_astats_0 @ 000001d4af817c40] Crest factor: 8.113748
# [Parsed_astats_0 @ 000001d4af817c40] Flat factor: 0.000000
# [Parsed_astats_0 @ 000001d4af817c40] Peak count: 2
# [Parsed_astats_0 @ 000001d4af817c40] Noise floor dB: -78.266739
# [Parsed_astats_0 @ 000001d4af817c40] Noise floor count: 296
# [Parsed_astats_0 @ 000001d4af817c40] Entropy: 0.789929
# [Parsed_astats_0 @ 000001d4af817c40] Bit depth: 16/16
# [Parsed_astats_0 @ 000001d4af817c40] Dynamic range: 94.936419
# [Parsed_astats_0 @ 000001d4af817c40] Zero crossings: 506844
# [Parsed_astats_0 @ 000001d4af817c40] Zero crossings rate: 0.074918
# [Parsed_astats_0 @ 000001d4af817c40] Channel: 2
# [Parsed_astats_0 @ 000001d4af817c40] DC offset: -0.000015
# [Parsed_astats_0 @ 000001d4af817c40] Min level: -21538.000000
# [Parsed_astats_0 @ 000001d4af817c40] Max level: 27906.000000
# [Parsed_astats_0 @ 000001d4af817c40] Min difference: 0.000000
# [Parsed_astats_0 @ 000001d4af817c40] Max difference: 20066.000000
# [Parsed_astats_0 @ 000001d4af817c40] Mean difference: 313.041942
# [Parsed_astats_0 @ 000001d4af817c40] RMS difference: 713.741173
# [Parsed_astats_0 @ 000001d4af817c40] Peak level dB: -1.394782
# [Parsed_astats_0 @ 000001d4af817c40] RMS level dB: -19.577316
# [Parsed_astats_0 @ 000001d4af817c40] RMS peak dB: -10.242352
# [Parsed_astats_0 @ 000001d4af817c40] RMS trough dB: -84.536465
# [Parsed_astats_0 @ 000001d4af817c40] Crest factor: 8.111977
# [Parsed_astats_0 @ 000001d4af817c40] Flat factor: 0.000000
# [Parsed_astats_0 @ 000001d4af817c40] Peak count: 2
# [Parsed_astats_0 @ 000001d4af817c40] Noise floor dB: -72.246139
# [Parsed_astats_0 @ 000001d4af817c40] Noise floor count: 40039
# [Parsed_astats_0 @ 000001d4af817c40] Entropy: 0.789932
# [Parsed_astats_0 @ 000001d4af817c40] Bit depth: 16/16
# [Parsed_astats_0 @ 000001d4af817c40] Dynamic range: 94.934552
# [Parsed_astats_0 @ 000001d4af817c40] Zero crossings: 506928
# [Parsed_astats_0 @ 000001d4af817c40] Zero crossings rate: 0.074931
# [Parsed_astats_0 @ 000001d4af817c40] Overall
# [Parsed_astats_0 @ 000001d4af817c40] DC offset: -0.000016
# [Parsed_astats_0 @ 000001d4af817c40] Min level: -21538.000000
# [Parsed_astats_0 @ 000001d4af817c40] Max level: 27912.000000
# [Parsed_astats_0 @ 000001d4af817c40] Min difference: 0.000000
# [Parsed_astats_0 @ 000001d4af817c40] Max difference: 20066.000000
# [Parsed_astats_0 @ 000001d4af817c40] Mean difference: 313.038747
# [Parsed_astats_0 @ 000001d4af817c40] RMS difference: 713.818476
# [Parsed_astats_0 @ 000001d4af817c40] Peak level dB: -1.392914
# [Parsed_astats_0 @ 000001d4af817c40] RMS level dB: -19.577330
# [Parsed_astats_0 @ 000001d4af817c40] RMS peak dB: -10.241804
# [Parsed_astats_0 @ 000001d4af817c40] RMS trough dB: -84.629314
# [Parsed_astats_0 @ 000001d4af817c40] Flat factor: 0.000000
# [Parsed_astats_0 @ 000001d4af817c40] Peak count: 2.000000
# [Parsed_astats_0 @ 000001d4af817c40] Noise floor dB: -72.246139
# [Parsed_astats_0 @ 000001d4af817c40] Noise floor count: 20167.500000
# [Parsed_astats_0 @ 000001d4af817c40] Entropy: 0.789931
# [Parsed_astats_0 @ 000001d4af817c40] Bit depth: 16/16
# [Parsed_astats_0 @ 000001d4af817c40] Number of samples: 6765293

# audio\\brazil football pkg.wav good
# {'DC offset': '-0.000037',
 # 'Min level': '-11782.000000',
 # 'Max level': '11360.000000',
 # 'Min difference': '0.000000',
 # 'Max difference': '13743.000000',
 # 'Mean difference': '269.731321',
 # 'RMS difference': '636.557964', 
 # 'Peak level dB': '-8.884353',
 # 'RMS level dB': '-24.147546', 
 # 'RMS peak dB': '-16.668227', 
 # 'RMS trough dB': '-84.994177', 
 # 'Flat factor': '0.000000', 
 # 'Peak count': '2.000000', 
 # 'Noise floor dB': '-78.266739', 
 # 'Noise floor count': '1392.000000', 
 # 'Entropy': '0.743339',
 # 'Bit depth': '16/16', 
 # 'Number of samples': '3622904'}
 
# getting loudness info of 
# {'measured_I': '-20.85', 'measured_TP': '-8.89', 'measured_LRA': '2.80', 'measured_thresh': '-31.07', 'offset': '0.40'}
# getting astats



# audio\\dairy-vigil-pkg.wav needs compression
# {'DC offset': '0.000004', 
# 'Min level': '-30694.000000', 
# 'Max level': '27475.000000', 
# 'Min difference': '0.000000', 
# 'Max difference': '24736.000000',
 # 'Mean difference': '263.917003', 
 # 'RMS difference': '625.550851', 
 # 'Peak level dB': '-0.567664', 
 # 'RMS level dB': '-22.364183', 
 # 'RMS peak dB': '-12.007413', 
 # 'RMS trough dB': '-63.335835', 
 # 'Flat factor': '0.000000', 
 # 'Peak count': '2.000000', 
 # 'Noise floor dB': '-55.987871', 
 # 'Noise floor count': '1624.500000', 
 # 'Entropy': '0.752058', 
 # 'Bit depth': '16/16', 
 # 'Number of samples': '4997765'}
# getting loudness info of 
# {'measured_I': '-18.83', 'measured_TP': '-0.55', 'measured_LRA': '7.60', 'measured_thresh': '-29.30', 'offset': '0.12'}

