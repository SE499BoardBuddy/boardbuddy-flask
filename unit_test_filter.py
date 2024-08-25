import unittest

from build_filter import build_filter_min_age, build_filter_min_players, build_filter_max_players, build_filter_min_playtime
from build_filter import build_filter_max_playtime, build_filter_min_year, build_filter_max_year, build_filter_match

class testBuildFilter(unittest.TestCase):
    # min_age
    def test_filter_min_age_default(self):
        filter_query = []
        min_age = "6"
        self.assertEqual(build_filter_min_age(filter_query, min_age), [{'range': {'age': {'gte': '6'}}}])

    def test_filter_min_age_none(self):
        filter_query = []
        min_age = None
        self.assertEqual(build_filter_min_age(filter_query, min_age), [])
    
    def test_filter_min_age_empty(self):
        filter_query = []
        min_age = ""
        self.assertEqual(build_filter_min_age(filter_query, min_age), [])
    
    def test_filter_min_age_zero(self):
        filter_query = []
        min_age = "0"
        self.assertEqual(build_filter_min_age(filter_query, min_age), [])
    
    def test_filter_min_age_string(self):
        filter_query = []
        min_age = "test"
        self.assertEqual(build_filter_min_age(filter_query, min_age), [])

    # min_players
    def test_filter_min_players_default(self):
        filter_query = []
        min_players = "4"
        self.assertEqual(build_filter_min_players(filter_query, min_players), [{'range': {'min_players': {'lte': '4'}}}])

    def test_filter_min_players_zero(self):
        filter_query = []
        min_players = "0"
        self.assertEqual(build_filter_min_players(filter_query, min_players), [{'range': {'min_players': {'gte': '0'}}}])

    def test_filter_min_players_none(self):
        filter_query = []
        min_players = None
        self.assertEqual(build_filter_min_players(filter_query, min_players), [])

    def test_filter_min_players_empty(self):
        filter_query = []
        min_players = ""
        self.assertEqual(build_filter_min_players(filter_query, min_players), [])

    def test_filter_min_players_string(self):
        filter_query = []
        min_players = "test"
        self.assertEqual(build_filter_min_players(filter_query, min_players), [])

    # max_players
    def test_filter_max_players_default(self):
        filter_query = []
        max_players = "6"
        self.assertEqual(build_filter_max_players(filter_query, max_players), [{'range': {'max_players': {'gte': '6'}}}])

    def test_filter_max_players_none(self):
        filter_query = []
        max_players = None
        self.assertEqual(build_filter_max_players(filter_query, max_players), [])

    def test_filter_max_players_empty(self):
        filter_query = []
        max_players = ""
        self.assertEqual(build_filter_max_players(filter_query, max_players), [])

    def test_filter_max_players_zero(self):
        filter_query = []
        max_players = "0"
        self.assertEqual(build_filter_max_players(filter_query, max_players), [])

    def test_filter_max_players_string(self):
        filter_query = []
        max_players = "test"
        self.assertEqual(build_filter_max_players(filter_query, max_players), [])

    # min_playtime
    def test_filter_min_playtime_default(self):
        filter_query = []
        min_playtime = "4"
        self.assertEqual(build_filter_min_playtime(filter_query, min_playtime), [{'range': {'min_playtime': {'lte': '4'}}}])

    def test_filter_min_playtime_zero(self):
        filter_query = []
        min_playtime = "0"
        self.assertEqual(build_filter_min_playtime(filter_query, min_playtime), [{'range': {'min_playtime': {'gte': '0'}}}])

    def test_filter_min_playtime_none(self):
        filter_query = []
        min_playtime = None
        self.assertEqual(build_filter_min_playtime(filter_query, min_playtime), [])

    def test_filter_min_playtime_empty(self):
        filter_query = []
        min_playtime = ""
        self.assertEqual(build_filter_min_playtime(filter_query, min_playtime), [])

    def test_filter_min_playtime_string(self):
        filter_query = []
        min_playtime = "test"
        self.assertEqual(build_filter_min_playtime(filter_query, min_playtime), [])

    # max_playtime
    def test_filter_max_playtime_default(self):
        filter_query = []
        max_playtime = "6"
        self.assertEqual(build_filter_max_playtime(filter_query, max_playtime), [{'range': {'max_playtime': {'gte': '6'}}}])

    def test_filter_max_playtime_none(self):
        filter_query = []
        max_playtime = None
        self.assertEqual(build_filter_max_playtime(filter_query, max_playtime), [])
    
    def test_filter_max_playtime_empty(self):
        filter_query = []
        max_playtime = ""
        self.assertEqual(build_filter_max_playtime(filter_query, max_playtime), [])
    
    def test_filter_max_playtime_zero(self):
        filter_query = []
        max_playtime = "0"
        self.assertEqual(build_filter_max_playtime(filter_query, max_playtime), [])
    
    def test_filter_max_playtime_string(self):
        filter_query = []
        max_playtime = "test"
        self.assertEqual(build_filter_max_playtime(filter_query, max_playtime), [])

    # min_year
    def test_filter_min_year_default(self):
        filter_query = []
        min_year = "6"
        self.assertEqual(build_filter_min_year(filter_query, min_year), [{'range': {'year_published': {'gte': '6'}}}])

    def test_filter_min_year_none(self):
        filter_query = []
        min_year = None
        self.assertEqual(build_filter_min_year(filter_query, min_year), [])
    
    def test_filter_min_year_empty(self):
        filter_query = []
        min_year = ""
        self.assertEqual(build_filter_min_year(filter_query, min_year), [])
    
    def test_filter_min_year_zero(self):
        filter_query = []
        min_year = "0"
        self.assertEqual(build_filter_min_year(filter_query, min_year), [])
    
    def test_filter_min_year_string(self):
        filter_query = []
        min_year = "test"
        self.assertEqual(build_filter_min_year(filter_query, min_year), [])

    # max_year
    def test_filter_max_year_default(self):
        filter_query = []
        max_year = "6"
        self.assertEqual(build_filter_max_year(filter_query, max_year), [{'range': {'year_published': {'lte': '6'}}}])

    def test_filter_max_year_none(self):
        filter_query = []
        max_year = None
        self.assertEqual(build_filter_max_year(filter_query, max_year), [])
    
    def test_filter_max_year_empty(self):
        filter_query = []
        max_year = ""
        self.assertEqual(build_filter_max_year(filter_query, max_year), [])
    
    def test_filter_max_year_zero(self):
        filter_query = []
        max_year = "0"
        self.assertEqual(build_filter_max_year(filter_query, max_year), [])
    
    def test_filter_max_year_string(self):
        filter_query = []
        max_year = "test"
        self.assertEqual(build_filter_max_year(filter_query, max_year), [])
    
    # bg_designer, bg_publisher, bg_subdomain
    def test_filter_match_all_empty(self):
        match_query = []
        bg_designer = ''
        bg_publisher = ''
        bg_subdomain = ''
        self.assertEqual(build_filter_match(match_query, bg_designer, bg_publisher, bg_subdomain), [{'match_all': {}}])
    
    def test_filter_match_all_filled(self):
        match_query = []
        bg_designer = 'test'
        bg_publisher = 'test'
        bg_subdomain = 'test'
        self.assertEqual(build_filter_match(match_query, bg_designer, bg_publisher, bg_subdomain), [
            {'match': {'boardgame_designer': 'test'}},
            {'match': {'boardgame_publisher': 'test'}},
            {'match': {'boardgame_subdomain': 'test'}}
        ])
    
    def test_filter_match_only_designer(self):
        match_query = []
        bg_designer = 'test'
        bg_publisher = ''
        bg_subdomain = ''
        self.assertEqual(build_filter_match(match_query, bg_designer, bg_publisher, bg_subdomain), [
            {'match': {'boardgame_designer': 'test'}},
        ])
    
    def test_filter_match_only_publisher(self):
        match_query = []
        bg_designer = ''
        bg_publisher = 'test'
        bg_subdomain = ''
        self.assertEqual(build_filter_match(match_query, bg_designer, bg_publisher, bg_subdomain), [
            {'match': {'boardgame_publisher': 'test'}},
        ])

    def test_filter_match_only_subdomain(self):
        match_query = []
        bg_designer = ''
        bg_publisher = ''
        bg_subdomain = 'test'
        self.assertEqual(build_filter_match(match_query, bg_designer, bg_publisher, bg_subdomain), [
            {'match': {'boardgame_subdomain': 'test'}},
        ])

    def test_filter_match_des_and_pub(self):
        match_query = []
        bg_designer = 'test'
        bg_publisher = 'test'
        bg_subdomain = ''
        self.assertEqual(build_filter_match(match_query, bg_designer, bg_publisher, bg_subdomain), [
            {'match': {'boardgame_designer': 'test'}},
            {'match': {'boardgame_publisher': 'test'}}
        ])

    def test_filter_match_des_and_sub(self):
        match_query = []
        bg_designer = 'test'
        bg_publisher = ''
        bg_subdomain = 'test'
        self.assertEqual(build_filter_match(match_query, bg_designer, bg_publisher, bg_subdomain), [
            {'match': {'boardgame_designer': 'test'}},
            {'match': {'boardgame_subdomain': 'test'}}
        ])

    def test_filter_match_pub_and_sub(self):
        match_query = []
        bg_designer = ''
        bg_publisher = 'test'
        bg_subdomain = 'test'
        self.assertEqual(build_filter_match(match_query, bg_designer, bg_publisher, bg_subdomain), [
            {'match': {'boardgame_publisher': 'test'}},
            {'match': {'boardgame_subdomain': 'test'}}
        ])

