import os, sys
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, MODULE_PATH)

# __doc__ at the bottom

import atom
import atom.data    #essential to pygcal
import gdata
import pygcal
import pygmail
import pygsheet

try:
    # EMAIL = "someone@gmail.com", PASSWORD = "abcdefghijkl"
    from pygmailconfig import EMAIL, PASSWORD
    def Mail(to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None):
        """Mail(to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)
        to/bcc/cc: ['a@a.com','b@b.com'] or 'a@a.com, b@b.com'
        reply_to: 'a@a.com'
        attachment: 'file_in_working_dir.txt' or ['a.txt','b.py','c.pdf']
        """
        return pygmail.Mail(EMAIL, PASSWORD, to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)

    def AddEvent(event):
        """AddEvent(event)     on DATE at TIME for DURATION in PLACE"""
        return pygcal.AddEvent(EMAIL, PASSWORD, event)

    def Sheet(fileName):
        """Sheet(fileName)
                returns a sheet object representing "Sheet 1"

                your google account doesn't have to the owner of this sheet, as long as you can edit it.
                but you need to initialize/create this sheet and maybe the header by hand to begin with
                the header could have spaces, ? etc, and when they are used as the keywords of dictionary, they are all converted to lowercase and all illegal characters are removed e.g. Delayed Test_date?  --> delayedtestdate

                fileName should be unique, can have spaces


            GetRows(query=None, order_by=None,
                    reverse=None, filter_func=None)
                :param query:
                    A string structured query on the full text in the worksheet.
                      [columnName][binaryOperator][value]
                      Supported binaryOperators are:
                      - (), for overriding order of operations
                      - = or ==, for strict equality
                      - <> or !=, for strict inequality
                      - and or &&, for boolean and
                      - or or ||, for boolean or.
                :param order_by:
                    A string which specifies what column to use in ordering the
                    entries in the feed. By position (the default): 'position' returns
                    rows in the order in which they appear in the GUI. Row 1, then
                    row 2, then row 3, and so on. By column:
                    'column:columnName' sorts rows in ascending order based on the
                    values in the column with the given columnName, where
                    columnName is the value in the header row for that column.
                :param reverse:
                    A string which specifies whether to sort in descending or ascending
                    order.Reverses default sort order: 'true' results in a descending
                    sort; 'false' (the default) results in an ascending sort.
                :param filter_func:
                    A lambda function which applied to each row, Gets a row dict as
                    argument and returns True or False. Used for filtering rows in
                    memory (as opposed to query which filters on the service side).
                :return:
                    A list of row dictionaries.


            UpdateRow(row_data):
                Update Row (By ID).

                Only the fields supplied will be updated.
                :param row_data:
                    A dictionary containing row data. The row will be updated according
                    to the value in the ID_FIELD.
                :return:
                    The updated row.


            UpdateRowByIndex(index, row_data):
                Update Row By Index

                :param index:
                    An integer designating the index of a row to update (zero based).
                    Index is relative to the returned result set, not to the original
                    spreadseet.
                :param row_data:
                    A dictionary containing row data.
                :return:
                    The updated row.


            InsertRow(row_data):
                Append Row at the end

                :param row_data:
                    A dictionary containing row data.
                    each dict key maps to a column name, if the key/column name does not exist, it will be ignore
                    if an existing column name is not included in the keys, that column will not be update (i.e. remain unchanged)
                :return:
                    A row dictionary for the inserted row.


            DeleteRow(row):
                Delete Row (By ID).

                Requires that the given row dictionary contains an ID_FIELD.
                :param row:
                    A row dictionary to delete.


            DeleteRowByIndex(index):
                Delete Row By Index

                :param index:
                    A row index. Index is relative to the returned result set, not to
                    the original spreadsheet.


            DeleteAllRows():
                Delete All Rows"""
        return pygsheet.Sheet(EMAIL, PASSWORD, fileName)
