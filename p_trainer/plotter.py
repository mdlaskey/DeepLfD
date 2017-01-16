import matplotlib.pyplot as plt 

def plot_net(training, test):
	''''
	Plots training and test loss vs. iterations
	Parameters
	----------
	training : list
		training error at each iteration 
	test : list
		test error at each iteration 

	'''

	print(len(training), len(test))
	iterations = [i for i in range(len(training))]
	plt.plot(iterations, training, 'b')
	plt.plot(iterations, test, 'g')
	plt.xlabel('iterations')
	plt.ylabel('error')
	plt.show()