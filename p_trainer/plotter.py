import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches

def plot_net(training, test, filter_name, save_dir, plot_num, step_size = 10):
	''''
	Saves plot training and test loss vs. iterations
	Parameters
	----------
	training : list
		training error at each iteration 
	test : list
		test error at each iteration 
	filter_name : string
		grayscale, rgb, etc.
	save_dir : path 
		directory to save plot at
	plot_num : int
		number of plot
	'''

	iterations = [step_size * i for i in range(len(training))]
	
	plt.figure(plot_num)
	plt.title(filter_name)

	plt.plot(iterations, training, 'b', label = 'Training')
	plt.plot(iterations, test, 'g', label = 'Test')
	
	plt.xlabel('Iterations')
	plt.ylabel('Error')

	plt.ylim((0, 1))

	plt.legend()

	plt.savefig(save_dir + '/' + filter_name)