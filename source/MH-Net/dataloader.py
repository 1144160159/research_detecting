import dgl
from dgl.data import DGLDataset

from config import Config

config = Config()

class MixTrafficFlowDataset4DGL(DGLDataset):
    def __init__(self, hetro_path,  bit_hetro_path , point, perc=1.0):
        self.hetro_path = hetro_path
        self.bit_hetro_path = bit_hetro_path
        self.point = point
        self.perc = perc
        super(MixTrafficFlowDataset4DGL, self).__init__(name="MixTrafficFlowDataset4DGL")

    def process(self):
        self.hetro_data,self.label = dgl.load_graphs(self.hetro_path)
        self.bit_hetro_data , self.label= dgl.load_graphs(self.bit_hetro_path)
        self.label = self.label["glabel"]
        
        trunc_index = int(self.perc * len(self.hetro_data) / config.FLOW_PAD_TRUNC_LENGTH)
        self.label = self.label[:trunc_index]
        
        self.hetro_data = self.hetro_data[:int(trunc_index * config.FLOW_PAD_TRUNC_LENGTH)]
        self.bit_hetro_data = self.bit_hetro_data[:int(trunc_index * config.FLOW_PAD_TRUNC_LENGTH)]
        
        self.hetro_mask = []
        self.bit_hetro_mask = []
        
        for sg in self.hetro_data:
            if int(sg.num_nodes('header') == 0) or int(sg.number_of_edges(etype = 'h')) == 0 or int(sg.num_nodes('payload') == 0) or int(sg.num_nodes('header_p') == 0) \
                or int(sg.number_of_edges(etype = 'p')) == 0 or int(sg.number_of_edges(etype = 'h_p')) == 0:
                self.hetro_mask.append(False)
            else:
                self.hetro_mask.append(True)
        
        for sg in self.bit_hetro_data:
            if int(sg.num_nodes('header') == 0) or int(sg.number_of_edges(etype = 'h')) == 0 or int(sg.num_nodes('payload') == 0) or int(sg.num_nodes('header_p') == 0) \
                or int(sg.number_of_edges(etype = 'p')) == 0 or int(sg.number_of_edges(etype = 'h_p')) == 0:
                self.bit_hetro_mask.append(False)
            else:
                self.bit_hetro_mask.append(True)

        print(len(self.hetro_data),len(self.bit_hetro_data))
        print(len(self.label))
        
    def __getitem__(self, index):
        start_ind = config.FLOW_PAD_TRUNC_LENGTH * index
        
        return  self.hetro_data[start_ind:start_ind+self.point], self.bit_hetro_data[start_ind:start_ind+self.point], self.label[index],\
            self.hetro_mask[start_ind:start_ind+self.point], self.bit_hetro_mask[start_ind:start_ind+self.point]

    def __len__(self):
        return int(len(self.hetro_data) / config.FLOW_PAD_TRUNC_LENGTH)

if __name__ == '__main__':
    pass
