import numpy as np
import statsmodels.api as sm
import sklearn.metrics as sk



data = np.array([
    [4.711274994,18.7083919965382], [12.203381,8.35022136989966], [11.70460186,8.54342534196065], [14.99061906,7.60617569558319],
    [14.57329585,5.64272502326726], [1.41706675538465,63.9989588518081], [26.1226698,4.34734095250333], [40.4342113,3.17223628744976],
    [13.9951,7.56340893538087], [500,0.188324008829066], [49.9518,1.84171812616208]
])

# log transforming the data
x_log = np.log2(data[:, 0]).reshape(-1,1)
y_log = np.log2(data[:, 1])

# have to add constant ones to our x_log vector. 
X = sm.add_constant(x_log)

test_data = np.array([[25.44378109,3.651403353],
[3.677271056,24.58642214],
[10.55348391,9.870157041],
[21.84550631,4.914253887]])
x_test = np.log2(test_data[:, 0]).reshape(-1,1)
y_actual = np.log2(test_data[:, 1])
x_test = sm.add_constant(x_test)

model = sm.OLS(y_log, X).fit()
y_predicted = model.predict(x_test)
print(model.summary())

print(sk.r2_score(np.exp2(y_actual), np.exp2(y_predicted)))
print(sk.mean_squared_error(np.exp2(y_actual), np.exp2(y_predicted)))

data = [[1.0, 2.997]]
print(model.predict(data))

