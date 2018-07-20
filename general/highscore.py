DIFFICULTIES = ['Very Easy', 'Easy', 'Normal', 'Hard', 'Insane']


def generate_highscore_file(file):
    with open(file, 'w') as f:
        for i in range(5):
            names = []
            times = []
            for j, name in enumerate('ABCDE'):
                names.append(name*(i+1))
                times.append('{:02d}:00:0'.format((j+1)*(i+1)))
            info = [','.join([name, time]) for name, time in zip(names, times)]
            f.write('\n'.join(info))
            if not i == 4:
                f.write('\n---\n')


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


def write_highscore_file(file, data):
    with open(file, 'w') as f:
        for diff in DIFFICULTIES:
            info = [','.join([placing_info['name'], placing_info['time']]) for placing_info in data[diff]]
            f.write('\n'.join(info))
            if not diff == DIFFICULTIES[-1]:
                f.write('\n---\n')


def replace_placing(data, difficulty, name, time):
    for i, info in enumerate(data[difficulty]):
        if time < info['time']:
            data[difficulty].insert(i, {'name': name, 'time': time})
            data[difficulty].pop(-1)
            break


def check_ranking(data, difficulty, time):
    rank = -1
    for rnk, info in enumerate(data[difficulty]):
        if time < info['time']:
            rank = rnk
            break
    return rank


if __name__ == "__main__":
    #score = read_highscore_file("./highscore.txt")
    #replace_placing(score, DIFFICULTIES[2], 'abcv', 12345)
    #write_highscore_file("./new_highscore.txt", score)
    generate_highscore_file("./highscore.txt")
