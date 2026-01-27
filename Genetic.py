import random
import copy
from Constants import MAX_ATTRIBUTE, NUM_ATTRIBUTES

MIN_A = -MAX_ATTRIBUTE
MAX_A = MAX_ATTRIBUTE


class Genetic:
    def __init__(self, pop_size=200, mutation_prob=0.15, elite_size=2):
        self.pop_size = pop_size
        self.base_mutation_prob = mutation_prob
        self.mutation_prob = mutation_prob
        self.elite_size = elite_size

        self.population = []
        self.fitness = []
        self.best_individual = None
        self.best_fitness = -1e18
        self.best_rounds = -1
        self.best_cum = -1e18
        self.diversity_history = []

    def init_population(self, seed=None):
        self.population = [
            [random.randint(MIN_A, MAX_A) for _ in range(NUM_ATTRIBUTES)]
            for _ in range(self.pop_size)
        ]

        if seed is not None:
            self.population[0] = seed[:]

    def calculate_diversity(self):
        # Utilisation d'IAG ici pour m'aider avec la syntaxe
        """Calculate population diversity"""
        if len(self.population) < 2:
            return 0
        
        total_distance = 0
        count = 0
        for i in range(min(50, len(self.population))):
            for j in range(i + 1, min(50, len(self.population))):
                dist = sum(abs(a - b) for a, b in zip(self.population[i], self.population[j]))
                total_distance += dist
                count += 1
        
        return total_distance / count if count > 0 else 0

    def evaluate(self, monster, base_player):
        self.fitness = []
        found4 = False

        for indiv in self.population:
            p = copy.deepcopy(base_player)
            p.attributes = indiv[:]
            rounds, cumulative = monster.mock_fight(p)
            cumulative = float(cumulative)

            fit = 1000.0 * rounds + cumulative
            self.fitness.append((fit, rounds, cumulative))

            if (rounds > self.best_rounds) or (rounds == self.best_rounds and cumulative > self.best_cum):
                self.best_rounds = rounds
                self.best_cum = cumulative
                self.best_fitness = 1000.0 * rounds + cumulative
                self.best_individual = indiv[:]

            if rounds == 4:
                found4 = True

        rounds_list = [r for _, r, _ in self.fitness]
        diversity = self.calculate_diversity()
        self.diversity_history.append(diversity)
        
        print(
            f"GEN: max={max(rounds_list)} avg={sum(rounds_list)/len(rounds_list):.2f} "
            f"best={self.best_rounds} cum={self.best_cum:.2f} div={diversity:.0f}"
        )
        return found4

    def select_parent(self, k=4):
        # Fonction utilitaire suggérée par IA générative
        candidates = random.sample(range(self.pop_size), k)
        best = max(candidates, key=lambda i: self.fitness[i][0])
        return self.population[best][:]

    def crossover(self, p1, p2):
        """Multiple crossover strategies"""
        # aide par IA générative pour suggérer des stratégies de croisement
        strategy = random.random()
        
        if strategy < 0.3:
            return [a if random.random() < 0.5 else b for a, b in zip(p1, p2)]
        elif strategy < 0.6:
            alpha = random.uniform(0.3, 0.7)
            return [int(alpha * a + (1-alpha) * b) for a, b in zip(p1, p2)]
        elif strategy < 0.8:
            points = sorted(random.sample(range(NUM_ATTRIBUTES), 2))
            child = p1[:]
            child[points[0]:points[1]] = p2[points[0]:points[1]]
            return child
        else:
            return [int(random.uniform(min(a, b) - abs(a-b)*0.2, 
                                       max(a, b) + abs(a-b)*0.2))
                    for a, b in zip(p1, p2)]

    def mutate(self, indiv):
        # Aide par IA générative pour la me permettre de briser le plateau obtenu à 3 combats remportés vs le monstre
        if random.random() > self.mutation_prob:
            return indiv

        child = indiv[:]
        mutation_type = random.random()

        if mutation_type < 0.3:
            # Aggressive multi-attribute mutation
            m = random.randint(3, 8)
            idxs = random.sample(range(NUM_ATTRIBUTES), m)
            for i in idxs:
                if random.random() < 0.5:
                    child[i] = random.randint(MIN_A, MAX_A)
                else:
                    step = max(50, MAX_ATTRIBUTE // 4)
                    child[i] = max(MIN_A, min(MAX_A, child[i] + random.randint(-step, step)))
        
        elif mutation_type < 0.6:
            # Gaussian-like mutation
            m = random.randint(4, NUM_ATTRIBUTES)
            idxs = random.sample(range(NUM_ATTRIBUTES), m)
            for i in idxs:
                sigma = MAX_ATTRIBUTE // 3
                delta = int(random.gauss(0, sigma))
                child[i] = max(MIN_A, min(MAX_A, child[i] + delta))
        
        else:
            # Swap and permute
            if NUM_ATTRIBUTES >= 4:
                idxs = random.sample(range(NUM_ATTRIBUTES), min(4, NUM_ATTRIBUTES))
                vals = [child[i] for i in idxs]
                random.shuffle(vals)
                for i, v in zip(idxs, vals):
                    child[i] = v

        return child

    def next_generation(self):
        ranked = sorted(
            zip(self.population, self.fitness),
            key=lambda x: x[1][0],
            reverse=True
        )

        # Elite preservation
        new_pop = [indiv[:] for indiv, _ in ranked[:self.elite_size]]

        # Generate offspring
        while len(new_pop) < self.pop_size:
            p1 = self.select_parent()
            p2 = self.select_parent()
            child = self.crossover(p1, p2)
            child = self.mutate(child)
            new_pop.append(child)

        self.population = new_pop

    def random_restart(self, keep_best=10):
        """Restart with random population but keep best individuals"""
        ranked = sorted(
            zip(self.population, self.fitness),
            key=lambda x: x[1][0],
            reverse=True
        )
        
        new_pop = [indiv[:] for indiv, _ in ranked[:keep_best]]
        
        while len(new_pop) < self.pop_size:
            new_pop.append([random.randint(MIN_A, MAX_A) for _ in range(NUM_ATTRIBUTES)])
        
        self.population = new_pop
        print("*** RANDOM RESTART ***")

    def focused_exploration(self, monster, base_player, center, tries=15000):
        """Systematic exploration around current best"""
        # Fonction générée par IA générative pour m'aider à briser le plateau des 3 combats remportés
        best = center[:]
        p = copy.deepcopy(base_player)
        p.attributes = best
        best_r, best_c = monster.mock_fight(p)
        best_c = float(best_c)
        
        improvements = 0
        
        for trial in range(tries):
            cand = best[:]
            
            # Progressive exploration strategies
            if trial < tries // 3:
                # Extreme random jumps
                m = random.randint(5, NUM_ATTRIBUTES)
                idxs = random.sample(range(NUM_ATTRIBUTES), m)
                for i in idxs:
                    cand[i] = random.randint(MIN_A, MAX_A)
            
            elif trial < 2 * tries // 3:
                # Moderate perturbations
                m = random.randint(3, 7)
                idxs = random.sample(range(NUM_ATTRIBUTES), m)
                for i in idxs:
                    step = random.randint(150, 400)
                    cand[i] = max(MIN_A, min(MAX_A, cand[i] + random.randint(-step, step)))
            
            else:
                # Fine-tuning around best found so far
                m = random.randint(2, 5)
                idxs = random.sample(range(NUM_ATTRIBUTES), m)
                for i in idxs:
                    step = random.randint(50, 150)
                    cand[i] = max(MIN_A, min(MAX_A, cand[i] + random.randint(-step, step)))
            
            p2 = copy.deepcopy(base_player)
            p2.attributes = cand
            r, c = monster.mock_fight(p2)
            c = float(c)
            
            if (r > best_r) or (r == best_r and c > best_c):
                best, best_r, best_c = cand, r, c
                improvements += 1
                if best_r == 4:
                    print(f"Found round 4 in focused exploration after {trial} trials!")
                    return best, best_r, best_c
        
        print(f"Focused exploration: {improvements} improvements found")
        return best, best_r, best_c

    def run(self, monster, base_player, generations=160, seed=None):
        self.init_population(seed)

        stagnant = 0
        last_best_rounds = -1
        last_best_cum = -1e18
        restart_count = 0

        # Aide par IA générative pour la stagnation et suggestion de valeurs de probabilité de mutation
        for gen in range(generations):
            found4 = self.evaluate(monster, base_player)
            if found4:
                print("Found solution with 4 rounds!")
                break

            if self.best_rounds == last_best_rounds and abs(self.best_cum - last_best_cum) < 1e-6:
                stagnant += 1
            else:
                stagnant = 0
                last_best_rounds = self.best_rounds
                last_best_cum = self.best_cum

            if stagnant >= 15:
                self.mutation_prob = min(0.4, self.base_mutation_prob * 2.0)
            elif stagnant >= 10:
                self.mutation_prob = min(0.3, self.base_mutation_prob * 1.5)
            else:
                self.mutation_prob = self.base_mutation_prob

            if len(self.diversity_history) > 5:
                recent_div = self.diversity_history[-5:]
                avg_div = sum(recent_div) / len(recent_div)
                if avg_div < 5000 and stagnant >= 12:  # Low diversity
                    self.random_restart(keep_best=5)
                    restart_count += 1
                    stagnant = 0
                    continue

            self.next_generation()

            # Aide par IA générative pour la diversification
            if stagnant >= 18 and self.best_rounds == 3:
                for i in range(self.pop_size * 2 // 3):
                    self.population[-(i+1)] = [random.randint(MIN_A, MAX_A) 
                                               for _ in range(NUM_ATTRIBUTES)]
                stagnant = 0
                print("*** AGGRESSIVE DIVERSIFICATION ***")

        # Post-evolution refinement
        if self.best_rounds >= 3:
            print(f"\n=== Post-evolution refinement (best={self.best_rounds}) ===")
            if self.best_rounds == 3:
                for attempt in range(3):
                    print(f"\nFocused search attempt {attempt + 1}/3")
                    center, r, c = self.focused_exploration(
                        monster, base_player, self.best_individual, tries=20000
                    )
                    if r > self.best_rounds or (r == self.best_rounds and c > self.best_cum):
                        self.best_individual = center
                        self.best_rounds = r
                        self.best_cum = c
                        print(f"Improved to rounds={r}, cum={c:.4f}")
                    
                    if r == 4:
                        break
            
            for step, tries in [(300, 10000), (150, 10000), (60, 10000)]:
                center, r, c = self.local_search_around(
                    monster, base_player, self.best_individual, tries=tries, step=step
                )
                if r > self.best_rounds or (r == self.best_rounds and c > self.best_cum):
                    self.best_individual = center
                    self.best_rounds = r
                    self.best_cum = c
                    print(f"Local search (step={step}): rounds={r}, cum={c:.4f}")
                
                if r == 4:
                    break

        print(f"\nFinal: rounds={self.best_rounds}, cumulative={self.best_cum:.4f}")
        print(f"Restarts performed: {restart_count}")
        
        return self.best_individual

    def local_search_around(self, monster, base_player, center, tries=3000, step=120):
        # Fonction générée par IA générative pour m'aider à briser le plateau des 3 combats remportés
        best = center[:]
        p = copy.deepcopy(base_player)
        p.attributes = best
        best_r, best_c = monster.mock_fight(p)
        best_c = float(best_c)

        for _ in range(tries):
            cand = best[:]
            m = random.randint(2, 6)
            idxs = random.sample(range(NUM_ATTRIBUTES), m)
            for i in idxs:
                cand[i] = max(MIN_A, min(MAX_A, cand[i] + random.randint(-step, step)))

            p2 = copy.deepcopy(base_player)
            p2.attributes = cand
            r, c = monster.mock_fight(p2)
            c = float(c)

            if (r > best_r) or (r == best_r and c > best_c):
                best, best_r, best_c = cand, r, c
                if best_r == 4:
                    return best, best_r, best_c

        return best, best_r, best_c


def solve_monster(monster, player, attempts=10):
    """Solve with multiple attempts and progressive strategies"""
    # Formatting des logs par IA générative
    best_stats = None
    best_r = -1
    best_c = -1e18

    for t in range(attempts):
        print(f"\n{'='*60}")
        print(f"ATTEMPT {t+1}/{attempts}")
        print(f"{'='*60}")
        
        pop = min(250 + (t * 25), 450)
        mut = min(0.15 + (t * 0.02), 0.35)
        gens = 160 + (t * 10)
        
        ga = Genetic(pop_size=pop, mutation_prob=mut, elite_size=4)
        stats = ga.run(monster, player, generations=gens, seed=best_stats)

        r = ga.best_rounds
        c = ga.best_cum

        if (r > best_r) or (r == best_r and c > best_c):
            best_stats, best_r, best_c = stats, r, c
            print(f"\n*** NEW BEST: Rounds={r}, Cumulative={c:.4f} ***")

        if r == 4:
            print(f"\n*** PERFECT SOLUTION FOUND ON ATTEMPT {t+1}! ***")
            return best_stats

    print(f"\n{'='*60}")
    print(f"FINAL RESULT: Rounds={best_r}, Cumulative={best_c:.4f}")
    print(f"{'='*60}")
    return best_stats