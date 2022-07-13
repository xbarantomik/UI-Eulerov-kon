import time

# 8 moznych operatorov (posunov na sachovnici)
move_x = [1, 1, -1, -1, 2, 2, -2, -2]
move_y = [2, -2, 2, -2, 1, -1, 1, -1]
tree = []                   # hlavny tree
stack = []                  # pole pre susedne uzly
board_size = None           # dlzka hrany sachovnice
SPECIAL = -20
end_statement_symbol = -1
input_parameters = [15, 5000000, False]         # moznosti
    # 0 - pocet sekund povolenych na bezanie programu
    # 1 - pocet krokov povolenych na bezanie programu
    # 2 - |True| -> vypisovat kazdy krok s poradovim cislom, |False| -> iba prvy a finalny krok

# list suradnic k prezentovaniu
prese_list_x = [5, 4, 1, 1, 2, 2, 3, 3, 4, 4]
prese_list_y = [7, 1, 1, 6, 7, 3, 4, 5, 2, 7]


#....trieda node...................................................................................
class Node:
    def __init__(self, x, y, position, prev_node):
        self.x_p = x                                #suradnica x
        self.y_p = y                                #suradnica y
        self.position = position                    #pozicia, napisana na sachovnici
        self.previous_node = prev_node              #odkaz pre predosly uzol
        self.is_root = False                        #ci je uzol root
        self.nodes_left_on_this_height = None       #pocet susecnych uzlov, skor pre kontrolu v Stacku
        self.w3n = None                             #VDT - vaha dalsieho tahu, urcena Warnsdorffovym algoritmom (v komenratoch sa to spomina)


#....vypis na konci pt. 1..........................................................................
def end_statement_base():
    print('Starting position: ')
    print('    X: ' + str(now_y))
    print('    Y: ' + str(now_x))
    print('Board size:')
    print('    ' + str(board_size) + 'x' + str(board_size))


#....vypis na konci pt. 2, podla symbolu(speci pre kazdy koniec)...................................
def end_statement(symbol, time_f):
    time_str = "{:.5f}".format(time_f)
    if symbol == 1:             #..uspesny koniec
        print_board(chessboard)
        print()
        end_statement_base()
        print('Finish: SUCCESSFUL')
        print('Number of steps: ' + str(counter))
        print('Time: ' + time_str + 's')
    elif symbol == 2:           #..stack bol prazdny
        print_board(chessboard)
        print()
        end_statement_base()
        print('Finish: UNSUCCESSFUL -> Stack was empty')
        print('Number of steps: ' + str(counter))
        print('Time: ' + time_str + 's')
    elif symbol == 3:           #..cas bol preshiahnuty
        print_board(chessboard)
        print()
        end_statement_base()
        print('Finish: UNSUCCESSFUL -> Time Exceeded')
        print('Number of steps: ' + str(counter))
        print('Time: ' + time_str + 's (stopped at)')
    elif symbol == 4:           # ..pocet krokov bol prekroceny
        print()
        end_statement_base()
        print('Finish: UNSUCCESSFUL -> Number of Steps Exceeded')
        print('Number of steps: ' + str(counter) + ' (stopped at)')
        print('Time: ' + time_str + 's')
    elif symbol == -1:
        print()
        print('end_statement_symbol bol -1')


#....vypise (nakresli) sachovnicu..................................................................
def print_board(chessboard):
    for i in range(board_size):
        for j in range(board_size):
            print(chessboard[i][j], end=' ')
        print()


#....ziska input pre parametre(cas, kroky).........................................................
def get_parameters():
    global input_parameters

    print('---------------------------')
    print('Max Time: ' + str(input_parameters[0]))
    print('Max Steps: ' + str(input_parameters[1]))
    print('Print all steps: ' + str(input_parameters[2]))
    print('---------------------------')
    parameters = input('Change? [Y/n]')
    print()
    if parameters == 'y' or parameters == 'Y':
        input_parameters[0] = int(input('Time: '))
        input_parameters[1] = int(input('Steps: '))
        pas = input('Print all steps: [Y/n]')
        if pas == 'Y' or pas == 'y':
            input_parameters[2] = True
        else:
            input_parameters[2] = False
        print()
        print('New parameters:')
        print('---------------------------')
        print('Max Time: ' + str(input_parameters[0]))
        print('Max Steps: ' + str(input_parameters[1]))
        print('Print all steps: ' + str(input_parameters[2]))
        print('---------------------------')


