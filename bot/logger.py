import logging
import os


def setup_logging():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(current_dir, '..')

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "discord_bot.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.WARNING,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Определение обработчика для вывода в консоль
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    logging.getLogger('').addHandler(console)
