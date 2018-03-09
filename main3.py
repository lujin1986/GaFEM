#!/usr/bin/python
from numpy import savetxt, loadtxt, array
from deap import base, creator, tools
from scipy import interpolate
from pickle import load, dump
from os import system, access, remove, path
from time import sleep
from glob import glob
from queue import Queue, Empty
from threading import Thread
from random import randint
from math import log
from time import sleep
from datetime import datetime
from sys import exit, argv
from time import time
from grow import grow
from objective import objective
from random import random
from sys import stdout
from pandas import read_csv
import traceback


Name = argv[-1]
restart = int(argv[-2])
indList = Queue() # set up the queue for parallization of jobs

f=open("%s.opt" % Name, 'rb')
parameters = load(f)
f.close()

if parameters['Case']['type'] == "single-objective":
	Multi = 0
else:
	Multi = 1
	objectives = parameters['obj_setting']
Nind=int(parameters['GA parameters']['population size'])          # number of individuals in the population
Inddigs = int(log(Nind, 10))+1
NGEN= int(parameters['GA parameters']['max. number of generations'])           # maximum number of generation
Gendigs =int(log(Nind, 10))+1
CXPB = float(parameters['GA parameters']['crossover rate'])        # crossover rate
MUTPB = float(parameters['GA parameters']['mutation rate (individual)'])      # mutation rate at individual level
indpb = float(parameters['GA parameters']['mutation rate (allele)']) 
tournsize = int(parameters['GA parameters']['tournament size'])
typeCrossover = parameters['GA parameters']['type of crossover']
elitism = parameters['elitism']
if parameters['multithreading'][0]:
	ths = int(parameters['multithreading'][1]) # number of threads
else:
	ths = 1   
	
templates = []
for template in parameters['template'].split(','):
	if template:
		templates.append(path.split(template)[1])	
variableList = parameters['design variables']
flag_constraint = parameters['constraint'][0]

if parameters['seed'][0]:
	seed = parameters['seed'][1]
else:
	seed = []


switch = 1
genotype =[]
valid_ind = []

result_GEN = []
err1 = 0
err2 = 0

	

def setGenotype(variableList):
	global genotype
	initial = 0
	for i in variableList:
		copy = i[:]
		if i[1]== 'discrete':
			N_candidate = len(i[-1])
			digit = int(log(N_candidate, 2))+1
			copy[2] = digit
		else:
			copy[2] = int(i[2])
			copy[3] = float(i[3])
			copy[4] = float(i[4])
			digit = int(i[2])
		copy.append(initial)
		genotype.append(copy)
		initial+=digit
	return initial		
		
def individual_():
	""" Method to randomly generate a genotype""" 
	
	individual = toolbox.get_indi()
	return individual

	
def population_(n):
	"""Method to generate a randomized population with no duplication"""
	
	pop = []
	for i in range(n):
		if i == 0:
			pop.append(individual_())
		else:
			new = individual_()
			flag = 0
			for ind in pop:
				if ind == new:
					flag = 1
			while flag:
				new = individual_()
				flag = 0
				for ind in pop:
					if ind== new:
						flag = 1
			pop.append(new)
	return pop	
	


def save_result_GEN(result_GEN):
	if Multi:	
		if result_GEN[-1]:
			last = -1
		else:
			last = -2
		GEN = int(result_GEN[last][0][0].split('_')[0])
		n = len(glob("result_GEN*.txt"))-1
		if n < 0:
			GEN_saved = 0
		else: GEN_saved = n
		for GEN in range(GEN_saved, GEN+1):
			with open("result_GEN%d.txt" % GEN, 'w') as f:
				f.write("name; \t values of variables; ")
				if Multi:
					for i in objectives[:-1]:
						f.write("\t %s; " % i[0])
					f.write("\t %s\n" % objectives[-1][0])
				else: f.write("\t fitness\n")

				for i in result_GEN[GEN]:
					f.write("%s; \t %s; " % (i[0], str(i[1])))
					for obj in i[2][:-1]:
						f.write("\t %s; " % str(obj))
					f.write("\t %s\n" % str(i[2][-1]))
	else:
		with open("result.txt", 'w') as f:
			f.write("name; \t values of variables; \t fitness\n")
			for i in result_GEN:
				f.write("%s; \t %s; \t %s\n" % (i[0], str(i[1]), str(i[2])))


