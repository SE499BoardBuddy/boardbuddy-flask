# min_age
def build_filter_min_age(array, min_age):
    try:
        if min_age != None and len(min_age) != 0 and int(min_age) > 0:
            array.append({ "range": { "age": { "gte": min_age }}})
        return array
    except ValueError:
        return array

# min_players
def build_filter_min_players(array, min_players):
    try:
        if min_players != None and len(min_players) != 0:
            if int(min_players) > 0:
                array.append({ "range": { "min_players": { "lte": min_players }}})
            else:
                array.append({ "range": { "min_players": { "gte": min_players }}})
        return array
    except ValueError:
        return array

# max_players
def build_filter_max_players(array, max_players):
    try:
        if max_players != None and len(max_players) != 0 and int(max_players) > 0:
            array.append({ "range": { "max_players": { "gte": max_players }}})
        return array
    except ValueError:
        return array
    
# min_playtime
def build_filter_min_playtime(array, min_playtime):
    try:
        if min_playtime != None and len(min_playtime) != 0:
            if int(min_playtime) > 0:
                array.append({ "range": { "min_playtime": { "lte": min_playtime }}})
            else:
                array.append({ "range": { "min_playtime": { "gte": min_playtime }}})
        return array
    except ValueError:
        return array

# max_playtime
def build_filter_max_playtime(array, max_playtime):
    try:
        if max_playtime != None and len(max_playtime) != 0 and int(max_playtime) > 0:
            array.append({ "range": { "max_playtime": { "gte": max_playtime }}})
        return array
    except ValueError:
        return array
    
# min_year
def build_filter_min_year(array, min_year):
    try:
        if min_year != None and len(min_year) != 0 and int(min_year) > 0:
            array.append({ "range": { "year_published": { "gte": min_year }}})
        return array
    except ValueError:
        return array
    
# max_year
def build_filter_max_year(array, max_year):
    try:
        if max_year != None and len(max_year) != 0 and int(max_year) > 0:
            array.append({ "range": { "year_published": { "lte": max_year }}})
        return array
    except ValueError:
        return array

# bg_designer
# bg_publisher
# bg_subdomain
def build_filter_match(array, bg_designer, bg_publisher, bg_subdomain):
    if (bg_designer == None or len(bg_designer) == 0)\
        and (bg_publisher == None or len(bg_publisher) == 0)\
        and (bg_subdomain == None or len(bg_subdomain) == 0):
        array.append({ "match_all": {} })
    else:
        if bg_designer != None and len(bg_designer) != 0:
            array.append({ "match": { "boardgame_designer": bg_designer }})
        if bg_publisher != None and len(bg_publisher) != 0:
            array.append({ "match": { "boardgame_publisher": bg_publisher }})
        if bg_subdomain != None and len(bg_subdomain) != 0:
            array.append({ "match": { "boardgame_subdomain": bg_subdomain }})
    return array