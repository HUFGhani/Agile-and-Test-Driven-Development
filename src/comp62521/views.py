from comp62521 import app
from database import database
from flask import (render_template, request)

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
    error_message,allpublications,conference_papers,journal_articles,book_chapters,books,co_authors,first,last,sole = db.get_search_name(author)
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
        args["sole"] = 'NULL'
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
        args["sole"] = sole

    return render_template("serch_name.html", args=args)

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
