import pandas as pd 

def setSort(df, column):
    col = str(column)
    top = df.sort_values(by=[col], ascending=False)[:10]
    return top[['name',col]]

def colMover(df, column, destColumn):
    cols = list(df)
    index = int(cols.index(str(destColumn))) + 1 #index number of desination colum +1 to move to right 
    cols.insert(index, cols.pop(cols.index(str(column)))) # move column using index, pop and insert
    df = df.ix[:, cols]
    return df

def colMatch(df, partial):
    partial = partial.upper()
    cols =  list(df.columns)
    upper = [x.upper() for x in cols]
    found = []
    for i in upper:
        if partial in i:
            ind = upper.index(i)
            name = cols[ind]
            found.append(name)
    if len(found) > 1:
        print('*** Column Matcher Error: check for duplicates ***\n\t' + str(found))
    elif len(found) == 1:
        return name