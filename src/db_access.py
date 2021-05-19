import psycopg2  # use this package to work with postgresql
import psycopg2.sql  # use this package to work with postgresql
import datetime
credentials = {
    "host": "127.0.0.1",
    "port": "15432",
    "dbname": "newspapers",
    "user": "cmsc828d",
}


def get_connection(debug=False):
    try:
        con = psycopg2.connect(
            host=credentials["host"],
            database=credentials["dbname"],
            user=credentials["user"],
            port=credentials["port"])
        return (con, con.cursor())
    except psycopg2.OperationalError:
        return None


def get_paper_from_range(nonce, start_date, end_date, keywords=None):
    if keywords:
        key_query = "&".join(keywords.split(" "))
        query = "SELECT paper_id, paper, string_agg(id::text, ', ') ,\
            year, title, bool_or(has_keyword) FROM\
                (SELECT paper_id, paper, id,\
                    year, title, (tokens @@ to_tsquery('{query}')) as has_keyword\
                    FROM articles) as temp\
            WHERE year between %s and %s\
            GROUP BY (paper_id, paper, year, title)"\
            .format(query=key_query)

        nonce[1].execute(query, (start_date, end_date))
        data = nonce[1].fetchall()
        data = [tuple(i) for i in data]

    else:
        query = "SELECT paper_id, paper, string_agg(id::text, ', ') as art_ids,\
            year, title FROM articles WHERE year between %s and %s\
            GROUP BY (paper_id, paper, year, title)"

        nonce[1].execute(query, (start_date, end_date))
        data = nonce[1].fetchall()
        data = [tuple(i) + (None,) for i in data]

    return data


def real_get_data_query(nonce, identity):
    if not nonce:
        return None
    query = "Select * From articles Where id =" +str(identity)+";"

    nonce[1].execute(query)
    query_data = nonce[1].fetchall()

    data = {}
    data["id"] = query_data[0][0]
    data["title"] = query_data[0][1]
    data["body"] = query_data[0][2]
    data["date"] = str(query_data[0][3])
    data["paper"] = query_data[0][4]

    return data


def real_get_range_query(nonce, start_date, end_date):
    if not nonce:
        return None
    query = "Select * From articles Where year BETWEEN "+ "'"+ str(start_date)+ "'" + " and "+ "'"+ str(end_date)+ "'"+ ";"

    nonce[1].execute(query)
    query_data = nonce[1].fetchall()
    data = [None]*len(query_data)

    start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
    year_diff = end_date.year - start_date.year

    bin_years = [ [] for _ in range(year_diff+1) ]

    for i in range(0,len(query_data)):
        data[i] = {"id":query_data[i][0],
                   "title": query_data[i][1],
                   "date": str(query_data[i][3]),
                   "paper": query_data[i][4]
                   }
        year_ind = query_data[i][3].year - start_date.year
        bin_years[year_ind].append(query_data[i][0])
    new_data={}
    new_data["result"] = data
    new_data["start_year"] = start_date.year
    new_data["end_year"] = end_date.year
    new_data["bin_years"] = bin_years
    return new_data


def real_get_month_bin(nonce, start_date, end_date):
    if not nonce:
        return None
    query = "Select * From articles Where year BETWEEN "+ "'"+ str(start_date)+ "'" + " and "+ "'"+ str(end_date)+ "'"+ ";"

    nonce[1].execute(query)
    query_data = nonce[1].fetchall()
    data = [None]*len(query_data)

    start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
    year_diff = end_date.year - start_date.year

    bin_months = [[] for _ in range((year_diff+1)*12)]

    # This goes through each index of the data
    for (i, row) in enumerate(query_data):
        # Puts the data in this form
        data[i] = {"id": row[0],
                   "title": row[1],
                   "date": str(row[3]),
                   "paper": row[4]
                   }

        # Finds the year and the month
        year_ind = row[3].year - start_date.year
        month_ind = row[3].month

        # Stores that month wise in bin_months
        bin_months[(year_ind*12)+month_ind-1].append(data[i])

    new_data = {}
    new_data["result"] = data
    new_data["start_year"] = start_date.year
    new_data["end_year"] = end_date.year
    new_list = []

    for b in bin_months:
        thisdict = {"data": b}
        new_list.append(thisdict)
    new_data["bin_month"] = new_list
    return new_data


def real_get_paper_range_query(nonce, paper, start_date, end_date):
    query = "Select * From articles Where paper="+ "'"+ str(paper)+ "'"+" and "+  "year BETWEEN "+ "'"+ str(start_date)+ "'" + " and "+ "'"+ str(end_date)+ "'"+ ";"

    nonce[1].execute(query)
    query_data = nonce[1].fetchall()
    data = [None]*len(query_data)

    start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
    year_diff = end_date.year - start_date.year

    bin_years = [ [] for _ in range(year_diff+1) ]

    for i in range(0,len(query_data)):
        data[i] = {"id":query_data[i][0],
                   "title": query_data[i][1],
                   "date": str(query_data[i][3]),
                   "paper": query_data[i][4]
                   }
        year_ind = query_data[i][3].year - start_date.year
        bin_years[year_ind].append(query_data[i][0])
    new_data={}
    new_data["result"] = data
    new_data["start_year"] = start_date.year
    new_data["end_year"] = end_date.year
    new_data["bin_years"] = bin_years
    return new_data
