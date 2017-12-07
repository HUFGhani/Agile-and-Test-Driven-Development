from comp62521.statistics import average
import itertools
import numpy as np
import networkx as nx
from xml.sax import handler, make_parser, SAXException


PublicationType = [
    "Conference Paper","Conference Paper", "Journal", "Book", "Book Chapter"]

class Publication:
    CONFERENCE_PAPER = 0
    JOURNAL = 1
    BOOK = 2
    BOOK_CHAPTER = 3

    def __init__(self, pub_type, title, year, authors):
        self.pub_type = pub_type
        self.title = title
        if year:
            self.year = int(year)
        else:
            self.year = -1
        self.authors = authors

class Author:
    def __init__(self, name):
        self.name = name

class Stat:
    STR = ["Mean", "Median", "Mode"]
    FUNC = [average.mean, average.median, average.mode]
    MEAN = 0
    MEDIAN = 1
    MODE = 2

class Database:
    def read(self, filename):
        self.publications = []
        self.authors = []
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

        handler = DocumentHandler(self)
        parser = make_parser()
        parser.setContentHandler(handler)
        infile = open(filename, "r")
        valid = True
        try:
            parser.parse(infile)
        except SAXException as e:
            valid = False
            print "Error reading file (" + e.getMessage() + ")"
        infile.close()

        for p in self.publications:
            if self.min_year == None or p.year < self.min_year:
                self.min_year = p.year
            if self.max_year == None or p.year > self.max_year:
                self.max_year = p.year

        return valid

    def get_all_authors(self):
        return self.author_idx.keys()

    def get_coauthor_data(self, start_year, end_year, pub_type):
        coauthors = {}
        for p in self.publications:
            if ((start_year == None or p.year >= start_year) and
                (end_year == None or p.year <= end_year) and
                (pub_type == 4 or pub_type == p.pub_type)):
                for a in p.authors:
                    for a2 in p.authors:
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])
        def display(db, coauthors, author_id):
            return "%s (%d)" % (db.authors[author_id].name, len(coauthors[author_id]))

        header = ("Author", "Co-Authors")
        data = []
        for a in coauthors:
            data.append([ display(self, coauthors, a),
                ", ".join([
                    display(self, coauthors, ca) for ca in coauthors[a] ]) ])

        return (header, data)

    def get_average_authors_per_publication(self, av):
        header = ("Conference Paper", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ func(auth_per_pub[i]) for i in np.arange(4) ] + [ func(list(itertools.chain(*auth_per_pub))) ]
        return (header, data)

    def get_average_publications_per_author(self, av):
        header = ("Conference Paper","Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))

        for p in self.publications:
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(pub_per_auth[:, i]) for i in np.arange(4) ] + [ func(pub_per_auth.sum(axis=1)) ]
        return (header, data)

    def get_average_publications_in_a_year(self, av):
        header = ("Conference Paper","Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        ystats = np.zeros((int(self.max_year) - int(self.min_year) + 1, 4))

        for p in self.publications:
            ystats[p.year - self.min_year][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(4) ] + [ func(ystats.sum(axis=1)) ]
        return (header, data)

    def get_author_publication(self, pub_type):
        header = ("Author","Author", "Number of sole author", "Number of first author", "Number of last author")
        astats = [[0, 0, 0, 0, 0, 0, 0] for _ in range(len(self.authors))]
        for p in self.publications:
            if (pub_type == 4 or pub_type == p.pub_type):
                for a in p.authors:

                    astats[a][p.pub_type] += 1

                    if a == p.authors[0] and len(p.authors) == 1:
                        astats[a][4] += 1
                    elif a == p.authors[0]:
                        astats[a][5] += 1
                    elif a == p.authors[-1]:
                        astats[a][6] += 1
        data = [[self.authors[i].name] + astats[i][4:7]
                for i in range(len(astats))]

        return (header, data)



    def get_average_authors_in_a_year(self, av):
        header = ("Conference Paper","Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        yauth = [ [set(), set(), set(), set(), set()] for _ in range(int(self.min_year), int(self.max_year) + 1) ]

        for p in self.publications:
            for a in p.authors:
                yauth[p.year - self.min_year][p.pub_type].add(a)
                yauth[p.year - self.min_year][4].add(a)

        ystats = np.array([ [ len(S) for S in y ] for y in yauth ])

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(5) ]
        return (header, data)

    def get_publication_summary_average(self, av):
        header = ("Details","Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))
        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        name = Stat.STR[av]
        func = Stat.FUNC[av]

        data = [
            [name + " authors per publication"]
                + [ func(auth_per_pub[i]) for i in np.arange(4) ]
                + [ func(list(itertools.chain(*auth_per_pub))) ],
            [name + " publications per author"]
                + [ func(pub_per_auth[:, i]) for i in np.arange(4) ]
                + [ func(pub_per_auth.sum(axis=1)) ] ]
        return (header, data)

    def get_publication_summary(self):
        header = ("Details","Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "Total")

        plist = [0, 0, 0, 0]
        alist = [set(), set(), set(), set()]

        for p in self.publications:
            plist[p.pub_type] += 1
            for a in p.authors:
                alist[p.pub_type].add(a)
        # create union of all authors
        ua = alist[0] | alist[1] | alist[2] | alist[3]

        data = [
            ["Number of publications"] + plist + [sum(plist)],
            ["Number of authors"] + [ len(a) for a in alist ] + [len(ua)] ]
        return (header, data)

    def get_average_authors_per_publication_by_author(self, av):
        header = ("Author","Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "All publications")

        astats = [ [[], [], [], []] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [self.authors[i].name]
            + [ func(L) for L in astats[i] ]
            + [ func(list(itertools.chain(*astats[i]))) ]
            for i in range(len(astats)) ]
        return (header, data)


    def get_publications_by_author(self):
        header = ("Author","Surname","Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total","Number of the first author","Number of the last author","Solo Author")

        astats = [ [0, 0, 0, 0, 0, 0, 0] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type] += 1
                
                if a == p.authors[0]and len(p.authors) != 1:
                    astats[a][4] += 1
                if a == p.authors[-1]and len(p.authors) != 1:
                    astats[a][5] += 1
                if a == p.authors[0] and len(p.authors) == 1:
                    astats[a][6] += 1

        data = [ [self.authors[i].name] + astats[i][0:4] + [sum(astats[i][0:4])] + astats[i][4:7]
            for i in range(len(astats)) ]
        return (header, data)

    def get_average_authors_per_publication_by_year(self, av):
        header = ("Year","Year" "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type].append(len(p.authors))
            except KeyError:
                ystats[p.year] = [[], [], [], []]
                ystats[p.year][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(L) for L in ystats[y] ]
            + [ func(list(itertools.chain(*ystats[y]))) ]
            for y in ystats ]
        return (header, data)

    def get_publications_by_year(self):
        header = ("Year","Year" "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type] += 1
            except KeyError:
                ystats[p.year] = [0, 0, 0, 0]
                ystats[p.year][p.pub_type] += 1

        data = [ [y] + ystats[y] + [sum(ystats[y])] for y in ystats ]
        return (header, data)

    def get_fuzzy_search_name(self,author):
        author_names=[]
        if author is not None:
            for a in self.authors:
                if author.lower() in a.name.lower():
                   author_names.append(a.name)

        return author_names

    def get_search_name(self,author):
        allpublications=0
        conference_papers=0
        journal_articles=0
        book_chapters=0
        books=0
        co_authors=0
        first=0
        last=0
        sole=0
        error_message=0

        astats = [[0, 0, 0, 0, 0, 0, 0, 0, 0] for _ in range(len(self.authors))]
        coauthors = {}
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type+1] += 1

                if a == p.authors[0] and len(p.authors) != 1:
                    astats[a][6] += 1
                elif a == p.authors[-1] and len(p.authors) != 1:
                    astats[a][7] += 1
                elif a == p.authors[0] and len(p.authors) == 1:
                   astats[a][8] += 1

                for a2 in p.authors:
                    if a != a2:
                        try:
                            coauthors[a].add(a2)
                        except KeyError:
                            coauthors[a] = set([a2])
                astats[a][5]=len(coauthors[a])

            for a in p.authors:
                astats[a][0]=sum(astats[a][1:5])

        data=[ astats[i] for i in range(len(astats))]
        for i in range(len(data)):
            if self.authors[i].name == author:
                allpublications = data[i][0]
                conference_papers = data[i][1]
                journal_articles = data[i][2]
                books = data[i][3]
                book_chapters = data[i][4]
                co_authors = data[i][5]
                first = data[i][6]
                last = data[i][7]
                sole = data[i][8]
                error_message = 0
                break
            else:
                error_message = 'The author you entered does not exist in database'

        return (error_message,allpublications,conference_papers,journal_articles,book_chapters,books,co_authors,first,last,sole)

    def get_detail_information_by_author(self,author):
        allpublications = 0 #a [0]
        conference_papers = 0 #a [1]
        journal_articles = 0 #a [2]
        books = 0 #a [3]
        book_chapters = 0 #a [4]

        co_authors=0 #a [5]

        allpublications_first = 0 #a [6]
        allpublications_last = 0 #a [7]
        allpublications_solo = 0 #a [8]

        conference_papers_first = 0 #a [9]
        conference_papers_last = 0 #a [10]
        conference_papers_solo = 0 #a [11]

        journal_articles_first = 0 #a [12]
        journal_articles_last = 0 #a [13]
        journal_articles_solo = 0 #a [14]

        books_first = 0 #a [15]
        books_last = 0 #a [16]
        books_solo = 0 #a [17]

        book_chapters_first = 0 #a [18]
        book_chapters_last = 0 #a [19]
        book_chapters_solo = 0 #a [20]


        astats = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] for _ in range(len(self.authors))]
        coauthors = {}
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type+1] += 1

                astats[a][0]=sum(astats[a][1:5])

                for a2 in p.authors:
                    if a != a2:
                        try:
                            coauthors[a].add(a2)
                        except KeyError:
                            coauthors[a] = set([a2])
                astats[a][5]=len(coauthors[a])

                if a == p.authors[0] and len(p.authors) != 1:
                    astats[a][6] += 1
                if a == p.authors[-1] and len(p.authors) != 1:
                    astats[a][7] += 1
                if a == p.authors[0] and len(p.authors) == 1:
                    astats[a][8] += 1

                #Journal ArticalsS
                if p.pub_type == 1:
                    if a == p.authors[0] and len(p.authors) != 1:
                        astats[a][12] += 1
                    if a == p.authors[-1] and len(p.authors) != 1:
                        astats[a][13] += 1
                    if a == p.authors[0] and len(p.authors) == 1:
                        astats[a][14] += 1

                #Conference Papers
                if p.pub_type == 0:
                    if a == p.authors[0] and len(p.authors) != 1:
                        astats[a][9] += 1
                    if a == p.authors[-1] and len(p.authors) != 1:
                        astats[a][10] += 1
                    if a == p.authors[0] and len(p.authors) == 1:
                        astats[a][11] += 1

                #Book
                if p.pub_type == 2:
                    if a == p.authors[0] and len(p.authors) != 1:
                        astats[a][15] += 1
                    if a == p.authors[-1] and len(p.authors) != 1:
                        astats[a][16] += 1
                    if a == p.authors[0] and len(p.authors) == 1:
                        astats[a][17] += 1
                           
                #Book chapter
                if p.pub_type == 3:
                    if a == p.authors[0] and len(p.authors) != 1:
                        astats[a][18] += 1
                    if a == p.authors[-1] and len(p.authors) != 1:
                        astats[a][19] += 1
                    if a == p.authors[0] and len(p.authors) == 1:
                        astats[a][20] += 1



        data=[ astats[i] for i in range(len(astats))]
        for i in range(len(data)):
            if author == self.authors[i].name:
                allpublications = data[i][0]
                conference_papers = data[i][1]
                journal_articles = data[i][2]
                books = data[i][3]
                book_chapters = data[i][4]
                co_authors = data[i][5]

                allpublications_first = data[i][6]
                allpublications_last = data[i][7]
                allpublications_solo = data[i][8]

                conference_papers_first = data[i][9]
                conference_papers_last = data[i][10]
                conference_papers_solo = data[i][11]

                journal_articles_first = data[i][12]
                journal_articles_last = data[i][13]
                journal_articles_solo = data[i][14]

                books_first = data[i][15]
                books_last = data[i][16]
                books_solo = data[i][17]

                book_chapters_first = data[i][18]
                book_chapters_last = data[i][19]
                book_chapters_solo = data[i][20]

        return (allpublications,conference_papers,journal_articles,book_chapters,books,co_authors,
                allpublications_first,allpublications_last,allpublications_solo,
                conference_papers_first,conference_papers_last,conference_papers_solo,
                journal_articles_first,journal_articles_last,journal_articles_solo,
                books_first,books_last,books_solo,
                book_chapters_first,book_chapters_last,book_chapters_solo)

    def get_average_publications_per_author_by_year(self, av):
        header = ("Year","Year", "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year]
            except KeyError:
                s = np.zeros((len(self.authors), 4))
                ystats[p.year] = s
            for a in p.authors:
                s[a][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(ystats[y][:, i]) for i in np.arange(4) ]
            + [ func(ystats[y].sum(axis=1)) ]
            for y in ystats ]
        return (header, data)

    def get_author_totals_by_year(self):
        header = ("Year","Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year][p.pub_type]
            except KeyError:
                ystats[p.year] = [set(), set(), set(), set()]
                s = ystats[p.year][p.pub_type]
            for a in p.authors:
                s.add(a)
        data = [ [y] + [len(s) for s in ystats[y]] + [len(ystats[y][0] | ystats[y][1] | ystats[y][2] | ystats[y][3])]
            for y in ystats ]
        return (header, data)

    def add_publication(self, pub_type, title, year, authors):
        if year == None or len(authors) == 0:
            print "Warning: excluding publication due to missing information"
            print "    Publication type:", PublicationType[pub_type]
            print "    Title:", title
            print "    Year:", year
            print "    Authors:", ",".join(authors)
            return
        if title == None:
            print "Warning: adding publication with missing title [ %s %s (%s) ]" % (PublicationType[pub_type], year, ",".join(authors))
        idlist = []
        for a in authors:
            try:
                idlist.append(self.author_idx[a])
            except KeyError:
                a_id = len(self.authors)
                self.author_idx[a] = a_id
                idlist.append(a_id)
                self.authors.append(Author(a))
        self.publications.append(
            Publication(pub_type, title, year, idlist))
        if (len(self.publications) % 100000) == 0:
            print "Adding publication number %d (number of authors is %d)" % (len(self.publications), len(self.authors))

        if self.min_year == None or year < self.min_year:
            self.min_year = year
        if self.max_year == None or year > self.max_year:
            self.max_year = year

    def _get_collaborations(self, author_id, include_self):
        data = {}
        for p in self.publications:
            if author_id in p.authors:
                for a in p.authors:
                    try:
                        data[a] += 1
                    except KeyError:
                        data[a] = 1
        if not include_self:
            del data[author_id]
        return data

    def get_coauthor_details(self, name):
        author_id = self.author_idx[name]
        data = self._get_collaborations(author_id, True)
        return [ (self.authors[key].name, data[key])
            for key in data ]

    def get_coauthor(self, authorname):
        if authorname in self.author_idx:
            author_id = self.author_idx[authorname]
            data = self._get_collaborations(author_id, True)
            coauthors = [self.authors[item].name for item in data]
            coauthors.remove(authorname)
            return coauthors
        return None

    def convert_to_graph(self, data):
        graph = nx.Graph()
        for item in data:
            for i in range(len(item)):
                for j in range(len(item)):
                    if i != j:
                        graph.add_edge(item[i], item[j])
        return graph

    def degree_of_separation(self, graph, start, end):
        path = nx.all_pairs_shortest_path(graph)
        try:
            degree = len(path[start][end]) - 2
        except KeyError:
            degree = 'X'
        return degree

    def get_degree_of_separation(self, author1, author2):
        all_authors = [a.name for a in self.authors]
        if author1 in all_authors and author2 in all_authors:
            coauthors = [p.authors for p in self.publications]
            graph = self.convert_to_graph(coauthors)
            degree = self.degree_of_separation(graph, all_authors.index(author1), all_authors.index(author2))
            return degree
        return None

    def show_all_shortest_paths(self, author1, author2):
        all_authors = [a.name for a in self.authors]
        if author1 in all_authors and author2 in all_authors:
            coauthors = [p.authors for p in self.publications]
            graph = self.convert_to_graph(coauthors)
            paths = self.all_shortest_paths(graph, all_authors.index(author1), all_authors.index(author2))
            result = []
            for path in paths:
                result.append([all_authors[p] for p in path])
            return result
        return None

    def all_shortest_paths(self, graph, start, end):
        path = nx.all_shortest_paths(graph, start, end)
        try:
            path = list(path)
        except nx.exception.NetworkXNoPath:
            path = []
        return path

class DocumentHandler(handler.ContentHandler):
    TITLE_TAGS = [ "sub", "sup", "i", "tt", "ref" ]
    PUB_TYPE = {
        "inproceedings":Publication.CONFERENCE_PAPER,
        "article":Publication.JOURNAL,
        "book":Publication.BOOK,
        "incollection":Publication.BOOK_CHAPTER }

    def __init__(self, db):
        self.tag = None
        self.chrs = ""
        self.clearData()
        self.db = db

    def clearData(self):
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name in self.TITLE_TAGS:
            return
        if name in DocumentHandler.PUB_TYPE.keys():
            self.pub_type = DocumentHandler.PUB_TYPE[name]
        self.tag = name
        self.chrs = ""

    def endElement(self, name):
        if self.pub_type == None:
            return
        if name in self.TITLE_TAGS:
            return
        d = self.chrs.strip()
        if self.tag == "author":
            self.authors.append(d)
        elif self.tag == "title":
            self.title = d
        elif self.tag == "year":
            self.year = int(d)
        elif name in DocumentHandler.PUB_TYPE.keys():
            self.db.add_publication(
                self.pub_type,
                self.title,
                self.year,
                self.authors)
            self.clearData()
        self.tag = None
        self.chrs = ""

    def characters(self, chrs):
        if self.pub_type != None:
            self.chrs += chrs
