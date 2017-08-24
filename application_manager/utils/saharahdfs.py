import os

def get_input_path(paths, local_path):
    for path in paths:
        local_input_path = local_path
        splitted = path.split('/')

        if splitted[len(splitted)-1] == '':
            splitted.remove('')

        splitted.remove(splitted[len(splitted)-1])

        for string in splitted:
            local_input_path += '/' + string

        local_input_path += '/'

    return local_input_path

def get_output_path(path, local_path):
    local_output_path = local_path
    splitted = path.split('/')

    if splitted[len(splitted)-1] == '':
        splitted.remove('')

    for string in splitted:
        local_output_path += '/' + string

    local_output_path += '/'

    return local_output_path

def get_output_subpath(path, local_path):
    local_output_path = local_path
    splitted = path.split('/')

    if splitted[len(splitted)-1] == '':
        splitted.remove('')

    splitted.remove(splitted[len(splitted)-1])

    for string in splitted:
        local_output_path += '/' + string

    local_output_path += '/'

    return local_output_path

def get_binary_path(path, local_path):
    local_binary_path = local_path
    splitted = path.split('/')

    if splitted[len(splitted)-1] == '':
        splitted.remove('')

    splitted.remove(splitted[len(splitted)-1])

    for string in splitted:
        local_binary_path += '/' + string

    local_binary_path += '/'

    return local_binary_path

def get_binary_file(path):
    binary = ''
    for arg in os.listdir(path):
        if os.path.isfile(path + arg):
            binary = path + arg

    return binary
