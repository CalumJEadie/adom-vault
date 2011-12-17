#! /usr/bin/python

"""
Saves and restores adom game directories, constitutes and implements a save cheat.
"""

import datetime
import csv
import math
import os
import random
import shutil

### -------------------------------------------------------- DRAWING

def draw_title(title,width):
    """
    Draws a title to screen of the form:
    
    +------------------+
    |            TITLE |
    +------------------+
    """
    
    # calculate inner width, the width available for putting text in
    inner_width = width - 4
    
    # calculate width of text, and so the width of whitespace next to the text
    text_width = len(title)
    padding_width = inner_width - text_width
    
    # draw title
    print '+' + '-'*(width-2) + '+'
    print '| ' + ' '*padding_width + title + ' |'
    print '+' + '-'*(width-2) + '+'
    
def draw_prompt(text=''):
    """
    Draws a prompt to screen of the form:
    
    |
    +-<TEXT>-> <CURSOR>

    whilst waiting for input which is returned.
    """

    print '|'
    return raw_input('+-' + text + '-> ')

def draw_message(message=['']):
    """
    Draws a message, where message is iterable, to the screen of the form:

    | Line 1
    | Line 2
    """

    # print each line in the message
    for line in message:

        print '| ' + line

### -------------------------------------------------------- FILE HANDLING

def read_saved_games():
    """
    Reads the saved games file and returns a list of saved games.
    """

    # start with empty list
    saved_games = []

    # see if the file exists, if not then return empty list
    if os.access(saved_games_file_path,os.R_OK):

        # open saved games file and load contents into a list
        saved_games_file = open(saved_games_file_path,'r')

        saved_games_file_csv_reader = csv.reader(saved_games_file)

        saved_games = []

        # append each saved game to the list
        # DD-MM-YYYY,description,path
        for record in saved_games_file_csv_reader:

            saved_game_date_as_string = record[0]
            saved_game_date_as_date = string_to_date(saved_game_date_as_string)
            saved_game_description = record[1]
            saved_game_path = record[2]

            save = [saved_game_date_as_date,saved_game_description,saved_game_path]

            saved_games.append(save)

        # close saved games file
        saved_games_file.close()

    # return list of saved games
    return saved_games

def write_saved_games(saved_games):
    """
    Writes the list of saved games to the saved games file.
    """

    # open saved games file for writing and create a csv writer object
    saved_games_file = open(saved_games_file_path,'w')

    saved_games_csv_writer = csv.writer(saved_games_file)

    # write each save in the list to the file
    # DD-MM-YYYY,description,path
    for save in saved_games:

        saved_game_date_as_date = save[0]
        saved_game_date_as_string = date_to_string(saved_game_date_as_date)
        
        saved_game_description = save[1]
        saved_game_path = save[2]

        record = (saved_game_date_as_string,saved_game_description,saved_game_path)

        saved_games_csv_writer.writerow(record)

    # close saved games file
    saved_games_file.close()

### -------------------------------------------------------- DATES

def date_to_string(date_as_date):
    """
    Converts a date to a string in the format DD-MM-YYYY.
    """

    format = '%d-%m-%Y'

    date_as_string = date_as_date.strftime(format)

    return date_as_string

def string_to_date(date_as_string):
    """
    Converts a string in the format DD-MM-YYYYY" into a date.
    """

    format = '%d-%m-%Y'

    date_as_date = datetime.datetime.strptime(date_as_string,format)

    return date_as_date

### -------------------------------------------------------- TASKS

