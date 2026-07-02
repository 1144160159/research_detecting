import json
#from pandas.core.common import SettingWithCopyWarning
from pandas.errors import DtypeWarning
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
#warnings.filterwarnings("ignore", category=SettingWithCopyWarning)
warnings.filterwarnings("ignore", category=DtypeWarning)

###############################################################################
# Global path of the raw darknet traces
###############################################################################
#DATA  = f'idarkvec-toit/'
#DATA = 'dataset'
#DARKNETNO = 'darknet01'
#TRACES  = f'{DATA}/{DARKNETNO}'
# MODELS = f'{DATA}/models'
# GRAPHS = f'{DATA}/graphs'
# DATASETS = f'{DATA}/interim'
# SERVICES = f'{DATA}/services/services.json'
#GT = f'{DATA}/groundtruth/big_gt.csv'
# MANUAL_GT = f'{DATA}/groundtruth/manual_gt.csv'

###############################################################################
# Domain knowledge based services
###############################################################################
# with open(SERVICES, 'r') as file:
#     LANGUAGES = json.loads(file.read())
    

LOWER_BOUND = '20210501'
UPPER_BOUND = '20210505'