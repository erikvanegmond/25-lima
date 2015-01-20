import logging

logging.basicConfig(level=logging.WARN, format='%(levelname)s [%(asctime)s] [%(filename)s:%(lineno)s] %(message)s', filename='logging.log',  filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(console)