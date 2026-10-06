import random
import time


def clear_screen() -> str:
    """Return the terminal escape sequence needed to clear the current screen."""
    return "\033[2J\033[H"


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
    ],
    "advanced-space": [
        r"""
                 .          *       .
            *         .-.
                 .   (   )     *
          .          `-'       .       *
                  *       .         .
        """,
        r"""
             .       *       .
        *        .        .       *
             ____             .
          .-'    `-.    *
         /  .--.    \
         | (____)   |       .
          \        /
        *  `-.__.-'      .
        """,
    ],
    "advanced-vehicles": [
        r"""
             ______
        ____/|_||_\`.__
       (   _    _ _\  _\
       =`-(_)--(_)-'---'
        """,
        r"""
              __o
            _ \<_
           (_)/(_)
        """,
    ],
}

# ============================
#  ADVANCED ANIMATIONS
# ============================

def animate_fire():
    chars = ["^", "*", ".", "`", "'", " "]
    width = 40
    height = 12

    for _ in range(40):
        print(clear_screen(), end="")
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
        print(clear_screen(), end="")
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
        print(clear_screen(), end="")
        print("[Animation: bouncing text]\n")

        print(" " * pos + text)

        pos += direction
        if pos <= 0 or pos >= width - len(text):
            direction *= -1

        time.sleep(0.05)

def animate_starfield():
    width = 50
    height = 14
    stars = [" ", " ", " ", ".", "+", "*"]

    try:
        while True:
            print(clear_screen(), end="")
            print("[Animation: starfield] Press Ctrl+C to return to the menu\n")
            for _ in range(height):
                print("".join(random.choice(stars) for _ in range(width)))
            time.sleep(0.12)
    except KeyboardInterrupt:
        print(clear_screen(), end="")


animated_generators = {
    "fire": animate_fire,
    "rain": animate_rain,
    "bouncing-text": animate_bounce_text,
    "starfield": animate_starfield,
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
        print("Type a category or animation name. Commands: list, random, help, quit")

        choice = input("> ").strip().lower()

        if choice in {"q", "quit", "exit"}:
            break
        if choice in {"list", "help"}:
            print("\nStatic:", ", ".join(ascii_art))
            print("Animated:", ", ".join(animated_generators))
            print("Use Ctrl+C to stop an animation early.")
            continue
        if choice in {"random", "surprise"}:
            choices = [("static", name) for name in ascii_art] + [
                ("animation", name) for name in animated_generators
            ]
            kind, name = random.choice(choices)
            print(f"Surprise: {name}")
            if kind == "static":
                generate_static(name)
            else:
                generate_animation(name)
            continue
        if choice in ascii_art:
            generate_static(choice)
        elif choice in animated_generators:
            generate_animation(choice)
        else:
            print("Unknown option.")
