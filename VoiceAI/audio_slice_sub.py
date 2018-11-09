#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Keith'
# create on 2018/09/14

import sys
import os
import pandas as pd
import numpy as np
import time
import re

import wave
import pyaudio
import logging

reload(sys)
sys.setdefaultencoding('utf8')

__author__ = 'keith'


class AudioSlice(object):
    def __init__(self):
        self._cut_len = 16 # 8
        self._hz_range = [0.25, 3.3]
        self._if_awgn = False
        self._snr = 8
        self._sp_list = [',', '.', '!', ';', ':', '?', '，', '。', '！', '；', '：', '？', ]
        self._is_save = False
        self._fs = None
        self._c_len = None
        # # self.slice_dict = {'time_list':[], 'slice_dir_list':[], 'slice_info':''}

    def wgn(self, wav):
        snr = 10**(self._snr/10.0)
        xpower = np.sum(wav**2)/len(wav)
        npower = xpower / snr
        return np.random.randn(len(wav)) * np.sqrt(npower)

    def _save_wav(self, wav, save_dir, if_sign=None):
        if if_sign==None:
            if_sign = self._if_awgn
        if if_sign:
            max_val = max(abs(wav))
            awgn = self.wgn(wav)
            wav_w = wav + awgn
            max_val_w = max(abs(wav_w))
            wav_wgn = np.array(1.0*wav_w*max_val/max_val_w).astype(np.short)
        else:
            wav_wgn = wav

        f = wave.open(save_dir, "wb")
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(self._fs)
        f.writeframes(wav_wgn.tostring())
        f.close()

    def _sig_track(self, wav, cut_num=8):
        block_seq = map(lambda ii: wav[ii*self._c_len:min((ii+1)*self._c_len,len(wav))], xrange(int(len(wav)/self._c_len)))
        fft_vect = map(lambda x: abs(np.fft.fft(x)), block_seq)

        fft_sq = map(lambda x: np.square(x), fft_vect)
        use_range = map(lambda x: int(x*self._cut_len), self._hz_range)

        val_sq = map(lambda x: (np.mean(x[use_range[0]:use_range[1]]), np.mean(x[0:use_range[0]])), fft_sq)
        re_val_sq = map(lambda ii: (val_sq[ii][0],val_sq[ii][1],np.mean(map(lambda x:x[0], val_sq[max(0,ii-cut_num):ii])),np.mean(map(lambda x:x[1], val_sq[max(0,ii-cut_num):ii]))), xrange(1, len(val_sq)))
        power_sq = [(0,0,0,0,0,0)]
        power_sq.extend(map(lambda x: (x[0],x[1],x[2],x[3], x[0]/max(0.00001,x[2]),x[2]/max(0.00001,x[3])), re_val_sq))
        power_sq.append((0,0,0,0,0,0))
        return power_sq

    def _voice_det(self, power_seq, cut_num=8):
        use_range = map(lambda x: int(x*self._cut_len), self._hz_range)
        seq_in = []
        seq_out = []

        det_sig = []
        val_sq = []
        is_voice = False
        buff_sig_len = int(4*cut_num)
        st_check_len = 2*cut_num
        end_check_len = 2*cut_num

        for ii in xrange(0,len(power_seq)):
            seq_in,seq_out,seq_in_mean,seq_out_mean,seq_gate,seq_rate = power_seq[ii]
            if seq_in_mean>3/2.0:
                if det_sig[-1]==0 and len(det_sig)>buff_sig_len:
                    if det_sig[-buff_sig_len]==1:
                        buff_tmp_len = buff_sig_len
                    else:
                        buff_tmp_len = st_check_len
                    for jj in xrange(buff_tmp_len-1):
                        if det_sig[jj+1-buff_tmp_len]==0:
                            det_sig[jj+1-buff_tmp_len] = 1
                    is_voice = True

                det_sig.append(1)
            else:
                det_sig.append(0)
            if sum(det_sig[-end_check_len:])==0 and is_voice and det_sig[-end_check_len-1]==1:
                is_voice = False
                for jj in xrange(cut_num):
                    det_sig[-end_check_len+jj] = 1

        return det_sig

    def _tf_anals(self, wav, save_path, file_path):
        wav_len = 1000.0*len(wav)/self._fs


        power_seq = self._sig_track(wav/32768.0)
        det_signal = self._voice_det(power_seq)
        det_sig = map(lambda ii: det_signal[int(ii/self._c_len)], xrange(len(wav)))
        det_sig[0] = 0

        ec_wav = np.array(map(lambda ii: wav[ii]*det_sig[ii], range(len(wav)))).astype(np.short)

        time_list = []
        save_dir_list = []
        cnt = 0

        sig_pos = filter(lambda ii: det_sig[ii-1]+det_sig[ii]==1, range(1,len(ec_wav)))
        print(sig_pos)


        '''
        tf_name_list = []
        for ii in range(int(len(sig_pos)/2)):
            tf_name_list.append(str(ii).rjust(3, '0') + '.wav')
            tmp_save_dir = os.path.join(save_path, tf_name_list[-1])
            save_dir_list.append(tmp_save_dir)
            time_list.append(int(sig_pos[2*ii]*1000.0/self._fs))
            self._save_wav(ec_wav[sig_pos[2*ii]:sig_pos[2*ii+1]], tmp_save_dir)

        if len(sig_pos) % 2 == 1:
            tf_name_list.append(str(int(len(sig_pos)/2)+1).rjust(3, '0') + '.wav')
            tmp_save_dir = os.path.join(save_path, tf_name_list[-1])
            save_dir_list.append(tmp_save_dir)
            time_list.append(int(sig_pos[-1]*1000.0/self._fs))
            self._save_wav(ec_wav[sig_pos[-1]:], tmp_save_dir)
        '''
        tf_name_list = []
        end_pos0 = [0]
        for ii in range(len(sig_pos)):
            if ii%2==1:
                end_pos0.append(sig_pos[ii])
        print "end_pos0:", end_pos0

        end_pos = [0]
        for val in end_pos0:
            if (val - end_pos[-1]) / 16 > 1500 or val == end_pos0[-1]:
                end_pos.append(val)
        print "end_pos:", end_pos

        for ii in range(len(end_pos)-1):
            tf_name_list.append(str(len(tf_name_list)).rjust(3, '0') + '.wav')
            tmp_save_dir = os.path.join(save_path, tf_name_list[-1])
            save_dir_list.append(tmp_save_dir)
            time_list.append(int(end_pos[ii+1]*1000.0/self._fs))
            self._save_wav(wav[end_pos[ii]+16*256:min(end_pos[ii+1]+16*256,len(wav))], tmp_save_dir)

        if len(wav)-end_pos[-1]>16*256:
            tf_name_list.append(str(len(tf_name_list)).rjust(3, '0') + '.wav')
            tmp_save_dir = os.path.join(save_path, tf_name_list[-1])
            save_dir_list.append(tmp_save_dir)
            time_list.append(int(len(wav)*1000.0/self._fs))
            self._save_wav(wav[end_pos[-1]:], tmp_save_dir)


        with open(file_path, "w") as fw:
            fw.write("\r\n".join(tf_name_list))

        '''
        for ii in range(1,len(ec_wav)):
            if det_sig[ii-1]==0 and det_sig[ii]==1:
                tmp_save_dir = os.path.join(save_path,'slice_'+str(cnt)+'.wav')
                save_dir_list.append(tmp_save_dir)
                if self._is_save:
                    self._save_wav(ec_wav[ii:], tmp_save_dir)
                if cnt>0:
                    time_list.append(int(ii*1000.0/self._fs))
                cnt += 1
            else:
                continue
        '''

        return time_list,save_dir_list

    def parse_audio(self, audio_dir, text_dir, save_path, file_path):
        wf = wave.open(audio_dir, 'rb')
        params = wf.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        str_data = wf.readframes(nframes)
        wf.close()
        # logging.info("nchannels: %s, sampwidth: %s, framerate: %s, nframes: %s", params[:4])

        wav = np.fromstring(str_data, dtype=np.short)
        self._fs = framerate
        self._c_len = int(self._fs*self._cut_len/1000)

        time_list,save_dir_list = self._tf_anals(wav, save_path, file_path)
        '''
    file = open(text_dir,'r')
        line = file.readline()
        text_slice_num = len(re.split('[' + ''.join(self._sp_list) + ']', line.strip())) - 1
        if text_slice_num == len(time_list):
            slice_info = 'pass!'
        else:
            slice_info = 'fail!'
        return {'time_list':time_list, 'save_dir_list':save_dir_list, 'slice_info':slice_info}
        '''

