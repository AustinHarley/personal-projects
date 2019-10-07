import pandas as pd
import vscodepandas as vs 

sets = pd.read_csv("sets.csv")

print(vs.colMover(sets,'num_parts','name'))
match = vs.colMatch(sets,'num')
vs.setSort(sets, "num_parts")