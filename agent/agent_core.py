import time
import logging
from agent.content_gen import ContentGenerator
from agent.follower_manager import FollowerManager
from xiaohongshu_api import XiaohongshuAgent  # 假设有这样的API模块
import yaml
from apscheduler.schedulers.background import BackgroundScheduler

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCore:
    def __init__(self, config_path="config.yaml"):
        # 加载配置文件
        self.config = self.load_config(config_path)

        # 初始化小红书API，内容生成器，粉丝管理器
        self.xhs_agent = XiaohongshuAgent(self.config['xiaohongshu'])
        self.content_generator = ContentGenerator(self.config['content'])
        self.follower_manager = FollowerManager(self.config['follower'])

        # 初始化调度器
        self.scheduler = BackgroundScheduler()

        # 启动调度器
        self.scheduler.start()

    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise

    def add_task(self, func, trigger, *args, **kwargs):
        """添加定时任务"""
        self.scheduler.add_job(func, trigger, *args, **kwargs)
        logger.info(f"Task {func.__name__} scheduled with trigger {trigger}")

    def post_note(self):
        """生成并发布小红书笔记"""
        try:
            prompt = "Write an engaging note for Xiaohongshu about lifestyle tips."
            note_content = self.content_generator.generate_post(prompt)
            self.xhs_agent.post_note(note_content)
            logger.info(f"Note posted successfully: {note_content}")
        except Exception as e:
            logger.error(f"Error posting note: {e}")

    def update_follower_tags(self):
        """更新粉丝标签"""
        try:
            followers = self.xhs_agent.get_followers()
            for follower in followers:
                tag = self.follower_manager.assign_tag(follower)
                logger.info(f"Updated follower {follower['name']} with tag: {tag}")
        except Exception as e:
            logger.error(f"Error updating follower tags: {e}")

    def run(self):
        """启动 Agent"""
        # 添加定时任务
        self.add_task(self.post_note, 'cron', hour=10, minute=0)  # 每天 10 点发布笔记
        self.add_task(self.update_follower_tags, 'interval', minutes=30)  # 每 30 分钟更新粉丝标签

        try:
            # 运行调度器，保持程序运行
            while True:
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            # 处理退出
            logger.info("Agent stopped.")
            self.scheduler.shutdown()