import random
import sqlite3
from sqlite3 import Connection

import bcrypt

# global var
conn: Connection = None


class Player:

    def __init__(self, name, points):
        self.name = name
        self.points = points


def calPts(roll1, roll2):
    pts = roll1 + roll2
    if roll1 % 2 == 0 and roll2 % 2 == 0:
        print("Both even! points +10!")
        pts += 10
    if roll1 % 2 == 1 and roll2 % 2 == 1:
        print("Both odd! points -5!")
        pts -= 5
    if roll1 == roll2:
        print("Rolled a double! Extra roll!")
        roll3 = rollADice()
        print(f"Roll 3: {roll3}")
        pts += roll3
    print(f"points gained this round: {pts}")
    return pts


def rollADice():
    input("press enter to roll")
    return random.randint(1, 6)


def roll(player):
    print(f"{player.name}'s turn!")
    roll1 = rollADice()
    print(f"Roll 1: {roll1}")
    roll2 = rollADice()
    print(f"Roll 2: {roll2}")
    player.points += calPts(roll1, roll2)
    if player.points < 0:
        player.points = 0
    print(f"{player.name}'s points: {player.points}")
    print()


def turn(players):
    for player in players:
        roll(player)


def db_connection():
    global conn
    conn = sqlite3.connect("csl.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS players (id INTEGER PRIMARY KEY, name TEXT, password TEXT, points INTEGER)")
    conn.commit()


def welcome_screen():
    print("[----Welcome----]")
    print("Welcome to dice gamble!")
    print("Two players are required.")
    print()


def game():
    print("[----Game Started----]")
    players = []
    for no in range(0, 2):
        players.append(get_user())

    for turns in range(0, 5):
        turn(players)

    if players[0].points == players[1].points:
        print("Equal points!")
        print("[----Over Time----]")
    while players[0].points == players[1].points:
        turn(players)

    print("[----Game Over----]")
    for player in players:
        print(f"{player.name}'s points: {player.points}")
        update_score(player)
    if players[0].points > players[1].points:
        print("Player 1 wins!")
    elif players[0].points < players[1].points:
        print("Player 2 wins!")


def add_user():
    while True:
        print("Do you want to create new user?")
        ans = input("(Y/N): ")
        if ans.upper() == "Y":
            print("Create new user")
            cur = conn.cursor()
            name = input("Name:")
            res = cur.execute("SELECT name FROM players WHERE name = ?", (name,))
            if res.fetchone() is not None:
                print("User already exists")
                continue
            password_hash = bcrypt.hashpw(input("Password:").encode("utf-8"), bcrypt.gensalt())

            cur.execute("INSERT INTO players (name, password, points) VALUES (?, ?, ?)", (name, password_hash, 0))
            conn.commit()
        else:
            break


def get_user():
    print("Account login")

    try:
        name = input("Name: ")

        cur = conn.cursor()
        res = cur.execute("SELECT password, points FROM players WHERE name = ?", (name,))
        password_hash, points = res.fetchone()
        if bcrypt.checkpw(input("Password: ").encode("utf-8"), password_hash):
            return Player(name, points)
    except TypeError:
        pass

    print("Wrong player name or password")
    exit(1)


def update_score(player):
    cur = conn.cursor()
    res = cur.execute("SELECT points FROM players WHERE name = ?", (player.name,))
    old_points, = res.fetchone()
    if player.points > old_points:
        cur.execute("UPDATE players SET points = ? WHERE name = ?", (player.points, player.name))
        conn.commit()


def display_scores():
    print("[----Scores----]")
    cur = conn.cursor()
    res = cur.execute("SELECT name, points FROM players ORDER BY points DESC")
    no = 1
    for name, points in res.fetchall():
        print(f"no.{no} | {name}: {points}")
        no += 1


def main():
    db_connection()
    welcome_screen()
    add_user()
    game()
    display_scores()


main()
