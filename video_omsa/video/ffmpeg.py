#!/usr/bin/env python
# -*- coding:utf8 -*-
# __author__ 史怡国
# __date__ 201709

import MySQLdb as mdb
import sys, os, time, commands, hashlib, logging, random, shutil
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from Crypto import Random
import types,json

reload(sys)
sys.setdefaultencoding('utf8')


class Aes(object):
    """
        aes 加密类指定iv和key
    """

    def __init__(self):
        self.iv = '5efd3f6060e20330'
        self.key = '049053296491e492'
        self.mode = AES.MODE_CBC
        # self.BS = AES.block_size
        self.BS = 16
        # self.pad = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
        self.pad = lambda s: s + (self.BS - len(s) % self.BS) * chr(0)
        # self.unpad = lambda s : s[0:-ord(s[-1])]
        self.unpad = lambda s: s[0:-ord(s[-1])]

    def encrypt(self, text):
        text = self.pad(text)
        self.obj1 = AES.new(self.key, self.mode, self.iv)
        self.ciphertext = self.obj1.encrypt(text)
        return self.ciphertext

    def decrypt(self, text):
        self.obj2 = AES.new(self.key, self.mode, self.iv)
        plain_text = self.obj2.decrypt(text)
        return self.unpad(plain_text.rstrip('\0'))

    # # 构造器
    # def __init__(self):
    #     self.iv = '5efd3f6060e20330'
    #     self.key = '049053296491e492'
    #
    # # 解密函数
    # def decryption_file(self, fs):
    #     cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
    #     # if fs is a multiple of 16
    #     x = len(fs) % 16
    #     if x != 0:
    #         fs_pad = fs + '0' * (16 - x)  # It shoud be 16-x not
    #     else:
    #         fs_pad = fs
    #     msg = cipher.decrypt(fs_pad)
    #     return msg
    #
    # # 加密函数
    # def AES_File(self, fs):
    #     cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
    #     x = len(fs) % 16
    #     if x != 0:
    #         fs_pad = fs + '0' * (16 - x)  # It shoud be 16-x not
    #     else:
    #         fs_pad = fs
    #     msg = cipher.encrypt(fs_pad)
    #     return msg

    # 文件加密测试
    def file_encryption(self, srcfilePath, destfilePath):
        fs = open(srcfilePath, 'rb')
        fs_msg = fs.read()
        fs.close()
        fc = open(destfilePath, 'wb')
        fc_msg = self.encrypt(fs_msg)
        fc.writelines(fc_msg)
        fc.close()

    # 文件解密测试
    def file_decryption(self, aesfilePath):
        fs = open(aesfilePath, 'rb')
        fs_msg = fs.read()
        fs.close()
        str = self.decrypt(fs_msg)
        return str