def save_final_GEN(pop, g):
	with open("final_GEN%d.txt" % g, 'w') as f:
		f.write("name; \t values of variables; ")
		for i in objectives[:-1]:
			f.write("\t %s; " % i[0])
		f.write("\t %s\n" % objectives[-1][0])


		for i in range(len(pop)):
			f.write("%s-%s; \t %s; " % (str(g).zfill(Gendigs), str(i).zfill(Inddigs), str(decoder(pop[i]))))
			for fitness in pop[i].fitness.values[:-1]:
				f.write("\t %s; " % str(fitness))
			f.write("\t %s\n" % str(pop[i].fitness.values[-1]))


			
	


def getfitness(templateFiles):
	"""Automated generation of FEM models and execuation of simulations"""
	global switch, valid_ind, indList, err1, err2, result_GEN
 
	while switch:
		try:
			job=indList.get(block=False)
		except Empty:
			break
		else:
		    # define the name in the form "index of generation"_"index of individual":
			flag=1
			name = job[0]
			GEN = int(name.split('_')[0])
			phenotype = decoder(job[1])
			if Multi:
				for x in result_GEN:
					for y in x:
						if y[1]==phenotype:
							job[1].fitness.values = y[2]
							result_GEN[GEN].append([job[0], phenotype, job[1].fitness.values])
							flag=0
							break
					if flag==0:
						break
			else:
				for y in result_GEN:
					same = 0
					for key in y[1].keys():
						if y[1][key] != phenotype[key]:
							same = 0
							break
						same = 1
					if same:
						print("%s is the same as %s." % (name, y[0]))
						job[1].fitness.values = (y[2],)
						flag=0
						break

			if flag:
				print("starting the evaluation of %s at %s." % (name, datetime.now()))
				stdout.flush()
				for n, templateFile in enumerate(templateFiles):
					replacedFile=str(templateFile[1])
					replacedFile= replacedFile.replace('NAME', name)
					for key in phenotype.keys():
						replacedFile= replacedFile.replace(key, str(phenotype[key]))	
					if not n:
						end = templateFile[0].split('.')[1]
						f1 = open('I%s.%s' % (name, end), 'w')	
					else:
						f1 = open('T%s_%s' % (name, templateFile[0]), 'w')
					f1.write(replacedFile+'\n')
					f1.close()
				print("start growing %s" % name)
				stdout.flush()
				try:
					grow(name, phenotype)
				except:
					switch = 0
					err1 = traceback.format_exc()
					stdout.flush()
				else:
					try:
						fitness = objective(name, phenotype)
					except:
						switch = 0
						err2 = traceback.format_exc()
						stdout.flush()
					else:
						files = glob("*%s*" % name)
						for file in files:
							remove(file)
						job[1].fitness.values = fitness
						if Multi:
							result_GEN[GEN].append([job[0], decoder(job[1]), job[1].fitness.values])
						else:
							result_GEN.append([job[0], decoder(job[1]), job[1].fitness.values[0]])
			
						valid_ind.append(job[1])
						print("The evaluation of %s bas completed at %s" % (name, datetime.now()))
						stdout.flush()


		
def decoder(individual):
	global genotype
	phenotype = {}
	for item in genotype:
		gene = individual[item[-1]:item[-1]+item[2]]
		integer = 0 
		for i in range(item[2]):
			integer+=gene[i]*2**(item[2]-i-1)
		if item [1] == "discrete":
			excess =  2**item[2]-len(item[-2])
			if integer+1 <= 2*excess:
				index = integer/2
			else:
				index = integer-excess
			phenotype[item[0]] = item[-2][index]
		else:
			phenotype[item[0]] = item[3]+float(integer)/float(2**item[2]-1)*(item[4]-item[3])
	if flag_constraint:
		from constraint import constraint
		phenotype = constraint(phenotype)
	return phenotype
			
	
	
