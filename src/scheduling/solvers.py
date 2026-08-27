"""Role B: solve via simulated annealing."""
import neal


def solve_simulated_annealing(bqm, num_reads=100):
    sampler = neal.SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=num_reads)
    best = sampleset.first.sample
    selected = {node for node, val in best.items() if val == 1}
    return {"selected": selected, "energy": sampleset.first.energy}