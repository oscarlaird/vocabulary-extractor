#LEVENSHTEIN
#Based in part on an article on fuzzy string matching by Francisco Javier Carrera Arias at DataCamp.com

#These letters may be interchanged at a discounted cost
phonetic_groups = [['b','p'],['c','k','g'],['m','n'],['d','t'],['c','s','z']]
vowels = ['a','e','i','o','u','y']
def get_sub_cost(c1,c2):
    if c1==c2:
        return 0
    elif [True for g in phonetic_groups if (c1 in g and c2 in g)]:
        return .5
    elif c1 in vowels and c2 in vowels:
        return 1
    else:
        return 2
def get_del_cost(c):
    if c in vowels:
        return .75
    else:
        return 1
def get_ins_cost(c):
    if c in vowels:
        return .75
    else:
        return 1
def distance(s, t, truncate=False):
    #preprocess
    s,t = s.lower(),t.lower()
    if truncate:
        s,t=s[:len(t)],t[:len(s)]
    # Initialize matrix of zeros
    num_rows = len(s)+1
    num_cols = len(t)+1
    distance = [[0 for x in range(num_cols)] for y in range(num_rows)] #initialize matrix

    #first row and first column represent the cost of simple addition
    for i in range(1, num_rows):
        for k in range(1,num_cols):
            distance[i][0] = i
            distance[0][k] = k
    #recursively define the distance between initial segments of the strings
    for col in range(1, num_cols):
        for row in range(1, num_rows):
            sub_cost = get_sub_cost(s[row-1],t[col-1])
            
            distance[row][col] = min(distance[row-1][col] + 1, #deletion
                                 distance[row][col-1] + 1, #insertion
                                 distance[row-1][col-1] + sub_cost) #substitution
    #for r in distance: print(r) #Uncomment to understand the algorithm
    return distance[-1][-1]
def ratio(s,t,truncate=False):
    if truncate:
        num_chars = 2*min(len(s),len(t))
    else:
        num_chars = len(s) + len(t)
    return (num_chars - distance(s,t,truncate)) / num_chars
        