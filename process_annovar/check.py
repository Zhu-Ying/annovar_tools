import re
import csv


def load_info(info: str) -> dict:
    data = dict()
    for field in info.split(';'):
        match = re.match(re.compile(r'^(\S+)=(\S+)$'), field)
        if match:
            data.setdefault(match.group(1).lower(), match.group(2))
    return data


def dump_info(data: dict) -> str:
    return ';'.join([f'{k.upper()}={v}' for k, v in data.items()])


def check_header(header: list):
    if header[0] != 'Chr' or header[1] != 'Start' or header[2] != 'End' or header[3] != 'Ref' or header[4] != 'Alt':
        raise Exception('ERROR: this is no header or header is wrong')


def check_info(row: dict):
    variant = f'{row["Chr"]}:{row["Start"]}-{row["End"]}:{row["Ref"]}/{row["Alt"]}'
    otherinfo = row.get('Otherinfo1')
    if not otherinfo:
        raise Exception(f'ERROR: Otherinfo1 not found: {variant}')
    ref, alt = row.get('Ref'), row.get('Alt')
    if ref == '0' and alt == '0':
        info = load_info(otherinfo)
        ref, alt = info.pop('ref', None), info.pop('alt', None)
        if not ref or not alt:
            raise Exception(f'ERROR: ref or alt not found in otherinfo: {variant}')
        row.update({'Ref': ref, 'Alt': alt, 'Otherinfo1': dump_info(info)})
    else:
        if ref == '0' or alt == '0':
            raise Exception(f'ERROR: ref or alt is wrong: {variant}')


def check(input: str, output: str):
    fi = open(input)
    fo = open(output, 'w')
    reader = csv.DictReader(fi, delimiter='\t')
    check_header(reader.fieldnames)
    writer = csv.DictWriter(fo, delimiter='\t', fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        check_info(row)
        writer.writerow(row)
    fi.close()
    fo.close()
