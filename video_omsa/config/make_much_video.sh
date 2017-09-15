#! /usr/bin/env bash
# 批量处理视频转码切片 -加密版本

sh_dir=/root/shell
sh_convert_file=$sh_dir"/""m_fs_convert_mixed.sh"
#sh_encrypt_file=$sh_dir"/""m_fs_encrypt_mixed.sh"
config_pre=$sh_dir"/""config.ini_"
#config_ini=(tcms_chuanranbing xiyizonghe_zhenduanxue xiyizonghe_neike xiyizonghe_waike zhiyi_jingshenbing zhiyi_neike zhiyi_shengli)
config_ini=(xiyizonghe_waike)

# 定义要处理的学科科目
get_chapter(){
	echo "ok"
}

# 自动生成要切片的配置文件
make_ini(){
	echo "ok"
}

# 批量处理视频转码切片
make_video(){
	for config in ${config_ini[@]}
	do
	      if [ ! -f $config_pre$config ];then
	          $sh_dir"/make_new_config.sh" $config	
	      fi
	      $sh_convert_file  $config_pre$config
	done
}
make_video

