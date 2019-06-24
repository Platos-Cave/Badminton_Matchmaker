import random
import time

class Candidate:
    '''Representing a combination of players, to be tested'''
    def __init__(self, population=[], no_courts=3, attrs=(set(), set(),set()),
                mutation=False, mutationRate = 0.1, players_on_court = []):

        self.courts, self.orange_bench, self.red_bench = attrs
        self.population = population
        self.greens, self.oranges, self.reds = self.population
        self.no_courts = no_courts
        self.mutationRate = mutationRate
        self.players_on_court = players_on_court
        self.tried = False #haven't retrieved fitness yet
        self.fitness = 0
        # self.courts = courts
        # self.orange_bench = set()
        # self.red_bench = set()
        if not mutation:
            self.generate_from_scratch()

    def generate_from_scratch(self):
        # From passed im players, generate a random candidate

        spaces = 4 * self.no_courts
        no_oranges = spaces - len(self.greens)
        random.shuffle(self.oranges)
        poc = self.greens + self.oranges[:no_oranges]
        self.orange_bench = set(self.oranges[no_oranges:])
        self.red_bench = set(self.reds)
        random.shuffle(poc)
        self.players_on_court = poc[:]


        for _ in range(self.no_courts):
            new_court = frozenset(frozenset(poc.pop() for i in range(2)) for
                                  j in range(2))
            self.courts.add(new_court)
            #print(new_court)

        # print(self.courts)
        # print(self.players_on_court)
        # print(self.orange_bench)
        # print(self.red_bench)
        # print('')

    def generate_mutation(self):

        mutated = False

        self.new_courts = set()
        self.new_orange_bench = set()

        self.swappable = self.players_on_court[:]
        self.all_swappable = self.players_on_court + list(self.orange_bench)
        self.original = self.all_swappable[:]

        # print('\n',self.swappable)
        # print(self.all_swappable)
        # print(self.players_on_court)

        for i, plyr in enumerate(self.players_on_court):
            if random.random() < self.mutationRate:
                mutated = True
                index_1 = i
                if plyr in self.greens:
                    while True:
                        index_2 = random.randint(0,len(self.swappable)-1)
                        if index_1 != index_2:
                            break
                if plyr in self.oranges:
                    while True:
                        index_2 = random.randint(0,len(self.all_swappable)-1)
                        if index_1 != index_2:
                            break

                # print(index_1)
                # print(index_2)

                first_swap = self.all_swappable[index_1]
                second_swap = self.all_swappable[index_2]

                # print(first_swap)
                # print(second_swap, '\n')

                self.all_swappable[index_1] = second_swap
                self.all_swappable[index_2] = first_swap

        #print(self.all_swappable)

        if mutated:

            #players on court, to pass to mutant
            poc = self.all_swappable[:12]
            #print(poc)

            final = list(reversed(self.all_swappable))

            for _ in range(self.no_courts):
                new_court = frozenset(frozenset(final.pop() for i in range(2)) for
                                      j in range(2))
                self.new_courts.add(new_court)

            for remainer in final:
                self.new_orange_bench.add(remainer)

            return Candidate(self.population, no_courts=3, attrs=(
                self.new_courts, self.new_orange_bench,
                self.red_bench), mutation=True, players_on_court = poc)

        else:
            return None

    def get_fitness(self):
        # Fitness of the candidate

        if self.tried:
            return self.fitness
        else:
            self.fitness = 0
            #print(self.players_on_court)
            for i in range(self.no_courts):
                court = self.players_on_court[(i*4):(i*4)+4]
                # print(court)
                self.fitness -= 25 * (((court[0] + court[1]) - (court[2] +
                                                                court[
                    3]))**2)
                #self.fitness -= 2 * (max(court) - min(court)) ** 1.5
            self.tried = True
            return self.fitness


population = [[10*random.random() for _ in range(6)],[10*random.random() for
                                                      _ in
                                                      range(12)],
              [10 *random.random() for _ in range(4)]]
# print(population)
# print(len(population[0]))
#Bob = Candidate(population, 3)
# Jim = Candidate(population, 3)
# Jim.get_fitness()
candidates = [Candidate(population, 3) for i in range(20)]

t1 = time.time()

generations = 10000
trials = 0

while trials < generations:
    trials += 1

    mod = 10 ** (len(str(trials)) - 1)  # want to print only 1 sf nums

    # mut_rate = starting_mut / mod

    if (trials%(mod) == 0):
        print(f'\nGeneration {trials}')
        for cand in candidates[:3]:
             print(cand.fitness, [round(c,2) for c in \
                     cand.players_on_court])

# for i in range(1000):
    mutants = []
    for cand in candidates:
        for i in range(1):
            mutant = cand.generate_mutation()
            if mutant:
                mutants.append(mutant)

    new_candidates = candidates[:]

    for mut in mutants:
        if mut.get_fitness() not in [cand.get_fitness() for cand in candidates]:
            new_candidates.append(mut)

    candidates = sorted(new_candidates, key=lambda x: x.get_fitness(),
                        reverse=True)[:20]
    #print([cand.fitness for cand in candidates])
t2 = time.time()

print('\nDone!')
print(candidates[0].players_on_court)
print(candidates[0].fitness)
print(f'Took {t2-t1}')



#new_candidates =



# print("Jim")
# print(Jim.courts)
# print(Jim.orange_bench)
# print(Jim.red_bench)
# print("")


#mutants = [Jim.generate_mutation() for i in range(10)]


# for m in mutants:
#     if m:
#         # print("Mutant")
#         # print(m.courts)
#         # print(m.orange_bench)
#         # print(m.red_bench)
#         b = m.generate_mutation()
#         if b:
#             print("Mutate mutant!")

# print("Jim")
# print(Jim.courts)
# print(Jim.orange_bench)
# print(Jim.red_bench)
# print("")

# t1 = time.time()
# mutants = [Jim.generate_mutation() for i in range(10000)]
#
# t2 = time.time()
# print(t2-t1)










