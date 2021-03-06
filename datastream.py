import numpy as np
import pickle

class TortillaDataStream:
    """
    A TortillaDataStream represents a temporal stream of values, which can be
    scalars or tensors.
    They first get stored in a buffer, and whenever the buffer length is exceeded beyond a threshold,
    the value in the buffer is pushed into the actual datastream.
    a max_buffer_length of 1 can be used in the case all the values want to be stored
    """

    def __init__(self, name, column_names=False,
                merge_mode="weighted_mean",
                max_buffer_length=10**10):
        self.name = name
        self.column_names = column_names
        self.max_buffer_length = max_buffer_length
        self.merge_mode = merge_mode

        self.datastream = []

        self.reset_buffer()

    def reset_buffer(self):
        # Important to intialize like this,
        # as we want the buffer to be flexible in picking up the data shape
        # with the first addition to the buffer
        self.buffer_empty = True
        self.buffer = False
        self.buffer_length = 0

    def merge_with_buffer(self, d):
        if self.merge_mode == "weighted_mean":
            weight_of_buffer = (float(self.buffer_length)/(self.buffer_length+1))
            weight_of_new_data = 1 - weight_of_buffer
            return weight_of_buffer*self.buffer + (weight_of_new_data * d)
        elif self.merge_mode == "sum":
            return self.buffer + d
        else:
            raise("merge_mode `\"{}`\" not implemented !".format(self.merge_mode))

    def add_to_buffer(self, d):
        if self.buffer_length >= self.max_buffer_length:
            self.flush_buffer()

        if not self.buffer_empty:
            assert type(d) == type(self.buffer)

            self.buffer = self.merge_with_buffer(d)
        else:
            self.buffer = d

        self.buffer_empty = False
        self.buffer_length += 1

    def flush_buffer(self):
        # TODO: Add checks to ensure that the buffer is of the same shape
        #       as the datastream elements
        if not self.buffer_empty:
            self.datastream.append(self.buffer)
        self.reset_buffer()
        # print(self.name, self.get_last())

    def get_last(self):
        return self.datastream[-1]

        if not self.buffer_empty:
            return self.datastream[-1]
        else:
            return None

    def dump(self, path):
        self.flush_buffer()
        pickle.dump(self.datastream, open(path, "wb"))


if __name__ == "__main__":
    ds = TortillaDataStream(name="test", column_names=["a", "b", "c"])
    ds.add_to_buffer(np.array([1,2,3]))
    print(ds.buffer)
    assert ds.buffer.all() == np.array([1,2,3]).all()
    ds.add_to_buffer(np.array([1,2,3]))
    print(ds.buffer)
    assert ds.buffer.all() == np.array([1,2,3]).all()
    ds.add_to_buffer(np.array([1,2,3]))
    print(ds.buffer)
    assert ds.buffer.all() == np.array([1,2,3]).all()
    ds.flush_buffer()
    print(ds.datastream)
    assert len(ds.datastream) == 1
    assert ds.get_last().all() == np.array([1,2,3]).all()
    ds.dump("test.pickle")
