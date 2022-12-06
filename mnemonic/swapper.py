# The software swaps two words in the dictionary

class ConfigurationError(Exception):
    pass


def check_key_existence_error(loaded_dict: dict,
                              replace_by: str,
                              syntactic_replace_by: str,
                              copy_from=None):
    """
        This function complete checks if given words exists where it should and does not exist where it should not

    Parameters
    ----------
    loaded_dict : dict
        This is the base dictionary where all changes will be done
    replace_by : str
        This is the word wanted to introduce in the list
    syntactic_replace_by : str
        This is the syntactic position of the word "replace_by", e.g. "SUBJECT"
    copy_from :
        This is where the list is copied if "replace_by" did not exist previously
    """
    key_existence_condition = [replace_by not in loaded_dict[syntactic_replace_by][each_restriction].keys() for
                               each_restriction in loaded_dict[syntactic_replace_by]["RESTRICTS"]
                               ]

    condition = any(key_existence_condition) or len(loaded_dict[syntactic_replace_by]["RESTRICTS"]) == 0
    if (replace_by not in loaded_dict[syntactic_replace_by]["TOTAL_LIST"] or not condition) and copy_from is None:
        raise ConfigurationError(
            "The key \"%s\" does not exist in the lists of \"%s\""
            % (replace_by, syntactic_replace_by)
        )

    condition = all(key_existence_condition) or len(loaded_dict[syntactic_replace_by]["RESTRICTS"]) == 0
    if replace_by in loaded_dict[syntactic_replace_by]["TOTAL_LIST"] and condition and copy_from is not None:
        raise ConfigurationError(
            "The key \"%s\" already exist in the lists of \"%s\""
            % (replace_by, syntactic_replace_by)
        )


def check_collision(replace_by: str,
                    to_be_replaced: str,
                    words_list: list):
    """
        This function checks the collision criteria of first two letters

    Parameters
    ----------
    replace_by : str
        This is the word wanted to introduce in the list
    to_be_replaced : str
        This is the word wanted to be removed from the list
    words_list : list
        This is the list of mapped restricted words or the total words if there is no restriction
    """
    first_letters_list = [each_word[:2]
                          for each_word in words_list
                          ]

    first_letters_string = " ".join(first_letters_list)
    first_letters_word = replace_by[:2]
    first_letters_to_replace = to_be_replaced[:2]
    if (first_letters_word in first_letters_string) and (first_letters_word != first_letters_to_replace):
        word_index = first_letters_string.index(first_letters_word) // 3
        raise ConfigurationError(
            "Collision \"%s\" with \"%s\""
            % (replace_by, words_list[word_index])
        )


def word_swap(loaded_dict: dict,
              replace_by: str,
              syntactic_replace_by: str,
              replace_in: str,
              syntactic_replace_in: str,
              to_be_replaced: str,
              copy_from=None) -> (dict, str):
    """
        This function swaps a word by another in the loaded dictionary in the given list of a word key

    Parameters
    ----------
    loaded_dict : dict
        This is the base dictionary where all changes will be done
    replace_by : str
        This is the word wanted to introduce in the list
    syntactic_replace_by : str
        This is the syntactic position of the word "replace_by", e.g. "SUBJECT"
    replace_in : str
        This is the key where wanted to introduce the word "replace_by"
    syntactic_replace_in : str
        This is the syntactic position of the word "replace_in", e.g. "VERB"
    to_be_replaced : str
        This is the word wanted to be removed from the list
    copy_from :
        This is where the list is copied if "replace_by" did not exist previously

    Returns
    -------
    dict, str
        Returns the edited base dictionary and a message with the changes
    """
    check_key_existence_error(loaded_dict, replace_by, syntactic_replace_by, copy_from)

    words_list = loaded_dict[syntactic_replace_in][syntactic_replace_by]["MAPPING"][replace_in] \
        if syntactic_replace_in != "NONE" else loaded_dict[syntactic_replace_by]["TOTAL_LIST"]

    check_collision(replace_by, to_be_replaced, words_list)

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
         each_restriction in loaded_dict[syntactic_replace_by]["RESTRICTS"]]

    success_phrase = to_be_replaced + " substituted by " + replace_by
    if syntactic_replace_in != "NONE":
        success_phrase = success_phrase + " at " + syntactic_replace_in + " " + replace_in
    if copy_from is not None:
        success_phrase = success_phrase + " borrowed dependencies from " + copy_from
    print(success_phrase)
    return loaded_dict, success_phrase
