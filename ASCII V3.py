import random
import time
import os

# ============================
#  ADVANCED STATIC CATEGORIES
# ============================

ascii_art = {
    "advanced-animals": [
        r"""
           |\__/,|   (`\
           |o o  |__ _) )
         _.( T   )  `  /
       (((`-'(((____.'
        """,

        r"""
             /\_____/\
            /  o   o  \
           ( ==  ^  == )
            )         (
           (           )
          ( (  )   (  ) )
         (__(__)___(__)__)
        """,

        r"""
              .--.
             (    )
            (______)
           (________)
         (____________)
        (______________)
        """,
    ],

    "advanced-shapes": [
        r"""
           ___________
         /           \
        /             \
       |               |
       |               |
        \             /
         \___________/
        """,

        r"""
           *     *
        *     *     *
      *     * * *     *
        *     *     *
           *     *
        """,

        r"""
        .---------------------.
        |   COMPLEX SHAPE     |
        |   ASCII GEOMETRY    |
        '---------------------'
        """,
    ],

    "advanced-robots": [
        r'''
          [:::: ROBOT MK I ::::]
              .-""""-.
             / -   -  \
            |  .-. .- |
            |  \o| |o (
            \     ^    \
             '.  )--'  /
               '-...-'`
        ''',

        r"""
        [:::: SENTINEL UNIT ::::]
              _____
           .-"     "-.
          /           \
         |  .--. .--.  |
         | (    Y    ) |
         (  '--' '--'  )
          \           /
           '-._____.-'
           / /  |  \ \
          /_/   |   \_\
        """,

        r"""
        [:::: MECH-DRONE ::::]
             ________
          .-'        '-.
         /    .----.    \
        |   (        )   |
        |    '--.__.--'  |
         \              /
          '-.________.-'
        """
    ]
}

# ============================
#  ADVANCED ANIMATIONS
# ============================

def animate_fire():
    chars = ["^", "*", ".", "`", "'", " "]
    width = 40
    height = 12

    for _ in range(40):
        os.system("cls" if os.name == "nt" else "clear")
        print("[Animation: fire]\n")

        for y in range(height):
            row = ""
            for x in range(width):
                if y > height * 0.7:
                    row += random.choice(["^", "*", "*", "*", ".", "`"])
                elif y > height * 0.4:
                    row += random.choice(["*", ".", "`", "'"])
                else:
                    row += random.choice(chars)
            print(row)

        time.sleep(0.05)


def animate_rain():
    width = 40
    height = 12
    drops = ["|", "'", ".", "`"]

    for _ in range(40):
        os.system("cls" if os.name == "nt" else "clear")
        print("[Animation: rain]\n")

        for y in range(height):
            row = ""
            for x in range(width):
                row += random.choice(drops + [" "] * 6)
            print(row)

        time.sleep(0.07)


def animate_bounce_text():
    text = "<<< BOUNCING TEXT >>>"
    width = 50
    direction = 1
    pos = 0

    for _ in range(60):
        os.system("cls" if os.name == "nt" else "clear")
        print("[Animation: bouncing text]\n")

        print(" " * pos + text)

        pos += direction
        if pos <= 0 or pos >= width - len(text):
            direction *= -1

        time.sleep(0.05)


animated_generators = {
    "fire": animate_fire,
    "rain": animate_rain,
    "bouncing-text": animate_bounce_text
}

# ============================
#  GENERATION FUNCTIONS
# ============================

def generate_static(category):
    if category not in ascii_art:
        print(f"Category '{category}' not found.")
        return
    art = random.choice(ascii_art[category])
    print(f"\n[Static Art: {category}]\n{art}")

def generate_animation(name):
    if name not in animated_generators:
        print(f"Animation '{name}' not found.")
        return
    animated_generators[name]()

# ============================
#  MAIN LOOP
# ============================

if __name__ == "__main__":
    while True:
        print("\nADVANCED ASCII ART ENGINE")
        print("==========================")
        print("Static:", ", ".join(ascii_art.keys()))
        print("Animated:", ", ".join(animated_generators.keys()))
        print("\nType a static category or animation name.")

        choice = input("> ").strip().lower()

        if choice in ascii_art:
            generate_static(choice)
        elif choice in animated_generators:
            generate_animation(choice)
        else:
            print("Unknown option.")

        again = input("\nGenerate again (y/n): ").strip().lower()
        if again != "y":
            break