import pandas as pd

model = pd.read_csv('ModelHs.txt', delim_whitespace=True)
print(model.head(10))

model.to_hdf('model.h5', key='model', mode='w')
model2 = pd.read_hdf('model.h5', key='model')
print(model2.head(10))