from pick_filter import pick_filter_min_age, pick_filter_min_players, pick_filter_max_players, pick_filter_min_playtime, pick_filter_max_playtime

pick_list = [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ]

class testPickFilter(unittest.TestCase):    
    def test_pick_filter_min_age_zero(self):
        min_age = 0
        self.assertEqual(pick_filter_min_age(pick_list, min_age), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_min_age_string(self):
        min_age = '14'
        self.assertEqual(pick_filter_min_age(pick_list, min_age), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_min_age_num(self):
        min_age = 16
        self.assertEqual(pick_filter_min_age(pick_list, min_age), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            }
        ])

    def test_pick_filter_min_playtime_zero(self):
        min_playtime = 0
        self.assertEqual(pick_filter_min_playtime(pick_list, min_playtime), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_min_playtime_string(self):
        min_playtime = '30'
        self.assertEqual(pick_filter_min_playtime(pick_list, min_playtime), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_min_playtime_num(self):
        min_playtime = 60
        self.assertEqual(pick_filter_min_playtime(pick_list, min_playtime), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            }
        ])

    def test_pick_filter_max_playtime_zero(self):
        max_playtime = 0
        self.assertEqual(pick_filter_max_playtime(pick_list, max_playtime), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_max_playtime_string(self):
        max_playtime = '140'
        self.assertEqual(pick_filter_max_playtime(pick_list, max_playtime), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_max_playtime_num  (self):
        max_playtime = 140
        self.assertEqual(pick_filter_max_playtime(pick_list, max_playtime), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
        ])
    
    def test_pick_filter_min_players_zero(self):
        min_players = 0
        self.assertEqual(pick_filter_min_players(pick_list, min_players), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_min_players_string(self):
        min_players = '3'
        self.assertEqual(pick_filter_min_players(pick_list, min_players), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_min_players_num(self):
        min_players = 3
        self.assertEqual(pick_filter_min_players(pick_list, min_players), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
        ])
    
    def test_pick_filter_max_players_string(self):
        max_players = 0
        self.assertEqual(pick_filter_max_players(pick_list, max_players), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_max_players_string(self):
        max_players = '6'
        self.assertEqual(pick_filter_max_players(pick_list, max_players), [
            {
                'min_age': 14,
                'min_playtime': 60,
                'max_playtime': 120,
                'min_players': 1,
                'max_players': 5
            },
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])
    def test_pick_filter_max_players_num(self):
        max_players = 6
        self.assertEqual(pick_filter_max_players(pick_list, max_players), [
            {
                'min_age': 20,
                'min_playtime': 30,
                'max_playtime': 260,
                'min_players': 4,
                'max_players': 8
            }
        ])

if __name__ == '__main__':
    unittest.main()