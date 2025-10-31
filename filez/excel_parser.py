from pathlib import Path
from typing import Union, List


def get_xls_sheet_data(sheet, header=False, skip=0):
    assert isinstance(skip, int) and skip >= 0
    data = [sheet.row_values(i) for i in range(skip, sheet.nrows)]

    if header is True and data:  # todo column name as header
        headers = data[0]
        return [dict(zip(headers, line)) for line in data[1:]]
    return data


def load_xls(file_path: Union[Path, str], skip=0, header=False, sheets=None) -> Union[list, dict]:
    # todo float->int ->str, FALSE -> False, '' -> None
    xlrd = __import__('xlrd')  # todo change to openpyxl
    wb = xlrd.open_workbook(file_path)

    if sheets is None:
        return get_xls_sheet_data(wb.sheet_by_index(0), header=header, skip=skip)  # list

    if isinstance(sheets, (list, tuple)):
        keep_sheets = [wb.sheet_by_index(i) if isinstance(i, int) else wb.sheet_by_name(i)
                       for i in sheets]  # todo try
    else:
        keep_sheets = wb.sheets()

    data = {}
    for sh in keep_sheets:
        data[sh.name] = get_xls_sheet_data(sh, header=header, skip=skip)
    return data


def get_xlsx_sheet_data(sheet, header=False, skip=0) -> Union[List[dict], List[list]]:
    assert isinstance(skip, int) and skip >= 0
    assert sheet.max_row > skip

    data = []
    if header is True:
        headers, row_data = [], []
        for row in sheet.iter_rows(min_row=skip, max_row=1 + skip):
            headers = [cell.value for cell in row]
        for row in sheet.iter_rows(min_row=2 + skip):
            row_data = [cell.value for cell in row]
            data.append(dict(zip(headers, row_data)))
    else:
        for row in sheet.iter_rows(min_row=1 + skip):
            row_data = [cell.value for cell in row]
            data.append(row_data)
    return data


def load_xlsx(file_path, header=False, skip=0, sheets=None) -> Union[dict, list]:
    openpyxl = __import__('openpyxl')
    wb = openpyxl.load_workbook(file_path)  # 有路径应带上路径

    # todo 使用指定工作表
    if sheets is None:
        return get_xlsx_sheet_data(wb.active, header=header, skip=skip)

    if isinstance(sheets, (list, tuple)):
        keep_sheets = [wb.worksheets[i] if isinstance(i, int) else wb[i]
                       for i in sheets]  # todo try
    else:
        keep_sheets = wb.sheets()

    data = {}
    for sh in keep_sheets:
        data[sh.title] = get_xlsx_sheet_data(sh, header=header, skip=skip)
    return data
