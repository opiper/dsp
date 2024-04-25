import numpy as np


class WarehouseEnvironment:
    def __init__(self, dimensions, max_capacity):
        self.dimensions = dimensions
        self.max_capacity = max_capacity
        self.warehouse = np.zeros(dimensions)
        
    def is_placeable(self, item, position):
        """Check if the item can be placed at the specified position."""
        x, y, z = position
        return self.warehouse[x, y, z] + item <= self.max_capacity
    
    def place_item(self, item, position):
        """Place the item at the specified position."""
        x, y, z = position
        if self.is_placeable(item, (x, y, z)):
            self.warehouse[x, y, z] += item
            return True
        return False
    
    def try_to_place_item(self, item):
        """Try to place an item in the first available spot."""
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                for z in range(self.dimensions[2]):
                    if self.place_item(item, (x, y, z)):
                        return True
        return False

class ItemGenerator:
    def __init__(self, num_items, low_size, high_size):
        self.num_items = num_items
        self.low_size = low_size
        self.high_size = high_size
    
    def generate_items(self):
        """Generate a list of item sizes."""
        return np.random.randint(self.low_size, self.high_size, size=self.num_items).tolist()

def main():
    num_items = 125
    item_size_range = (1, 4)
    warehouse_dimensions = (3, 5, 5)
    max_capacity_per_position = 5

    # Setup environment
    env = WarehouseEnvironment(warehouse_dimensions, max_capacity_per_position)
    
    # Generate items
    generator = ItemGenerator(num_items, *item_size_range)
    items = generator.generate_items()

    # Process each item
    for item in items:
        env.try_to_place_item(item)
    
    print(env.warehouse)

if __name__ == "__main__":
    main()
