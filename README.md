# Pal bot for KOOK


- [Pal bot for KOOK](#pal-bot-for-kook)
  - [功能](#功能)
  - [前置需求](#前置需求)
    - [systemd](#systemd)
    - [crontab](#crontab)


简单的幻兽帕鲁服务器的辅助机器人，配合KOOK使用，仅支持Linux环境，在Ubuntu与Debian上工作良好，需要Python 3.10+<br>
使用此机器人需要先[申请token](https://developer.kookapp.cn/app/index)，接着在配置文件中填入token，备份路径，游戏安装路径等信息。

![](img/image.png)
![](img/image-2.png)
![](img/image-1.png)

## 功能
- `/帮助` (`/help`): 查询指令信息. 
- `/状态` (`/status`): 查询服务器当前内存和CPU占用，以及systemd的日志<br>
    等效于
    ```bash
    sudo systemctl status pal
    ```
- `/重启` (`/restart`): 重启服务器<br>
    等效于
    ```bash
    sudo systemctl restart pal
    ```
- `/日志` (`/log`): 查询systemd的最新日志<br>
    可选参数：行数。例如：`/日志 20`<br>
    等效于
    ```bash
    sudo journalctl -u pal -r -n 20 {行数}
    ```
- `/查看备份` (`/listbak`): 查询备份文件夹.<br>
    可选参数：搜索参数。仅显示包含指定字符串的文件夹。例如根据文件名规则，`/listbak 31_17` 会显示31号17时的所有备份文件夹<br>
    等效于
    ```bash
    ls -lt {backup_path} | grep {搜索参数}
    ```
- `/立即备份` (`/backup`): 立即备份, 需要管理员权限<br>
    等效于
    ```bash
    cp -r {saved_path} {backup_path}/Saved_$(date +\%Y\%m\%d_\%H\%M\%S)
    ```
- `/恢复备份` (`/recbak`): 恢复备份, 需要管理员权限<br>
    该操作会先关掉服务器，移除saved文件夹(并不会真的移除，只是原地生成一份带有时间戳的备份)，从备份文件夹恢复指定时间点的备份后再启动。<br>
    格式：`/恢复备份 {备份文件夹名}` (推荐先使用 **/查看备份** 获取后直接复制)。<br>
    例如：`/恢复备份 Saved_20240130_170001`<br>
    等效于
    ```bash
    sudo systemctl stop pal
    mv {saved_path} {saved_path}_botbak_{int(time.time())}
    cp -r {backup_path}{备份文件夹名} {saved_path}
    sudo systemctl start pal
    ```
- `/添加管理员` (`/addadmin`): 添加管理员, 需要管理员权限



## 前置需求
### systemd
使用systemd来管理PalWorld服务，在oom-killer杀死进程后自动重启，顺带实现方便的日志和状态查询。
1. 创建服务文件
    ```bash
    sudo vi /etc/systemd/system/pal.service
    ```
2. 粘贴以下内容, 请根据自己服务器配置修改路径
    ```
    [Unit]
    Description=PalWorld

    [Service]
    WorkingDirectory=/home/ubuntu/Steam/steamapps/common/PalServer
    ExecStart=/home/ubuntu/Steam/steamapps/common/PalServer/PalServer.sh -useperfthreads -NoAsyncLoadingThread -UseMultithreadForDS
    Restart=always
    User=ubuntu

    [Install]
    WantedBy=multi-user.target
    ```
3. 启用服务
    ```bash
    sudo systemctl enable pal
    ```
4. 刷新systemd
    ```bash
    sudo systemctl daemon-reload
    ```
5. 启动服务
    ```bash
    sudo systemctl start pal
    ```
### crontab
使用crontab来定时备份服务器
1. 编辑crontab
    ```bash
    crontab -e
    ```

2. 添加备份任务, 请根据自己服务器配置修改路径
    ```
    */10 * * * * cp -r /home/ubuntu/Steam/steamapps/common/PalServer/Pal/Saved /home/ubuntu/pal-bak/Saved_$(date +\%Y\%m\%d_\%H\%M\%S)
    ```



---

感谢群友，炸档两次，通宵几天的成果全没了，还愿意陪我一起开荒第三次呜呜呜<br>
开荒第三次时，群友发动钞能力友情提供了8c32g的新服务器(此前是通过4c8g服务器，开20g的swap玩的)。换新服务器后，除了偶尔炸档、恢复存档会重启，中间只遇见过一次内存爆炸，解决内存泄露的最好方法就是给它加内存！