except ImportError:
    def Mail(EMAIL, PASSWORD, to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None):
        """Mail(EMAIL, PASSWORD, to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)
        to/bcc/cc: ['a@a.com','b@b.com'] or 'a@a.com, b@b.com'
        reply_to: 'a@a.com'
        attachment: 'file_in_working_dir.txt' or ['a.txt','b.py','c.pdf']
        """
        return pygmail.Mail(EMAIL, PASSWORD, to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)

    def AddEvent(EMAIL, PASSWORD, event):
        """AddEvent(EMAIL, PASSWORD, event)     on DATE at TIME for DURATION in PLACE"""
        return pygcal.AddEvent(EMAIL, PASSWORD, event)

    def Sheet(EMAIL, PASSWORD, fileName):
        """Sheet(EMAIL, PASSWORD, fileName)
                returns a sheet object representing "Sheet 1"

                your google account doesn't have to the owner of this sheet, as long as you can edit it.
                but you need to initialize/create this sheet and maybe the header by hand to begin with
                the header could have spaces, ? etc, and when they are used as the keywords of dictionary, they are all converted to lowercase and all illegal characters are removed e.g. Delayed Test_date?  --> delayedtestdate

                fileName should be unique, can have spaces


            GetRows(query=None, order_by=None,
                    reverse=None, filter_func=None)
                :param query:
                    A string structured query on the full text in the worksheet.
                      [columnName][binaryOperator][value]
                      Supported binaryOperators are:
                      - (), for overriding order of operations
                      - = or ==, for strict equality
                      - <> or !=, for strict inequality
                      - and or &&, for boolean and
                      - or or ||, for boolean or.
                :param order_by:
                    A string which specifies what column to use in ordering the
                    entries in the feed. By position (the default): 'position' returns
                    rows in the order in which they appear in the GUI. Row 1, then
                    row 2, then row 3, and so on. By column:
                    'column:columnName' sorts rows in ascending order based on the
                    values in the column with the given columnName, where
                    columnName is the value in the header row for that column.
                :param reverse:
                    A string which specifies whether to sort in descending or ascending
                    order.Reverses default sort order: 'true' results in a descending
                    sort; 'false' (the default) results in an ascending sort.
                :param filter_func:
                    A lambda function which applied to each row, Gets a row dict as
                    argument and returns True or False. Used for filtering rows in
                    memory (as opposed to query which filters on the service side).
                :return:
                    A list of row dictionaries.


            UpdateRow(row_data):
                Update Row (By ID).

                Only the fields supplied will be updated.
                :param row_data:
                    A dictionary containing row data. The row will be updated according
                    to the value in the ID_FIELD.
                :return:
                    The updated row.


            UpdateRowByIndex(index, row_data):
                Update Row By Index

                :param index:
                    An integer designating the index of a row to update (zero based).
                    Index is relative to the returned result set, not to the original
                    spreadseet.
                :param row_data:
                    A dictionary containing row data.
                :return:
                    The updated row.


            InsertRow(row_data):
                Append Row at the end

                :param row_data:
                    A dictionary containing row data.
                    each dict key maps to a column name, if the key/column name does not exist, it will be ignore
                    if an existing column name is not included in the keys, that column will not be update (i.e. remain unchanged)
                :return:
                    A row dictionary for the inserted row.


            DeleteRow(row):
                Delete Row (By ID).

                Requires that the given row dictionary contains an ID_FIELD.
                :param row:
                    A row dictionary to delete.


            DeleteRowByIndex(index):
                Delete Row By Index

                :param index:
                    A row index. Index is relative to the returned result set, not to
                    the original spreadsheet.


            DeleteAllRows():
                Delete All Rows"""
        return pygsheet.Sheet(EMAIL, PASSWORD, fileName)

mail = Mail
addevent = AddEvent

def Mail2(EMAIL, PASSWORD, to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None):
    """Mail(EMAIL, PASSWORD, to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)
    to/bcc/cc: ['a@a.com','b@b.com'] or 'a@a.com, b@b.com'
    reply_to: 'a@a.com'
    attachment: 'file_in_working_dir.txt' or ['a.txt','b.py','c.pdf']
    """
    return pygmail.Mail(EMAIL, PASSWORD, to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)
