dec= input("Enter the Decimal number :")
parts=dec.split(".")
binary_ip=[]

for part in parts:
    binary_ip.append(format(int(part),"08b"))


print(".".join(binary_ip))

bina=input("Enter a Binary Adress")
partss=bina.split(".")
decimal_ip=[]

for part in partss:
    decimal_ip.append(str(int(part,2)))

print(".".join(decimal_ip))
#added a comment
