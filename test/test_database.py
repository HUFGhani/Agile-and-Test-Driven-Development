from os import path
import unittest
import networkx as nx

from comp62521.database import database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        dir, _ = path.split(__file__)
        self.data_dir = path.join(dir, "..", "data")

    def test_read(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        self.assertEqual(len(db.publications), 1)

    def test_read_invalid_xml(self):
        db = database.Database()
        self.assertFalse(db.read(path.join(self.data_dir, "invalid_xml_file.xml")))

    def test_read_missing_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_year.xml")))
        self.assertEqual(len(db.publications), 0)

    def test_read_missing_title(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_title.xml")))
        # publications with missing titles should be added
        self.assertEqual(len(db.publications), 1)

    def test_get_average_authors_per_publication(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        _, data = db.get_average_authors_per_publication(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.3, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 2, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MODE)
        self.assertEqual(data[0], [2])

    def test_get_average_publications_per_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        _, data = db.get_average_publications_per_author(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MODE)
        self.assertEqual(data[0], [0, 1, 2, 3])

    def test_get_average_publications_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        _, data = db.get_average_publications_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.5, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [3])

    def test_get_average_authors_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-4.xml")))
        _, data = db.get_average_authors_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.8, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [0, 2, 4, 5])
        # additional test for union of authors
        self.assertEqual(data[-1], [0, 2, 4, 5])

    def test_get_publication_summary(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publication_summary()
        self.assertEqual(len(header)-1, len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data[0]), 6,
            "incorrect number of columns in data")
        self.assertEqual(len(data), 2,
            "incorrect number of rows in data")
        self.assertEqual(data[0][1], 1,
            "incorrect number of publications for conference papers")
        self.assertEqual(data[1][1], 2,
            "incorrect number of authors for conference papers")

    def test_get_average_authors_per_publication_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        header, data = db.get_average_authors_per_publication_by_author(database.Stat.MEAN)
        self.assertEqual(len(header)-1, len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 3,
            "incorrect average of number of conference papers")
        self.assertEqual(data[0][1], 1.5,
            "incorrect mean journals for author1")
        self.assertEqual(data[1][1], 2,
            "incorrect mean journals for author2")
        self.assertEqual(data[2][1], 1,
            "incorrect mean journals for author3")

    def test_get_publications_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_author()
        self.assertEqual(len(header)-1, len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 2,
            "incorrect number of authors")
        self.assertEqual(data[0][-3], 1,
            "incorrect total")
        self.assertEqual(data[0][-2], 1,
            "incorrect number of first author")
        self.assertEqual(data[0][-1], 0,
            "incorrect number of last author")

    def test_get_search_name(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        self.assertEqual(db.get_search_name('aaa'), ('The author you entered does not exist in database', 0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.assertEqual(db.get_search_name('Yoonkyong Lee'), (0, 1, 1, 0, 0, 0, 4, 0, 0, 0))
        self.assertEqual(db.get_search_name('Daniele Braga'), (0, 30, 20, 10, 0, 0, 43, 14, 0, 0))
        self.assertEqual(db.get_search_name('Piero Fraternali'), (0, 49, 29, 18, 1, 1, 49, 0, 7, 0))

    def test_get_detail_information_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        self.assertEqual(db.get_detail_information_by_author('aaa'), (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.assertEqual(db.get_detail_information_by_author('Carole A. Goble'), (199, 115, 79, 5, 0, 405, 17, 72, 7, 10, 42, 4, 6, 27, 2, 0, 0, 0, 1, 3, 1))


    def test_get_average_publications_per_author_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_average_publications_per_author_by_year(database.Stat.MEAN)
        self.assertEqual(len(header)-1, len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_publications_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_year()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_publications_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_author()
        self.assertEqual(len(header)-1, len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 2,
            "incorrect number of authors")
        self.assertEqual(data[0][-4], 1,
            "incorrect total")
        self.assertEqual(data[0][-3], 1,
            "incorrect number of first author")
        self.assertEqual(data[0][-2], 0,
            "incorrect number of last author")
        self.assertEqual(data[0][-1], 0,
            "incorrect number of solo author")

    def test_solo_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        header, data = db.get_publications_by_author()
        self.assertEqual(data[0][-1], 1,
            "incorrect number of solo author1")
        self.assertEqual(data[3][-1], 1,
            "incorrect number of solo author2")
        self.assertEqual(data[1][-1], 0,
            "incorrect number of solo author3")
        self.assertEqual(data[2][-1], 0,
            "incorrect number of solo author4")

    def test_get_author_totals_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_author_totals_by_year()
        self.assertEqual(len(header)-1, len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")
        self.assertEqual(data[0][1], 2,
            "incorrect number of authors in result")

    def test_get_author_publication(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        # Test conference paper
        header, data = db.get_author_publication(0)
        self.assertEqual(data[0][-3], 7,"incorrect number of sole author1 in conference paper")
        header, data = db.get_author_publication(0)
        self.assertEqual(data[0][-2], 28,"incorrect number of first author1 in conference paper")
        header, data = db.get_author_publication(0)
        self.assertEqual(data[0][-1], 10,"incorrect number of last author1 in conference paper")
        header, data = db.get_author_publication(0)
        self.assertEqual(data[1][-3], 0, "incorrect number of sole author2 in conference paper")
        header, data = db.get_author_publication(0)
        self.assertEqual(data[1][-2], 0, "incorrect number of first author2 in conference paper")
        header, data = db.get_author_publication(0)
        self.assertEqual(data[1][-1], 3, "incorrect number of last author2 in conference paper")

        # Test journal article
        header, data = db.get_author_publication(1)
        self.assertEqual(data[0][-3], 0, "incorrect number of sole author1 in journal article")
        header, data = db.get_author_publication(1)
        self.assertEqual(data[0][-2], 43, "incorrect number of first author1 in journal article")
        header, data = db.get_author_publication(1)
        self.assertEqual(data[0][-1], 10, "incorrect number of last author1 in journal article")

        # Test Book
        header, data = db.get_author_publication(2)
        self.assertEqual(data[0][-3], 0, "incorrect number of sole author1 in book")
        header, data = db.get_author_publication(2)
        self.assertEqual(data[0][-2], 3 , "incorrect number of first author1 in book")
        header, data = db.get_author_publication(2)
        self.assertEqual(data[0][-1], 0, "incorrect number of last author1 in book")

       # Test book chapter
        header, data = db.get_author_publication(3)
        self.assertEqual(data[0][-3], 1, "incorrect number of sole author1 in book chapter")
        header, data = db.get_author_publication(3)
        self.assertEqual(data[0][-2], 4, "incorrect number of first author1 in book chapter")
        header, data = db.get_author_publication(3)
        self.assertEqual(data[0][-1], 5, "incorrect number of last author1 in book chapter")

        # Test all publications
        header, data = db.get_author_publication(4)
        self.assertEqual(data[0][-3], 8, "incorrect number of sole author1 in all publications ")
        header, data = db.get_author_publication(4)
        self.assertEqual(data[0][-2], 78, "incorrect number of first author1 in all publications")
        header, data = db.get_author_publication(4)
        self.assertEqual(data[0][-1], 25, "incorrect number of last author1 in all publications")

    def test_get_fuzzy_search_name(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        # Test an author that does not exist in database
        self.assertEqual(db.get_search_name(db.get_fuzzy_search_name('aaa')),('The author you entered does not exist in database', 0, 0, 0, 0, 0, 0, 0, 0, 0))
        # Test an author that is the only searching results
        author_names = db.get_fuzzy_search_name('Richard Cooper')
        self.assertEqual(db.get_search_name(author_names[0]), (0, 6, 4, 2, 0, 0, 11, 1, 0, 0))
        # Test an author was part of a name and matches several authors in database
        author_names=db.get_fuzzy_search_name('Daniele')
        author_names.sort()
        self.assertEqual(db.get_search_name(author_names[0]), (0, 30, 20, 10, 0, 0, 43, 14, 0, 0))

    def test_show_all_shortest_paths(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        self.assertEqual(db.show_all_shortest_paths('AUTHOR1','AUTHOR2'),[[u'AUTHOR1', u'AUTHOR2']])
        self.assertEqual(db.show_all_shortest_paths('AUTHOR3','AUTHOR4'),[[u'AUTHOR3', u'AUTHOR1', u'AUTHOR4'], [u'AUTHOR3', u'AUTHOR2', u'AUTHOR4']])

    def test_get_degree_of_separation(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        self.assertEqual(db.get_degree_of_separation('AUTHOR1','AUTHOR2'),(0))
        self.assertEqual(db.get_degree_of_separation('AUTHOR3','AUTHOR4'),(1))

if __name__ == '__main__':
    unittest.main()

