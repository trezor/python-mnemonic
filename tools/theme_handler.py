# The software multiplies the word data tables and matrices in "Data.txt",
# it removes collisions of the first two letters between words rearranging it alphabetically,
# it uses dictionary "Data.json" as template saving the result dictionary in the file "main.json"
# if called with arguments it will replace a word of your will passed as argument

from collections import OrderedDict
from pathlib import Path
import hashlib
import json
import sys


class ConfigurationError(Exception):
    pass


def open_files(themes_directory):
    parent_path = Path(__file__).parent.absolute()
    json_file_name = "Data.json"
    txt_file_name = "Data.txt"
    with open(parent_path / themes_directory / json_file_name) as json_file:
        main_dict = json.load(json_file)
    with open(parent_path / themes_directory / txt_file_name, "r", encoding="utf-8") as table_file:
        relation_matrices = [each_line.strip() for each_line in table_file.readlines()]
    return main_dict, relation_matrices


def find_header_indexes(main_dict, adequacy_matrices):
    # It finds the index of start and end of each table and matrix in the entire string
    start_indexes = []
    relation_indexes = []
    for filling_word in main_dict["FILLING_ORDER"]:
        for raw_row in adequacy_matrices:
            index_exists = raw_row.find(filling_word)
            row_index = adequacy_matrices.index(raw_row)
            if (index_exists != -1) and not (row_index in start_indexes) and not (
                    row_index - 1 in start_indexes):
                start_indexes.append(row_index)
                if len(raw_row.split(" ")) == 2:
                    relation_indexes.append(row_index)
    end_indexes = list(map(lambda x: x - 1, start_indexes))
    end_indexes[0] = len(adequacy_matrices) - 1
    start_indexes.sort()
    end_indexes.sort()
    relation_indexes.sort()
    return start_indexes, end_indexes, relation_indexes