def task_save():
    """
    Save Task, copies the adom config directory to another location.
    """

    # check that there is an actual adom dir to be able to copy
    if not os.access(adom_data_dir,os.F_OK):

        # print blank line, followed by error message
        draw_message(['','Error: There is not any adom data to save.'])

    else:

        # display saved games
        task_list()

        # read the saved games file
        saved_games = read_saved_games()

        # start with saved as false, loop until game saved
        saved = False

        while not saved:

            # get input
            input = draw_prompt('Save ID? (ID/Q)')

            # user may want to quit this task, upper wouldn't be sensible
            if input == 'Q' or input == 'q':

                break

            # now we can convert to int and get on with saving
            save_id = int(input)

            # validate it, if it fails alert user and skip this iteration
            if save_id < 0 or save_id > len(saved_games):

                task_invalid(save_id)

                continue

            # set date
            save_date = datetime.date.today()

            # if save is zero we need to prompt user or make ourselves, otherwise there recorded
            if save_id == 0:

                save_description = draw_prompt('Description?')

                # must ensure that save directory is unique, so should keep testing into happy
                unique = False

                while not unique:

                    # generate a string of random digits
                    random_string = ''

                    for i in range(0,4):

                        random_string += str(random.randint(0,9))

                    save_dir = adom_vault_dir + '/' + random_string

                    unique = not os.access(save_dir,os.F_OK)

                # we now need to append this information to the list of saved games
                save = (save_date,save_description,save_dir)

                saved_games.append(save)

            # otherwise read from save list
            else:

                save_description = saved_games[save_id-1][1]
                save_dir = saved_games[save_id-1][2]

                # need to update the date in the list of saved games
                saved_games[save_id-1][0] = save_date

            # delete old save if it exists
            if os.access(save_dir,os.F_OK):

                shutil.rmtree(save_dir)

            # then copy the data dir into the yet non existent save dir
            shutil.copytree(adom_data_dir,save_dir)

            # and then ammend the saved games file
            write_saved_games(saved_games)

            saved = True

def task_restore():
    """
    Restore Task, copies a previously copied config directory to the adom config directory.
    """

    # read the saved games file
    saved_games = read_saved_games()

    # check there is any games that could be restored
    if len(saved_games) == 0:

        # print blank line, followed by error message
        draw_message(['','Error: There is not any save data to restore'])

    else:

        # display saved games
        task_list()

        # start with restored as false, loop until save restored
        restored = False

        while not restored:

           # get input
            input = draw_prompt('Save ID? (ID/Q)')

            # user may want to quit this task, upper wouldn't be sensible
            if input == 'Q' or input == 'q':

                break

            # now we can convert to int and get on with erasing
            save_id = int(input)

            # validate it, if it fails alert user and skip this iteration
            if save_id < 1 or save_id > len(saved_games):

                task_invalid(save_id)

                continue

            # check with user that they definately want to restore this save
            confirm_char = draw_prompt('Are you sure? (Y/N/Q)')
            confirm_char = confirm_char.upper()

            # if user declines then skip this iteration, this is default
            if confirm_char == 'N':

                continue

            elif confirm_char == 'Q':

                break

            elif confirm_char != 'Y':

                continue

            # get the save dir
            save_dir = saved_games[save_id-1][2]

            # delete adom data dir it exists
            if os.access(adom_data_dir,os.F_OK):

                shutil.rmtree(adom_data_dir)

            # copy the save dir to the adom data dir
            shutil.copytree(save_dir,adom_data_dir)

            restored = True


def task_erase():
    """
    Erase Task, erases a particular copied config directory.
    """

    # read the saved games file
    saved_games = read_saved_games()

    # check there is any games that could be erased
    if len(saved_games) == 0:

        # print blank line, followed by error message
        draw_message(['','Error: There is not any save data to erase'])

    else:

        # display saved games
        task_list()

        # start with erased as false, loop until save erased
        erased = False

        while not erased:

           # get input
            input = draw_prompt('Save ID? (ID/Q)')

            # user may want to quit this task, upper wouldn't be sensible
            if input == 'Q' or input == 'q':

                break

            # now we can convert to int and get on with erasing
            save_id = int(input)

            # validate it, if it fails alert user and skip this iteration
            if save_id < 1 or save_id > len(saved_games):

                task_invalid(save_id)

                continue

            # check with user that they definately want to erase this save
            confirm_char = draw_prompt('Are you sure? (Y/N/Q)')
            confirm_char = confirm_char.upper()

            # if user declines then skip this iteration, this is default
            if confirm_char == 'N':

                continue

            elif confirm_char == 'Q':

                break

            elif confirm_char != 'Y':

                continue

            # get the save dir
            save_dir = saved_games[save_id-1][2]

            # remove the save dir recursively, if it exists
            if os.access(save_dir,os.F_OK):

                shutil.rmtree(save_dir)

            # remove that save from the list and then ammend the saved games file
            del saved_games[save_id-1]

            write_saved_games(saved_games)

            erased = True

