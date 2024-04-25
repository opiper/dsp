import numpy as np

item_sizes_queue = np.random.randint(1, 4, size=125).tolist()
warehouse = np.zeros((3, 5, 5))



for item_size in item_sizes_queue:
    placed = False
    for height_index in range(warehouse.shape[0]):
        for row_index in range(warehouse.shape[1]):
            for col_index in range(warehouse.shape[2]):
                if warehouse[height_index][row_index][col_index] + item_size <= 5:
                    warehouse[height_index][row_index][col_index] += item_size
                    placed = True
                    break
            if placed:
                break
        if placed:
            break

print(warehouse)