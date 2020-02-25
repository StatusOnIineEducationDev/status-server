import json

if __name__ == '__main__':
    record_dict = {
        'uid': '1',
        'course_id': '1',
        'lesson_id': '1',
        'begin_timestamp': 1,
        'end_timestamp': 1,
        'conc_score': 1
    }

    print(json.dumps(record_dict))

