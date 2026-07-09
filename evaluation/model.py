import numpy as np
import statsmodels.api as sm
import sklearn.metrics as sk




data = np.array([
    [4.71127499418185,19.6918089413389], 
[12.2033809992473,8.35633694063186], 
[11.704601861427,8.91780593601013], 
[14.9906190601035,7.79247297100638], 
[14.5732958538299,5.65044674909809], 
[1.41706675538465,63.9989650278346], 
[26.1226697736351,4.34734070011086], 
[40.4342113089927,3.1722362177967], 
[13.9951,7.56340893598812], 
[500,0.188324004927631], 
[49.9518,1.84171812555508]
])

# log transforming the data
x_log = np.log2(data[:, 0]).reshape(-1,1)
y_log = np.log2(data[:, 1])

# have to add constant ones to our x_log vector. 
x_log = sm.add_constant(x_log)

test_data = np.array([[10.5534839122096, 9.87012077692965], 
[21.8455063134439, 4.91425388708229], 
[1.33454766241651, 64.2948569725799], 
[2.06204311152764, 44.4943697330688], 
[25.4437811, 3.97057935], 
[2.46508032, 35.9791488], 
[7.8956229, 10.5484501], ])
x_test = np.log2(test_data[:, 0]).reshape(-1,1)
y_actual = np.log2(test_data[:, 1])
x_test = sm.add_constant(x_test)

model = sm.OLS(y_log, x_log).fit()
y_predicted = model.predict(x_test)
print(model.summary())

print(sk.r2_score(np.exp2(y_actual), np.exp2(y_predicted)))
print(sk.mean_absolute_error(np.exp2(y_actual), np.exp2(y_predicted)))

data = [[1.0, np.log2(2.997)]]
print(np.exp2(model.predict(data)))
print(np.column_stack((np.exp2(y_actual), np.exp2(y_predicted))))




# setting the slope to -1 manually

y_predicted_log_manual = model.params[0] - 1.0 * x_test[:, 1]

y_predicted_manual = np.exp2(y_predicted_log_manual)

print(sk.mean_absolute_error(np.exp2(y_actual), y_predicted_manual))