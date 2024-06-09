from typing import Callable

from CreateSheet import create_monthly_sheet
from WriteItem import write_item
from CreateReport import make_monthly_report


def get_purpose() -> list:
    print("What would you like to do today?")
    opt_dict = {e: i for i, e in enumerate(['To create a sheet for new month', 'To add items to the sheet', 'To create monthly reports', 'Done'])}
    for k, v in opt_dict.items():
        print(f"{v}. {k}")

    purposes = []
    while True:
        purpose_input = input("Your purpose is?\n**Enter the number or type the name\n**If you picked all of the purposes, type 3 or Done: ")
        if purpose_input.isdigit():
            purpose_index = int(purpose_input)
            try:
                purpose = list(opt_dict.keys())[list(opt_dict.values()).index(purpose_index)]
            except IndexError:
                print("Invalid choice, Select a valid option")
                continue
        else:
            purpose = purpose_input

        if purpose.lower() == 'done' or purpose == '3':
            break

        if purpose not in opt_dict.keys():
            print("Invalid choice, Select a valid option")
            continue

        purposes.append(purpose)

    purposes = list(dict.fromkeys(purposes))
    return sorted(purposes, key=lambda x: opt_dict[x])


def repeat_question(yn_question: str, param_question: str, func: Callable, param: str=None):
    while True:
        answer = input(yn_question)
        if answer.lower() not in ['yes', 'no']:
            print("Provide a valid answer (hint: Yes or No)")
        else:
            if answer.lower() == 'no':
                break
            if answer.lower() == 'yes':
                if param is not None:
                    func(param)
                else:
                    param = input(param_question)
                    func(param)


def start(purposes: list):
    if len(purposes) == 0:
        invalid_purpose = input("You didn't provide any valid answer. Do you want to exit? Answer this Yes or No")
        if invalid_purpose.lower() == 'yes':
            return
        elif invalid_purpose.lower() == 'no':
            purposes = get_purpose()
            start(purposes)
            return
        else:
            print("Answer has to be either Yes or No. Exiting the program")
            return

    else:
        for p in purposes:
            if p == "To create a sheet for new month":
                print("Let's create a sheet for new month")
                param_question = "Provide a title of the new sheet"
                new_sheet_title = input(param_question)
                create_monthly_sheet(new_sheet_title)
                yn_question = "Do you have more sheet to create? Answer Yes or No"
                repeat_question(yn_question=yn_question, param_question=param_question, func=create_monthly_sheet)
            if p == "To add items to the sheet":
                print("Let's record spending or earning")
                param_question = "Provide the sheet's title that you'd like to write in"
                sheet_title = input(param_question)
                write_item(sheet_title)
                yn_question = "Do you have more item to punch in? Answer Yes or No"
                repeat_question(yn_question=yn_question, param_question=param_question, func=write_item, param=sheet_title)
            if p == "To create monthly reports":
                print("Let's pull monthly reports")
                param_question = "Provide the sheet's title that you'd like to pull monthly reports from"
                sheet_title = input(param_question)
                make_monthly_report(sheet_title)
                yn_question = "Do you have another month to generate a report on? Answer Yes or No"
                repeat_question(yn_question=yn_question, param_question=param_question, func=make_monthly_report)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    purposes = get_purpose()
    start(purposes)
