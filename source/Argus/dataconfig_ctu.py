#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dataconfig_ctu.py
@Contact :   hanxueying@iie.ac.cn
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2024/6/25 19:54   xueying      1.0       
'''


class Mydict:
    def __init__(self):
        self.class_dict = {
            'traffic_20240311.pickle': 0,
            'traffic_20240312.pickle': 0,
            'traffic_20240313.pickle': 0,
            'traffic_20240314.pickle': 0,
            'traffic_20240315.pickle': 0,
            'traffic_20240318.pickle': 0,
            'traffic_20240319.pickle': 0,
            'traffic_20240320.pickle': 0,
            'traffic_20240321.pickle': 0,
            'traffic_20240322.pickle': 0,
            'traffic_20240325.pickle': 0,
            'traffic_20240326.pickle': 0,
            'traffic_20240327.pickle': 0,
            'traffic_20240328.pickle': 0,
            'traffic_20240329.pickle': 0,
            'traffic_20240401.pickle': 0,
            'traffic_20240402.pickle': 0,
            'traffic_20240403.pickle': 0,
            'traffic_20240407.pickle': 0,
            'traffic_20240408.pickle': 0,
            'traffic_20240411.pickle': 0,
            'traffic_20240412.pickle': 0,
            'traffic_20240415.pickle': 0,
            'traffic_20240416.pickle': 0,
            'traffic_20240417.pickle': 0,
            'traffic_20240418.pickle': 0,
            'traffic_20240419.pickle': 0,

            'botware_1_trickbot_2017-04-12_win5.pickle': 1,
            'botware_1_trickbot_2017-04-17_win14.pickle': 1,
            'botware_1_trickbot_2017-05-15_win15.pickle': 1,
            'botware_1_trickbot_2017-06-24_win4.pickle': 1,
            'botware_1_trickbot_2017-06-24_win5.pickle': 1,
            'botware_1_trickbot_2017-06-24_win6.pickle': 1,
            'botware_1_trickbot_2017-06-24_win12.pickle': 1,
            'botware_1_trickbot_2017-3-29_win8.pickle': 1,

            'botware_4_emotet_2017-06-24_win3.pickle': 1,
            'botware_4_emotet_2017-06-24_win7.pickle': 1,
            'botware_4_emotet_2017-06-24_win8.pickle': 1,
            'botware_4_emotet_2017-06-24_win10.pickle': 1,
            'botware_4_emotet_2017-06-24_win11.pickle': 1,
            'botware_4_emotet_2017-06-24_win15.pickle': 1,
            'botware_4_emotet_2017-06-24_win16.pickle': 1,
            'botware_4_emotet_2017-06-24_win17.pickle': 1,

            'ransomware_2_dirdex_2017-15-05_win11.pickle': 1,
            'ransomware_2_dirdex_2018-01-29_win6.pickle': 1,
            'ransomware_2_dridex_2017-04-17_win1.pickle': 1,
            'ransomware_2_dridex_2017-04-18_win18.pickle': 1,
            'ransomware_2_dridex_2017-04-18_win20.pickle': 1,
            'ransomware_2_dridex_2017-05-16_win5.pickle': 1,
            'ransomware_2_dridex_2018-04-03_win12.pickle': 1,

            'spyware_4_zesus_2013-11-06_capture-win6.pickle': 1,
            'spyware_4_zesus_2014-05-30_capture-win8.pickle': 1,
            'spyware_4_zesus_2014-06-06_capture-win8.pickle': 1,
            'spyware_4_zesus_2014-12-20_capture-win3.pickle': 1,

            'miner_2_minertrojan_2018-03-27_win4.pickle': 1,
            'ransomware_1_wannacry_2017-05-15_win4.pickle': 1,
            'spyware_1_magic_2017-11-22_win4.pickle': 1,
            'spyware_2_trickster_2017-06-24_win18.pickle': 1,
            'spyware_3_ccleaner_2018-01-30_win17.pickle': 1,

            'spyware_4_zesus_2014-06-06_capture-win8_2.pickle': 1,
            'botware_4_emotet_2017-06-24_win17_2.pickle': 1,
            'ransomware_2_dirdex_2017-15-05_win11_2.pickle': 1,
            'botware_4_emotet_2017-06-24_win11_2.pickle': 1,
            'botware_1_trickbot_2017-3-29_win8_2.pickle': 1,
            'spyware_4_zesus_2014-12-20_capture-win3_2.pickle': 1,
            'ransomware_2_dridex_2018-04-03_win12_2.pickle': 1,
            'botware_4_emotet_2017-06-24_win16_2.pickle': 1,
            'ransomware_2_dridex_2017-04-18_win18_2.pickle': 1,
            'botware_1_trickbot_2017-06-24_win12_2.pickle': 1,

            # scp
            'scp1.pickle': 0,
            'scpDown1.pickle': 0,
            'scpDown2.pickle': 0,
            'scpDown3.pickle': 0,
            'scpDown4.pickle': 0,
            'scpDown5.pickle': 0,
            'scpDown6.pickle': 0,
            'scpUp1.pickle': 0,
            'scpUp2.pickle': 0,
            'scpUp3.pickle': 0,
            'scpUp5.pickle': 0,
            'scpUp6.pickle': 0,

            # sftp
            'sftp1.pickle': 0,
            'sftpDown1.pickle': 0,
            'sftpDown2.pickle': 0,
            'sftpUp1.pickle': 0,
            'sftp_down_3.pickle': 0,
            'sftp_down_3b.pickle': 0,
            'sftp_up_2.pickle': 0,
            'sftp_up_2b.pickle': 0,

            # skype audio
            'skype_audio1.pickle': 0,
            'skype_audio1b.pcapng.pickle': 0,
            'skype_audio2.pickle': 0,
            'skype_audio2b.pickle': 0,
            'skype_audio3.pickle': 0,
            'skype_audio4.pickle': 0,

            # skype chat
            'skype_chat1.pickle': 0,
            'skype_chat1b.pickle': 0,

            # skype file
            'skype_file1.pickle': 0,
            'skype_file2.pickle': 0,
            'skype_file3.pickle': 0,
            'skype_file4.pickle': 0,
            'skype_file5.pickle': 0,
            'skype_file6.pickle': 0,
            'skype_file7.pickle': 0,
            'skype_file8.pickle': 0,

            # skype video
            'skype_video1.pickle': 0,
            'skype_video1b.pickle': 0,
            'skype_video2.pickle': 0,
            'skype_video2b.pickle': 0,

            # spotify
            'spotify1.pickle': 0,
            'spotify2.pickle': 0,
            'spotify3.pickle': 0,
            'spotify4.pickle': 0,

            # vimeo
            'vimeo1.pickle': 0,
            'vimeo2.pickle': 0,
            'vimeo3.pickle': 0,
            'vimeo4.pickle': 0,

            # voipbuster
            'voipbuster1b.pickle': 0,
            'voipbuster2b.pickle': 0,
            'voipbuster3b.pickle': 0,
            'voipbuster4.pickle': 0,
            'voipbuster4b.pickle': 0,

            # yotube
            'youtube1.pickle': 0,
            'youtube2.pickle': 0,
            'youtube3.pickle': 0,
            'youtube4.pickle': 0,
            'youtube5.pickle': 0,
            'youtube6.pickle': 0,
            'youtubeHTML5_1.pickle': 0,

            # aim chat
            'AIMchat1.pickle': 0,
            'AIMchat2.pickle': 0,
            'AIMchat3.pickle': 0,
            'AIMchat3b.pickle': 0,

            # email
            'email1.pickle': 0,
            'email1b.pickle': 0,
            'email2.pickle': 0,
            'email2b.pickle': 0,

            # facebook chat
            'facebookchat1.pickle': 0,
            'facebookchat2.pickle': 0,
            'facebookchat3.pickle': 0,

            # facebook audio
            'facebook_audio1.pickle': 0,
            'facebook_audio1b.pickle': 0,
            'facebook_audio2.pickle': 0,
            'facebook_audio2b.pickle': 0,
            'facebook_audio3.pickle': 0,
            'facebook_audio4.pickle': 0,

            # facebook chat
            'facebook_chat_4.pickle': 0,
            'facebook_chat_4b.pickle': 0,

            # facebook video
            'facebook_video1.pickle': 0,
            'facebook_video1b.pickle': 0,
            'facebook_video2.pickle': 0,
            'facebook_video2b.pickle': 0,

            # ftp
            'ftps_down_1.pickle': 0,
            'ftps_down_1b.pickle': 0,
            'ftps_up_2.pickle': 0,
            'ftps_up_2b.pickle': 0,

            # gmail chat
            'gmailchat1.pickle': 0,
            'gmailchat2.pickle': 0,
            'gmailchat3.pickle': 0,

            # hangouts audio
            'hangouts_audio1.pickle': 0,
            'hangouts_audio1b.pickle': 0,
            'hangouts_audio2.pickle': 0,
            'hangouts_audio2b.pickle': 0,
            'hangouts_audio3.pickle': 0,
            'hangouts_audio4.pickle': 0,

            # hangout chat
            'hangouts_chat_4.pickle': 0,
            'hangouts_chat_4b.pickle': 0,

            # hangout video
            'hangouts_video1b.pickle': 0,
            'hangouts_video2.pickle': 0,
            'hangouts_video2b.pickle': 0,

            # icq chat
            'icq_chat_1.pickle': 0,
            'icq_chat_2.pickle': 0,
            'icq_chat_3.pickle': 0,
            'icq_chat_3b.pickle': 0,

            # netflix
            'netflix1.pickle': 0,
            'netflix2.pickle': 0,
            'netflix3.pickle': 0,
            'netflix4.pickle': 0,
        }

        self.detail_class_dict = {
            'traffic_20240311.pickle': 0,
            'traffic_20240312.pickle': 0,
            'traffic_20240313.pickle': 0,
            'traffic_20240314.pickle': 0,
            'traffic_20240315.pickle': 0,
            'traffic_20240318.pickle': 0,
            'traffic_20240319.pickle': 0,

            'traffic_20240320.pickle': 1,
            'traffic_20240321.pickle': 1,
            'traffic_20240322.pickle': 1,

            'traffic_20240325.pickle': 2,
            'traffic_20240326.pickle': 2,
            'traffic_20240327.pickle': 2,
            'traffic_20240328.pickle': 2,
            'traffic_20240329.pickle': 2,
            'traffic_20240401.pickle': 2,
            'traffic_20240402.pickle': 2,

            'traffic_20240403.pickle': 3,
            'traffic_20240407.pickle': 3,
            'traffic_20240408.pickle': 3,

            'traffic_20240411.pickle': 4,
            'traffic_20240412.pickle': 4,
            'traffic_20240415.pickle': 4,
            'traffic_20240416.pickle': 4,
            'traffic_20240417.pickle': 4,
            'traffic_20240418.pickle': 4,
            'traffic_20240419.pickle': 4,

            'botware_1_trickbot_2017-04-12_win5.pickle': 11,
            'botware_1_trickbot_2017-04-17_win14.pickle': 11,
            'botware_1_trickbot_2017-05-15_win15.pickle': 11,
            'botware_1_trickbot_2017-06-24_win4.pickle': 11,
            'botware_1_trickbot_2017-06-24_win5.pickle': 11,
            'botware_1_trickbot_2017-06-24_win6.pickle': 11,
            'botware_1_trickbot_2017-06-24_win12.pickle': 11,
            'botware_1_trickbot_2017-3-29_win8.pickle': 11,

            'botware_4_emotet_2017-06-24_win3.pickle': 12,
            'botware_4_emotet_2017-06-24_win7.pickle': 12,
            'botware_4_emotet_2017-06-24_win8.pickle': 12,
            'botware_4_emotet_2017-06-24_win10.pickle': 12,
            'botware_4_emotet_2017-06-24_win11.pickle': 12,
            'botware_4_emotet_2017-06-24_win15.pickle': 12,
            'botware_4_emotet_2017-06-24_win16.pickle': 12,
            'botware_4_emotet_2017-06-24_win17.pickle': 12,

            'ransomware_2_dirdex_2017-15-05_win11.pickle': 13,
            'ransomware_2_dirdex_2018-01-29_win6.pickle': 13,
            'ransomware_2_dridex_2017-04-17_win1.pickle': 13,
            'ransomware_2_dridex_2017-04-18_win18.pickle': 13,
            'ransomware_2_dridex_2017-04-18_win20.pickle': 13,
            'ransomware_2_dridex_2017-05-16_win5.pickle': 13,
            'ransomware_2_dridex_2018-04-03_win12.pickle': 13,

            'spyware_4_zesus_2013-11-06_capture-win6.pickle': 14,
            'spyware_4_zesus_2014-05-30_capture-win8.pickle': 14,
            'spyware_4_zesus_2014-06-06_capture-win8.pickle': 14,
            'spyware_4_zesus_2014-12-20_capture-win3.pickle': 14,

            'miner_2_minertrojan_2018-03-27_win4.pickle': 15,
            'ransomware_1_wannacry_2017-05-15_win4.pickle': 16,
            'spyware_1_magic_2017-11-22_win4.pickle': 17,
            'spyware_2_trickster_2017-06-24_win18.pickle': 18,
            'spyware_3_ccleaner_2018-01-30_win17.pickle': 19,

            'spyware_4_zesus_2014-06-06_capture-win8_2.pickle': 14,
            'botware_4_emotet_2017-06-24_win17_2.pickle': 12,
            'ransomware_2_dirdex_2017-15-05_win11_2.pickle': 13,
            'botware_4_emotet_2017-06-24_win11_2.pickle': 12,
            'botware_1_trickbot_2017-3-29_win8_2.pickle': 11,
            'spyware_4_zesus_2014-12-20_capture-win3_2.pickle': 14,
            'ransomware_2_dridex_2018-04-03_win12_2.pickle': 13,
            'botware_4_emotet_2017-06-24_win16_2.pickle': 12,
            'ransomware_2_dridex_2017-04-18_win18_2.pickle': 13,
            'botware_1_trickbot_2017-06-24_win12_2.pickle': 11,

            # scp
            'scp1.pickle': 21,
            'scpDown1.pickle': 21,
            'scpDown2.pickle': 21,
            'scpDown3.pickle': 21,
            'scpDown4.pickle': 21,
            'scpDown5.pickle': 21,
            'scpDown6.pickle': 21,
            'scpUp1.pickle': 21,
            'scpUp2.pickle': 21,
            'scpUp3.pickle': 21,
            'scpUp5.pickle': 21,
            'scpUp6.pickle': 21,

            # sftp
            'sftp1.pickle': 22,
            'sftpDown1.pickle': 22,
            'sftpDown2.pickle': 22,
            'sftpUp1.pickle': 22,
            'sftp_down_3.pickle': 22,
            'sftp_down_3b.pickle': 22,
            'sftp_up_2.pickle': 22,
            'sftp_up_2b.pickle': 22,

            # skype audio
            'skype_audio1.pickle': 23,
            'skype_audio1b.pcapng.pickle': 23,
            'skype_audio2.pickle': 23,
            'skype_audio2b.pickle': 23,
            'skype_audio3.pickle': 23,
            'skype_audio4.pickle': 23,

            # skype chat
            'skype_chat1.pickle': 24,
            'skype_chat1b.pickle': 24,

            # skype file
            'skype_file1.pickle': 25,
            'skype_file2.pickle': 25,
            'skype_file3.pickle': 25,
            'skype_file4.pickle': 25,
            'skype_file5.pickle': 25,
            'skype_file6.pickle': 25,
            'skype_file7.pickle': 25,
            'skype_file8.pickle': 25,

            # skype video
            'skype_video1.pickle': 26,
            'skype_video1b.pickle': 26,
            'skype_video2.pickle': 26,
            'skype_video2b.pickle': 26,

            # spotify
            'spotify1.pickle': 27,
            'spotify2.pickle': 27,
            'spotify3.pickle': 27,
            'spotify4.pickle': 27,

            # vimeo
            'vimeo1.pickle': 28,
            'vimeo2.pickle': 28,
            'vimeo3.pickle': 28,
            'vimeo4.pickle': 28,

            # voipbuster
            'voipbuster1b.pickle': 29,
            'voipbuster2b.pickle': 29,
            'voipbuster3b.pickle': 29,
            'voipbuster4.pickle': 29,
            'voipbuster4b.pickle': 29,

            # yotube
            'youtube1.pickle': 30,
            'youtube2.pickle': 30,
            'youtube3.pickle': 30,
            'youtube4.pickle': 30,
            'youtube5.pickle': 30,
            'youtube6.pickle': 30,
            'youtubeHTML5_1.pickle': 30,

            # aim chat
            'AIMchat1.pickle': 31,
            'AIMchat2.pickle': 31,
            'AIMchat3.pickle': 31,
            'AIMchat3b.pickle': 31,

            # email
            'email1.pickle': 32,
            'email1b.pickle': 32,
            'email2.pickle': 32,
            'email2b.pickle': 32,

            # facebook chat
            'facebookchat1.pickle': 33,
            'facebookchat2.pickle': 33,
            'facebookchat3.pickle': 33,

            # facebook audio
            'facebook_audio1.pickle': 34,
            'facebook_audio1b.pickle': 34,
            'facebook_audio2.pickle': 34,
            'facebook_audio2b.pickle': 34,
            'facebook_audio3.pickle': 34,
            'facebook_audio4.pickle': 34,

            # facebook chat
            'facebook_chat_4.pickle': 35,
            'facebook_chat_4b.pickle': 35,

            # facebook video
            'facebook_video1.pickle': 36,
            'facebook_video1b.pickle': 36,
            'facebook_video2.pickle': 36,
            'facebook_video2b.pickle': 36,

            # ftp
            'ftps_down_1.pickle': 37,
            'ftps_down_1b.pickle': 37,
            'ftps_up_2.pickle': 37,
            'ftps_up_2b.pickle': 37,

            # gmail chat
            'gmailchat1.pickle': 38,
            'gmailchat2.pickle': 38,
            'gmailchat3.pickle': 38,

            # hangouts audio
            'hangouts_audio1.pickle': 39,
            'hangouts_audio1b.pickle': 39,
            'hangouts_audio2.pickle': 39,
            'hangouts_audio2b.pickle': 39,
            'hangouts_audio3.pickle': 39,
            'hangouts_audio4.pickle': 39,

            # hangout chat
            'hangouts_chat_4.pickle': 40,
            'hangouts_chat_4b.pickle': 40,

            # hangout video
            'hangouts_video1b.pickle': 41,
            'hangouts_video2.pickle': 41,
            'hangouts_video2b.pickle': 41,

            # icq chat
            'icq_chat_1.pickle': 42,
            'icq_chat_2.pickle': 42,
            'icq_chat_3.pickle': 42,
            'icq_chat_3b.pickle': 42,

            # netflix
            'netflix1.pickle': 43,
            'netflix2.pickle': 43,
            'netflix3.pickle': 43,
            'netflix4.pickle': 43,
        }


# 在使用part1作为训练数据的时候，不指定new normal file，在其他时候都需要指定new normal file

class DatasetConfig1:
    def __init__(self, new_normal_file=None, new_attack_file=None):
        self.part1_normal_files = [
            'traffic_20240311.pickle',
            'traffic_20240312.pickle',
            'traffic_20240313.pickle',
            'traffic_20240314.pickle',
            'traffic_20240315.pickle',
            'traffic_20240318.pickle',
            'traffic_20240319.pickle',
        ]

        self.part1_normal_files_val = [
            'traffic_20240320.pickle',
            'traffic_20240321.pickle',
            'traffic_20240322.pickle',
        ]

        self.part1_normal_files_val_certain = self.part1_normal_files_val
        self.part1_normal_files_val_uncertain = []

        self.part2_normal_files = [
            'traffic_20240325.pickle',
            'traffic_20240326.pickle',
            'traffic_20240327.pickle',
            'traffic_20240328.pickle',
            'traffic_20240329.pickle',
            'traffic_20240401.pickle',
            'traffic_20240402.pickle',
        ]

        # 人工指定哪些是certain，哪些是uncertain，用于对比（用于模型更新）
        self.part2_normal_certain_files = self.part2_normal_files
        self.part2_normal_uncertain_files = [
            # 此时没有uncertain
        ]

        self.part2_normal_files_val = [
            'traffic_20240403.pickle',
            'traffic_20240407.pickle',
            'traffic_20240408.pickle',
        ]

        self.part2_normal_files_val_certain = self.part2_normal_files_val
        self.part2_normal_files_val_uncertain = []

        self.part3_normal_files = [
            'traffic_20240411.pickle',
            'traffic_20240412.pickle',
            'traffic_20240415.pickle',
            'traffic_20240416.pickle',
            'traffic_20240417.pickle',
            'traffic_20240418.pickle',
            'traffic_20240419.pickle',
        ]

        self.part3_normal_files_certain = self.part3_normal_files
        self.part3_normal_files_uncertain = []

        self.part4_normal_files = [
            # scp
            'scp1.pickle',
            'scpDown1.pickle',
            'scpDown2.pickle',
            'scpDown3.pickle',
            'scpUp1.pickle',
            'scpUp2.pickle',
            'scpUp3.pickle',
            # sftp
            'sftp1.pickle',
            'sftpUp1.pickle',
            'sftpDown1.pickle',
            'sftpDown2.pickle',
            # skype audio
            'skype_audio1.pickle',
            'skype_audio1b.pcapng.pickle',
            'skype_audio2.pickle',
            # skype chat
            'skype_chat1.pickle',
            # skype file
            'skype_file1.pickle',
            'skype_file2.pickle',
            'skype_file3.pickle',
            'skype_file4.pickle',
            'skype_file5.pickle',
            # skype video
            'skype_video1.pickle',
            'skype_video1b.pickle',
            # spotify
            'spotify1.pickle',
            'spotify2.pickle',
            # vimeo
            'vimeo1.pickle',
            'vimeo2.pickle',
            # voipbuster
            'voipbuster1b.pickle',
            'voipbuster2b.pickle',
            'voipbuster3b.pickle',
            # yotube
            'youtube1.pickle',
            'youtube2.pickle',
            'youtube3.pickle',
            'youtube4.pickle',
            # aim chat
            'AIMchat1.pickle',
            'AIMchat2.pickle',
            # email
            'email1.pickle',
            'email1b.pickle',
            # facebook chat
            'facebookchat1.pickle',
            'facebookchat2.pickle',
            # facebook audio
            'facebook_audio1.pickle',
            'facebook_audio1b.pickle',
            'facebook_audio2.pickle',
            'facebook_audio2b.pickle',
            # facebook chat
            'facebook_chat_4.pickle',
            # facebook video
            'facebook_video1.pickle',
            'facebook_video1b.pickle',
            # ftp
            'ftps_down_1.pickle',
            'ftps_up_2.pickle',
            # gmail chat
            'gmailchat1.pickle',
            'gmailchat2.pickle',
            # hangouts audio
            'hangouts_audio1.pickle',
            'hangouts_audio2.pickle',
            'hangouts_audio3.pickle',
            'hangouts_audio4.pickle',
            # hangout chat
            'hangouts_chat_4.pickle',
            # hangout video
            'hangouts_video1b.pickle',
            'hangouts_video2.pickle',
            # icq chat
            'icq_chat_1.pickle',
            'icq_chat_2.pickle',
            'icq_chat_3.pickle',
            # netflix
            'netflix1.pickle',
            'netflix2.pickle',
        ]

        self.part4_normal_certain_files = [
            # 没有certain
        ]

        self.part4_normal_uncertain_files = self.part4_normal_files

        self.part4_normal_files_val = [
            'scpDown4.pickle',
            'scpDown5.pickle',
            'scpDown6.pickle',
            'scpUp5.pickle',
            'scpUp6.pickle',
            'sftp_up_2.pickle',
            'sftp_up_2b.pickle',
            'sftp_down_3.pickle',
            'sftp_down_3b.pickle',
            'skype_audio2b.pickle',
            'skype_audio3.pickle',
            'skype_audio4.pickle',
            'skype_chat1b.pickle',
            'skype_file6.pickle',
            'skype_file7.pickle',
            'skype_file8.pickle',
            'skype_video2.pickle',
            'skype_video2b.pickle',
            'spotify3.pickle',
            'spotify4.pickle',
            'vimeo3.pickle',
            'vimeo4.pickle',
            'voipbuster4.pickle',
            'voipbuster4b.pickle',
            'youtube5.pickle',
            'youtube6.pickle',
            'AIMchat3.pickle',
            'AIMchat3b.pickle',
            'email2.pickle',
            'email2b.pickle',
            'facebookchat3.pickle',
            'facebook_audio3.pickle',
            'facebook_audio4.pickle',
            'facebook_chat_4b.pickle',
            'facebook_video2.pickle',
            'facebook_video2b.pickle',
            'ftps_down_1b.pickle',
            'ftps_up_2b.pickle',
            'gmailchat3.pickle',
            'hangouts_audio1b.pickle',
            'hangouts_audio2b.pickle',
            'hangouts_chat_4b.pickle',
            'hangouts_video2b.pickle',
            'icq_chat_3b.pickle',
            'netflix3.pickle',
            'netflix4.pickle',
        ]

        self.part4_normal_files_val_certain = []
        self.part4_normal_files_val_uncertain = self.part4_normal_files_val

        # zesus作为未知
        self.part1_attack_files = [
            'botware_1_trickbot_2017-04-12_win5.pickle',
            'botware_1_trickbot_2017-04-17_win14.pickle',
            'botware_1_trickbot_2017-05-15_win15.pickle',

            'botware_4_emotet_2017-06-24_win3.pickle',
            'botware_4_emotet_2017-06-24_win7.pickle',
            'botware_4_emotet_2017-06-24_win8.pickle',

            'ransomware_2_dirdex_2017-15-05_win11.pickle',
            'ransomware_2_dirdex_2018-01-29_win6.pickle',
        ]

        self.part1_attack_files_val = [
            'botware_1_trickbot_2017-06-24_win4.pickle',
            'botware_4_emotet_2017-06-24_win10.pickle',
            'ransomware_2_dridex_2017-04-17_win1.pickle',
        ]

        self.part1_attack_files_val_certain = self.part1_attack_files_val
        self.part1_attack_files_val_uncertain = []

        self.part2_attack_files = [
            'botware_1_trickbot_2017-06-24_win5.pickle',
            'botware_1_trickbot_2017-06-24_win6.pickle',

            'botware_4_emotet_2017-06-24_win15.pickle',
            'botware_4_emotet_2017-06-24_win16.pickle',

            'ransomware_2_dridex_2017-04-18_win20.pickle',
            'ransomware_2_dridex_2017-05-16_win5.pickle',

            'spyware_4_zesus_2013-11-06_capture-win6.pickle',
            'spyware_4_zesus_2014-05-30_capture-win8.pickle',
        ]

        self.part2_attack_certain_files = [
            'botware_1_trickbot_2017-06-24_win5.pickle',
            'botware_1_trickbot_2017-06-24_win6.pickle',

            'botware_4_emotet_2017-06-24_win15.pickle',
            'botware_4_emotet_2017-06-24_win16.pickle',

            'ransomware_2_dridex_2017-04-18_win20.pickle',
            'ransomware_2_dridex_2017-05-16_win5.pickle',
        ]

        self.part2_attack_uncertain_files = [
            'spyware_4_zesus_2013-11-06_capture-win6.pickle',
            'spyware_4_zesus_2014-05-30_capture-win8.pickle',
        ]

        self.part2_attack_files_val = [
            'botware_1_trickbot_2017-06-24_win12.pickle',
            'botware_4_emotet_2017-06-24_win17.pickle',
            'ransomware_2_dridex_2017-04-18_win18.pickle',
            'spyware_4_zesus_2014-06-06_capture-win8.pickle',
        ]

        self.part2_attack_files_val_certain = [
            'botware_1_trickbot_2017-06-24_win12.pickle',
            'botware_4_emotet_2017-06-24_win17.pickle',
            'ransomware_2_dridex_2017-04-18_win18.pickle',
        ]
        self.part2_attack_files_val_uncertain = [
            'spyware_4_zesus_2014-06-06_capture-win8.pickle',
        ]


        self.part3_attack_files = [
            'botware_1_trickbot_2017-3-29_win8.pickle',
            'botware_4_emotet_2017-06-24_win11.pickle',
            'ransomware_2_dridex_2018-04-03_win12.pickle',
            'spyware_4_zesus_2014-12-20_capture-win3.pickle',

            'miner_2_minertrojan_2018-03-27_win4.pickle',
            'ransomware_1_wannacry_2017-05-15_win4.pickle',
            'spyware_1_magic_2017-11-22_win4.pickle',
            'spyware_2_trickster_2017-06-24_win18.pickle',
            'spyware_3_ccleaner_2018-01-30_win17.pickle',
        ]

        self.part3_attack_files_certain = [
            'botware_1_trickbot_2017-3-29_win8.pickle',
            'botware_4_emotet_2017-06-24_win11.pickle',
            'ransomware_2_dridex_2018-04-03_win12.pickle',
        ]

        self.part3_attack_files_uncertain = [
            'spyware_4_zesus_2014-12-20_capture-win3.pickle',

            'miner_2_minertrojan_2018-03-27_win4.pickle',
            'ransomware_1_wannacry_2017-05-15_win4.pickle',
            'spyware_1_magic_2017-11-22_win4.pickle',
            'spyware_2_trickster_2017-06-24_win18.pickle',
            'spyware_3_ccleaner_2018-01-30_win17.pickle',
        ]


        # 使用的是part2val的数据，在每个后面都加了一个2
        self.part4_attack_files = [
            'botware_1_trickbot_2017-06-24_win12_2.pickle',
            'botware_4_emotet_2017-06-24_win17_2.pickle',
            'ransomware_2_dridex_2017-04-18_win18_2.pickle',
            'spyware_4_zesus_2014-06-06_capture-win8_2.pickle',
        ]

        self.part4_attack_certain_files = [
            'botware_1_trickbot_2017-06-24_win12_2.pickle',
            'botware_4_emotet_2017-06-24_win17_2.pickle',
            'ransomware_2_dridex_2017-04-18_win18_2.pickle',
        ]

        self.part4_attack_uncertain_files = [
            'spyware_4_zesus_2014-06-06_capture-win8_2.pickle',
        ]

        # 使用的是part3中前4个文件
        self.part4_attack_files_val = [
            'botware_1_trickbot_2017-3-29_win8_2.pickle',
            'botware_4_emotet_2017-06-24_win11_2.pickle',
            'ransomware_2_dridex_2018-04-03_win12_2.pickle',
            'spyware_4_zesus_2014-12-20_capture-win3_2.pickle',
        ]

        self.part4_attack_files_val_certain = [
            'botware_1_trickbot_2017-3-29_win8_2.pickle',
            'botware_4_emotet_2017-06-24_win11_2.pickle',
            'ransomware_2_dridex_2018-04-03_win12_2.pickle',
        ]

        self.part4_attack_files_val_uncertain = [
            'spyware_4_zesus_2014-12-20_capture-win3_2.pickle',
        ]

        self.my_dict = Mydict()
        self.class_dict = self.my_dict.class_dict
        self.detail_class_dict = self.my_dict.detail_class_dict

        if new_normal_file is not None:
            self.part1_normal_files = [new_normal_file]
            self.class_dict[new_normal_file] = 0
            self.detail_class_dict[new_normal_file] = 0
        if new_attack_file is not None:
            self.part1_attack_files = [new_attack_file]
            self.class_dict[new_attack_file] = 1
            self.detail_class_dict[new_attack_file] = -1


class DatasetConfig2:
    def __init__(self, new_normal_file=None):
        self.part1_normal_files = [
            'traffic_20240311.pickle',
            'traffic_20240312.pickle',
            'traffic_20240313.pickle',
            'traffic_20240314.pickle',
            'traffic_20240315.pickle',
            'traffic_20240318.pickle',
            'traffic_20240319.pickle',
        ]

        self.part1_normal_files_val = [
            'traffic_20240320.pickle',
            'traffic_20240321.pickle',
            'traffic_20240322.pickle',
        ]

        self.part2_normal_files = [
            'traffic_20240325.pickle',
            'traffic_20240326.pickle',
            'traffic_20240327.pickle',
            'traffic_20240328.pickle',
            'traffic_20240329.pickle',
            'traffic_20240401.pickle',
            'traffic_20240402.pickle',
        ]

        self.part2_normal_files_val = [
            'traffic_20240403.pickle',
            'traffic_20240407.pickle',
            'traffic_20240408.pickle',
        ]

        self.part3_normal_files = [
            'traffic_20240411.pickle',
            'traffic_20240412.pickle',
            'traffic_20240415.pickle',
            'traffic_20240416.pickle',
            'traffic_20240417.pickle',
            'traffic_20240418.pickle',
            'traffic_20240419.pickle',
        ]

        self.part4_normal_files = [
            # scp
            'scp1.pickle',
            'scpDown1.pickle',
            'scpDown2.pickle',
            'scpDown3.pickle',
            'scpUp1.pickle',
            'scpUp2.pickle',
            'scpUp3.pickle',
            # sftp
            'sftp1.pickle',
            'sftpUp1.pickle',
            'sftpDown1.pickle',
            'sftpDown2.pickle',
            # skype audio
            'skype_audio1.pickle',
            'skype_audio1b.pcapng.pickle',
            'skype_audio2.pickle',
            # skype chat
            'skype_chat1.pickle',
            # skype file
            'skype_file1.pickle',
            'skype_file2.pickle',
            'skype_file3.pickle',
            'skype_file4.pickle',
            'skype_file5.pickle',
            # skype video
            'skype_video1.pickle',
            'skype_video1b.pickle',
            # spotify
            'spotify1.pickle',
            'spotify2.pickle',
            # vimeo
            'vimeo1.pickle',
            'vimeo2.pickle',
            # voipbuster
            'voipbuster1b.pickle',
            'voipbuster2b.pickle',
            'voipbuster3b.pickle',
            # yotube
            'youtube1.pickle',
            'youtube2.pickle',
            'youtube3.pickle',
            'youtube4.pickle',
            # aim chat
            'AIMchat1.pickle',
            'AIMchat2.pickle',
            # email
            'email1.pickle',
            'email1b.pickle',
            # facebook chat
            'facebookchat1.pickle',
            'facebookchat2.pickle',
            # facebook audio
            'facebook_audio1.pickle',
            'facebook_audio1b.pickle',
            'facebook_audio2.pickle',
            'facebook_audio2b.pickle',
            # facebook chat
            'facebook_chat_4.pickle',
            # facebook video
            'facebook_video1.pickle',
            'facebook_video1b.pickle',
            # ftp
            'ftps_down_1.pickle',
            'ftps_up_2.pickle',
            # gmail chat
            'gmailchat1.pickle',
            'gmailchat2.pickle',
            # hangouts audio
            'hangouts_audio1.pickle',
            'hangouts_audio2.pickle',
            'hangouts_audio3.pickle',
            'hangouts_audio4.pickle',
            # hangout chat
            'hangouts_chat_4.pickle',
            # hangout video
            'hangouts_video1b.pickle',
            'hangouts_video2.pickle',
            # icq chat
            'icq_chat_1.pickle',
            'icq_chat_2.pickle',
            'icq_chat_3.pickle',
            # netflix
            'netflix1.pickle',
            'netflix2.pickle',
        ]

        self.part4_normal_files_val = [
            'scpDown4.pickle',
            'scpDown5.pickle',
            'scpDown6.pickle',
            'scpUp5.pickle',
            'scpUp6.pickle',
            'sftp_up_2.pickle',
            'sftp_up_2b.pickle',
            'sftp_down_3.pickle',
            'sftp_down_3b.pickle',
            'skype_audio2b.pickle',
            'skype_audio3.pickle',
            'skype_audio4.pickle',
            'skype_chat1b.pickle',
            'skype_file6.pickle',
            'skype_file7.pickle',
            'skype_file8.pickle',
            'skype_video2.pickle',
            'skype_video2b.pickle',
            'spotify3.pickle',
            'spotify4.pickle',
            'vimeo3.pickle',
            'vimeo4.pickle',
            'voipbuster4.pickle',
            'voipbuster4b.pickle',
            'youtube5.pickle',
            'youtube6.pickle',
            'AIMchat3.pickle',
            'AIMchat3b.pickle',
            'email2.pickle',
            'email2b.pickle',
            'facebookchat3.pickle',
            'facebook_audio3.pickle',
            'facebook_audio4.pickle',
            'facebook_chat_4b.pickle',
            'facebook_video2.pickle',
            'facebook_video2b.pickle',
            'ftps_down_1b.pickle',
            'ftps_up_2b.pickle',
            'gmailchat3.pickle',
            'hangouts_audio1b.pickle',
            'hangouts_audio2b.pickle',
            'hangouts_chat_4b.pickle',
            'hangouts_video2b.pickle',
            'icq_chat_3b.pickle',
            'netflix3.pickle',
            'netflix4.pickle',
        ]

        # dridex作为未知
        self.part1_attack_files = [
            'botware_1_trickbot_2017-04-12_win5.pickle',
            'botware_1_trickbot_2017-04-17_win14.pickle',
            'botware_1_trickbot_2017-05-15_win15.pickle',

            'botware_4_emotet_2017-06-24_win3.pickle',
            'botware_4_emotet_2017-06-24_win7.pickle',
            'botware_4_emotet_2017-06-24_win8.pickle',

            'spyware_4_zesus_2013-11-06_capture-win6.pickle',
            'spyware_4_zesus_2014-05-30_capture-win8.pickle',
            'spyware_4_zesus_2014-06-06_capture-win8.pickle',
        ]

        self.part1_attack_files_val = [
            'botware_1_trickbot_2017-06-24_win4.pickle',
            'botware_4_emotet_2017-06-24_win10.pickle',
            'spyware_4_zesus_2014-12-20_capture-win3.pickle',
        ]

        self.part2_attack_files = [
            'botware_1_trickbot_2017-06-24_win5.pickle',
            'botware_1_trickbot_2017-06-24_win6.pickle',

            'botware_4_emotet_2017-06-24_win11.pickle',
            'botware_4_emotet_2017-06-24_win15.pickle',

            'ransomware_2_dridex_2017-04-18_win20.pickle',
            'ransomware_2_dridex_2017-05-16_win5.pickle',
        ]

        self.part2_attack_files_val = [
            'botware_1_trickbot_2017-06-24_win12.pickle',
            'botware_4_emotet_2017-06-24_win16.pickle',
            'ransomware_2_dirdex_2017-15-05_win11.pickle',
        ]

        self.part3_attack_files = [
            'botware_1_trickbot_2017-3-29_win8.pickle',
            'botware_4_emotet_2017-06-24_win17.pickle',
            'ransomware_2_dridex_2018-04-03_win12.pickle',

            'miner_2_minertrojan_2018-03-27_win4.pickle',
            'ransomware_1_wannacry_2017-05-15_win4.pickle',
            'spyware_1_magic_2017-11-22_win4.pickle',
            'spyware_2_trickster_2017-06-24_win18.pickle',
            'spyware_3_ccleaner_2018-01-30_win17.pickle',
        ]

        # part2val
        self.part4_attack_files = [
            'botware_1_trickbot_2017-06-24_win12_2.pickle',
            'botware_4_emotet_2017-06-24_win16_2.pickle',
            'ransomware_2_dirdex_2017-15-05_win11_2.pickle',
        ]

        # part3前面的数据
        self.part4_attack_files_val = [
            'botware_1_trickbot_2017-3-29_win8_2.pickle',
            'botware_4_emotet_2017-06-24_win17_2.pickle',
            'ransomware_2_dridex_2018-04-03_win12_2.pickle',
        ]

        self.my_dict = Mydict()
        self.class_dict = self.my_dict.class_dict
        self.detail_class_dict = self.my_dict.detail_class_dict

        if new_normal_file is not None:
            self.part1_normal_files = [new_normal_file]
            self.class_dict[new_normal_file] = 0
            self.detail_class_dict[new_normal_file] = 0


class DatasetConfig3:
    def __init__(self, new_normal_file=None):
        self.part1_normal_files = [
            'traffic_20240311.pickle',
            'traffic_20240312.pickle',
            'traffic_20240313.pickle',
            'traffic_20240314.pickle',
            'traffic_20240315.pickle',
            'traffic_20240318.pickle',
            'traffic_20240319.pickle',
        ]

        self.part1_normal_files_val = [
            'traffic_20240320.pickle',
            'traffic_20240321.pickle',
            'traffic_20240322.pickle',
        ]

        self.part2_normal_files = [
            'traffic_20240325.pickle',
            'traffic_20240326.pickle',
            'traffic_20240327.pickle',
            'traffic_20240328.pickle',
            'traffic_20240329.pickle',
            'traffic_20240401.pickle',
            'traffic_20240402.pickle',
        ]

        self.part2_normal_files_val = [
            'traffic_20240403.pickle',
            'traffic_20240407.pickle',
            'traffic_20240408.pickle',
        ]

        self.part3_normal_files = [
            'traffic_20240411.pickle',
            'traffic_20240412.pickle',
            'traffic_20240415.pickle',
            'traffic_20240416.pickle',
            'traffic_20240417.pickle',
            'traffic_20240418.pickle',
            'traffic_20240419.pickle',
        ]

        self.part4_normal_files = [
            # scp
            'scp1.pickle',
            'scpDown1.pickle',
            'scpDown2.pickle',
            'scpDown3.pickle',
            'scpUp1.pickle',
            'scpUp2.pickle',
            'scpUp3.pickle',
            # sftp
            'sftp1.pickle',
            'sftpUp1.pickle',
            'sftpDown1.pickle',
            'sftpDown2.pickle',
            # skype audio
            'skype_audio1.pickle',
            'skype_audio1b.pcapng.pickle',
            'skype_audio2.pickle',
            # skype chat
            'skype_chat1.pickle',
            # skype file
            'skype_file1.pickle',
            'skype_file2.pickle',
            'skype_file3.pickle',
            'skype_file4.pickle',
            'skype_file5.pickle',
            # skype video
            'skype_video1.pickle',
            'skype_video1b.pickle',
            # spotify
            'spotify1.pickle',
            'spotify2.pickle',
            # vimeo
            'vimeo1.pickle',
            'vimeo2.pickle',
            # voipbuster
            'voipbuster1b.pickle',
            'voipbuster2b.pickle',
            'voipbuster3b.pickle',
            # yotube
            'youtube1.pickle',
            'youtube2.pickle',
            'youtube3.pickle',
            'youtube4.pickle',
            # aim chat
            'AIMchat1.pickle',
            'AIMchat2.pickle',
            # email
            'email1.pickle',
            'email1b.pickle',
            # facebook chat
            'facebookchat1.pickle',
            'facebookchat2.pickle',
            # facebook audio
            'facebook_audio1.pickle',
            'facebook_audio1b.pickle',
            'facebook_audio2.pickle',
            'facebook_audio2b.pickle',
            # facebook chat
            'facebook_chat_4.pickle',
            # facebook video
            'facebook_video1.pickle',
            'facebook_video1b.pickle',
            # ftp
            'ftps_down_1.pickle',
            'ftps_up_2.pickle',
            # gmail chat
            'gmailchat1.pickle',
            'gmailchat2.pickle',
            # hangouts audio
            'hangouts_audio1.pickle',
            'hangouts_audio2.pickle',
            'hangouts_audio3.pickle',
            'hangouts_audio4.pickle',
            # hangout chat
            'hangouts_chat_4.pickle',
            # hangout video
            'hangouts_video1b.pickle',
            'hangouts_video2.pickle',
            # icq chat
            'icq_chat_1.pickle',
            'icq_chat_2.pickle',
            'icq_chat_3.pickle',
            # netflix
            'netflix1.pickle',
            'netflix2.pickle',
        ]

        self.part4_normal_files_val = [
            'scpDown4.pickle',
            'scpDown5.pickle',
            'scpDown6.pickle',
            'scpUp5.pickle',
            'scpUp6.pickle',
            'sftp_up_2.pickle',
            'sftp_up_2b.pickle',
            'sftp_down_3.pickle',
            'sftp_down_3b.pickle',
            'skype_audio2b.pickle',
            'skype_audio3.pickle',
            'skype_audio4.pickle',
            'skype_chat1b.pickle',
            'skype_file6.pickle',
            'skype_file7.pickle',
            'skype_file8.pickle',
            'skype_video2.pickle',
            'skype_video2b.pickle',
            'spotify3.pickle',
            'spotify4.pickle',
            'vimeo3.pickle',
            'vimeo4.pickle',
            'voipbuster4.pickle',
            'voipbuster4b.pickle',
            'youtube5.pickle',
            'youtube6.pickle',
            'AIMchat3.pickle',
            'AIMchat3b.pickle',
            'email2.pickle',
            'email2b.pickle',
            'facebookchat3.pickle',
            'facebook_audio3.pickle',
            'facebook_audio4.pickle',
            'facebook_chat_4b.pickle',
            'facebook_video2.pickle',
            'facebook_video2b.pickle',
            'ftps_down_1b.pickle',
            'ftps_up_2b.pickle',
            'gmailchat3.pickle',
            'hangouts_audio1b.pickle',
            'hangouts_audio2b.pickle',
            'hangouts_chat_4b.pickle',
            'hangouts_video2b.pickle',
            'icq_chat_3b.pickle',
            'netflix3.pickle',
            'netflix4.pickle',
        ]

        # trickbot作为未知
        self.part1_attack_files = [
            'botware_4_emotet_2017-06-24_win3.pickle',
            'botware_4_emotet_2017-06-24_win7.pickle',
            'botware_4_emotet_2017-06-24_win8.pickle',

            'ransomware_2_dirdex_2017-15-05_win11.pickle',
            'ransomware_2_dirdex_2018-01-29_win6.pickle',

            'spyware_4_zesus_2013-11-06_capture-win6.pickle',
            'spyware_4_zesus_2014-05-30_capture-win8.pickle',
            'spyware_4_zesus_2014-06-06_capture-win8.pickle',
        ]

        self.part1_attack_files_val = [
            'botware_4_emotet_2017-06-24_win10.pickle',
            'ransomware_2_dridex_2017-04-17_win1.pickle',
            'spyware_4_zesus_2014-12-20_capture-win3.pickle',
        ]

        self.part2_attack_files = [
            'botware_1_trickbot_2017-06-24_win5.pickle',
            'botware_1_trickbot_2017-06-24_win6.pickle',

            'botware_4_emotet_2017-06-24_win11.pickle',
            'botware_4_emotet_2017-06-24_win15.pickle',

            'ransomware_2_dridex_2017-04-18_win20.pickle',
            'ransomware_2_dridex_2017-05-16_win5.pickle',
        ]

        self.part2_attack_files_val = [
            'botware_1_trickbot_2017-06-24_win12.pickle',
            'botware_4_emotet_2017-06-24_win16.pickle',
            'ransomware_2_dridex_2017-04-18_win18.pickle',
        ]

        self.part3_attack_files = [
            'botware_1_trickbot_2017-3-29_win8.pickle',
            'botware_4_emotet_2017-06-24_win17.pickle',
            'ransomware_2_dridex_2018-04-03_win12.pickle',

            'miner_2_minertrojan_2018-03-27_win4.pickle',
            'ransomware_1_wannacry_2017-05-15_win4.pickle',
            'spyware_1_magic_2017-11-22_win4.pickle',
            'spyware_2_trickster_2017-06-24_win18.pickle',
            'spyware_3_ccleaner_2018-01-30_win17.pickle',
        ]

        self.part4_attack_files = [
            'botware_1_trickbot_2017-06-24_win12_2.pickle',
            'botware_4_emotet_2017-06-24_win16_2.pickle',
            'ransomware_2_dridex_2017-04-18_win18_2.pickle',
        ]

        self.part4_attack_files_val = [
            'botware_1_trickbot_2017-3-29_win8_2.pickle',
            'botware_4_emotet_2017-06-24_win17_2.pickle',
            'ransomware_2_dridex_2018-04-03_win12_2.pickle',
        ]

        self.my_dict = Mydict()
        self.class_dict = self.my_dict.class_dict
        self.detail_class_dict = self.my_dict.detail_class_dict

        if new_normal_file is not None:
            self.part1_normal_files = [new_normal_file]
            self.class_dict[new_normal_file] = 0
            self.detail_class_dict[new_normal_file] = 0


class DatasetConfig4:
    def __init__(self, new_normal_file=None, new_attack_file=None):
        self.part1_normal_files = [
            'traffic_20240311.pickle',
            'traffic_20240312.pickle',
            'traffic_20240313.pickle',
            'traffic_20240314.pickle',
            'traffic_20240315.pickle',
            'traffic_20240318.pickle',
            'traffic_20240319.pickle',
        ]

        self.part1_normal_files_val = [
            'traffic_20240320.pickle',
            'traffic_20240321.pickle',
            'traffic_20240322.pickle',
        ]

        self.part2_normal_files = [
            'traffic_20240325.pickle',
            'traffic_20240326.pickle',
            'traffic_20240327.pickle',
            'traffic_20240328.pickle',
            'traffic_20240329.pickle',
            'traffic_20240401.pickle',
            'traffic_20240402.pickle',
        ]

        self.part2_normal_files_val = [
            'traffic_20240403.pickle',
            'traffic_20240407.pickle',
            'traffic_20240408.pickle',
        ]

        self.part3_normal_files = [
            'traffic_20240411.pickle',
            'traffic_20240412.pickle',
            'traffic_20240415.pickle',
            'traffic_20240416.pickle',
            'traffic_20240417.pickle',
            'traffic_20240418.pickle',
            'traffic_20240419.pickle',
        ]

        self.part4_normal_files = [
            # scp
            'scp1.pickle',
            'scpDown1.pickle',
            'scpDown2.pickle',
            'scpDown3.pickle',
            'scpUp1.pickle',
            'scpUp2.pickle',
            'scpUp3.pickle',
            # sftp
            'sftp1.pickle',
            'sftpUp1.pickle',
            'sftpDown1.pickle',
            'sftpDown2.pickle',
            # skype audio
            'skype_audio1.pickle',
            'skype_audio1b.pcapng.pickle',
            'skype_audio2.pickle',
            # skype chat
            'skype_chat1.pickle',
            # skype file
            'skype_file1.pickle',
            'skype_file2.pickle',
            'skype_file3.pickle',
            'skype_file4.pickle',
            'skype_file5.pickle',
            # skype video
            'skype_video1.pickle',
            'skype_video1b.pickle',
            # spotify
            'spotify1.pickle',
            'spotify2.pickle',
            # vimeo
            'vimeo1.pickle',
            'vimeo2.pickle',
            # voipbuster
            'voipbuster1b.pickle',
            'voipbuster2b.pickle',
            'voipbuster3b.pickle',
            # yotube
            'youtube1.pickle',
            'youtube2.pickle',
            'youtube3.pickle',
            'youtube4.pickle',
            # aim chat
            'AIMchat1.pickle',
            'AIMchat2.pickle',
            # email
            'email1.pickle',
            'email1b.pickle',
            # facebook chat
            'facebookchat1.pickle',
            'facebookchat2.pickle',
            # facebook audio
            'facebook_audio1.pickle',
            'facebook_audio1b.pickle',
            'facebook_audio2.pickle',
            'facebook_audio2b.pickle',
            # facebook chat
            'facebook_chat_4.pickle',
            # facebook video
            'facebook_video1.pickle',
            'facebook_video1b.pickle',
            # ftp
            'ftps_down_1.pickle',
            'ftps_up_2.pickle',
            # gmail chat
            'gmailchat1.pickle',
            'gmailchat2.pickle',
            # hangouts audio
            'hangouts_audio1.pickle',
            'hangouts_audio2.pickle',
            'hangouts_audio3.pickle',
            'hangouts_audio4.pickle',
            # hangout chat
            'hangouts_chat_4.pickle',
            # hangout video
            'hangouts_video1b.pickle',
            'hangouts_video2.pickle',
            # icq chat
            'icq_chat_1.pickle',
            'icq_chat_2.pickle',
            'icq_chat_3.pickle',
            # netflix
            'netflix1.pickle',
            'netflix2.pickle',
        ]

        self.part4_normal_files_val = [
            'scpDown4.pickle',
            'scpDown5.pickle',
            'scpDown6.pickle',
            'scpUp5.pickle',
            'scpUp6.pickle',
            'sftp_up_2.pickle',
            'sftp_up_2b.pickle',
            'sftp_down_3.pickle',
            'sftp_down_3b.pickle',
            'skype_audio2b.pickle',
            'skype_audio3.pickle',
            'skype_audio4.pickle',
            'skype_chat1b.pickle',
            'skype_file6.pickle',
            'skype_file7.pickle',
            'skype_file8.pickle',
            'skype_video2.pickle',
            'skype_video2b.pickle',
            'spotify3.pickle',
            'spotify4.pickle',
            'vimeo3.pickle',
            'vimeo4.pickle',
            'voipbuster4.pickle',
            'voipbuster4b.pickle',
            'youtube5.pickle',
            'youtube6.pickle',
            'AIMchat3.pickle',
            'AIMchat3b.pickle',
            'email2.pickle',
            'email2b.pickle',
            'facebookchat3.pickle',
            'facebook_audio3.pickle',
            'facebook_audio4.pickle',
            'facebook_chat_4b.pickle',
            'facebook_video2.pickle',
            'facebook_video2b.pickle',
            'ftps_down_1b.pickle',
            'ftps_up_2b.pickle',
            'gmailchat3.pickle',
            'hangouts_audio1b.pickle',
            'hangouts_audio2b.pickle',
            'hangouts_chat_4b.pickle',
            'hangouts_video2b.pickle',
            'icq_chat_3b.pickle',
            'netflix3.pickle',
            'netflix4.pickle',
        ]

        # emotet作为未知
        self.part1_attack_files = [
            'botware_1_trickbot_2017-04-12_win5.pickle',
            'botware_1_trickbot_2017-04-17_win14.pickle',
            'botware_1_trickbot_2017-05-15_win15.pickle',

            'ransomware_2_dirdex_2017-15-05_win11.pickle',
            'ransomware_2_dirdex_2018-01-29_win6.pickle',

            'spyware_4_zesus_2013-11-06_capture-win6.pickle',
            'spyware_4_zesus_2014-05-30_capture-win8.pickle',
            'spyware_4_zesus_2014-06-06_capture-win8.pickle',
        ]

        self.part1_attack_files_val = [
            'botware_1_trickbot_2017-06-24_win4.pickle',
            'ransomware_2_dridex_2017-04-17_win1.pickle',
            'spyware_4_zesus_2014-12-20_capture-win3.pickle',
        ]

        self.part2_attack_files = [
            'botware_1_trickbot_2017-06-24_win5.pickle',
            'botware_1_trickbot_2017-06-24_win6.pickle',

            'botware_4_emotet_2017-06-24_win11.pickle',
            'botware_4_emotet_2017-06-24_win15.pickle',

            'ransomware_2_dridex_2017-04-18_win20.pickle',
            'ransomware_2_dridex_2017-05-16_win5.pickle',
        ]

        self.part2_attack_files_val = [
            'botware_1_trickbot_2017-06-24_win12.pickle',
            'botware_4_emotet_2017-06-24_win16.pickle',
            'ransomware_2_dridex_2017-04-18_win18.pickle',
        ]

        self.part3_attack_files = [
            'botware_1_trickbot_2017-3-29_win8.pickle',
            'botware_4_emotet_2017-06-24_win17.pickle',
            'ransomware_2_dridex_2018-04-03_win12.pickle',

            'miner_2_minertrojan_2018-03-27_win4.pickle',
            'ransomware_1_wannacry_2017-05-15_win4.pickle',
            'spyware_1_magic_2017-11-22_win4.pickle',
            'spyware_2_trickster_2017-06-24_win18.pickle',
            'spyware_3_ccleaner_2018-01-30_win17.pickle',
        ]

        self.part4_attack_files = [
            'botware_1_trickbot_2017-06-24_win12_2.pickle',
            'botware_4_emotet_2017-06-24_win16_2.pickle',
            'ransomware_2_dridex_2017-04-18_win18_2.pickle',
        ]

        self.part4_attack_files_val = [
            'botware_1_trickbot_2017-3-29_win8_2.pickle',
            'botware_4_emotet_2017-06-24_win17_2.pickle',
            'ransomware_2_dridex_2018-04-03_win12_2.pickle',
        ]

        self.my_dict = Mydict()
        self.class_dict = self.my_dict.class_dict
        self.detail_class_dict = self.my_dict.detail_class_dict

        if new_normal_file is not None:
            self.part1_normal_files = [new_normal_file]
            self.class_dict[new_normal_file] = 0
            self.detail_class_dict[new_normal_file] = 0
        if new_attack_file is not None:
            self.part1_attack_files = [new_attack_file]
            self.class_dict[new_attack_file] = 1
            self.detail_class_dict[new_attack_file] = -1
