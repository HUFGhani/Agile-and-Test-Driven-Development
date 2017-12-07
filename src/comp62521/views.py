from comp62521 import app
from database import database
from flask import (render_template, request, url_for, redirect, jsonify)
import json


def format_data(data):
    fmt = "%.2f"
    result = []
    for item in data:
        if type(item) is list:
            result.append(", ".join([ (fmt % i).rstrip('0').rstrip('.') for i in item ]))
        else:
            result.append((fmt % item).rstrip('0').rstrip('.'))
    return result

@app.route("/averages")
def showAverages():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"averages"}
    args['title'] = "Averaged Data"
    tables = []
    headers = ["Average", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications"]
    averages = [ database.Stat.MEAN, database.Stat.MEDIAN, database.Stat.MODE ]
    tables.append({
        "id":1,
        "title":"Average Authors per Publication",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_per_publication(i)[1])
                for i in averages ] })
    tables.append({
        "id":2,
        "title":"Average Publications per Author",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_per_author(i)[1])
                for i in averages ] })
    tables.append({
        "id":3,
        "title":"Average Publications in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_in_a_year(i)[1])
                for i in averages ] })
    tables.append({
        "id":4,
        "title":"Average Authors in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_in_a_year(i)[1])
                for i in averages ] })

    args['tables'] = tables
    return render_template("averages.html", args=args)

@app.route("/coauthors")
def showCoAuthors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset":dataset, "id":"coauthors"}
    args["title"] = "Co-Authors"

    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["data"] = db.get_coauthor_data(start_year, end_year, pub_type)
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("coauthors.html", args=args)

@app.route("/")
def showStatisticsMenu():
    dataset = app.config['DATASET']
    args = {"dataset":dataset}
    return render_template('statistics.html', args=args)

@app.route("/statisticsdetails/<status>")
def showPublicationSummary(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":status}

    if (status == "publication_summary"):
        args["title"] = "Publication Summary"
        args["data"] = db.get_publication_summary()

    if (status == "publication_author"):
        args["title"] = "Author Publication"
        args["data"] = db.get_publications_by_author()

    if (status == "publication_year"):
        args["title"] = "Publication by Year"
        args["data"] = db.get_publications_by_year()

    if (status == "author_year"):
        args["title"] = "Author by Year"
        args["data"] = db.get_author_totals_by_year()

    return render_template('statistics_details.html', args=args)

@app.route("/search_name")
def showSerchName():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"search_name"}
    args["title"] = "search author"
    author = str(request.args.get("author"))
    error_message,allpublications,conference_papers,journal_articles,book_chapters,books,co_authors,first,last = db.get_search_name(author)
    if error_message != 0:
        args["author"]= 'None search result for ' + author + '. Please check the name and try again!'
        args["allpublications"] = 'NULL'
        args["conference_papers"] = 'NULL'
        args["journal_articles"] = 'NULL'
        args["book_chapters"] = 'NULL'
        args["books"] = 'NULL'
        args["co_authors"] = 'NULL'
        args["first"] = 'NULL'
        args["last"] = 'NULL'
    else:
        args["author"] = author
        args["allpublications"] = allpublications
        args["conference_papers"] = conference_papers
        args["journal_articles"] = journal_articles
        args["book_chapters"] = book_chapters
        args["books"] = books
        args["co_authors"] = co_authors
        args["first"] = first
        args["last"] = last

    return render_template("search_name.html", args=args)

@app.route("/search_type")
def showAuthorsPublication():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset":dataset, "id":"search_type"}
    args["title"] = "Search Author by Publication Type"


    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["data"] = db.get_author_publication(pub_type)

    args["pub_type"] = pub_type

    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("search_type.html", args=args)

