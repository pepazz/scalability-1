#@title Imports

import numpy as np
import datetime
from datetime import datetime
from datetime import timedelta
from IPython.display import clear_output
import timeit
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import scipy
from scipy.spatial import distance
#from scipy.stats import chi2
from sklearn.ensemble import IsolationForest
from sklearn.mixture import GaussianMixture
from sklearn.cluster import DBSCAN
from itertools import combinations
from itertools import product
import random
from sklearn.linear_model import LinearRegression
from sklearn.utils import resample
from sklearn.base import clone
import statsmodels.api as sm
import warnings
from statsmodels.tools.sm_exceptions import ValueWarning
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from statsmodels.tools.sm_exceptions import HessianInversionWarning
warnings.simplefilter('ignore', ValueWarning)
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', HessianInversionWarning)
warnings.simplefilter('ignore', RuntimeWarning)
warnings.simplefilter('ignore', FutureWarning)

np.seterr(divide='ignore', invalid='ignore')
#%load_ext google.colab.data_table
import calendar
import unicodedata
def colored(texto,cor):
  if cor == 'red' or cor == 'r':
    return f'\033[1;31m{texto}\033[0;0;0m'
  elif cor == 'green' or cor == 'g':
    return f'\033[1;32m{texto}\033[0;0;0m'
  elif cor == 'yellow' or cor == 'y':
    return f'\033[1;33m{texto}\033[0;0;0m'
  elif cor == 'blue' or cor == 'b':
    return f'\033[1;34m{texto}\033[0;0;0m'
  else:
    return texto
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')


import itertools
from itertools import compress

import difflib
from difflib import SequenceMatcher



