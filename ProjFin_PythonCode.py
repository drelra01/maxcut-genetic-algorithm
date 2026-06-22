import math
import random
from statistics import mean
from statistics import pstdev


# ==========  Maximum Cut Problem ========= #


def Create_Graph(a, b, seed=None):   #Random Graph that will be generated
    if seed is not None:
        random.seed(seed)
    edges = []
    for x in range(a):
        for y in range(x+1, a):
            if random.random() < b:
                edges.append((x, y))
    return a, edges

a, return_edges = Create_Graph(a=100, b=0.5, seed=0)

def Cut(assign, edges):      #Listing 0 or 1 of length of 'a' and returns number of edges
    cut_value = 0            #that crosses the cut
    A = assign
    for (x, y) in edges:
        cut_value += (A[x] ^ A[y])
    return cut_value

def list_of_nodes(not_used=None):    #List lengths of 'a'
    return list(range(a))
            
def Initialize_Population(size, nodes):  #Records Initial Population (In Bitstrings)
    L = len(nodes)
    population = []
    for P in range(size):
        individual = [random.randint(0, 1) for P in range(L)]
        population.append(individual)
    return population
    
def fitness(edges):   #The fitness will record what is higher (Max-cut value)
    def Fit(assign):
        return Cut(assign, edges)
    return Fit

def Select_Random(population, Fit):  #Initalizes Random Selection
    total = 0.0
    for f in Fit:
        total += f

    R = random.random() * total
    run = 0.0
    for i in range(len(population)):
        run += Fit[i]
        if run >= R:
            return list(population[i])
    return list(population[-1])

def Select_Random_HighFit(population, Fit, k=5):       #Tournament for Hight Fit
    indexes = random.sample(range(len(population)), k)
    optimal = indexes[0]
    for i in indexes[1:]:
        if Fit[i] > Fit[optimal]:
            optimal = i
    return list(population[optimal])

def Parent_Roulette(population, Fit, selection):
    if selection == 'roulette':
        return Select_Random(population, Fit)
    elif selection == 'tournament':
        return Select_Random_HighFit(population, Fit, k=5)

def Reproduction(p1, p2):   #Uniform crossover for the bitstrings
   length_a = len(p1)
   child = [None] * length_a
   for i in range(length_a):
       child[i] = p1[i] if random.random() < 0.5 else p2[i]
   return child

def Mutation(assign):         #Flipping a Random Bit
    L = len(assign)
    if L == 0:
        return assign
    i = random.randrange(L)
    assign[i] = 1 - assign[i]
    
    return assign

#=======================================================

# Wisdom Of Crowds Implementation

#=======================================================

def Voting_Experts(population, fits, top=0.2):   #Take the top-k individuals and then count the votes for one bit
    p = len(population)                          #at each position and return outcome
    s = max(1, int(top * p))
    pairs = list(zip(fits, population))
    def first_of_pair(t):
        return t[0]
    pairs.sort(key=first_of_pair, reverse=True)
    elites = [index for (f, index) in pairs[:s]]

    L = len(elites[0])
    one_to_vote = [0] * L
    for index in elites:
        for i, bit in enumerate(index):
            one_to_vote[i] += bit
    return one_to_vote, s

def agreed_assignment(one_to_vote, k):      #The Majority vote for each bit
    return [1 if one_to_vote[i] > (k / 2) else 0 for i in range(len(one_to_vote))]

def flip_and_improve(assign, edges, I=1):   #Flip any bit that will increase the cut_value
    A = assign[:]
    for X in range(I):
        improve = False
        base = cut_value(A, edges)
        for i in range(len(A)):
            A[i] ^= 1
            new = cut_value(A, edges)
            if new > base:
                base = new
                improve = True
            else:
                A[i] ^= 1
        if not improve:
            break
    return A

#=======================================================

# End Of Wisdom Of Crowds Implementation

#=======================================================

def Genetic_Algorithm(population, Fit, Mutate, generation, selection='roulette'):   #The Genetic Algorithm
    for GA in range(generation):
        Fits = [Fit(index) for index in population]

        new_pop = []
        for GA in range(len(population)):
            par1 = Parent_Roulette(population, Fits, selection)
            par2 = Parent_Roulette(population, Fits, selection)
            child = Reproduction(par1, par2)
            if random.random() < Mutate:
                child = Mutation(child)
            new_pop.append(child)

            if (GA + 1) % 25 == 0:    #Wisdom of Crowds: For every 25 generations, input the consensus for each generation
                new_fits = [Fit(t) for t in new_pop]
                one_to_vote, k = Voting_Experts(new_pop, new_fits, top=0.20)
                consensus = agreed_assignment(one_to_vote, k)
                
                worst_index = 0            #Replace the worst person with consensus
                worst_fit = new_fits[0]
                for i in range (1, len(new_pop)):
                    if new_fits[i] < worst_fit:
                        worst_fit = new_fits[i]
                        worst_index = i
                new_pop[worst_index] = consensus

        population = new_pop

    optimal = population[0]
    optimal_fit = Fit(optimal)
    for index in population[1:]:
        f = Fit(index)
        if f > optimal_fit:
            optimal = index
            optimal_fit = f
    return optimal

Set = [('roulette', 0.02), ('roulette', 0.10), ('tournament', 0.02), ('tournament', 0.10)]

for select, mutate_rate in Set:   #2x2 stats with sample run
    cuts = []
    for S in range(10):
        random.seed(S)
        nodes = list_of_nodes()
        population = Initialize_Population(200, nodes)
        Fit = fitness(return_edges)
        optimal = Genetic_Algorithm(population, Fit, Mutate=mutate_rate, generation=500, selection=select)
        cuts.append(Cut(optimal, return_edges))

    min_cut = min(cuts)
    max_cut = max(cuts)
    avg_cut = mean(cuts)
    std_cut = pstdev(cuts)
    

    print(
        f" Selection: {select}\n"
        f" Rate of Mutation: {mutate_rate:.2f}\n"
        f" Runs: 10\n"
        f" Min: {min_cut}\n"
        f" Max: {max_cut}\n"
        f" Average: {avg_cut:.3f}\n"
        f" Standard Deviation: {std_cut:.3f}\n"
        )

Optimal_Assignment = None          #Best Cut for the best setting
Optimal_Cut = -1
for P in range(10):
    random.seed(P)
    nodes = list_of_nodes()
    population = Initialize_Population(200, nodes)
    Fit = fitness(return_edges)
    Assign = Genetic_Algorithm(population, Fit, Mutate=0.10, generation=500, selection='tournament')
    CV = Cut(Assign, return_edges)
    if CV > Optimal_Cut:
        Optimal_Cut = CV
        Optimal_Assignment = Assign[:]


print("Optimal Solution - Tournament (k=5), Mutate = 0.10\n")
print("Cut Value (Edges Crossing):", Optimal_Cut, "\n")
print("First 64 Assigned Bits:", Optimal_Assignment[:64])