class ffmpeg(object):
    """
        根据shell版本封装成的一个python版本的ffmpeg工具类
    """

    # 传入一个服务器储存路径名称,根据这个名称生成对应的config配置
    def __init__(self, task_id, video_id, server_full_save_path):
        self.task_id = task_id
        self.video_id = video_id
        filename = '/'.join(server_full_save_path.replace('//', '/').split('/')[:-1])
        mp4_root_path = '/data/original/'
        # 当前日期
        self.date = time.strftime('%Y_%m_%d', time.localtime(time.time()))
        # 随机字符串文件名称
        self.t_filename = self.get_random_str(16)
        # 随机字符串
        self.t_random_p = self.get_random_str(8)
        self.mp4Name = server_full_save_path.replace('//', '/').split('/')[-1]
        # 切片缓存位置
        self.tmp_path = '/data/fs_convert/new/' + self.mp4Name + os.sep + self.date + os.sep
        # 切片临时mp4文件
        self.tmp_file = self.tmp_path + 'tmp_' + self.mp4Name
        # 服务器存储绝对路劲
        self.media_path = filename
        # 图片切片位置存放地址
        self.thumb_path = '/data/hls/thumb/new/' + self.mp4Name + os.sep + self.date + os.sep
        self.thumb_url = self.thumb_path + self.get_random_str(16) + '.jpg'
        # 视频分辨率(含图片分辨率)
        self.resolution = '720x406'
        # 加密串
        self.key = ' 000102030405060708090a0b0c0d0e0f'
        # 视频章节缩写
        self.s_chapterName = '_'.join(self.media_path.split('/')[2:-1])
        # 日志文件存储路劲
        self.log_path = '/data/ffmpeg_logs' + os.sep + self.s_chapterName + os.sep + self.mp4Name + os.sep + self.date + os.sep
        # 日志文件名称
        self.Log = self.log_path + self.t_filename + '_sql.log'
        # 错误日志
        self.error_Log = self.log_path + self.t_filename + '_error.log'
        # 视频时长G
        self.duration = '0'
        # 视频大小
        self.file_size = '0'
        # ts最终存放路劲
        self.out_put_pre_path = '/data/hls/new/'
        # m3u8 服务器存储地址
        self.m3u8_serverPath = self.out_put_pre_path + self.s_chapterName + os.sep + self.mp4Name + os.sep + self.date + os.sep + self.t_filename + ".m3u8"
        # m3u8_aes 服务器存储地址
        self.aes_m3u8_serverPath = self.out_put_pre_path + self.s_chapterName + os.sep + "aes_" + self.mp4Name + os.sep + self.date + os.sep + self.t_filename + "_aes.m3u8"
        # m3u8 web地址
        self.m3u8_webUrl = self.m3u8_serverPath.replace('/data/hls/', 'http://m1.letiku.net/')
        # aes_m3u8 web地址
        self.aes_m3u8_webUrl = self.aes_m3u8_serverPath.replace('/data/hls/', 'http://m1.letiku.net/')
        # self ts path name
        self.ts_path_name = os.path.dirname(self.m3u8_serverPath.replace('.m3u8', '.ts'))
        # hls path
        self.hlsPath = self.ts_path_name + os.sep

    # md5 一个‘纳秒级别的’ 随机字符串可以指定其位数
    def get_random_str(self, num_position):
        str1 = repr(time.time()) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))
        m = hashlib.md5()
        m.update(str1)
        res = m.hexdigest()
        return res[0:num_position]

    # 检查object中所有path,并生成相应的路劲
    def check_path(self):
        for name, path in vars(self).items():
            if 'path' in name or 'log' in name:
                if not os.path.exists(path):
                    os.makedirs(path)

    # 日志记录
    def logging_cut(self, mess):
        print mess
        self.recoder_to_file(mess)

    # 转码并生成临时文件
    # 同尺寸的也得转码，否则会出错，可能与视频格式有关
    def convert(self):
        if not os.path.exists(self.tmp_file):
            cmd = 'ffmpeg -i ' + self.media_path + os.sep + self.mp4Name + ' -s ' + self.resolution + ' ' + self.tmp_file + ' &>/dev/null'
            self.logging_cut('开始给' + self.mp4Name + '转码并生成临时文件')
            print cmd
            rs = commands.getstatusoutput(cmd)
            return rs
        else:
            self.logging_cut("临时文件已经存在，跳过转码")
            return (0, 'ok')

    # 生成略缩图
    def cut_thumb(self):
        cmd = 'ffmpeg -i ' + self.tmp_file + ' -y -f mjpeg -ss 3 -t 0.001 -s 720x406 ' + self.thumb_url + ' &>/dev/null'
        self.logging_cut('开始给' + self.mp4Name + '生成缩略图')
        print cmd
        rs = commands.getstatusoutput(cmd)
        return rs

    # 获取视频时长
    def get_duration(self):
        self.logging_cut("开始获取视频时长")
        cmd = "ffmpeg -i " + self.tmp_file + " 2>&1 | awk -F ':' '$1~/Duration/{print $2 * 3600 + $3*60 + $4;}'"
        print cmd
        rs = commands.getstatusoutput(cmd)
        self.duration = float(rs[1]) - 10.00
        self.logging_cut("视频时长为" + str(self.duration) + "s")
        return rs

    # 生成ts
    def cut_to_ts(self):
        cmd = "ffmpeg -y -i " + self.tmp_file + " -f mpegts -c:v copy -c:a copy  -vbsf h264_mp4toannexb " + self.hlsPath + self.t_filename + ".ts &>/dev/null"
        self.logging_cut("开始生成切片..")
        print cmd
        rs = commands.getstatusoutput(cmd)
        return rs

    # 切片
    def cut(self):
        self.logging_cut("开始生成m3u8:  " + self.m3u8_serverPath)
        print self.m3u8_webUrl
        cmd = "segmenter -y -i " + self.hlsPath + self.t_filename + ".ts -d 30 -p " + self.hlsPath + self.t_filename + " -m " + self.hlsPath + self.t_filename + ".m3u8 -u " + self.m3u8_webUrl + "  &>/dev/null"
        print cmd
        rs = commands.getstatusoutput(cmd)
        return rs

    # 修改m3u8文件中的ts地址
    def modify_ts_url(self):
        print "正在修改" + self.m3u8_serverPath + "ts url地址"
        cmd = "sed -ri 's/" + (self.m3u8_webUrl + '/data/hls/').replace('/', '\/').replace('.',
                                                                                           '\.') + "/http:\/\/m1\.letiku\.net\//g" + "' " + self.m3u8_serverPath
        print cmd
        rs = commands.getstatusoutput(cmd)
        return rs

    # 修改aes m3u8文件中的ts地址
    def modify_aes_ts_url(self):
        print "正在修改" + self.aes_m3u8_serverPath + "ts url地址"
        cmd = "sed -ri 's/" + self.mp4Name + "/aes_" + self.mp4Name + "/g' " + self.aes_m3u8_serverPath
        print cmd
        rs = commands.getstatusoutput(cmd)
        return rs

    # 获取切片大小
    def get_file_size(self):
        self.logging_cut("正在获取视频大小")
        cmd = "du -sh " + os.path.dirname(self.m3u8_serverPath) + " |awk '{print $1}'"
        self.file_size = commands.getstatusoutput(cmd)[1]
        self.logging_cut("视频大小为:" + self.file_size)

    # COPY切片并加密
    def aes_video(self):
        tsFiles = self.getAllTsFiles()
        for ts in tsFiles:
            aes_ts_path = os.path.dirname(self.aes_m3u8_serverPath)
            if not os.path.exists(aes_ts_path):
                os.makedirs(aes_ts_path)
            aes_ts = aes_ts_path + os.sep + ts.split('/')[-1]
            aes = Aes()
            aes.file_encryption(ts, aes_ts)
            # aes.file_decryption(aesfile)
            shutil.copy(self.m3u8_serverPath, self.aes_m3u8_serverPath)

    # 获取未加密版本所有ts文件
    def getAllTsFiles(self):
        ts_parent_dir = os.path.dirname(self.m3u8_serverPath) + os.sep
        tsFiles = [ts_parent_dir + file for file in os.listdir(ts_parent_dir) if '.ts' in file.split('/')[-1]]
        return tsFiles

    # 获取未加密版本所有ts文件
    def getAllaesTsFiles(self):
        aes_ts_parent_dir = os.path.dirname(self.aes_m3u8_serverPath) + os.sep
        tsFiles = [aes_ts_parent_dir + file for file in os.listdir(aes_ts_parent_dir) if '.ts' in file.split('/')[-1]]
        return tsFiles

    # 将结构记录到数据库
    def recoder_to_db(self, mess=''):
        message = ''
        if type(mess) is types.TupleType:
            message = mess[1]
        if type(mess) is types.StringType:
            message = mess
        try:
            db_conn = mdb.connect('localhost', 'root', 'yjy_video@123', 'django_video')
            cursor = db_conn.cursor()
            sql = "insert into `django_video`.`mp4_cut_recoder`(`task_id`,`video_id`,`thumb_url`,`resolution`,`duration`,`log`,`error_log`,`m3u8_serverPath`,`aes_m3u8_serverPath`,`m3u8_webUrl`,`aes_m3u8_webUrl`,`file_size`) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (self.task_id, self.video_id, self.thumb_url, self.resolution, self.duration, self.Log, message,self.m3u8_serverPath, self.aes_m3u8_serverPath, self.m3u8_webUrl, self.aes_m3u8_webUrl, self.file_size)
            self.logging_cut(sql)
            cursor.execute(sql)
            rs = cursor.fetchall()
            db_conn.commit()
            return rs

        except mdb.Error, e:
            print e

            # 将结构记录到日志文件

    def recoder_to_file(self, mess):
        with open(self.Log, 'ab+') as f:
            # for name, value in vars(self).items():
            #     f.write(str(name) + " = " + str(value))
            #     f.write('\n')
            f.write(mess)

    def change_mp4_cutStatus(self):
        try:
            db_conn = mdb.connect('localhost', 'root', 'yjy_video@123', 'django_video')
            cursor = db_conn.cursor()
            sql = "update yjy_mp4 set `cut_staus`='3' where id='%s'"%(self.video_id)
            self.logging_cut("正在修改视频MP4状态3"+sql)
            cursor.execute(sql)
            rs = cursor.fetchall()
            db_conn.commit()
            return rs
        except Exception,e:
            self.logging_cut(e)
            return e

    # 预热到cdn(暂未实现)
    def push_to_cdn(self):
        aes_ts_files = getAllaesTsFiles()
        ts_files = getAllTsFiles()
        Allts = ts_files.extends(aes_ts_files)
        for ts in Allts:
            url = ts.replace('/data/hls/', 'http://m1.letiku.net/')  # 开始切片

    # 主入口
    def start_cut(self):
        self.check_path()
        c_status = self.convert()
        if c_status[0] == 0:
            t_status = self.cut_thumb()
            self.logging_cut("缩略图生成ok!")
            if t_status[0] == 0:
                d_status = self.get_duration()
                if d_status[0] == 0:
                    ts_status = self.cut_to_ts()
                    if ts_status[0] == 0:
                        cut_status = self.cut()
                        if cut_status[0] == 0:
                            self.modify_ts_url()
                            self.get_file_size()
                            self.logging_cut("切片完成!开始记录生成加密版本的ts!")
                            self.aes_video()
                            self.modify_aes_ts_url()
                            self.logging_cut("加密版本切片完成!开始记录将切片信息写入到文件并记录到数据库!")
                            self.recoder_to_db()
                            self.recoder_to_file("all done !! and ok")
                            self.change_mp4_cutStatus()
                            self.logging_cut("切片完毕!")
                            return "切片顺利完成!"
                            # self.push_to_cdn()

                        else:
                            self.logging_cut(str(ts_status[1]) + "生成切片失败!")
                            return json.dumps(str(ts_status[1]) + "生成切片失败!")

                    else:
                        self.logging_cut("生成ts失败!")
                        return "生成ts失败!"+str(ts_status[1])

                else:
                    self.logging_cut("获取视频时长失败!")
                    return "获取视频时长失败!"+str(d_status[1])
            else:
                self.logging_cut("生成缩略图失败!")
                return "生成缩略图失败!"+str(t_status[1])
        else:
            self.logging_cut('转码尺寸失败'+str(c_status[1]))
            return "转码尺寸失败!"+str(c_status[1])

# # 脚本测试
# if __name__ == '__main__':
#     fg = ffmpeg(1,1,'/root/shell/demo/20170925/zyys_1.mp4')
#     fg.start_cut()
# aes = Aes()
# srcfile = '/test.ts'
# aesfile = '/aes_py_test.ts'
# aes.file_encryption(srcfile, aesfile)
# aes.file_decryption(aesfile)