#....ziska input pre velkost sachovnice............................................................
def get_input():
    global board_size
    while True:
        b_size = int(input('Chessboard length: '))
        if b_size >= 5:
            break
        print('Must be at least 5')
    return b_size


#....ziska suradnice zaciatocneho bodu.............................................................
def get_starting_point():
    global board_size
    print('Starting point:')
    while True:
        y = int(input('X: '))
        x = int(input('Y: '))
        if y <= board_size and x <= board_size:
            break
        print('Must be smaller than ' + str(board_size))
    return x, y


def one_time_inputs():
    global board_size
    print('-------------------------------------------------')
    print('Press 1 for 10 predetermined starting points (min 8x8)')  # toto, kvoli prezentovaniu
    print('Press anything else to input your own starting points')
    if input() == '1':              #zistim board_size a parametere a 10x urobim vypis
        board_size = get_input()    #s tymito udajmi a x,y je v prese_list_x/y
        get_parameters()
        return True
    else:
        get_parameters()            #ak else tak klasicky po jednom
        return False


#....nastavy prvy uzol, teda root..................................................................
def set_root(now_x, now_y):
    root = Node(now_x, now_y, 1, None)
    root.is_root = True
    return root


#....z novych uzlov ide jeden do tree a ostatne do stacku (zoradene aby LIFO mal w3n najmensi).....
def sort_out_neighbor_nodes(nn_list, warnsdorff_list, used_index):
    if len(warnsdorff_list) != 0:
        warnsdorff_list.pop(used_index)             #popnem uzol (aj index) z listu na idexte, z ktoreho isiel uzol do tree
    nn_list.pop(used_index)
    tree[len(tree) - 1].nodes_left_on_this_height = len(nn_list)
    for i in range(len(nn_list)):
        nn_list[i].w3n = warnsdorff_list[i]         #pripisem uzlom VDT
        nn_list[i].nodes_left_on_this_height = len(nn_list)

    for i in range(len(nn_list)):                   #zoradim(vacsie cislo skorsie) a pridam uzly do stacku
        warn_max = warnsdorff_list.index(max(warnsdorff_list))
        stack.append(nn_list.pop(warn_max))
        if len(warnsdorff_list) != 0:
            warnsdorff_list.pop(warn_max)


#....zisti mozne dalsie tahy a vrati list s indexami pre move_x a move_y listy.....................
def is_in_board_and_free(chessboard, now_x, now_y):
    just_list = [1, 1, 1, 1, 1, 1, 1, 1]
    free_positions = []

    # ci je mimo sachovnicu
    for i in range(8):
        next_x = now_x + move_x[i]
        next_y = now_y + move_y[i]
        if next_x < 0 or next_y < 0 or next_x > board_size-1 or next_y > board_size-1:
            just_list[i] = 0

    #ci nie je uz obsadene to miesto
    for i in range(len(just_list)):
        if just_list[i] == 1:
            next_x = now_x + move_x[i]
            next_y = now_y + move_y[i]
            if chessboard[next_x][next_y] == 0:
                free_positions.append(i)

    return free_positions   # vraciam list s indexami volnych pozicii pre move_x a move_y


