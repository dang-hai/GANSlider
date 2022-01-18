from uuid import uuid4
import pandas as pd

from itertools import product
import numpy as np

class UserStudy:
    def __init__(self):
        self.count = 0

    def next(self, pid):
        seed = [ord(c) for c in pid]
        np.random.seed(seed)

        types = ["REGULAR", "FILMSTRIP"]
        num_sliders = [1,2,3,4,5,8,10]
        target_edits = [[(j, np.round(np.random.uniform(-5, 5), decimals=1)) for j in range(i)] for i in num_sliders]
        seeds = [np.random.randint(1, 9999) for _ in num_sliders]

        combinations = product(types, target_edits)

        tmp = pd.DataFrame.from_records(list(combinations))
        tmp.columns = ["slider_type", "targ_edit"]
        tmp['edits'] = tmp['targ_edit'].apply(lambda ls: [(i, 0.0) for i in range(len(ls))])
        tmp['seed'] = np.hstack([np.random.permutation(seeds), np.random.permutation(seeds)])
        tmp['pid'] = self.count
        tmp['taskid'] = [str(uuid4()) for i in range(tmp.shape[0])]

        if (self.count % 2 == 0):
            tmp = tmp.sort_values(by="slider_type")

        df = tmp.set_index(['pid'])

        self.count += 1

        return df.to_dict(orient="records")


if __name__ == "__main__":
    ctl = UserStudy()
    iterator = ctl.iter()
    print(next(iterator))
    print(next(iterator))
    print(next(iterator))

