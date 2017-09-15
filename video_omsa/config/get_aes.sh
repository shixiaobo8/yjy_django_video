#!/usr/bin/env bash
# 将旧的视频转码切片使用aes加密(php版本)

# 旧的地址文件
#original_media_files=/root/shell/aes_ssl_media.txt
old_media_files=/root/shell/rs.txt
#old_media_files=`cat $original_media_files`
videos=`cat $old_media_files`

# 加密
aes_video(){
	cd /root/scripts/
	for video in $videos
	do
		echo $video
		video_dir=`dirname $video`
		cd $video_dir
		dir_name=`basename $video_dir`
		rm -rf .."/aes_"$dir_name
		mkdir .."/aes_"$dir_name
		# 将m3u8 文件命名为aes_m3u8
		m3u8_file=`find ./ -name "*.m3u8"`
		file_prefix=`basename $m3u8_file | cut -d"." -f1`
		cp $m3u8_file ../"aes_"$dir_name"/"$file_prefix"_aes.m3u8"
		# 使用php加密ts文件
		ts_files=`find ./ -name "*.ts"`
		for ts in $ts_files
		do
			/usr/bin/php /root/scripts/aes.php $ts .."/aes_"$dir_name"/"$ts
		done
		echo "正在修改aes_m3u8文件"
		sed -i "s/$dir_name/aes_$dir_name/g" .."/aes_"$dir_name"/"$file_prefix"_aes.m3u8"
		# 使用python脚预热ts并上传到oss
		cat .."/aes_"$dir_name"/"$file_prefix"_aes.m3u8" | grep ts >> /tmp/tss_file.txt
		# 获取加密版本的m3u8里面所有的加密ts的文件的总大小
		aes_file_size=`du -sh .."/aes_"$dir_name`
		echo $aes_file_size >> ~/shell/aes_file_size.txt 
	done
	# 使用python脚预热ts并上传到oss
	/usr/bin/python /root/scripts/push_new_url_to_cdn.py /tmp/tss_file.txt
	paste ~/shell/aes_file_size.txt /root/shell/aes_ssl_media.txt > /root/shell/result.txt
}
aes_video
