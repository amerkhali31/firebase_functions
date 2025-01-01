from random import seed, randint

def generate_daily_random_number(seed_date):
    seed = seed_date.day * seed_date.month + seed_date.year
    # Use the current date as the seed for the random number generator
    seed(seed)
    
    # Generate a random number between 1 and 7563
    return randint(1, 7563)