@app.route("/author_details")
def showAuthorDetails():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"author_details"}
    args["title"] = "Author Details"
    author = str(request.args.get("author"))
    (allpublications,conference_papers,journal_articles,book_chapters,books,co_authors,
     allpublications_first,allpublications_last,allpublications_solo,
     conference_papers_first,conference_papers_last,conference_papers_solo,
     journal_articles_first,journal_articles_last,journal_articles_solo,
     books_first,books_last,books_solo,
     book_chapters_first,book_chapters_last,book_chapters_solo) = db.get_detail_information_by_author(author)

    args["author"] = author

    args["allpublications"] = allpublications
    args["conference_papers"] = conference_papers
    args["journal_articles"] = journal_articles
    args["books"] = books
    args["book_chapters"] = book_chapters

    args["co_authors"] = co_authors

    args["allpublications_first"] = allpublications_first
    args["allpublications_last"] = allpublications_last
    args["allpublications_solo"] = allpublications_solo

    args["conference_papers_first"] = conference_papers_first
    args["conference_papers_last"] = conference_papers_last
    args["conference_papers_solo"] = conference_papers_solo

    args["journal_articles_first"] = journal_articles_first
    args["journal_articles_last"] = journal_articles_last
    args["journal_articles_solo"] = journal_articles_solo

    args["books_first"] = books_first
    args["books_last"] = books_last
    args["books_solo"] = books_solo

    args["book_chapters_first"] = book_chapters_first
    args["book_chapters_last"] = book_chapters_last
    args["book_chapters_solo"] = book_chapters_solo

    return render_template("author_details.html", args=args)

@app.route("/getcoauthor/<authorname>")
def getCoauthor(authorname):
    db = app.config['DATABASE']
    coauthor = db.get_coauthor(authorname)
    data = {"type": "force", "categories": [{"name": "author"}, {"name": "coauthor"}]}
    nodes = [{"name": authorname, "category": "author", "symbolSize": 30}] + \
            [{"name": name, "category": "coauthor", "symbolSize": 20} for name in coauthor]
    links = [{"source": 0, "target": i+1} for i in range(len(nodes)-1)]
    data["nodes"] = nodes
    data["links"] = links
    return jsonify(data)

@app.route("/fuzzy_search_name")
def showFuzzySearchName():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"fuzzy_search_name"}
    args["title"] = "fuzzy search author"
    author = str(request.args.get("author")).decode('utf-8')
    author_names=[]
    if author == 'None':
        pass
    else:
        author_names = db.get_fuzzy_search_name(author)
        author_names.sort()
    authors = []

    if len(author_names) > 1:
        for author in author_names:
            authors.append(author)
        args["authors"] = authors
        return render_template("search_name_link.html", args=args)

    elif len(author_names) == 1:
        a = author_names[0]
        error_message, allpublications, conference_papers, journal_articles, book_chapters, books, co_authors, first, last,sole = db.get_search_name(a)
        args["author"] = a
        args["allpublications"] = allpublications
        args["conference_papers"] = conference_papers
        args["journal_articles"] = journal_articles
        args["book_chapters"] = book_chapters
        args["books"] = books
        args["co_authors"] = co_authors
        args["first"] = first
        args["last"] = last
        args["sole"] = sole
        return render_template("search_name_link.html", args=args)

    elif len(author_names) == 0:
        args["author"]= 'None result returned for ' + author + '. Please check the name and try again!'
        args["allpublications"] = 'NULL'
        args["conference_papers"] = 'NULL'
        args["journal_articles"] = 'NULL'
        args["book_chapters"] = 'NULL'
        args["books"] = 'NULL'
        args["co_authors"] = 'NULL'
        args["first"] = 'NULL'
        args["last"] = 'NULL'
        args["sole"] = 'NULL'
        return render_template("fuzzy_search_name.html", args=args)

@app.route("/separation")
def degreeOfSeparation():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"degreeofseparation"}
    args["title"] = "Degrees of Separation"
    args["authors"] = db.get_all_authors()
    if "author1" in request.args and "author2" in request.args:
        author1 = request.args.get("author1").strip()
        author2 = request.args.get("author2").strip()
        args["degrees"] = [author1, author2, db.get_degree_of_separation(author1, author2)]
        args["author1"] = author1
        args["author2"] = author2
        paths = db.show_all_shortest_paths(author1, author2)
        nodes = set()
        edges = []
        for path in paths:
            for p in path:
                nodes.add(p)
            for i in range(0, len(path)-1):
                if [path[i], path[i+1]] not in edges:
                    edges.append([path[i], path[i+1]])
        args["nodes"] = json.dumps(list(nodes))
        args["edges"] = json.dumps(edges)
    return render_template("separation.html", args=args)