#....vracanie sa naspat po tree az pokym nebude na rovnakej vyske ako najvyssi uzol v stack-u......
def backing_up(chessboard):
    if len(stack) == 0:
        return True
    top_tree = tree.pop()                               #popne sa psledny pridany node z tree
    chessboard[top_tree.x_p][top_tree.y_p] = 0          #jeho pozicia na sachovnici sa nastavi na nulu
    top_node = stack.pop()                              #popne sa posledny pridany node zo stacku
    while True:                                         #porovnavam ci ich pozicia je rovnaka
        if top_node.position == top_tree.position:          #ak hej tak sa na sachovnici nastavi ich pozicia na suradniciach z nody zo stacku
            chessboard[top_node.x_p][top_node.y_p] = top_node.position
            tree.append(top_node)                           #a node zo stacku sa prida do tree
            break                                           #koniec
        else:
            del top_tree
            top_tree = tree.pop()                           #ak nie tak sa popne dalsi uzol z tree
            chessboard[top_tree.x_p][top_tree.y_p] = 0      #a jeho pozicia na sachovnici sa nastavi na 0
    del top_tree
    del top_node
    return False


#....zistovanie dalsich krokov z aktualnej pozicie.................................................
def next_move(prev_node, chessboard, now_x, now_y):
    free_pos = is_in_board_and_free(chessboard, now_x, now_y)
    next_nodes = []                                             #pole na nove uzly
    for i in range(len(free_pos)):                              #vytvoria sa nove mozne uzly
        node = Node(now_x + move_x[free_pos[i]], now_y + move_y[free_pos[i]], prev_node.position + 1, prev_node)
        next_nodes.append(node)
        del node

    if len(free_pos) != 0:                                      #ak aspon jeden volny dalsi stav
        index, next_nodes, warnsdorff_list = warnsdorff(chessboard, next_nodes)
                                                                #warnsdorff vrati pole uzlov a index s najlacnejsim dalsim
        if index == SPECIAL:                                    #ak vratil warnsdorff vrati SPECIAL ako index...
            return SPECIAL                                      #tak sa bude vraciat a hladat uzlt zo stacku

        chessboard[next_nodes[index].x_p][next_nodes[index].y_p] = next_nodes[index].position
        tree.append(next_nodes[index])                          #vybrany uzol pridam ku tree

        sort_out_neighbor_nodes(next_nodes, warnsdorff_list, index)
    else:                                                       #toto by nemalo nastat
        print('len(free_pos) == 0, ale nemalo by toto nikdy nastat')
        return True

    if tree[len(tree) - 1].position == board_size ** 2:         #ak to bol posledny finalny krok tak nastavim
        global end_statement_symbol                             #end_statement_symbol a vratim True aby nepokracoval while
        end_statement_symbol = 1
        return True

    return False


#....Warnsdorffova heuristika..zistovanie vahy dalsich dalsich krokov..............................
def warnsdorff(chessboard, new_nodes):
    possible_next_moves_of_nodes = []
    min_index = -1
    num_of_zeros = 0

    #..zistujem VDT a zapisem v indexovom poradi do possible_next_moves_of_nodes
    for i in range(len(new_nodes)):
        free_pos = is_in_board_and_free(chessboard, new_nodes[i].x_p, new_nodes[i].y_p)
        possible_next_moves_of_nodes.append(len(free_pos))

    #..ak to nieje posledna node
    if (new_nodes[0].position < (board_size ** 2)) and (len(possible_next_moves_of_nodes) > 0):
                                        #..zistujem ci VDT je 0
        for i in range(len(possible_next_moves_of_nodes)):
            if possible_next_moves_of_nodes[i] == 0:
                num_of_zeros += 1

                                        #..pripad kedy sa idem vracat a hladat novu node zo stocku
        if (len(possible_next_moves_of_nodes) == 1) and (possible_next_moves_of_nodes[0] == 0):
            return SPECIAL, new_nodes, possible_next_moves_of_nodes

        if num_of_zeros == 0:           #..ak je num_of_zeros 0 tak pokracujem
            pass
        elif num_of_zeros == 1:         #..ak je num_of_zeros 1 tak tu node popnem
            for i in range(len(possible_next_moves_of_nodes)):
                if possible_next_moves_of_nodes[i] == 0:
                    new_nodes.pop(i)
                    possible_next_moves_of_nodes.pop(i)
                    break
        else:                       #..ak je num_of_zeros > 1
                                        #..ak niesu same 0 tak ich popnem z new_nodes a z possible_next_moves_of_nodes
            if any(possible_next_moves_of_nodes) != 0:
                iterator = 0
                list_len = len(possible_next_moves_of_nodes)
                for i in range(list_len):
                    if possible_next_moves_of_nodes[iterator] == 0:
                        new_nodes.pop(iterator)
                        possible_next_moves_of_nodes.pop(iterator)
                        iterator -= 1
                    iterator += 1
                pass
            else:                       #..su same nuly, idem sa vraciat a hladat novu node
                return SPECIAL, new_nodes, possible_next_moves_of_nodes

        min_index = possible_next_moves_of_nodes.index(min(possible_next_moves_of_nodes))

    elif (len(possible_next_moves_of_nodes) == 0) and (new_nodes[0].position < (board_size ** 2)):
        print('Nastal pripad, ktory som si myslel ze nenastane')
    else:                       # je to posledna node s poradim board_size ** 2
        min_index = 0

    return min_index, new_nodes, possible_next_moves_of_nodes


