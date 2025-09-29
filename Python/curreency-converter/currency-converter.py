import random

def generate_number():
    digits=list(range(10))
    random.shuffle(digits)
    return ''.join([str(digit) for digit in digits[:4]])

def cal_cow_bull(secret,guess):
    bull= sum([1 for i in range(4) if guess[i]==secret[i]])
    cow=sum([1 for i in range(4) if guess[i] in secret])-bull
    
    return cow,bull

def main():
    secret = generate_number()
    print("System have generated a 4-Digit number,Try to guess...!")

    while True:
        guess= input('Guess :')
        if len(guess)==4 and guess.isdigit and len(set(guess))==4:
            cow,bull = cal_cow_bull(secret,guess)
            print(f"{cow} Cows & {bull} Bull")

            if bull == 4:
                print("You have guessed the Corrrct number!!!")
                break
            else:
                print("Wrong Guess...Give it a another try enter 4-Digit number.")

if __name__=='__main__':
    main()
    