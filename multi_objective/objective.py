def objective(name, phenotype):
	from deap import benchmarks
	f = benchmarks.dtlz2
	from numpy import loadtxt
	a = loadtxt('T%s_template.txt' % name)
	result = f(a,2)
	return result	
