import pandas as pd
import vscodepandas as vs 

sets = pd.read_csv("sets.csv")



print(vs.colMover(sets,'num_parts','name'))
print(vs.colMatch(sets,'part'))
vs.setSort(sets, "num_parts")