import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def log_dir_check():
    """
    检查日志存储目录
    :return:
    """
    if "logs" not in os.listdir("./"):
        os.makedirs("logs")
        os.makedirs("logs/all")
        os.makedirs("logs/error")
    else:
        logs_dir = os.listdir("./logs")
        if "all" not in logs_dir:
            os.makedirs("./logs/all")
        elif "error" not in logs_dir:
            os.makedirs("./logs/error")


def setup_log(name):
    """
    初始化日志器
    :param name: 调用者, 期待 __name__
    :return: 直接可用的日志器, 包含控制台输出[除 ERROR 的所有日志]/ALL 文件输出[每日更新]/ERROR 文件输出[大小更新]
    """
    log_dir_check()

    def should_log(record):
        """
        定义日志过滤规则
        :param record: 日志信息,拥有日志的自有属性,如 lineno
        :return: True or False
        """
        if record.levelname not in ["INFO", "WARNING"]:
            return False
        return True

    # 初始化干净的日志器
    logger = logging.getLogger(name)

    logger.setLevel(level=logging.INFO)

    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    _ = '%(asctime)s - %(levelname)s - %(module)s:%(funcName)s - lineno:%(lineno)d - %(message)s'
    formatter = logging.Formatter(_)

    # 创建三个日志记录器,分别为控制台输出, ALL 文件输出, ERROR 文件输出
    # 文件输出指明日志保存的路径、保存的日志文件个数上限、以及各不同日志器的属性
    console = logging.StreamHandler()
    all_handler = TimedRotatingFileHandler("logs/all/all_log.log", when='midnight', interval=1, backupCount=10)
    error_handler = RotatingFileHandler("logs/error/error_log.log", maxBytes=1024 * 1024 * 100, backupCount=10)

    # 对日志器等级进行配置
    console.setLevel(logging.INFO)
    all_handler.setLevel(logging.INFO)
    error_handler.setLevel(logging.ERROR)

    # 为刚创建的日志记录器设置日志记录格式
    console.setFormatter(formatter)
    all_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # 初始化日志过滤器,并添加至指定 handler
    logging_filter = logging.Filter()
    logging_filter.filter = should_log
    console.addFilter(logging_filter)

    # 设置 TimedRotatingFileHandler 后缀名称，跟 strftime 的格式一样
    all_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"

    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logger.addHandler(console)
    logger.addHandler(all_handler)
    logger.addHandler(error_handler)

    return logger
