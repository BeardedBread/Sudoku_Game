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
            time = int(placing_info[1])
            info['time'] = "{:02d}:{:02d}.{:1d}".format(int(time / 600), int(time / 10) % 60, time % 10)
            diff_list.append(info)
        highscore_list[diff] = diff_list

    return highscore_list


def write_highscore_file(file, data):
    with open(file, 'w') as f:
        for diff in DIFFICULTIES:
            info = [','.join([placing_info['name'], str(placing_info['time'])]) for placing_info in data[diff]]
            f.write('\n'.join(info))
            if not diff == DIFFICULTIES[-1]:
                f.write('\n---\n')


def replace_placing(data, difficulty, name, time):
    for info in data[difficulty]:
        if time < info['time']:
            info['name'] = name
            info['time'] = time
            break


def check_ranking(data, difficulty, name, time):
    rank = -1
    for rnk, info in enumerate(data[difficulty]):
        if time < info['time']:
            info['name'] = name
            info['time'] = time
            rank = -1
            break
    return rank


if __name__ == "__main__":
    score = read_highscore_file("./highscore.txt")
    replace_placing(score, DIFFICULTIES[2], 'abcv', 12345)
    write_highscore_file("./new_highscore.txt", score)