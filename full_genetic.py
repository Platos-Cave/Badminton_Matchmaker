import random
import time
from enumerate_b import score_court, tolerance_cost, bench_cost, final_game_cost
from math import log
import sys
import b_scorer


class Candidate:
    '''Representing a combination of players, to be tested'''
    def __init__(self, population=[], no_courts=3, attrs=(set(), set(),set()),
                mutation=False, mutationRate = 0.01, players_on_court = []):

        self.courts, self.orange_bench, self.red_bench = attrs
        self.population = population
        self.greens, self.oranges, self.reds = self.population
        self.no_courts = no_courts
        self.mutationRate = mutationRate
        self.players_on_court = players_on_court
        self.tried = False #haven't retrieved fitness yet
        self.fitness = 0
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

    def generate_mutation(self, mutrate):
        mutated = False

        self.new_courts = set()
        self.new_orange_bench = set()

        self.swappable = self.players_on_court[:]
        self.all_swappable = self.players_on_court + list(self.orange_bench)
        self.original = self.all_swappable[:]

        muts = 0

        for i, plyr in enumerate(self.players_on_court):
            if random.random() < self.mutationRate:
                mutated = True
                index_1 = i
                if self.all_swappable[i] in self.greens:
                    # should only be swappable with other players on the
                    # court - not to the bench
                    while True:
                        index_2 = random.randint(0,len(self.swappable)-1)
                        if index_1 != index_2:
                            break
                elif self.all_swappable[i] in self.oranges:
                    while True:
                        index_2 = random.randint(0,len(self.all_swappable)-1)
                        if index_1 != index_2:
                            break
                else:
                    print("Not in either??")
                    sys.exit(1)
                # print(index_1)
                # print(index_2)

                first_swap = self.all_swappable[index_1]
                second_swap = self.all_swappable[index_2]

                # print(first_swap)
                # print(second_swap, '\n')

                self.all_swappable[index_1] = second_swap
                self.all_swappable[index_2] = first_swap

                muts +=1

        if mutated:

            #players on court, to pass to mutant
            poc = self.all_swappable[:(4*self.no_courts)]
            #print(poc)

            final = list(reversed(self.all_swappable))

            for _ in range(self.no_courts):
                new_court = frozenset(frozenset(final.pop() for i in range(2)) for
                                      j in range(2))
                self.new_courts.add(new_court)

            for remainer in final:
                self.new_orange_bench.add(remainer)
                if (remainer in self.greens):
                    print("Problem!")
                    print("no muts", muts)
                    print(index_1, index_2)
                    print(remainer.name)
                    print([p.name for p in self.swappable])
                    print([p.name for p in self.all_swappable])
                    sys.exit()



            return Candidate(self.population, no_courts=self.no_courts, attrs=(
                self.new_courts, self.new_orange_bench,
                self.red_bench), mutation=True, mutationRate = mutrate,
                             players_on_court = poc)

        else:
            return None

    def get_fitness_OLD(self):
        # Fitness of the candidate

        if self.tried:
            return self.fitness
        else:
            self.fitness = 0
            #print(self.players_on_court)
            for i in range(self.no_courts):
                court = self.players_on_court[(i*4):(i*4)+4]
                print("Court is", court)
                # print(court)
                self.fitness -= 25 * (((court[0] + court[1]) - (court[2] +
                                                                court[
                    3]))**2)
                #self.fitness -= 2 * (max(court) - min(court)) ** 1.5
            self.tried = True
            return self.fitness

    def get_fitness(self, verbose=False):
        if (self.tried) and not verbose:
            return self.fitness
        else:
            self.fitness = 0
            scores = 0
            for i in range(self.no_courts):
                court = self.players_on_court[(i*4):(i*4)+4]

                set_court = frozenset([frozenset([court[0], court[1]]),
                                      frozenset([court[2], court[3]])])
                try:
                    score = score_dict[set_court]
                except KeyError:
                    score = score_court(court, trial_players=None, unpack=False)
                    score_dict[set_court] = score

                scores -= score

            self.fitness += scores

            self.fitness -= tolerance_cost(self.players_on_court)
            bench = self.orange_bench.union(self.red_bench)

            if b_scorer.final_round_boost:
                self.fitness += final_game_cost(list(bench))
                self.fitness += final_game_cost(self.players_on_court)
            else:
                self.fitness += bench_cost(list(bench))
                self.fitness += bench_cost(self.players_on_court)

            if verbose:
                print("Court Scores", -scores)
                # print(tolerance_cost(self.players_on_court))
                # print(bench_cost(list(bench)))
                # print(bench_cost(self.players_on_court))
                # print("")

            self.tried = True

            return self.fitness


def gen_population(court_num=3):
    population = [[10*random.random() for _ in range(court_num*2)],
                  [10*random.random() for _ in range(court_num*4)],
                  [10*random.random() for _ in range(court_num)]]
    return population


def run_ga(population, court_num=3, cands=1, mutRate=0.1, max_time=2.5):

    global score_dict
    score_dict = {}

    original_mut = mutRate

    candidates = [Candidate(population, no_courts=court_num,
                            mutationRate=mutRate) for i in range(cands)]

    t1 = time.time()
    generation_times = 0


    generations = 100000000000
    trials = 0

    while trials < generations:
        trials += 1

        mod = 10 ** (len(str(trials)) - 1)  # want to print only 1 sf nums

        # mut_rate = starting_mut / mod

        # if trials==1000:
        #     mutRate = mutRate/5
        mutRate = original_mut/log(trials + 2)


        if (trials%(mod) == 0):

            print(f'\nGeneration {trials}')
            for cand in candidates[:3]:
                print(cand.fitness, [c.name for c in \
                          cand.players_on_court])
                cand.get_fitness(verbose=True)
                 # print(cand.fitness, [round(c,2) for c in \
            print(len(score_dict.keys()))
            print("Mutation Rate", mutRate)
        #t = time.perf_counter()

                 #         cand.players_on_court])
    # for i in range(1000):
        mutants = []
        for cand in candidates:
            for i in range(1):

                mutant = cand.generate_mutation(mutrate=mutRate)
                if mutant:
                    mutants.append(mutant)


        new_candidates = candidates[:]


        for mut in mutants:
            t= time.perf_counter()
            if mut.get_fitness() not in [cand.get_fitness() for cand in candidates]:
                new_candidates.append(mut)
            tt = time.perf_counter()
            generation_times += tt - t

        candidates = sorted(new_candidates, key=lambda x: x.get_fitness(),
                            reverse=True)[:cands]



        if (time.time() - t1) > max_time:
            # print(f"Finished at trial {trials}")
            break

        #print([cand.fitness for cand in candidates])
    t2 = time.time()

    print('\nDone!')
    print([c.name for c in candidates[0].players_on_court])
    print(candidates[0].fitness)
    print(f'Took {t2-t1}')
    print(f'Getting fitness took {generation_times}!')
    return candidates[0]

def run_experiment(experiments=10, trials=10):
    fitnesses = []

    single_pop = [gen_population(court_num=4) for i in range(trials)]

    for i in range(experiments):
        this_fitness = 0
        # max_time_ = (i+1)/10
        max_time_ = 2
        mutRate_ = (i+1)/100
        for j in range(trials):
            this_fitness += run_ga(court_num=4, max_time = max_time_,
                                   population=single_pop[i], cands=10,
                                   mutRate=mutRate_).fitness

        fitness = this_fitness / trials

        print(f"Fitness over {mutRate_} mutRate: {fitness}")
        fitnesses.append(fitness)

    print(fitnesses)

score_dict = {}