def task_list():
    """
    List Task, lists the currently saved config directories.
    """

    # blank line
    draw_message()

    # print save id 0
    draw_message(['[0] Empty'])

    # get the list of saved games
    saved_games = read_saved_games()

    # work out how many saved game there are
    largest_id = len(saved_games)

    # can't loop is nothing to loop over!
    if largest_id != 0:

        # work out how many digits we need, zfill requires integer value
        digits = math.log10(largest_id)
        digits = int(math.floor(digits))

        # current id will start at 1
        current_id = 1

        # for each saved game display information and a number to be identified with
        for saved_game in saved_games:

            # start with an empty line
            line = ''

            # add the identifying number, with zeros for presentation
            line += '[' + str(current_id).zfill(digits) + '] '

            # add the date
            date_as_time = saved_game[0]
            date_as_string = date_to_string(date_as_time)

            line += date_as_string + ' '

            # add the description
            description = saved_game[1]

            line += '\"' + description + '\" '

            # print the information about particular saved game
            draw_message([line])

            # increment the current id
            current_id += 1

def task_adom():
    """
    Adom Task, starts an instance of adom.
    """

    # blank line
    draw_message()

    # run adom command, run in a subshell
    os.system(adom_command)

def task_help():
    """
    Help Task, displays help text.
    """

    # blank line
    draw_message()

    # split help into lines and print each line
    draw_message(help.split('\n'))

def task_quit():
    """
    Quit Task, exits the script.
    """

def task_invalid(invalid_input):
    """
    Invalid Task, prints an error message for invalid input.
    """

    # print invalid input with blank lines before
    draw_message()
    draw_message(['Invalid Input: \'' + str(invalid_input) + '\''])

### -------------------------------------------------------- MAIN

# if being imported then we don't to go through the main logic
if __name__ == '__main__':

    # define global constants
    home_dir = os.path.expanduser("~")
    adom_data_dir = home_dir + '/.adom.data'
    adom_command = home_dir + '/bin/adom'
    adom_vault_dir = home_dir + '/.adom_vault'
    saved_games_file_path = adom_vault_dir + '/saved_games.csv'
    help = """[S]ave..............[A]dom..............
[R]estore...........[H]elp..............
[E]rase.............[Q]uit..............
[L]ist.................................."""

    # define other constants
    width = 77

    # set up environment
    if not os.access(adom_vault_dir,os.F_OK):

        os.mkdir(adom_vault_dir)

    # print opening title
    draw_title('Adom Vault',width)

    # display help
    task_help()

    # enter main loop, keep looping until user wants to quit
    task = ''
    task_char = ''

    while task_char != 'Q':

        # get task from user
        task_input = draw_prompt('Task?')

        # get first letter of task and then convert it to uppercase
        task_char = task_input[0]

        task_char = task_char.upper()

        # perform task
        if task_char == 'S':

            task_save()

        elif task_char == 'R':

            task_restore()

        elif task_char == 'E':

            task_erase()

        elif task_char == 'L':

            task_list()

        elif task_char == 'A':

            task_adom()

        elif task_char == 'H':

            task_help()

        elif task_char == 'Q':

            task_quit()

        else:

            task_invalid(task_input)