def history(pop, g, append = True):

	"""record the present generation and its relevant statistics
	   in plain text file """
	   
	# Gather all the fitnesses and phenotypes in one list
	fits = [ind.fitness.values[0] for ind in pop]
	phenotypes = [str(decoder(ind)) for ind in pop]

	length = len(pop)
	mean = sum(fits) / length
	sum2 = sum(x*x for x in fits)
	std = abs(sum2 / length - mean**2)**0.5
	ind = [i for i, j in enumerate(fits) if j==max(fits)]    
	fittest = pop[ind[0]]
	
	if append:
		mode = 'a'
	else:
		mode = 'w'
	with open("history.txt", 'w') as history:
		history.write( "=============== Generation %d results ================\n" % g)
		print("=============== Generation %d results ================" % g)
		print("  Min %s" % min(fits))
		history.write("  Min %s\n" % min(fits))
		print("  Max %s" % max(fits))
		history.write("  Max %s\n" % max(fits))
		print("  Avg %s" % mean )
		history.write("  Avg %s\n" % mean)
		print("  Std %s" % std)
		history.write("  Std %s\n" % std)
		print("phenotype of fittest individual: %s" % fittest) 
		history.write("phenotype of fittest individual: %s\n" % fittest) 
		print("genotype of fittest individual: %s" % decoder(fittest))
		history.write("genotype of fittest individual: %s\n" % decoder(fittest)) 

	return fittest
	
	
def parallelization(work):
	""" parallilization of jobs"""
	templateFiles = []
	for template in templates:
		f = open(template, 'r')
		templateFile = f.read()
	templateFiles.append([template, templateFile])
	workers = [Thread(target=getfitness, args=(templateFiles,)) for i in range(ths)]
	for worker in workers:
		worker.start()
	for worker in workers:
		worker.join()	

	
def main(restart, elitism, seed):
	""" the main routine to perform FEM-GA coupled optimization
	    restart: to restart the optimization from a broken point
		elitism: the switch on/off elitism in the optimization
	"""
	global valid_ind, result_GEN, fitnesses, switch
	#start = time()
	initGEN = 0   
	if restart:
		# load the archive for evaluated individuals:
		f = open("valid_ind.txt" , 'rb')    
		valid_ind = load(f)
		f.close()

		# list of files containing all the genotypes in the beginning of each generation:
		nameListOff = glob("offspring_Gen_*.txt")  
		initGEN =  max([int(i[14:-4]) for i in nameListOff])
		f = open("offspring_Gen_%d.txt" % initGEN, 'rb')
		offspring = load(f)
		f.close()	
		if Multi:
			for g in range(initGEN+1):
				result_GEN.append([])
				try:
					evaluated = read_csv("result_GEN%d.txt" % g, sep='; \t ', engine='python')
					for i in range(len(evaluated)):
						name=evaluated.iloc[i]['name']
						exec('genotype='+evaluated.iloc[i]['values of variables'])
						fitness=[]
						for obj in objectives:
							fitness.append(float(evaluated.iloc[i][obj]))
						result_GEN[g].append([name, genotype, fitness])
				except:
					pass
			for index in range(len(offspring)):
				indList.put(["%s_%s" % (str(g).zfill(Gendigs), str(index).zfill(Inddigs)), offspring[index]])
					
		else:
			evaluated = read_csv("result.txt", sep='; \t ', engine='python')
			for i in range(len(evaluated)):
				name=evaluated.iloc[i]['name']
				exec('genotype='+evaluated.iloc[i]['values of variables'])
				fitness=evaluated.iloc[i]['fitness']
				result_GEN.append([name, genotype, fitness])
			for index in range(len(offspring)):
				indList.put(["%s_%s" % (str(initGEN).zfill(Gendigs), str(index).zfill(Inddigs)), offspring[index]])

	
			

		print("restart at generation %d " % initGEN)
			
		parallelization(indList)
		if not switch:
			exit()
		if Multi:
			if initGEN:
				f = open("population_Gen_%d.txt" % (initGEN-1), 'rb')
				pop = load(f)
				f.close()
				pop = toolbox.select(offspring+pop, k=Nind)
			else:	
				pop=offspring
			save_final_GEN(pop, initGEN)			
			f = open("population_Gen_%d.txt" % initGEN, 'wb')
			dump(pop, f)
			f.close()	
			initGEN = initGEN+1				
		else:
			pop=offspring
			f = open("population_Gen_%d.txt" % initGEN, 'wb')
			dump(pop, f)
			f.close()
			fittest = history(pop, initGEN)
			initGEN = initGEN+1


			

	for g in range(initGEN,NGEN):	
		if g==0:
			print("starting generation %d at %s\n."	% (g, datetime.now()))
			stdout.flush()
			if Multi:
				result_GEN.append([])
			pop = toolbox.population(n=Nind)
			if seed:
				pop[0] = creator.Individual(seed)
			# pickle the state of the population in the beginning of the generation
			f = open("offspring_Gen_0.txt", 'wb')
			dump(pop, f)
			f.close()
			for index in range(Nind):
				indList.put(["%s_%s" % (str(g).zfill(Gendigs), str(index).zfill(Inddigs)), pop[index]])
			parallelization(pop)
			if not switch:
				break
			f = open("population_Gen_%d.txt" % g, 'wb')
			dump(pop, f)
			f.close()
			if not Multi:
				fittest = history(pop, g, append=False)
			else:
				save_final_GEN(pop, g)	
		
		else:
			print("Generation %d is being generated... at %s." % (g, datetime.now()))
			if Multi:
				result_GEN.append([])
			# Select the next generation individuals:
			if not Multi:
				offspring = toolbox.select(pop, len(pop))
			else:
				offspring = list(map(toolbox.clone, pop))
			# Clone the selected individuals:
			offspring = list(map(toolbox.clone, offspring))
			
			# Apply crossover and mutation on the offspring:
			for child1, child2 in zip(offspring[::2], offspring[1::2]):
				if random() < CXPB:
					toolbox.mate(child1, child2)
					del child1.fitness.values
					del child2.fitness.values
			for mutant in offspring:
				if random() < MUTPB:
					toolbox.mutate(mutant)
					del mutant.fitness.values
					

			f = open("offspring_Gen_%d.txt" % g, 'wb')
			dump(offspring, f)
			f.close()
			
			if not Multi and elitism:
				if fittest not in offspring:
					offspring[0] = fittest
			for index in range(Nind):
				indList.put(["%s_%s" % (str(g).zfill(Gendigs), str(index).zfill(Inddigs)), offspring[index]])
			parallelization(offspring)
			if not switch:
				break
			print("The evaluation of generation: %d has been complete!" % g)
			if Multi:
				pop = toolbox.select(offspring+pop, k=Nind)
				initGEN = initGEN+1
				save_final_GEN(pop, g)
			else:
				pop[:] = offspring
				fittest = history(pop, g)
				save_result_GEN(result_GEN)
			f = open("population_Gen_%d.txt" % g, 'wb')
			dump(pop, f)
			f.close()
	
	savetxt("switch.txt", array([0]))
	#sleep(2)
	archive()


