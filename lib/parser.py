# -*- coding: <UTF-8> -*-
import lib.main_storage as ms
from lib.movie import Movie
from lib.patricia_trie import PatriciaTrie
from lib.btree import BTree
import lib.reversed_files as rf
from operator import gt, ge, lt, le, eq
import lib._globals as _globals

class Parser:

    def __init__(self, database_name='lpmdb.bin'):
        self.names = {}
        self.db_name = database_name
        self.func_dict = {'>': gt, '>=': ge, '<': lt, '<=': le, '=': eq, '==': eq}
        self.help = """help:"""


    def parse(self, string):
        if string == 'exit':
            return False
        elif string == 'help':
            print(self.help)
            return True
        else:
            try:
                command, query = string.lower().split(' ', 1)
                if command == 'filter:':
                    command = 'filter'
                    query = 'default: ' + query
            except ValueError:
                if string == 'help' or string == 'names':
                    command, query = string, ''
                else:
                    print('Invalid Syntax')
                    return True

            if command in self.names.keys():
                print(self.quickprint(command, query))
                return True
            elif command == 'query' or command == '::':
                print(self.parse_query(query))
                return True
            elif command == 'filter':
                print(self.parse_filter(query))
                return True
            elif command == 'make':
                print(self.parse_make(query))
                return True
            elif command == 'show':
                print(self.parse_show(query))
                return True
            elif command == 'len':
                print(self.parse_len(query))
                return True
            elif command == 'print':
                print(self.parse_print(query))
                return True
            elif command == 'names':
                print(self.names.keys())
                return True
            elif command == "delete" or command == "del":
                print(self.delete(query))
                return True
            elif command == 'help':
                print(self.parse_help(query))
                return True
            else:
                print('Invalid Syntax')
                return True

    def quickprint(self, name, field):
        return [x.__dict__[field] for x in self.names.get(name, [None])]

    def parse_query(self, query):
        apply_filter = '|' in query
        if apply_filter:
            query = query.split('|')
            query, filters_stack = query[0], query[:0:-1]  # reverse the second so that it can behave like a stack

        if 'as' in query:
            query, name = query.split(' as ')
        else:
            name = 'default'

        name = name.replace(' ', '') # get rid of any extra ' '
        cache = self.parse_expression(query)
        if cache is None:
            return
        else:
            cache = ms.populate(cache)

        if apply_filter:
            cache = self.apply_pipe_filters(filters_stack, cache)

        self.names[name] = cache
        return [x.title for x in cache]

    def parse_expression(self, query):
        command, query = query.split(' ', 1)
        if command == 'rf':
            return self.parse_rf(query)
        elif command == 'from':
            return self.parse_ptrie(query)
        else:
            return self.parse_btree(command + ' ' + query)

    @staticmethod
    def parse_rf(query):
        field, desired_value = query.split(' ')
        content = rf.read(field)
        if content is None:
            print("hint: use 'make rf " + field + "' to create this reversed file")
            return None
        else:
            return content[desired_value]

    def parse_ptrie(self, query):
        field, _type, exp = [x for x in query.split(' ') if x != '']
        suffix = exp[0] == '*' and exp[-1] != '*'
        start_on_border = exp[0] != '*' or suffix

        ptrie = PatriciaTrie.load(field, suffix=suffix)

        if ptrie is None:
            return None
        elif exp == '*':
            return [x[1] for x in PatriciaTrie.propagate_to_branches([ptrie.root])] # @ debug

        if suffix:
            exp = exp[::-1]  # invert expression to search in suffix tree from the last character up to the first

        exp = exp.split('*')  # split at each '*'
        exp_stack = exp[::-1]  # invert the order of the list so last of the list is first (it became a stack)

        if start_on_border and _type == 'fetch':
            node_list = ptrie.prefixSearch(exp_stack.pop())
        elif _type == 'match' or _type == 'filter':
            node_list = ptrie.infixSearch(exp_stack.pop())
        else:
            print("invalid type '" + _type + "'")
            return None

        node_list = PatriciaTrie.propagate_to_branches(self.parse_trie_expression(ptrie, exp_stack, node_list))

        return [x[1] for x in node_list]

    def parse_trie_expression(self, ptrie, exp_stack, node_list):
        if not exp_stack:
            return node_list
        else:
            node_list = ptrie._infixSearch(exp_stack.pop(), 0, node_list)
            return self.parse_trie_expression(ptrie, exp_stack, node_list)

    def parse_btree(self, query):
        args = [x for x in query.split(' ') if x != '']
        apply_filter = len(args) == 5

        if apply_filter:
            args[0], args[2] = args[2], args[0]
            args[1] = self.comparison_operator_conversion(args[1])

        if self.validate(args):
            field, comp_func, target_value = args[0], args[1], args[2]
        else:
            return None

        bt = BTree.load(field)
        if bt is None:
            print("hint: use 'make btree " + field + "' to create this reversed file")
            print("p.s.: the 'field' must be a integer or float")
            return None
        else:
            query_results = bt.search(self.func_dict[comp_func], int(target_value))

        if apply_filter:
            comp_func, target_value = args[3], args[4]
            query_results = filter(lambda x: self.func_dict[comp_func](x.key, int(target_value)), query_results)

        return [x.value for x in query_results]

    def apply_pipe_filters(self, filters_stack, cache):
        if not filters_stack:
            return cache
        else:
            cache = self.apply_filter_function(filters_stack.pop(), cache)
            return self.apply_pipe_filters(filters_stack, cache)

    def apply_filter_function(self, filter_exp, cache):
        filter_exp = [x for x in filter_exp.split(' ') if x != '']
        if filter_exp[0] == 'sort':
            reverse = len(filter_exp) == 3  # if len(filter_exp) == 3 it means that the query was field op reversed
            field = filter_exp[1]
            cache.sort(key=lambda x: x.__dict__[field], reverse=reverse)
            return cache
        elif len(filter_exp) == 3:
            field, comp_func, target_value = filter_exp
            comp_func = self.func_dict[comp_func]
            return list(filter(lambda x: comp_func(x.__dict__[field], target_value), cache))
        elif len(filter_exp) == 2:
            field, infix_search = filter_exp
            return list(filter(lambda x: infix_search in x.__dict__[field].lower(), cache))

    def parse_filter(self, query):

        if '<|:' in query:
            query = query.replace(':', ' default:')

        save = '<|' in query

        if save:
            new_var_name, query = query.split(' <| ')

        name, filters = query.split(': ')
        filters = filters.split(' | ')[::-1]  # inverting list so that we have a stack

        filtered_list = self.apply_pipe_filters(filters, self.names[name])
        if save:
            self.names[new_var_name] = filtered_list

        return [x.title for x in filtered_list]

    def parse_make(self, query):
        try:
            command, query = query.split(' ', 1)
        except ValueError:
            return 'Missing arguments in query: ' + query
        if command == 'btree':
            return self.makeBTree(query)
        elif command == 'ptrie':
            return self.makePTrie(query)
        elif command == 'rev_file' or command == 'rf':
            return self.makeReversedFile(query)
        else:
            return "ERROR: invalid argument for 'make' command -> " + command

    @staticmethod
    def makeBTree(query):
        query = query.split(' ')
        database_filename = query[0]
        query = query[1:]

        use_t, use_lambda = False, False

        for attr in query:
            try:
                t = int(attr)
                use_t = True
            except:
                use_lambda = True
                field = attr

        field = field if use_lambda else 'averageRating'  # @ tochange
        λ = lambda x: x.__dict__[field]
        t = t if use_t else _globals.default_min_degree

        bt = BTree.createBTree(database_filename, min_degree=t, λ=λ)
        bt.save(field)
        return "created BTree file indexing field '" + field + "'"

    @staticmethod
    def makePTrie(query):
        query = query.split(' ')
        field = query[1] if len(query) == 2 else 'title'
        λ = lambda x: x.__dict__[field].lower()

        pt = PatriciaTrie.create_patricia_trie(query[0], λ=λ)

        pt.save(field)
        return "created PATRICIA TRIE file indexing field '" + field + "'"

    @staticmethod
    def makeReversedFile(query):
        db_filename, field = query.split(' ')
        rf.new_reversed_file(db_filename, field)
        return "created Reversed File indexing field '" + field + "'"

    @staticmethod
    def comparison_operator_conversion(comparison_operator):
        if comparison_operator == '>':
            return '<'
        elif comparison_operator == '>=':
            return '<='
        elif comparison_operator == '<':
            return '>'
        elif comparison_operator == '<=':
            return '>='
        else:
            return '=='

    def parse_show(self, query):
        print(query)

    def parse_len(self, query):
        return len(self.names[query])

    def parse_print(self, query):
        print(query)

    def delete(self, query):
        try:
            del self.names[query]
            return "name '" + query + "' deleted"
        except NameError:
            return "name '" + query + "' was undefined"


    @staticmethod
    def validate(args):
        allowed_symbols = ['>', '>=', '<', '<=', '=', '==']

        if len(args) == 5:
            if not args[3] in allowed_symbols:
                return False
            try:
                int(args[4])
            except ValueError:
                return False

        try:
            int(args[2])
        except ValueError:
            return False

        return type(args[0]) is str and args[1] in allowed_symbols