def AddEvent2(EMAIL, PASSWORD, event):
    """AddEvent(EMAIL, PASSWORD, event)     on DATE at TIME for DURATION in PLACE"""
    return pygcal.AddEvent(EMAIL, PASSWORD, event)
def Sheet2(EMAIL, PASSWORD, fileName):
    """Sheet(EMAIL, PASSWORD, fileName)
    """
    return pygsheet.Sheet(EMAIL, PASSWORD, fileName)
mail2 = Mail2
addevent2 = AddEvent2


__doc__ = """
To avoid typing email password each time, place a file named pygmailconfig.py with
EMAIL = 'someone@gmail.com'
PASSWORD = 'abcdefghik'
in the site-packages/ez folder
The functions will no longer need email/password and become like this
Mail(to, subject, body, attach=None), AddEvent(event), Sheet(fileName)

Mail([EMAIL, PASSWORD, ] to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)
        to/bcc/cc: ['a@a.com','b@b.com'] or 'a@a.com, b@b.com'
        reply_to: 'a@a.com'
        attachment: 'file_in_working_dir.txt' or ['a.txt','b.py','c.pdf']
AddEvent([EMAIL, PASSWORD, ] event)     on DATE at TIME for DURATION in PLACE

Sheet([EMAIL, PASSWORD, ] fileName)
    returns a sheet object representing "Sheet 1"

    your google account doesn't have to the owner of this sheet, as long as you can edit it.
    but you need to initialize/create this sheet and maybe the header by hand to begin with
    the header could have spaces, ? etc, and when they are used as the keywords of dictionary, they are all converted to lowercase and all illegal characters are removed e.g. Delayed Test_date?  --> delayedtestdate

    fileName should be unique, can have spaces


GetRows(query=None, order_by=None,
        reverse=None, filter_func=None)
    :param query:
        A string structured query on the full text in the worksheet.
          [columnName][binaryOperator][value]
          Supported binaryOperators are:
          - (), for overriding order of operations
          - = or ==, for strict equality
          - <> or !=, for strict inequality
          - and or &&, for boolean and
          - or or ||, for boolean or.
    :param order_by:
        A string which specifies what column to use in ordering the
        entries in the feed. By position (the default): 'position' returns
        rows in the order in which they appear in the GUI. Row 1, then
        row 2, then row 3, and so on. By column:
        'column:columnName' sorts rows in ascending order based on the
        values in the column with the given columnName, where
        columnName is the value in the header row for that column.
    :param reverse:
        A string which specifies whether to sort in descending or ascending
        order.Reverses default sort order: 'true' results in a descending
        sort; 'false' (the default) results in an ascending sort.
    :param filter_func:
        A lambda function which applied to each row, Gets a row dict as
        argument and returns True or False. Used for filtering rows in
        memory (as opposed to query which filters on the service side).
    :return:
        A list of row dictionaries.


UpdateRow(row_data):
    Update Row (By ID).

    Only the fields supplied will be updated.
    :param row_data:
        A dictionary containing row data. The row will be updated according
        to the value in the ID_FIELD.
    :return:
        The updated row.


UpdateRowByIndex(index, row_data):
    Update Row By Index

    :param index:
        An integer designating the index of a row to update (zero based).
        Index is relative to the returned result set, not to the original
        spreadseet.
    :param row_data:
        A dictionary containing row data.
    :return:
        The updated row.


InsertRow(row_data):
    Append Row at the end

    :param row_data:
        A dictionary containing row data.
    :return:
        A row dictionary for the inserted row.


DeleteRow(row):
    Delete Row (By ID).

    Requires that the given row dictionary contains an ID_FIELD.
    :param row:
        A row dictionary to delete.


DeleteRowByIndex(index):
    Delete Row By Index

    :param index:
        A row index. Index is relative to the returned result set, not to
        the original spreadsheet.


DeleteAllRows():
    Delete All Rows
"""