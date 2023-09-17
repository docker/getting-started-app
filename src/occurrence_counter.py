from bs4 import BeautifulSoup
import requests
import string
from typing import Any

class OccurrenceCounter:
    
    def get_occurrences_from_file(self, file, n: int = -1) -> list[tuple]:
        """ Returns a list of the n most common bigrams in the file at path. If n is -1, returns all bigrams sorted by occurence count

        Args:
            path (str): path to the file to search for bigrams in
            n (int, optional): the amount of bigrams to return. -1 returns all. Defaults to -1.

        Raises:
            FileNotFoundError: Raised if the file at path does not exist

        Returns:
            list[tuple]: a list of tuples containing the bigram and the number of occurrences in the file
        """
        data = file.read().decode('utf-8')
        occurrences = self.get_occurrences_from_string(data, n)
        return occurrences
    
    def get_occurrences_from_wiki_page(self, url: str, n: int = -1) -> list[tuple]:
        """ Returns a list of the n most common bigrams in the file at path. If n is -1, returns all bigrams sorted by occurence count

        Args:
            url (str): url to the wiki page to search for bigrams in
            n (int, optional): the amount of bigrams to return. -1 returns all. . Defaults to -1.
            
        Raises:
            Exception: Raised if the wiki page could not be fetched

        Returns:
            list[tuple]: a list of tuples containing the bigram and the number of occurrences in the wiki page
        """
        try:
            wiki = self.get_wiki_page(url)
            wiki_parsed = self.parse_wiki_page(wiki)
            occurrences = self.get_occurrences_from_string(wiki_parsed, n)
            return occurrences
        except Exception as e:
            raise e
        
    def get_occurrences_from_string(self, data: str, n: int = -1) -> list[tuple]:
        """ Returns a list of the n most common bigrams in the given string. If n is -1, returns all bigrams sorted by occurence count

        Args:
            data (str): the data to search for bigrams in
            n (int, optional): the amount of bigrams to return. -1 returns all. Defaults to -1.

        Returns:
            list[tuple]: a list of tuples containing the bigram and the number of occurrences in the string
        """
        data_lower_no_punc = self.get_lower_data_no_punc(data)
        word_list = self.split_data(data_lower_no_punc)
        occurence_counts = self.create_occurrence_list(word_list)
        n_most_common = self.get_most_common(occurence_counts, n)
        return n_most_common

    def get_lower_data_no_punc(self, data: str) -> str:
        """ returns the given string with all punctuation removed (except for apostrophes) and all characters lowercased"""
        punctuation_no_apostrophe = string.punctuation.replace("'", '')
        for char in punctuation_no_apostrophe:
            data = data.replace(char, '')
        for char in string.whitespace:
            data = data.replace(char, ' ')
        data = data.lower()
        return data
        
    def split_data(self, data: str) -> list:
        return [ word for word in data.split(' ') if word != '']

    def create_occurrence_list(self, words_list: list) -> dict[str, int]:
        occurrences_dict = {}
        for index, word in enumerate(words_list):
            if index + 1 == len(words_list):
                return occurrences_dict.items()
            bigram = f"{word} {words_list[index + 1]}"
            if not bigram in occurrences_dict:
                occurrences_dict[bigram] = 1
            else:
                occurrences_dict[bigram] += 1
        
    def get_most_common(self, occurence_counts: list[tuple[Any, int]], n: int = -1) -> list[tuple]:
        """ returns the first n tuples with the highest 2nd value in the tuple

        Args:
            occurence_counts (list[tuple[Any, int]]): lists of tuples containing the bigram and the number of occurrences in the data
            n (int, optional): the number of tuples to return. -1 returns all. Defaults to -1

        Returns:
            list[tuple]: the highest n tuples
        """
        if n == -1 or n > len(occurence_counts):
            n = len(occurence_counts)
        occurence_counts_sorted = sorted(occurence_counts, key=lambda x: x[1], reverse=True)
        return occurence_counts_sorted[:n]

    def get_wiki_page(self, url: str) -> str:
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Error: {response.status_code}')
            raise Exception(f'Couldnt fetch wiki page: {response.status_code}')
        return response.text

    def parse_wiki_page(self, page_text: str) -> str:
        soup = BeautifulSoup(page_text, 'html.parser')
        text = ""
        for tag in soup.find_all('sup'):
            tag.decompose()
        for tag in soup.find_all('p'):
            text += tag.get_text()
        return text