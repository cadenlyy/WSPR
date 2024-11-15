class ordered_list:
    items = [];
    def add(self, v, low = 0,high = None, key = lambda a,i: a[i]):
        if high == None:
            high = len(self.items)-1
        if len(self.items) == 0:
            self.items.append(v)
        elif high >= low:
            mid = (high + low) // 2
            if self.items[mid] == v:
                self.items.insert(mid+1, v)
            elif key(self.items,mid,v):
                self.add(v, low, mid - 1, key)
            else:
                self.add(v, mid + 1, high, key)
        else:
            self.items.insert(low, v)
            
            
ol = ordered_list()

d = [{'lat': 1},{'lat': 2},{'lat': -1},{'lat': 4}]


def comp(arr,a,b):
    return arr[a].get('lat') < b.get('lat')

for i in d:
    ol.add(i, key = comp)
    
print(ol.items)