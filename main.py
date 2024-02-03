import os
import yaml
import time
import subprocess

from khl import Bot, Message, requester

from utils import *


bot = Bot(token = config["token"])     

@bot.command(name="状态", aliases=["status"], prefixes=prefixes)
async def check_pal_status(msg: Message):
    memory = psutil.virtual_memory()
    status = f"""
CPU: {psutil.cpu_percent(interval=1)}%
内存: {bytes2human(memory.used)}/{bytes2human(memory.total)} = {memory.percent}%

**systemd**:\n{subprocess.check_output(['sudo', 'systemctl', 'status', 'pal']).decode('utf-8')}
    """
    await msg.reply(f"pal status:{status}")


@bot.command(name="添加管理员", aliases=["addadmin"], prefixes=prefixes)
async def add_admin(msg:Message, text:str):
    if not check_admin(msg.author_id):
        await msg.reply(f"无权限进行此操作")
        return

    if not check_if_mention(text):
        await msg.reply(f"格式错误，请使用@进行提及")
        return
    
    mention_id = dump_mention_to_id(text)
    if check_admin(mention_id):
        await msg.reply(f"{text} 已经是管理员")
        return
    
    config["admin"].append(mention_id)
    with open('config.yml', 'w') as f:
        yaml.dump(config, f)
        
    await msg.reply(f"已添加管理员: {text}")

  
@bot.command(name="重启", aliases=["restart"], prefixes=prefixes)
async def restart_pal(msg: Message):
    if not check_admin(msg.author_id):
        await msg.reply(f"无权限进行此操作")
        return
    
    subprocess.check_output('sudo systemctl restart pal', shell=True)
    status = subprocess.check_output('sudo systemctl status pal', shell=True)
    await msg.reply(f"重启成功，当前状态：\npal status: {status.decode('utf-8')}")


@bot.command(name="日志", aliases=["log"], prefixes=prefixes)
async def check_pal_log(msg: Message, max_lines:str = "20"):
    log = subprocess.check_output(f'sudo journalctl -u pal -r -n {max_lines}', shell=True).decode('utf-8').split('\n')
    await msg.reply("\n".join(log))


@bot.command(name="查看备份", aliases=["listbak"], prefixes=prefixes)
async def check_backup(msg: Message, search_param:str = "", max_lines: str = "15"):
    backup = subprocess.check_output(f'ls -lt {config["backup_path"]} | grep \"{search_param}\" | head -n {max_lines}', shell=True).decode('utf-8').split('\n')
    backup = [line.split("4096")[1].strip() for line in backup[1:-1]]
    await msg.reply("\n".join(backup))


@bot.command(name="立即备份", aliases=["backup"], prefixes=prefixes)
async def backup_manual(msg: Message):
    if not check_admin(msg.author_id):
        await msg.reply(f"无权限进行此操作")
        return
    
    saved_path = config["game_saved_path"]
    backup_path = config["backup_path"]
    subprocess.check_output(fr'cp -r {saved_path} {backup_path}Saved_$(date +\%Y\%m\%d_\%H\%M\%S)', shell=True)
    folder = subprocess.check_output(f'ls -lt {backup_path} | head -n 2', shell=True).decode('utf-8').split('\n')[1]
    folder = folder.split("4096")[1].strip()
    await msg.reply(f"{folder} 备份成功")
 
  
@bot.command(name="恢复备份", aliases=["recbak"], prefixes=prefixes)
async def recover_backup(msg: Message, folder_name: str):
    if not check_admin(msg.author_id):
        await msg.reply(f"无权限进行此操作")
        return
        
    saved_path = config["game_saved_path"]
    backup_path = config["backup_path"]
    
    saved = os.listdir(backup_path)
    if folder_name not in saved:
        await msg.reply(f"指定的备份文件夹不存在")
        return

    subprocess.check_output('sudo systemctl stop pal', shell=True)
    subprocess.check_output(f'mv {saved_path} {saved_path}_botbak_{int(time.time())}', shell=True)
    subprocess.check_output(f'cp -r {backup_path}{folder_name} {saved_path}', shell=True)
    subprocess.check_output('sudo systemctl start pal', shell=True)
    
    await msg.reply(f"备份恢复成功")


@bot.command(name="帮助", aliases=["help"], prefixes=prefixes )
async def show_help(msg: Message):
    cmd = {
        "**/状态** (status)": "查看游戏服务器状态(systemd)\n",
        "**/日志** (log)": "查看游戏服务器日志。\n\t- 可选参数：行数，默认为20。例如：/日志 20\n",
        "**/查看备份** (listbak)": "查看目前已有的备份(当前默认每10分钟自动备份一次)。\n\t- 可选参数：搜索参数。仅显示包含指定字符串的文件夹。例如根据文件名规则，/listbak _17 会显示下午17时的所有备份文件夹\n",
        
        "**/立即备份** (backup)": "手动备份存档。*需要管理员权限*\n",
        "**/恢复备份** (recbak)": "（**谨慎使用**）恢复备份。*需要管理员权限*。\n该操作会先关掉服务器，移除saved文件夹，从备份文件夹恢复指定时间点的备份后再启动。\n格式：/恢复备份 {备份文件夹名}(推荐先使用 **/查看备份** 获取后直接复制)。\n例如：/恢复备份 Saved_20240130_170001\n",
        "**/添加管理员** (addadmin)": "添加管理员。*需要管理员权限*。格式：/添加管理员 @用户名\n",
        "**/重启** (restart)": "重启游戏服务器。*需要管理员权限*\n",
    }
    
    await msg.reply(f"命令列表：\n" + "\n".join([f"{k}: {v}" for k,v in cmd.items()]))



if __name__ == '__main__':
    bot.run()
