from datetime import date


def write_log(message, file_name='log/server.log'):
    with open(file_name, 'a', encoding='utf-8') as F_N:
        F_N.write(f'{date.today()} {message}\n')
        print(f'{date.today()} {message}')