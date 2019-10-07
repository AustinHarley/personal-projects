import pandas as pd 

def setSort(df, column):
    col = str(column)
    top = df.sort_values(by=[col], ascending=False)[:10]
    print(top[['name',col]])

def colMover(df, column, destColumn):
    cols = list(df)
    index = int(cols.index(str(destColumn))) + 1 #index number of desination colum +1 to move to right 
    cols.insert(index, cols.pop(cols.index(str(column)))) # move column using index, pop and insert
    df = df.ix[:, cols]
    return df

def colMatch(df, partial):
    cols = list(df.columns)
    found = []
    for i in cols:
        if partial in i:
            ind = cols.index(i)
            name = cols[ind]
            found.append(name)
    if len(found) > 1:
        print('\ncheck for duplicates')
        return found
    elif len(found) == 1:
        return name