from SignLang.logger import logging
from SignLang.exception import CustomException
import sys

logging.info("welcome to the project")

try:
    a = 7/0
    
except Exception as e:
    raise CustomException(e,sys)