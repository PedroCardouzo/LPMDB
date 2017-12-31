# -*- coding: <UTF-8> -*-
import lib.main_storage as ms
from lib.movie import Movie
from lib.patricia_trie import PatriciaTrie
from lib.btree import BTree
import lib.reversed_files as rf
from operator import gt, ge, lt, le, eq, ne
import lib._globals as _globals


def print_indexed(iter):
    out = []
    if iter is not None:
        counter = (x for x in range(len(iter)))
        for element in iter:
            out.append("{0}: {1}".format(next(counter), element))
    print(out)


class Parser:

    def __init__(self, database_name='lpmdb.bin'):
        self.names = {}
        self.db_name = database_name
        self.func_dict = {'>': gt, '>=': ge, '<': lt, '<=': le, '=': eq, '==': eq, '!=': ne}
        self.help = dict(
default=("\n"
         "# whenever <field> is referred it means one of the Movie attributes\n"
         "# whenever <name> is referred it means one of the local definitions from self.names>\n"
         "# [<arg>] means that <arg> is optional (probably has a default value)\n"
         "        help options:\n"
         "            help expressions\n"
         "            help piping\n"
         "            help filter\n"
         "            help sort\n"
         "            help make\n"
         "            help print\n"
         "            help quickprint\n"
         "            help names\n"
         "            help extract\n"
         "            help len\n"
         "            help delete\n"
         "            help split\n"
         "            help merge\n"
         "            help rename\n"
         "        *hint: start by expressions, then piping, then sort and filter\n"
         "        *hint: use 'help all' to show all documentation\n"),
expressions=("\n"
             "query or search or :: ->  # search functions\n"
             "    # BTree search\n"
             "        <field> <comparison_operator> <target_value> [as <name>]\n"
             "        # example: average_rating > 70 -> returns a list with movies that average_rating is above 70\n"
             "        # <comparison_operator>: supports >, >=, <, <=, != and == or =\n"
             "        <target_value1> <comparison_operator1> <field> <comparison_operator2> <target_value2>\n"
             "        # same as above but you may filter in a range\n"
             "        # example: 80 > average_rating >= 60 -> should return a list with movies that average_rating is above 60 and below 70\n"
             "\n"
             "    # PATRICIA Trie search\n"
             "        from <field> <alpha> <exp> [as <name>]\n"
             "        # <alpha>: fetch -> does a prefix search, but accepts wildcards after first letter\n"
             "                   match or filter -> does a implicit infix search and also accepts wildcards\n"
             "        # <exp>: expression to search as 'abc * dd *f'\n"
             "        # example: from title match 'harry * stone' -> should return harry potter and the philosopher stone\n"
             "\n"
             "    # Reversed File search:\n"
             "        rf <field> <desired> [as <name>]\n"
             "        # <desired> -> the desired field you want to fetch the movies from\n"),
piping=("\n"
        "# Piping -> <expression> | <filter_criteria1> | <filter_criteria2> ... | <filter_criteriaN>\n"
        "    You may apply as much filtering criteria as you want over the original expression with\n"
        "    piping each filter criteria must be as in the following structure\n"
        "    <field> <string>  # filters out the movies which the string couldn't be matched inside the field\n"
        "    # or\n"
        "    <field> <comparison_operator> <target_value>  # filters out movies which the field value compared to the \n"
        "    # target_value by that comparison_operator returned false\n"
        "    # or\n"
        "    sort <field>[ <reversed>]\n"
        "    # if third argument is provided, will sort in decreasing order\n"),
filter=("\n"
        "filter -> # filtering functions\n"
        "    # works pretty much like piping, but can be done after a search stored in names\n"
        "    # <name> defaults to 'default'\n"
        "\n"
        "    filter[ <name>]: <field> <string>\n"
        "    filter[ <name>]: <field> <comparison_operator> <target_value>\n"
        "    # ex.: filter: title harry -> filters the 'default' list of movies to those who have harry in their titles\n"
        "    # ex.: filter aa: title harry -> sabe thing but filters another variable called 'aa'\n"
        "\n"
        "    filter <name> <| <name2> <field> <string>\n"
        "    filter <name> <| <name2> <field> <comparison_operator> <target_value>\n"
        "    # same as above but now it filters <name2> and saves the result in <name>\n"),
sort=("\n"
      "sort -> # sorts stuff\n"
      "    sort <name> <field> [<reversed>] \n"
      "    # works exaclty the same as the ones used with piping but you also need to provide a\n"
      "    # <name> so it knows that list to sort\n"
      "    # doesn't makes sense to use it after a BTree query unless ordering for something else\n"),
make=("\n"
      "make -> # construction functions\n"
      "   # make is used to construct BTree, PATRICIA Trie or a reversed file from a database bin file \n"
      "   make btree <database_filename> [<field>]  # by default <field> value is average_rating\n"
      "   make ptrie <database_filename> [<field>]  # by default <field> value is title\n"
      "   make rf <database_filename> <field>       # no default values to field provided\n"),
print=("\n"
       "print -> # print information\n"
       "    print <name> <i> -> prints the i-th element from the list pointed by name\n"
       "    # or\n"
       "    print <name> all -> prints all elements from the list pointed by name\n"),
quickprint=("\n"
       "quickprint -> # print information\n"
       "    <name> <field> \n"
       "    # will print the desired <field> of every movie in the list pointed by <name>\n"),
extract=("\n"
       "extract -> # print selected fields\n"
       "    extract <fields> from <name>\n"
       "    # picks a name and shows the provided fields (separated by commas)\n"
       "    # title is always the first, where it provided or not\n"),
len=("\n"
     "len -> \n"
     "    len <name> -> prints the size of the list pointed by name\n"),
names=("\n"
       "names ->\n"
       "    names -> shows all the names that exists in the current execution\n"
       "    you may print a certain field of all the elements in a list pointed by one name with the following:\n"
       "    <name> <field>\n"),
delete=("\n"
       "delete or del -> #\n"
       "    del <name> -> deletes a entry on the names dictionary\n"),
split=("\n"
       "split or slice -> #\n"
       "    split <name> @ <position>\n"
       "    # splits the list pointed by <name> @ <position> and overrides it\n"),
merge=("\n"
       "merge -> #\n"
       "    merge <x>: <names>\n"
       "    # merge the lists pointed by each of <names> into the list pointed by <x> (<x> can be a new name)\n"),
rename=("\n"
        "rename -> #\n"
        "    rename <old_name> as <new_name>\n"
        "    # renames name <old_name> to <new_name>\n"),
help=("\n"
      "help -> # this\n"
      "    help [<command>]\n"
      "    # if used by itself provides the full documentation\n"
      "    # if used with a command as argument returns the documentation of that command only\n")
)


    def parse(self, string):
        if string == 'exit':
            return False
        elif string == 'help':
            print(self.help['default'])
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

            elif command == 'query' or command == 'search' or command == '::':
                print_indexed(self.parse_query(query))

            elif command == 'filter':
                print_indexed(self.parse_filter(query))

            elif command == 'sort':
                print_indexed(self.parse_sort(query))

            elif command == 'slice' or command == 'split':
                print_indexed(self.parse_split(query))

            elif command == 'make':
                print(self.parse_make(query))

            elif command == 'extract':
                print(self.parse_extract(query))

            elif command == 'reverse':
                print_indexed(self.parse_reverse(query))

            elif command == 'len':
                print(self.parse_len(query))

            elif command == 'merge':
                print(self.parse_merge(query))

            elif command == 'rename':
                print(self.parse_rename(query))

            elif command == 'print':
                print(self.parse_print(query))

            elif command == 'names':
                print(list(self.names.keys()))

            elif command == "delete" or command == "del":
                print_indexed(self.delete(query))

            elif command == 'help':
                print(self.parse_help(query))

            else:
                print('Invalid Syntax')

            return True

    def parse_help(self, query):
        if query == 'all':
            keys = ['expressions', 'piping', 'filter', 'sort', 'make', 'print', 'extract',
                    'len', 'names', 'delete', 'split', 'merge', 'rename', 'help']
            str_out = ''
            for key in keys:
                str_out += self.help[key]
            return str_out

        else:
            return self.help[query]

    def quickprint(self, name, field):
        return [x.__dict__.get(field, None) for x in self.names.get(name, [None])]

    def parse_merge(self, query):
        accumulator_name, query = query.split(': ', 1)
        temp = []

        for query_element in query.split(' '):
            temp += self.names[query_element]

        self.names[accumulator_name] = temp
        return [x.title for x in temp]

    def parse_rename(self, query):
        name_old, name_new = query.split(' as ')
        self.names[name_new] = self.names[name_old]
        del self.names[name_old]
        return [x.title for x in self.names[name_new]]

    def parse_sort(self, query):
        query = query.split(' ')
        reversed = len(query) == 3
        name, field = query[0], query[1]

        self.names[name].sort(key=lambda x: x.__dict__[field], reverse=reversed)
        return [x.title for x in self.names[name]]

    def parse_reverse(self, name):
        self.names[name].reverse()
        return [x.title for x in self.names[name]]

    def parse_query(self, query):
        apply_filter = '|' in query
        if apply_filter:
            query = query.split('|')
            query, filters_stack = query[0], query[:0:-1]  # reverse the second so that it can behave like a stack

        if ' as ' in query:
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
        field, desired_value = query.split(' ', 1)
        content = rf.read(field)
        if content is None:
            print("hint: use 'make rf " + field + "' to create this reversed file")
            return None
        else:
            for key in content.keys():
                if desired_value in key:
                    return content[key]

    def parse_ptrie(self, query):
        field, _type, exp = [x for x in query.split(' ', 2) if x != '']
        suffix = False # exp[0] == '*' and exp[-1] != '*'
        start_on_border = exp[0] != '*' or suffix

        ptrie = PatriciaTrie.load(field)

        if ptrie is None:
            return None
        elif exp == '*':
            return [x[1] for x in PatriciaTrie.propagate_to_branches([ptrie.root])] # @ debug
        #
        # if suffix:
        #     exp = exp[::-1]  # invert expression to search in suffix tree from the last character up to the first
        exp = [x for x in exp.split('*') if x != '']  # split at each '*'
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
            aux_node_list = []
            expression = exp_stack.pop()
            for node in node_list:
                aux_node_list = ptrie._infixSearch(expression, 0, node)

            return self.parse_trie_expression(ptrie, exp_stack, aux_node_list)

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
        elif comp_func == '!=':
            if len(args) == 5:
                print("inequality '!=' should only be used by itself")
                return None
            else:
                return [x.value for x in bt.search(lt, int(target_value)) + bt.search(gt, int(target_value))]

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
            reverse = len(filter_exp) == 3  # if len(filter_exp) == 3 it means that the query was 'sort' '<field>' 'reversed'
            field = filter_exp[1]
            cache.sort(key=lambda x: x.__dict__[field], reverse=reverse)
            return cache

        elif len(filter_exp) == 3:
            field, comp_func, target_value = filter_exp
            comp_func = self.func_dict[comp_func]
            return list(filter(lambda x: comp_func(int(x.__dict__[field]), int(target_value)), cache))

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

    def parse_split(self, query):
        name, position = query.split(' @ ')
        name = 'default' if name == '' else name
        position = int(position)
        self.names[name] = self.names[name][:position]
        return [x.title for x in self.names[name]]

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

        field = field if use_lambda else 'average_rating'
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

    def parse_extract(self, query):
        query, name = query.split(' from ')
        query = query.replace(' ', '')
        query = query.split(',')

        if 'title' in query:
            query.remove('title')  # remove the title so that it can be printed first, outside the loop
        string = ''
        for movie in self.names[name]:
            string += '\n\n' + movie.title
            for field in query:
                try:
                    string += '\n' + str(movie.__dict__[field])
                except KeyError:
                    string += "\nfield '" + field + "' doesn't exist"
        return string
    def parse_len(self, query):
        return len(self.names[query])

    # parse_print: self String ->
    def parse_print(self, query):
        name, index = query.split(' ')
        if index == 'all':
            out = ''
            counter = (str(x) + ' ->\n' for x in range(1, len(self.names[name])+1))
            for movie in self.names[name]:
                out += next(counter) + movie.__str__() + '\n'
            return out
        else:
            return self.names[name][int(index)].__str__()

    def delete(self, query):
        try:
            del self.names[query]
            return "name '" + query + "' deleted"
        except NameError:
            return "name '" + query + "' was undefined"


    def validate(self, args):
        allowed_symbols = self.func_dict.keys()

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