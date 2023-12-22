
class EntityInfo(object):
    
    
    def __init__(self, name):
        
        self.name = name        
        self.marks = dict()
        self.annotations = list()
        self.cuts = list()
        self.previous_cuts = list()
        self.processed = list()
             
             
    def set_start(self, frame, mask):
                
        self.marks[frame] = {"start": True, 
                             "mask": mask}
    
    
    def set_end(self, frame, mask):
        
        self.marks[frame] = {"start": False, 
                             "mask": mask}
    
    
    def set(self, frame, mask, mode):
    
        self.marks[frame] = {"start": mode == "start", 
                             "mask": mask}
    
    
    def counts(self):
        
        sorted_keys = sorted(self.marks.keys())
        
        expect_start = True
        count = 0
        
        for k in sorted_keys:
            
            if expect_start and self.marks[k]["start"]:
                expect_start = False
            else:
                count += 1
                expect_start = True
        
        return count
    
    
    def get_info(self):
        
        return {"start": self.starting_frame,
                "end": self.ending_frame,
                "mask_1": self.starting_mask,
                "mask_2": self.ending_mask }
    
    
    def get_sequences(self):
        
        sorted_keys = sorted(self.marks.keys())
        
        expect_start = True
        count = 0
        sequences = list()
        
        for k in sorted_keys:
            
            if expect_start and self.marks[k]["start"]:
                expect_start = False
                start_frame = k
                start_mask = self.marks[k]["mask"]
            else:
                count += 1
                expect_start = True

                sequences.append({"start": start_frame,
                                  "end": k,
                                  "mask_1": start_mask,
                                  "mask_2": self.marks[k]["mask"] })
                
        return sequences
        
        
    def add_annotation(self, annotation):
        
        self.annotations.append(annotation)
        
        
    def set_cut_status(self, index, status):
        
        for i in range(len(self.cuts)):
            if self.cuts[i][0] == index:
                self.cuts[i] = (index, status)
                break