import re
import ubelt
from pathlib import Path
# source_path = "/home/data2/"
# target_path = "/home/data2_ok/"
source_path = "/home/new_test"
target_path = "/home/new_test_result/"


def main():

    for wav_dir in Path(source_path).glob("*"):
        for wav_file in Path(wav_dir).glob("*.wav"):
            wav_file_name = wav_file.name.lower().replace(".wav", "")
            wav_file_name = re.sub(r"[\d]+[.][\d]+", "", wav_file_name)
            wav_file_name = re.sub(r"raz[ -]?[a-z][ ]", "", wav_file_name)
            wav_file_name = wav_file_name.strip()
            new_file_path = "%s%s - %s" % (
                target_path,
                wav_dir.name.replace(" ", "").replace("-", "").lower().replace("raz", ""),
                wav_file_name
            )
            print new_file_path
            ubelt.ensuredir(new_file_path + "/wav")
            ubelt.ensuredir(new_file_path + "/etc")

            audio_slice = AudioSlice()
            audio_slice.parse_audio("%s" % wav_file, "", new_file_path + "/wav", new_file_path + "/etc/prompts-original")

            # break
        # break


if __name__ == '__main__':
    main()


exit(1)

if __name__ == '__main__':
    # audio_dir = '../data/1536205763863_blob.wav'
    # audio_dir = '../data/phone_record-1534502123.wav'
    # audio_dir = '''/mine/github/coding/ShadowWalker/download/99076875\ -\ 轻微1224/raz-a/Oh\,raccoon.wav'''
    # audio_dir = '''/home/data/12338138 - RAZ-A/Fruit.wav'''
    audio_dir = '''/home/data2/18988369 - Raz d/Raz d maria's halloween.wav'''
    text_dir = '../data/huashu.txt'
    save_path = './data'
    audio_slice = AudioSlice()
    print(audio_slice.parse_audio(audio_dir,text_dir,save_path,"./data/fff.txt"))



