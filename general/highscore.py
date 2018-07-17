DIFFICULTIES = ['Very Easy', 'Easy', 'Medium', 'Hard', 'Insane']

def read_highscore_file(file):
    with open(file, 'r') as f:
        file_data = f.read()

    highscore_list = {}
    for diff, data in zip(DIFFICULTIES, file_data.split('\n---\n')):
        diff_list = []
        for line in data.split('\n'):
            info = {}
            placing_info = line.split(',')
            info['name'] = placing_info[0]
            info['time'] = placing_info[1]
            diff_list.append(info)
        highscore_list[diff] = diff_list

    return highscore_list


def write_highscore_file(data):
    pass


if __name__ == "__main__":
    score = read_highscore_file("./highscore.txt")