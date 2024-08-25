def pick_filter_min_age(return_list, min_age):
    if min_age and min_age != 0 and type(min_age) == int:
        return_list = [item for item in return_list if item["min_age"] <= min_age]
    return return_list

def pick_filter_min_playtime(return_list, min_playtime):
    if min_playtime and min_playtime != 0 and type(min_playtime) == int:
        return_list = [item for item in return_list if item["min_playtime"] >= min_playtime]
    return return_list

def pick_filter_max_playtime(return_list, max_playtime):
    if max_playtime and max_playtime != 0 and type(max_playtime) == int:
        return_list = [item for item in return_list if item["max_playtime"] <= max_playtime]
    return return_list

def pick_filter_min_players(return_list, min_players):
    if min_players and min_players != 0 and type(min_players) == int:
        return_list = [item for item in return_list if item["min_players"] <= min_players]
    return return_list

def pick_filter_max_players(return_list, max_players):
    if max_players and max_players != 0 and type(max_players) == int:
        return_list = [item for item in return_list if item["max_players"] >= max_players]
    return return_list