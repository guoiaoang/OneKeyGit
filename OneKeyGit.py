# author: Guoiaong
# timedate: 20210720
# description: 剪切板复制git地址，然后执行该脚本，自动在预设的目录执行git克隆或更新(要求安装有TortoiseGit)
# 

# url example:
# https://github.com/git/git.git
# https://hub.fastgit.org/git/git.git
# https://gitclone.com/github.com/git/git.git
# https://github.com.cnpmjs.org/git/git.git
# not support:
# https://github.com/git/git
# git@github.com:git/git.git
# git@git.zhlh6.cn:git/git.git
# git@hub.fastgit.org:git/git.git
# gh repo clone git/git
# https://github.com/git/git/archive/refs/heads/master.zip

# 1.获取剪切板
# 2.字符拆分
# 3.获取路径
# 4.执行命令
import logging  # logging.info
import os  # exists
import sys # executable
import winreg  # OpenKeyEx
import win32api  # ShellExecute
import win32clipboard  # GetClipboardData
import winshell  # my_documents

# 不设置root默认保存到我的文档，设置root后其他均可自动生成
config = { 
    # # 日志文件
    # 'root'   : 'D:\\Git\\'#, # D:\Git\
    # 'dir'    : 'D:\\Git\\.OneKeyGit\\',
    # 'log'    : 'D:\\Git\\.OneKeyGit\\OneKeyGit.log',
    # # 快捷方式
    # 'lnk'    : 'D:\\Git\\.OneKeyGit\\OneKeyGit.lnk',
    # 'py'     : 'D:\\Git\\.OneKeyGit\\OneKeyGit.py',
    # 'python' : 'C:\\exec\\Python39-64\\python.exe',
    # # 执行命令
    # 'git'    : 'C:\\exec\\TortoiseGit\\bin\\TortoiseGitProc.exe',
    # 'clone'  : '/command:clone /path:', # win32api.ShellExecute(0, 'open', git, cmd+author, '', 1)
    # 'pull'   : '/command:pull  /deletepathfile', # win32api.ShellExecute(0, 'open', git, cmd, project, 1)
    # # 克隆地址
    # 'url'    : '',          # https://github.com/git/git.git
    # # 项目路径
    # 'author' : '',          # D:\Git\git\
    # 'project': '',          # D:\Git\git\git\
    # 'config' : ''           # D:\Git\git\git\.git\config
    }

# 字典为空才更新
def emptySava(dict, key, value):
    if (not key in dict) or (len(dict[key]) <= 0):
        dict[key] = value

# 初始化目录及日志
def init():
    # TortoiseGitProc
    reg = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\TortoiseGitProc.exe')
    git = winreg.QueryValue(reg, "") # 默认值要填""
    # 获取文件名
    name = os.path.splitext(os.path.split(__file__)[1])[0]  # 不包含后缀的文件名
    # 基本执行路径
    emptySava(config, 'root'  , winshell.my_documents() + '\\Git\\') # 本地Git克隆目录
    emptySava(config, 'dir'   , config['root'] + '.' + name + '\\')  # 脚本目录
    emptySava(config, 'log'   , config['dir' ] + name + '.log')      # 脚本运行日志
    emptySava(config, 'git'   , git.strip('\"'))                     # TortoiseGitProc.exe
    emptySava(config, 'clone' , '/command:clone /path:')             # clone命令
    emptySava(config, 'pull'  , '/command:pull  /deletepathfile')    # pull命令
    # 设置日志路径、记录等级和内容格式
    if not os.path.exists(config['dir']):
        os.makedirs(config['dir'])
    logging.basicConfig(filename=config['log'], level=logging.INFO, format="[%(asctime)s][%(levelname)s]%(message)s") 
    logging.info('start...')
    logging.debug('git path root: ' + config['root'])
    logging.debug('.py dir: ' + config['dir'])
    logging.debug('git execute path : ' + config['git'])
    logging.debug('git clone command: ' + config['clone'])

# 创建快捷方式
def lnk():
    base = os.path.split(__file__)[1] # 不需要路径，只需要文件名
    name = os.path.splitext(base)[0]  # 不包含后缀的文件名
    emptySava(config, 'lnk'   , config['dir' ] + name + '.lnk') # 运行脚本快捷方式
    emptySava(config, 'py'    , config['dir' ] + base)          # 脚本文件
    emptySava(config, 'python', sys.executable)                 # python.exe 文件路径
    logging.debug('.lnk file: '     , config['lnk'])
    logging.debug('.py target: '    , config['py'])
    logging.debug('python execute: ', config['python'])
    if os.path.exists(config['lnk']):
        return
    win32api.CopyFile(__file__, config['py'])
    # 创建快捷方式
    winshell.CreateShortcut(
        Path=config['lnk'],
        Target=config['python'],
        Arguments=config['py'],
        StartIn=config['root'],
        Icon=(config['python'], 0),
        Description='一键 Git Clone'
    )
    # 提示手动锁定到任务栏以刷新界面
    win32api.ShellExecute(0, 'open', config['dir'], '', '', 1) # 打开文件夹
    win32api.MessageBox(0, "请手动锁定快捷方式到任务栏", "提示", 0)

# 从剪切板获取项目地址
def getUrl():
    win32clipboard.OpenClipboard()
    config['url'] = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    if not config['url'].endswith('.git'):
        logging.error('url error: ' + config['url'].split('\n')[0] + '...')
        logging.info('exit...')
        exit()
    logging.info('url: ' + config['url'])

# 设置项目相关的路径
def setProject():
    # 测试
    # config['url'] = 'https://github.com/git/git.git'
    # win32clipboard.OpenClipboard()
    # win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, config['url'])
    # win32clipboard.CloseClipboard()
    # 执行
    part = config['url'].split('/')
    lens = len(part)
    config['author']  = config['root']    + part[lens-2] + '\\'
    config['project'] = config['author']  + part[lens-1].removesuffix('.git') + '\\'
    config['config']  = config['project'] + '.git\\config'
    logging.debug('author dir: ' + config['author'])
    logging.info('project dir: ' + config['project'])
    logging.debug('project config file: ' + config['config'])

# 执行Git
def exec():
    if not os.path.exists(config['config']): # 项目文件夹不存在时才执行命令 # 不必手动创建作者文件夹
        logging.info('shellExecute: ' + config['git'] + ' ' + config['clone'] + config['author'])
        win32api.ShellExecute(0, 'open', config['git'], config['clone'] + config['author'], '', 1) # 执行克隆
    else:
        # 执行拉取
        logging.info('try to pull: ' + config['project'])
        win32api.ShellExecute(0, 'open', config['git'], config['pull'], config['project'], 1) # 执行拉取

if __name__ == '__main__':
    init()
    lnk()  # 创建快捷方式，非第一次执行可注释掉
    getUrl()
    setProject()
    exec()
    logging.info('end...')

