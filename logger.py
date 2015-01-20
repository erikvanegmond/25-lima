import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s [%(asctime)s] [%(filename)s:%(lineno)s] %(message)s', filename='logging.log',  filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s [%(asctime)s] [%(filename)s:%(lineno)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)