def checkSwitch():
	global switch
	while switch:
		switch = loadtxt("switch.txt")
		sleep(2)
	f = open("valid_ind.txt" , 'wb')
	dump(valid_ind,f)
	f.close()
	save_result_GEN(result_GEN)
	
		
def archive():
	global valid_ind, result_GEN, Multi, switch, fitnesses
	old = len(valid_ind)
	while switch:
		new = len(valid_ind)
		if new > old:
			f = open("valid_ind.txt" , 'wb')
			dump(valid_ind,f)
			f.close()
			save_result_GEN(result_GEN)
		old = new
		sleep(2)
if Multi:
	weights = [i[1] for i in objectives]
	creator.create("FitnessMax", base.Fitness, weights=tuple(weights))
else:
	creator.create("FitnessMax", base.Fitness, weights=(1,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# attribute generator:
toolbox.register("attr_bool", randint, 0, 1)
# randomly generate the genotype:
toolbox.register("get_indi", tools.initRepeat, creator.Individual, 
    toolbox.attr_bool, setGenotype(variableList))

# setting up important GA parameters:
if typeCrossover == 'one-point':
	toolbox.register("mate", tools.cxOnePoint)
else:
	toolbox.register("mate", tools.cxTwoPoint)                       
toolbox.register("mutate", tools.mutFlipBit, indpb=indpb)
if Multi:
	toolbox.register("select", tools.selNSGA2)
else:
	toolbox.register("select", tools.selTournament, tournsize=tournsize)		

toolbox.register("individual", individual_)
toolbox.register("population", population_)


if __name__ == "__main__":

	onOff = Thread(target=checkSwitch)
	mainThread = Thread(target=main, args=(restart, elitism, seed))
	archive_t = Thread(target=archive)
	onOff.setDaemon(True)
	archive_t.setDaemon(True)
	onOff.start()
	mainThread.start()
	archive_t.start()
	onOff.join()
	mainThread.join()
	archive_t.join()
	
	if err1:
		print("Something wrong has occured in running the \"grow\" function imported from grow.py")
		print(err1)
		exit(1)
	elif err2:
		print("Something wrong has occured in running the \"objective\" function imported from objective.py")
		print(err2)
		exit(1)