if __name__ == "__main__":
    #get_parameters()
    starting_points = one_time_inputs()                         #ci 10 uz zadanych zaciatocnych pozicii alebo po jednej

    while True:                                                 #po skonceny sa bude opakovat
        if starting_points:                                     #kvoli tomu prezentovaniu
            if len(prese_list_x) == 0:
                print('End of predetermined starting points')
                starting_points = False
                continue
            now_x = prese_list_x.pop(len(prese_list_x) - 1)
            now_y = prese_list_y.pop(len(prese_list_y) - 1)
        else:
            board_size = get_input()                            #ak by nebola moznost s listom zac. pozicii tak by toto bolo
            now_x, now_y = get_starting_point()

        time_start = time.perf_counter()                        #odtialto sa pocita cas
        chessboard = [[0 for i in range(board_size)] for j in range(board_size)]    #inicializujem chessboard
        chessboard[now_x][now_y] = 1                            #urcim zaciatocnu poziciu
        root = set_root(now_x, now_y)                           #urcim root
        tree.append(root)
        print_board(chessboard)                                 #vypisem root
        print()
        b = False
        counter = 0

        while not b:                                            #tu sa zacina hladanci cyklus

            if (counter + 1) > input_parameters[1]:                 #ak je pocet krokov prektoceny tak break
                end_statement_symbol = 4
                break
            counter += 1
            if input_parameters[2]:                                 #vypis krokov ak to je tak zadane v parametroch
                print(counter)
                                                                    #hlada sa dalsia pozicia
            b = next_move(tree[len(tree) - 1], chessboard, tree[len(tree) - 1].x_p, tree[len(tree) - 1].y_p)

            if b == SPECIAL:                                        #ak 1 tak uz neni dalsia pozicia a idem sa vraciat
                b = False
                if backing_up(chessboard):                          #vrati 1 ak je stack prazdny a tak koniec
                    end_statement_symbol = 2
                    break
            if end_statement_symbol != 1 and input_parameters[2]:   #vypise krok ak nieje uspesny koniec a moze(parametre)
                print_board(chessboard)
                print()
            time_now = time.perf_counter()
            if (time_now - time_start) >= input_parameters[0]:       #ak sa presiahol cas tak break
                end_statement_symbol = 3
                time_now = time_now - time_start                    #zisti sa cas trvania
                break
                                                                #koniec cyklu hladania
        time_fin = time.perf_counter() - time_start             #zisti sa cas trvania
        end_statement(end_statement_symbol, time_fin)           #vypis na koniec
        end_statement_symbol = -1
        tree.clear()                                            #vycistim stack aj tree
        stack.clear()

        print()
        go_again = input('Continue? [Y/n]')
        if go_again == 'y' or go_again == 'Y':                  #ci pokracovat alebo koniec
            print('-------------------------------------------------')
        else:
            break
