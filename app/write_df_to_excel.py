import os

import pandas as pd
from colorama import Fore, Style


def write_df_to_excel(
    file_path: str, df: pd.DataFrame, sheet_name: str = 'list_1'
):
    """Запись DataFrame в Excel файл."""
    try:
        if os.path.exists(file_path):
            with pd.ExcelWriter(
                file_path, mode='a', if_sheet_exists='replace'
            ) as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(
                    Fore.CYAN + Style.DIM +
                    'Данные в excel ' +
                    Style.RESET_ALL + Fore.WHITE + Style.BRIGHT +
                    file_path +
                    Style.RESET_ALL + Fore.CYAN + Style.DIM +
                    ' (лист ' +
                    Style.RESET_ALL + Fore.WHITE + Style.BRIGHT +
                    sheet_name +
                    Style.RESET_ALL + Fore.CYAN + Style.DIM +
                    ') перезаписаны.'
                )
        else:
            with pd.ExcelWriter(file_path, mode='w') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(
                    Fore.CYAN + Style.DIM +
                    'Файл excel создан ' +
                    Style.RESET_ALL + Fore.WHITE + Style.BRIGHT +
                    file_path +
                    Style.RESET_ALL + Fore.CYAN + Style.DIM +
                    ' (лист ' +
                    Style.RESET_ALL + Fore.WHITE + Style.BRIGHT +
                    sheet_name +
                    Style.RESET_ALL + Fore.CYAN + Style.DIM +
                    ') данные записаны.'
                )
    except PermissionError:
        print(
            Fore.YELLOW + Style.DIM + "Ошибка доступа к файлу: " +
            Style.RESET_ALL + Fore.WHITE + Style.BRIGHT +
            f'{file_path} ({sheet_name}).'
        )
