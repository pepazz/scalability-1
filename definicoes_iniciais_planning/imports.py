#@title Imports

import numpy as np
from numpy.ma.core import flatten_structured_array
from google.colab import files
import datetime
from datetime import datetime 
from datetime import timedelta
import math
from IPython.display import clear_output
import timeit
import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from gspread_dataframe import set_with_dataframe
import io
import scipy
from scipy import stats
from scipy.stats import pearsonr
from scipy.spatial import distance
from scipy.stats import chi2
from sklearn.ensemble import IsolationForest
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import seaborn as sns
from itertools import combinations
from itertools import product
import re
from sklearn.linear_model import LinearRegression
from sklearn.utils import resample
from sklearn.utils import shuffle
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


import statistics 
from statistics import mode

import itertools
from itertools import compress

from tabulate import tabulate

import difflib
from difflib import SequenceMatcher


from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
creds, _ = default()

gc = gspread.authorize(creds)

from google.colab import drive
drive.mount('/content/drive')

# Abaixo vamos definir alguns marcadores para garantir mensagens
# de erro legíveis caso o usuário não rode o programa na ordem certa ou
# tentar rodar células depois de receber mensagens de erro em blocos
# anteriores.
#_______________________________________________________________
flag_funcoes_auxiliares = False
flag_nome_sheets = False
flag_painel_de_controle = False
flag_abertura_bases = False
flag_checks = False
