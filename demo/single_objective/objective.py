def objective(name, phenotype):
	from numpy import loadtxt
	a = loadtxt('T%s_template.txt' % name)
	result = - ((a[0]-4.0)**2 + (a[1]-27.0)**2 + (a[2]-35.0)**2 + (a[3]-55.0)**2+ (a[4]-55.0)**2)
	#print "the fitness of %s is %.2f\n" % (name, result)
	return (result,)
