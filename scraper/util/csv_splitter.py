import os
import pandas as pd

path = 'data/datasets/fed/'

# for all files in die subdrectorys add to the name the ending '.csv'
for root, dirs, files in os.walk(path):
    for file in files:
        if not file.endswith('.csv'):
            os.rename(os.path.join(root, file), os.path.join(root, file + '.csv'))
        if 'DS_Store' in file:
            os.remove