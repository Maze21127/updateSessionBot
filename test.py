
def remove_from_file(string: str, file: str):
    with open(file, 'r') as f:
        names = [i.strip() for i in f.readlines()]
    with open(file, 'w') as f:
        f.write("\n".join([i for i in names if i != string]))


with open('app/static/files/names.txt', 'r') as file:
    names = [i.strip() for i in file.readlines()]

remove_from_file('kupityprav2d', 'app/static/files/names.txt')

