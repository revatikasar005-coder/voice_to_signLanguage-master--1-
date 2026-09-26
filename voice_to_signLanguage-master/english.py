import os
import sys
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.tree import Tree, ParentedTree
# from nltk.parse.stanford import StanfordParser
from conf import JAR_DIR

# Keep jar env if you want, but no JDK required for fallback:
os.environ.pop('JAVAHOME', None)
os.environ.pop('STANFORD_PARSER', None)
os.environ.pop('STANFORD_MODELS', None)
os.environ.pop('CLASSPATH', None)

nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

text = ""

def get_stanford_parser():
    # Always use the fallback parser engine (no Java dependency)
    # print("Using fallback parser (no JDK required)")
    return None


def simple_parse_tree(tokens):
    tagged = nltk.pos_tag(tokens)
    grammar = r"""
      NP: {<DT|PRP\$|JJ.*|NN.*|PRP>+}
      VP: {<MD>?<VB.*><RB.*>*<NP|PP|PRP|JJ.*|DT|NN.*>*}
      PRP: {<PRP>}
    """
    parser = nltk.RegexpParser(grammar)
    chunked = parser.parse(tagged)

    def convert_node(node):
        if isinstance(node, tuple):
            return node[0]
        return Tree(node.label(), [convert_node(child) for child in node])

    return convert_node(chunked)


def filter_stop_words(words):
    stopwords_set = set(['a', 'an','am', 'The', 'is','for','to'])
    # stopwords_set = set(stopwords.words("english"))
    words = list(filter(lambda x: x not in stopwords_set, words))
    return words


def lemmatize_tokens(token_list):
    lemmatizer = WordNetLemmatizer()
    ps = PorterStemmer()
    lemmatized_words = []
    for token in token_list:
        #token=ps.stem(token)
        token = lemmatizer.lemmatize(token)
        lemmatized_words.append(lemmatizer.lemmatize(token,pos="v"))
    return lemmatized_words


def label_parse_subtrees(parent_tree):
    tree_traversal_flag = {}

    for sub_tree in parent_tree.subtrees():
        tree_traversal_flag[sub_tree.treeposition()] = 0
    return tree_traversal_flag


def handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    # if clause is Noun clause and not traversed then insert them in new tree first
    if tree_traversal_flag[sub_tree.treeposition()] == 0 and tree_traversal_flag[sub_tree.parent().treeposition()] == 0:
        tree_traversal_flag[sub_tree.treeposition()] = 1
        modified_parse_tree.insert(i, sub_tree)
        i = i + 1
    return i, modified_parse_tree


def handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    # if clause is Verb clause or Proportion clause recursively check for Noun clause
    for child_sub_tree in sub_tree.subtrees():
        if child_sub_tree.label() == "NP" or child_sub_tree.label() == 'PRP':
            if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                tree_traversal_flag[child_sub_tree.treeposition()] = 1
                modified_parse_tree.insert(i, child_sub_tree)
                i = i + 1
    return i, modified_parse_tree


def modify_tree_structure(parent_tree):
    # Mark all subtrees position as 0
    tree_traversal_flag = label_parse_subtrees(parent_tree)
    # Initialize new parse tree
    modified_parse_tree = Tree('ROOT', [])
    i = 0
    for sub_tree in parent_tree.subtrees():
        if sub_tree.label() == "NP":
            i, modified_parse_tree = handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)
        if sub_tree.label() == "VP" or sub_tree.label() == "PRP":
            i, modified_parse_tree = handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)

    # recursively check for omitted clauses to be inserted in tree
    for sub_tree in parent_tree.subtrees():
        for child_sub_tree in sub_tree.subtrees():
            if len(child_sub_tree.leaves()) == 1:  #check if subtree leads to some word
                if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                    tree_traversal_flag[child_sub_tree.treeposition()] = 1
                    modified_parse_tree.insert(i, child_sub_tree)
                    i = i + 1

    return modified_parse_tree

def convert_eng_to_isl(input_string):
    tokens = input_string.strip().split()
    if not tokens:
        return []
    if len(tokens) == 1:
        return tokens

    parser = get_stanford_parser()
    parse_tree = None
    if parser is not None:
        try:
            possible_parse_tree_list = [tree for tree in parser.parse(tokens)]
            if possible_parse_tree_list:
                parse_tree = possible_parse_tree_list[0]
        except Exception as exc:
            print("StanfordParser parse failed; using fallback parse method:", exc)

    if parse_tree is None:
        parse_tree = simple_parse_tree(tokens)

    print(parse_tree)

    # Convert into tree data structure
    parent_tree = ParentedTree.convert(parse_tree)

    modified_parse_tree = modify_tree_structure(parent_tree)

    parsed_sent = modified_parse_tree.leaves()
    return parsed_sent

def pre_process(sentence):
    words = list(sentence.split())
    f = open('words.txt', 'r')
    eligible_words = f.read()
    f.close()
    final_string = ""

    for word in words:
        if word not in eligible_words:
            for letter in word:
                final_string += " " + letter
        else:
            final_string += " " + word

    return final_string

# DRIVER CODE

def isl(text):
    input_string = text.capitalize()
    print(input_string)
    isl_parsed_token_list = convert_eng_to_isl(input_string)
    print("isl parsed token list: ",isl_parsed_token_list)
    # lemmatize tokens
    lemmatized_isl_token_list = lemmatize_tokens(isl_parsed_token_list)
    print("LEMMATIZED WORDS",lemmatized_isl_token_list)

    # remove stop words
    filtered_isl_token_list = filter_stop_words(lemmatized_isl_token_list)
    print("filtered isl token list",filtered_isl_token_list)
    isl_text_string = ""

    for token in filtered_isl_token_list:
        isl_text_string += token
        isl_text_string += " "

    isl_text_string = isl_text_string.lower()

    print(isl_text_string)
    return isl_text_string


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("Enter English text to convert to ISL: ").strip()
    isl(text)