import click
import json
import psutil
import time
import os
import sys as system

CONFIG_FILE = None
config = None
todoList = None


def loadConfig():
    try:
        with open(CONFIG_FILE, 'r', encoding="utf-8") as f:
            global config
            config = json.load(f)
    except Exception as e:
        print(f"文件 config.json 出错，请检查其保存路径或编码格式。详细信息：{e}")


def saveConfig():
    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"文件‘config.json’出错，请检查其保存路径或编码格式。详细信息：{e}")


def get_network_usage(interval=1):
    # 获取当前网络传输速率（发送/接收）
    net_before = psutil.net_io_counters()
    start = time.monotonic()  # 使用单调时钟，避免系统时间调整影响
    time.sleep(interval)  # 等待一段时间计算速率
    elapsed = time.monotonic() - start  # 实际耗时
    elapsed = max(0.001, elapsed)  # 防止除0错误
    net_after = psutil.net_io_counters()

    sent_speed = (net_after.bytes_sent - net_before.bytes_sent) / elapsed  # 发送速率 (B/s)
    recv_speed = (net_after.bytes_recv - net_before.bytes_recv) / elapsed  # 接收速率 (B/s)
    return sent_speed, recv_speed


@click.group()
def go():
    # 获取exe所在目录
    if getattr(system, 'frozen', False):
        # 打包后的exe运行环境
        base_dir = os.path.dirname(system.executable)
    else:
        # 普通Python脚本运行环境
        base_dir = os.path.dirname(os.path.abspath(__file__))
    global CONFIG_FILE
    CONFIG_FILE = os.path.join(base_dir, "config.json")
    loadConfig()


@go.command(help="打个招呼")
def hi():
    click.echo(config["echo"]["hi"])


@go.command(help="你是谁")
def whoru():
    click.echo(config["echo"]["whoru"])


@go.command(help="计算表达式")
@click.option("-i", "expression", help="表达式")
def calc(expression):
    try:
        click.echo(f"计算结果：{eval(expression)}")
    except Exception as e:
        print(f"该表达式无法计算")


@go.command(help="系统资源占用信息")
def sys():
    # 该模块耗时较长，因此显示加载信息
    click.echo(f"{config["echo"]["loading_text"]}", nl=False)

    # CPU使用率
    cpuPercent = psutil.cpu_percent(interval=1)

    click.echo(".", nl=False)

    # 内存使用率
    mem = psutil.virtual_memory()
    memPercent = mem.percent

    # 磁盘使用率
    diskCPersent = psutil.disk_usage('C:\\').percent
    diskDPersent = psutil.disk_usage('D:\\').percent

    # 获取网络状况
    sent, recv = get_network_usage()

    click.echo(".")
    time.sleep(0.4)

    click.echo(f"CPU利用率: {cpuPercent}%")
    click.echo(f"内存占用率: {memPercent}%")
    click.echo(f"硬盘占用率(C/D): {diskCPersent}% / {diskDPersent}%")
    click.echo(f"网络速率(发送/接收): {sent / 1024:.2f} / {recv / 1024:.2f} KB/s")


@go.command(help="打开文件")
def apple():
    video_path = config["echo"]["filepath"]
    if system.platform == "win32":
        os.startfile(video_path)
    else:
        click.echo("该功能暂时只支持windows系统")


@go.group(help="ToDo List 模块")
def todo():
    global todoList
    todoList = config["todo"]


@todo.command(help="增加待办事项")
@click.option("-i", "text", help="待办事项")
def add(text):
    todoList.append(text)
    config["todo"] = todoList
    saveConfig()
    click.echo("已添加")


@todo.command(help="展示待办事项")
def list():
    if not todoList:
        click.echo("暂时没有待办事项")
    else:
        for i, t in enumerate(todoList):
            click.echo(f"[{i + 1}] {t}")


@todo.command(help="完成某待办事项(同时删除)")
@click.option("-i", "index", help="要删除的待办事项的序号")
def cpl(index):
    if len(todoList) < int(index):
        click.echo(f"当前待办清单只有{len(todoList)}项")
    elif int(index) <= 0:
        click.echo("？你干什么呢")
    else:
        todoList.pop(int(index) - 1)
        config["todo"] = todoList
        saveConfig()
        click.echo("已删除")


@todo.command(help="清空待办事项")
def rm():
    confirm = input("清空操作不可撤销，输入yes确认清空：")
    if confirm == "yes":
        config["todo"] = []
        saveConfig()
        click.echo("已清空")
    else:
        click.echo("清空操作已取消")


if __name__ == "__main__":
    go()
