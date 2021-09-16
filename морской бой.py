from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Мимо доски!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "В эту клетку уже стреляли"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'({self.x},{self.y})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Ship:
    def __init__(self, len_s, nos, naprav):
        self.len_s = len_s  # длинна корабля
        self.nos = nos  # координата носа
        self.naprav = naprav  # вертикаль/горизонталь расположение корабля
        self.lives = len_s  # сколько осталось попаданий

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.len_s):
            temp_x = self.nos.x
            temp_y = self.nos.y
            if self.naprav == 0:
                temp_x += i
            elif self.naprav == 1:
                temp_y += i
            ship_dots.append(Dot(temp_x, temp_y))
        return ship_dots

    def popal(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid=False, ship_live=4, size=6):
        self.cell = [["O"] * 6 for _ in range(6)]  # игровое поле
        self.ships = []  # список кораблей
        self.hid = hid  # видимость доски
        self.ship_live = ship_live  # количество живых кораблей
        self.busy = []
        self.count = 0

    def add_ship(self, ship):
        for p in ship.dots:
            if self.out(p) or p in self.busy:
                raise BoardWrongShipException()

        self.ships.append(ship)
        for p in ship.dots:
            self.cell[p.x][p.y] = '■'
            self.busy.append(p)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, hid_con=False):
        sdvig = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for p in ship.dots:
            for px, py in sdvig:
                temp = Dot(p.x + px, p.y + py)
                if not (self.out(temp)) and temp not in self.busy:
                    if hid_con:
                        self.cell[temp.x][temp.y] = "Т"
                    self.busy.append(temp)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.cell):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, p):
        return not ((0 <= p.x < 6) and (0 <= p.y < 6))

    def shot(self, p):
        if self.out(p):
            raise BoardOutException()
        if p in self.busy:
            raise BoardUsedException()
        self.busy.append(p)
        for ship in self.ships:
            if p in ship.dots:
                ship.lives -= 1
                self.cell[p.x][p.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, hid_con=True)
                    print("Корабль убит!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.cell[p.x][p.y] = "Т"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(l, Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска игрока:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит игрок!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Игрок выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.loop()

class Player:
    def __init__(self, board, other_board):
        self.board = board
        self.other_board = other_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.other_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        p = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {p.x + 1} {p.y + 1}")
        return p

class User(Player):
    def ask(self):
        while True:
            cords = input("Ход игрока: ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue
            x, y = int(x), int(y)
            print(x, y)
            return Dot(x - 1, y - 1)

g = Game()
g.start()