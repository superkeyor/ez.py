import os, sys
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, MODULE_PATH)

import atom
import atom.data    #essential to pygcal
import gdata
import pygcal
import pygmail
import pygsheet

# EMAIL = "someone@gmail.com", PASSWORD = "abcdefghijkl"
from pygmailconfig import EMAIL, PASSWORD

def Mail(to, subject, body, attach=None):
    return pygmail.Mail(EMAIL, PASSWORD, to, subject, body, attach)

def AddEvent(event):
    return pygcal.AddEvent(EMAIL, PASSWORD, event)

def Sheet(fileName):
    return pygsheet.Sheet(EMAIL, PASSWORD, fileName)

mail = Mail
addevent = AddEvent

__doc__ = """
Mail(to, subject, body, attach=None)
AddEvent(event)     on DATE at TIME for DURATION in PLACE

Sheet(fileName)
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