def split_matrices(relation_matrices_string, start_indexes, end_indexes, relation_indexes):
    # It splits each table and matrix accordingly to indexes
    if len(start_indexes) != len(end_indexes):
        raise ValueError(
            "Number of start indexes \"%d\" is different of end indexes \"%d\""
            % (len(start_indexes), len(end_indexes))
        )
    if len(relation_indexes) != (len(start_indexes) - 1) // 2:
        raise ValueError(
            "Number of relation indexes \"%d\" is different of \"%d\""
            % (len(relation_indexes), (len(start_indexes) - 1) // 2)
        )

    function_word = [relation_matrices_string[each_index].split("\t")[0] for each_index in start_indexes]
    words_matrices = [relation_matrices_string[start_indexes[each_index]:end_indexes[each_index]]
                      for each_index in range(len(start_indexes)) if len(function_word[each_index].split(" ")) == 1]
    relation_matrices = [relation_matrices_string[start_indexes[each_index]:end_indexes[each_index]]
                         for each_index in range(len(start_indexes))
                         if len(function_word[each_index].split(" ")) == 2]
    relation_pairs = []
    for each_index in relation_indexes:
        relation_pair = relation_matrices_string[each_index].split(" ")
        relation_pair[1] = relation_pair[1].split("\t")[0]
        relation_pairs.append(relation_pair)
    return words_matrices, relation_matrices, relation_pairs


def matrix_product(words_matrices, relation_matrices):
    # It calculates the adequacy with matrices multiplications
    if len(words_matrices) < len(relation_matrices):
        raise ValueError(
            "Number of words matrices \"%d\" is less than relation matrices \"%d\","
            % (len(words_matrices), len(relation_matrices))
        )

    adequacy_matrices = []
    data_columns = []
    data_rows = []
    matrices_order = [each_header.split("\t")[0] for each_header in [each_matrix[0] for each_matrix in words_matrices]]

    for each_relation_matrix in relation_matrices:
        order_relation_index = matrices_order.index(each_relation_matrix[0].split(" ")[0])
        relation_index = relation_matrices.index(each_relation_matrix)
        words_matrix = words_matrices[order_relation_index]
        next_order_relation_index = matrices_order.index(each_relation_matrix[0].split(" ")[1].split("\t")[0])
        next_words_matrix = words_matrices[next_order_relation_index]
        x = [each_column.split("\t")[1:] for each_column in words_matrix[1:]]
        y = [each_column.split("\t")[1:] for each_column in relation_matrices[relation_index][1:]]
        product_matrix = [[sum(float(a) * float(b) for a, b in zip(x_row, y_col))
                           for y_col in zip(*y)] for x_row in x]
        z = [each_column.split("\t")[1:] for each_column in next_words_matrix[1:]]
        z = [[z[column_index][row_index] for column_index in range(len(z))] for row_index in range(len(z[0]))]
        product_matrix = [[sum(float(a) * float(b) for a, b in zip(product_matrix_row, z_col))
                           for z_col in zip(*z)] for product_matrix_row in product_matrix]
        # add a row constant to untie same calculated values in the matrix (10^-4 - index*10^-7)
        product_matrix = [[each_column[row_index] + pow(10, -4) - row_index * pow(10, -7)
                           for row_index in range(len(each_column))] for each_column in product_matrix]
        data_column = [each_row.split("\t")[0] for each_row in words_matrix]
        data_row = [each_row.split("\t")[0] for each_row in next_words_matrix]
        data_columns.append(data_column)
        data_rows.append(data_row)
        adequacy_matrices.append(product_matrix)
    return adequacy_matrices, data_columns, data_rows


def most_adequate(adequacy_matrices, data_rows):
    # It sorts the values of the matrix to the "most adequate"
    if len(adequacy_matrices) != len(data_rows):
        raise ValueError(
            "Number of adequacy matrices \"%d\" is different than data rows \"%d\","
            % (len(adequacy_matrices), len(data_rows))
        )

    most_adequate_matrices = []
    for relation_index in range(len(adequacy_matrices)):
        most_adequate_matrix = []
        for each_column in adequacy_matrices[relation_index]:
            adequacy_sorted = sorted(each_column, reverse=True)
            index_of_sorted = [each_column.index(adequacy_sorted[row_index]) + 1
                               for row_index in range(len(adequacy_sorted))]
            most_adequate_row = [data_rows[relation_index][index_of_sorted[row_index]]
                                 for row_index in range(len(adequacy_sorted))]
            most_adequate_matrix.append(most_adequate_row)
        most_adequate_matrices.append(most_adequate_matrix)
    return most_adequate_matrices


def remove_collisions(most_adequate_matrices, adequacy_matrices, data_rows):
    # it removes the words with the same first two letters
    if len(adequacy_matrices) != len(data_rows):
        raise ValueError(
            "Number of adequacy matrices \"%d\" is different than data rows \"%d\","
            % (len(adequacy_matrices), len(data_rows))
        )
    if len(most_adequate_matrices) != len(data_rows):
        raise ValueError(
            "Number of most adequate matrices \"%d\" is different than data rows \"%d\","
            % (len(most_adequate_matrices), len(data_rows))
        )

    most_adequate_matrices_nc = []
    for each_adequate_matrix in most_adequate_matrices:
        most_adequate_matrix_nc = []
        for each_column in each_adequate_matrix:
            # Copying the list without referencing it
            column_nc = list(each_column)
            first_letters = []
            for each_word in each_column:
                if each_word[0:2] in first_letters:
                    # Pop the word and send it to the end of the list
                    column_nc.append(column_nc.pop(column_nc.index(each_word)))
                first_letters.append(each_word[0:2])
            most_adequate_matrix_nc.append(column_nc)
        most_adequate_matrices_nc.append(most_adequate_matrix_nc)
    return most_adequate_matrices_nc


def sort_adequate(main_dict, most_adequate_matrices, relation_pairs):
    # It sorts the most adequate values without collisions
    if len(most_adequate_matrices) != len(relation_pairs):
        error_message = "Number of adequate matrices %d is different than the relation pairs %d"
        raise ValueError(error_message % (len(most_adequate_matrices), len(relation_pairs)))

    sorted_matrices_nc = []
    for matrix_index in range(len(most_adequate_matrices)):
        each_matrix_nc = most_adequate_matrices[matrix_index]
        bits = main_dict[relation_pairs[matrix_index][1]]["BIT_LENGTH"]
        final_length = 2 ** bits
        sorted_matrix_nc = []
        for each_column in each_matrix_nc:
            adequate_sorted = sorted(each_column[:final_length], reverse=True)
            sorted_matrix_nc.append(adequate_sorted)
        sorted_matrices_nc.append(sorted_matrix_nc)
    return sorted_matrices_nc


def update_dictionary(main_dict, most_adequate_matrices, relation_pairs, data_columns):
    # It formats the dictionary with keys and lists of words
    if len(most_adequate_matrices) != len(data_columns):
        raise ValueError(
            "Number of non-conflicted matrices \"%d\" is different than data columns \"%d\","
            % (len(most_adequate_matrices), len(data_columns))
        )
    if len(most_adequate_matrices) != len(relation_pairs):
        raise ValueError(
            "Number of non-conflicted matrices \"%d\" is different than the relation_pairs \"%d\","
            % (len(most_adequate_matrices), len(relation_pairs))
        )

    least_adequate_dict = {"ID": "least_adequate"}
    for matrix_index in range(len(most_adequate_matrices)):
        relation_pair = relation_pairs[matrix_index]
        most_adequate_matrix_nc = most_adequate_matrices[matrix_index]
        if relation_pair[0] not in least_adequate_dict.keys():
            least_adequate_dict[relation_pair[0]] = {relation_pair[1]: {}}
        else:
            least_adequate_dict[relation_pair[0]].update({relation_pair[1]: {}})

        if relation_pair[1] not in main_dict[relation_pair[0]].keys():
            main_dict[relation_pair[0]][relation_pair[1]] = {"IMAGE": [], "MAPPING": {}}
        if relation_pair[1] not in main_dict[relation_pair[0]]["LEADS"]:
            main_dict[relation_pair[0]]["LEADS"].append(relation_pair[1])

        # Create a list of unique values "IMAGE"
        image_list = [each_word for each_row in most_adequate_matrix_nc for each_word in each_row]
        image_list = sorted(list(OrderedDict.fromkeys(image_list)))

        main_dict[relation_pair[0]][relation_pair[1]]["IMAGE"] = image_list

        # Create a list of total keys used "TOTAL_LIST"
        filling_order_index = [[each_row[0] for each_row in data_columns].index(each_word[0]) for each_word in
                               relation_pairs]
        main_dict[relation_pair[0]]["TOTAL_LIST"] = data_columns[filling_order_index[matrix_index]][1:]
        if not main_dict[relation_pair[1]]["LEADS"]:
            main_dict[relation_pair[1]]["TOTAL_LIST"] = image_list

        # Insert word lists in dictionaries
        dict_json = {}
        for column_index in range(len(most_adequate_matrix_nc)):
            column_key = data_columns[filling_order_index[matrix_index]][column_index + 1]
            last_word_dict = {column_key: most_adequate_matrix_nc[column_index][-1]}
            least_adequate_dict[relation_pair[0]][relation_pair[1]].update(last_word_dict)
            most_adequate_matrix_nc[column_index].sort()
            dict_json[column_key] = most_adequate_matrix_nc[column_index]
        main_dict[relation_pair[0]][relation_pair[1]]["MAPPING"] = dict_json
    allocate_global_variable(least_adequate_dict)
    return main_dict


def serialize_dict(dict_to_serialize: dict):
    # It creates a string containing whole information from the dictionary
    serialization = ""
    for each_key in dict_to_serialize:
        if each_key == "VERSION":
            continue
        serialization += each_key
        if type(dict_to_serialize[each_key]) == dict:
            serialization += serialize_dict(dict_to_serialize[each_key])
        elif type(dict_to_serialize[each_key]) == list:
            serialization += "".join(dict_to_serialize[each_key])
        elif type(dict_to_serialize[each_key]) == int:
            serialization += str(dict_to_serialize[each_key])
        elif type(dict_to_serialize[each_key]) == str:
            serialization += dict_to_serialize[each_key]
    return serialization


def dict_to_bytes(serialized_dict: str):
    # It converts the string to bytes
    bytes_dict = bytearray(0)
    for each_char in serialized_dict:
        bytes_dict.append(int.from_bytes(each_char.encode("UTF-8"), "big"))
    return bytes_dict


def calculate_version(bytes_dict, main_dict):
    # It creates a particular version for the string as bytes using hash function
    hash_bytes = hashlib.sha256(bytes_dict).digest()
    hash_string = hash_bytes.hex()
    main_dict["VERSION"]["SHA256_CONDENSED_FULL"] = hash_string
    allocate_global_variable(main_dict)
    return main_dict


def save_files(main_dict, file_name, themes_directory=None):
    parent_path = Path(__file__).parent.absolute()
    save_path = parent_path / file_name if themes_directory is None else parent_path / themes_directory / file_name
    with open(save_path, "w+") as f:
        json.dump(main_dict, f, indent=4, sort_keys=True)


def main():
    themes_directory = Path("edit_themes")
    main_dict, relation_matrices_string = open_files(themes_directory)

    start_indexes, end_indexes, relation_indexes = find_header_indexes(main_dict, relation_matrices_string)
    words_matrices, relation_matrices, relation_pairs = split_matrices(
        relation_matrices_string, start_indexes, end_indexes, relation_indexes
    )
    adequacy_matrices, data_columns, data_rows = matrix_product(words_matrices, relation_matrices)
    most_adequate_matrices = most_adequate(adequacy_matrices, data_rows)
    most_adequate_matrices_nc = remove_collisions(most_adequate_matrices, adequacy_matrices, data_rows)
    most_adequate_matrices_nc = sort_adequate(main_dict, most_adequate_matrices_nc, relation_pairs)
    main_dict = update_dictionary(
        main_dict, most_adequate_matrices_nc, relation_pairs, data_columns
    )

    serialized_dict = serialize_dict(main_dict)
    bytes_dict = dict_to_bytes(serialized_dict)
    main_dict = calculate_version(bytes_dict, main_dict)
    save_files(main_dict, "main.json", themes_directory)


def word_swap(file_name: str,
              replace_by: str,
              syntactic_replace_by: str,
              replace_in: str,
              syntactic_replace_in: str,
              to_be_replaced: str,
              copy_from=None,
              file_load=None):
    # It swaps a word by another in the loaded dictionary in the given list of a word key
    # "replace_by" is the word that you want to introduce in the list
    # "syntactic_replace_by" is the syntactic position of the word "replace_by", e.g. "OBJECT"
    # "to_be_replaced" is the word that you want to be removed from the list
    # "syntactic_replace_in" is the syntactic position of the word "replace_in", e.g. "SUBJECT"
    # "replace_in" is the key where you want to introduce the word "replace_by"
    # "copy_from" is where the list is copied if "replace_by" did not exist previously

    global loaded_dict
    if file_load is None or isinstance(file_load, str):
        with open(file_name) as json_file:
            loaded_dict = json.load(json_file)
    else:
        loaded_dict = file_load

    key_existence_condition = [replace_by not in loaded_dict[syntactic_replace_by][each_restriction].keys() for
                               each_restriction in loaded_dict[syntactic_replace_by]["LEADS"]]

    condition = any(key_existence_condition) or len(loaded_dict[syntactic_replace_by]["LEADS"]) == 0
    if (replace_by not in loaded_dict[syntactic_replace_by]["TOTAL_LIST"] or not condition) and copy_from is None:
        raise ConfigurationError(
            "The key \"%s\" does not exist in the lists of \"%s\""
            % (replace_by, syntactic_replace_by)
        )
    condition = all(key_existence_condition) or len(loaded_dict[syntactic_replace_by]["LEADS"]) == 0
    if replace_by in loaded_dict[syntactic_replace_by]["TOTAL_LIST"] and condition and copy_from is not None:
        raise ConfigurationError(
            "The key \"%s\" already exist in the lists of \"%s\""
            % (replace_by, syntactic_replace_by)
        )

    words_list = loaded_dict[syntactic_replace_in][syntactic_replace_by]["MAPPING"][replace_in] \
        if syntactic_replace_in != "NONE" else loaded_dict[syntactic_replace_by]["TOTAL_LIST"]

    # Concatenate first two letters of each word
    first_letters_list = [each_word[:2]
                          for each_word in words_list]

    first_letters_string = " ".join(first_letters_list)
    first_letters_word = replace_by[:2]
    first_letters_to_replace = to_be_replaced[:2]
    if (first_letters_word in first_letters_string) and (first_letters_word != first_letters_to_replace):
        word_index = first_letters_string.index(first_letters_word) // 3
        raise ConfigurationError(
            "Collision \"%s\" with \"%s\""
            % (replace_by, words_list[word_index])
        )
    else:
        word_index = words_list.index(to_be_replaced)
        total_list_word = loaded_dict[syntactic_replace_by]["TOTAL_LIST"]

        if syntactic_replace_in != "NONE":
            image_words = loaded_dict[syntactic_replace_in][syntactic_replace_by]["IMAGE"]
            list_mapping = loaded_dict[syntactic_replace_in][syntactic_replace_by]["MAPPING"]
            list_mapping[replace_in][word_index] = replace_by
            list_mapping[replace_in].sort()
            if replace_by not in image_words:
                image_words.append(replace_by)
                image_words.sort()

        if replace_by not in total_list_word:
            total_list_word.append(replace_by)
            total_list_word.sort()

        if copy_from is not None:
            [loaded_dict[syntactic_replace_by][each_restriction]["MAPPING"].update(
                {replace_by: loaded_dict[syntactic_replace_by][each_restriction]["MAPPING"][copy_from]}
            ) for
             each_restriction in loaded_dict[syntactic_replace_by]["LEADS"]]

        save_files(loaded_dict, file_name)

        success_phrase = to_be_replaced + " substituted by " + replace_by
        if syntactic_replace_in != "NONE":
            success_phrase = success_phrase + " at " + syntactic_replace_in
        if copy_from is not None:
            success_phrase = success_phrase + " borrowed dependencies from " + copy_from
        print(success_phrase)


def allocate_global_variable(variable):
    global loaded_dict
    global main_least_adequate
    if isinstance(variable, dict):
        if "ID" not in variable.keys():
            loaded_dict = variable
        else:
            if variable["ID"] == "least_adequate":
                main_least_adequate = variable


if __name__ == "__main__" and len(sys.argv) == 1:
    loaded_dict = {}
    main_least_adequate = []
    main()
elif __name__ == "__main__" and len(sys.argv) == 7:
    word_swap(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
elif __name__ == "__main__" and len(sys.argv) == 8:
    word_swap(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
