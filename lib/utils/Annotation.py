
class Annotation:

    # class to handle the creation of the annotations 
    # for the videos loaded in the graphical user interface

    def __init__(self, frames):

        # initializes the structure with the empty annotation

        self.annotations = [[1, frames, None]]
        self.frames = frames

    def clear(self):

        # empties the current annotations

        self.annotations = [[1, self.frames, None]]

    def add_annotation(self, start, end, name):

        # adds the specified annotation to the list

        new_annotations = []
        stop = False

        if start < 0:
            start = 1

        if end > self.frames:
            end = self.frames

        if end < start:
            return

        # head insertion
        if start == self.annotations[0][0]:
            new_annotations.append([start, end, name])

            for i in range(0, len(self.annotations)):

                if stop:
                    break

                if self.annotations[i][1] > end:
                    self.annotations[i][0] = end + 1

                    if self.annotations[i][0] <= self.annotations[i][1]:
                        new_annotations.append(self.annotations[i])

                        for j in range(i + 1, len(self.annotations)):
                            new_annotations.append(self.annotations[j])

                        stop = True

        # tail insertion
        elif end == self.frames:

            i = 0

            while self.annotations[i][1] < start:
                new_annotations.append(self.annotations[i])
                i += 1

            self.annotations[i][1] = start - 1

            if self.annotations[i][1] >= self.annotations[i][0]:
                new_annotations.append(self.annotations[i])

            new_annotations.append([start, end, name])
    
        # in-the-middle insertion
        else:
            
            i = 0

            while self.annotations[i][1] < start:
                new_annotations.append(self.annotations[i])
                i += 1

            if self.annotations[i][1] < end:

                self.annotations[i][1] = start - 1

                if self.annotations[i][0] <= self.annotations[i][1]:
                    new_annotations.append(self.annotations[i])

                i += 1

                new_annotations.append([start, end, name])

                while self.annotations[i][1] < end:
                    i += 1

                self.annotations[i][0] = end + 1

                if self.annotations[i][0] <= self.annotations[i][1]:
                    new_annotations.append(self.annotations[i])

                i += 1

                while i < len(self.annotations):
                    new_annotations.append(self.annotations[i])
                    i += 1

            else:
                
                temp = self.annotations[i].copy()

                temp[1] = start - 1

                if temp[0] <= temp[1]:
                    new_annotations.append(temp)

                new_annotations.append([start, end, name])

                self.annotations[i][0] = end + 1

                if self.annotations[i][0] <= self.annotations[i][1]:
                    new_annotations.append(self.annotations[i])

                i += 1

                while i < len(self.annotations):
                    new_annotations.append(self.annotations[i])
                    i += 1

        self.annotations = new_annotations
        # self.merge_annotations()

    def merge_annotations(self):

        # merges subsequent annotations with common labels

        i = 0

        if len(self.annotations) > 1:
            while i < len(self.annotations) - 1:
                if self.annotations[i][2] == self.annotations[i+1][2]:
                    self.annotations[i][1] = self.annotations[i+1][1]
                    del self.annotations[i+1]
                else:
                    i +=1 

    def print_annotations(self):

        # prints all the annotations saved

        print("---------------")
        for i in range(0, len(self.annotations)):
            print(self.annotations[i])

    def get_annotation_by_frame(self, frame):

        # given a frame, returns the corresponding annotation, if available

        if frame < self.annotations[0][0] or frame > self.annotations[-1][1]:
            return None, None, None

        i = 0

        while self.annotations[i][1] < frame:
            i += 1

        return self.annotations[i][2], self.annotations[i][0], self.annotations[i][1]

if __name__ == "__main__":
    
    ann = Annotation(100)
    ann.add_annotation(20,25,0)
    ann.add_annotation(70,80,0)
    ann.print_annotations()   
    print()
    ann.clear()
    
    ann.add_annotation(20,25,0)
    ann.add_annotation(55,75,0)
    ann.add_annotation(70,80,0)
    ann.print_annotations()    
    print()
    ann.clear()
    
    ann.add_annotation(20,25,0)
    ann.add_annotation(70,80,0)
    ann.add_annotation(75,85,0)
    ann.print_annotations()
    print()
    ann.clear()
    
    ann.add_annotation(20,25,0)
    ann.add_annotation(75,85,0)
    ann.add_annotation(70,80,0)
    ann.print_annotations()
